const { app, BrowserWindow, dialog, session, ipcMain } = require('electron');
const path = require('path');
const http = require('http');
const { spawn, execSync } = require('child_process');
const fs = require('fs');

let mainWindow = null;
let backendProcess = null;
const BACKEND_PORT = 8000;
const HEALTH_URL = `http://127.0.0.1:${BACKEND_PORT}/api/health`;

// Configure writable user-data directory
const userDataDir = path.join(app.getPath('userData'), 'ScrollixData');
if (!fs.existsSync(userDataDir)) {
  fs.mkdirSync(userDataDir, { recursive: true });
}
process.env.SCROLLIX_DATA_DIR = userDataDir;

function checkBackendHealth(retries = 30, interval = 1000) {
  return new Promise((resolve, reject) => {
    let attempts = 0;
    const check = () => {
      attempts++;
      const req = http.get(HEALTH_URL, (res) => {
        if (res.statusCode === 200) {
          resolve(true);
        } else if (attempts < retries) {
          setTimeout(check, interval);
        } else {
          reject(new Error('Backend health check returned non-200'));
        }
      });

      req.on('error', () => {
        if (attempts < retries) {
          setTimeout(check, interval);
        } else {
          reject(new Error('Could not connect to Scrollix AI backend'));
        }
      });
      req.setTimeout(800, () => req.destroy());
    };
    check();
  });
}

function startBackend() {
  const isPackaged = app.isPackaged;
  const projectRoot = path.join(__dirname, '..');

  // Check if already running on port 8000
  try {
    const net = require('net');
    const tester = net.createServer()
      .once('error', (err) => {
        if (err.code === 'EADDRINUSE') {
          console.log(`Port ${BACKEND_PORT} already active, reusing existing backend instance.`);
        }
      })
      .once('listening', () => {
        tester.close();
        launchProcess();
      })
      .listen(BACKEND_PORT, '127.0.0.1');
  } catch (e) {
    launchProcess();
  }

  function launchProcess() {
    const candidates = [
      path.join(process.resourcesPath || '', 'scrollix_backend.exe'),
      path.join(__dirname, '..', 'resources', 'scrollix_backend.exe'),
      path.join(projectRoot, 'backend_dist', 'scrollix_backend.exe'),
      path.join(projectRoot, 'backend', 'dist', 'scrollix_backend', 'scrollix_backend.exe')
    ];

    let backendExe = null;
    for (const cand of candidates) {
      if (cand && fs.existsSync(cand)) {
        backendExe = cand;
        break;
      }
    }

    function spawnPythonFallback() {
      const pythonScript = path.join(projectRoot, 'backend', 'app', 'main.py');
      console.log('Spawning Python backend fallback:', pythonScript);
      backendProcess = spawn('python', ['-m', 'uvicorn', 'app.main:app', '--host', '127.0.0.1', '--port', '8000'], {
        cwd: path.join(projectRoot, 'backend'),
        env: { ...process.env, SCROLLIX_DATA_DIR: userDataDir },
        shell: true
      });
      attachListeners(backendProcess);
    }

    function attachListeners(proc) {
      if (!proc) return;
      proc.stdout?.on('data', (d) => console.log(`[Backend stdout]: ${d}`));
      proc.stderr?.on('data', (d) => console.error(`[Backend stderr]: ${d}`));
      proc.on('exit', (code) => {
        console.log(`Backend process exited with code ${code}`);
        if (code !== 0 && proc === backendProcess && !app.isQuitting) {
          console.warn('Backend exited abnormally, attempting Python fallback...');
          spawnPythonFallback();
        }
      });
    }

    if (backendExe) {
      console.log('Spawning compiled backend executable:', backendExe);
      backendProcess = spawn(backendExe, [], {
        cwd: path.dirname(backendExe),
        env: { ...process.env, SCROLLIX_DATA_DIR: userDataDir },
        windowsHide: true
      });
      attachListeners(backendProcess);
    } else {
      spawnPythonFallback();
    }
  }
}

function stopBackend() {
  if (backendProcess && backendProcess.pid) {
    try {
      if (process.platform === 'win32') {
        execSync(`taskkill /F /T /PID ${backendProcess.pid}`);
      } else {
        backendProcess.kill('SIGTERM');
      }
    } catch (e) {
      // Process may already have terminated
    }
    backendProcess = null;
  }
}

function createWindow() {
  mainWindow = new BrowserWindow({
    width: 1360,
    height: 880,
    minWidth: 1024,
    minHeight: 700,
    title: 'Scrollix AI — Social Commerce & Location Video Recommendations',
    backgroundColor: '#0a0e17',
    webPreferences: {
      preload: path.join(__dirname, 'preload.js'),
      nodeIntegration: false,
      contextIsolation: true
    }
  });

  // Remove default menu bar for clean app look
  mainWindow.setMenuBarVisibility(false);

  const isDev = process.env.NODE_ENV === 'development';
  if (isDev) {
    mainWindow.loadURL('http://127.0.0.1:5173');
  } else {
    const bundledDist = path.join(__dirname, 'frontend_dist', 'index.html');
    const localDist = path.join(__dirname, '..', 'frontend', 'dist', 'index.html');
    if (fs.existsSync(bundledDist)) {
      mainWindow.loadFile(bundledDist);
    } else if (fs.existsSync(localDist)) {
      mainWindow.loadFile(localDist);
    } else {
      mainWindow.loadURL('http://127.0.0.1:5173');
    }
  }

  mainWindow.on('closed', () => {
    mainWindow = null;
  });
}

function setupSessionPermissions() {
  if (session.defaultSession) {
    session.defaultSession.setPermissionRequestHandler((webContents, permission, callback) => {
      if (permission === 'geolocation') {
        // Explicitly allow geolocation for local app window
        return callback(true);
      }
      callback(false);
    });

    session.defaultSession.setPermissionCheckHandler((webContents, permission, requestingOrigin) => {
      if (permission === 'geolocation') {
        return true;
      }
      return false;
    });
  }
}

// IPC handler providing reliable device geolocation for packaged desktop app
ipcMain.handle('get-device-location', async () => {
  return new Promise((resolve) => {
    const req = http.get(`http://127.0.0.1:${BACKEND_PORT}/api/location/device-ip`, (res) => {
      let data = '';
      res.on('data', chunk => data += chunk);
      res.on('end', () => {
        if (res.statusCode === 200) {
          try {
            resolve(JSON.parse(data));
          } catch (e) {
            resolve({ error: 'Failed to parse device location data' });
          }
        } else {
          resolve({ error: `Backend device location returned HTTP ${res.statusCode}` });
        }
      });
    });
    req.on('error', (err) => {
      resolve({ error: `Could not reach backend location endpoint: ${err.message}` });
    });
    req.setTimeout(5000, () => {
      req.destroy();
      resolve({ error: 'Device location detection timed out' });
    });
  });
});

app.whenReady().then(async () => {
  setupSessionPermissions();
  startBackend();

  try {
    console.log('Waiting for backend health check...');
    await checkBackendHealth(25, 800);
    console.log('Backend verified healthy!');
  } catch (err) {
    console.warn('Backend connection notice:', err.message);
  }

  createWindow();

  app.on('activate', () => {
    if (BrowserWindow.getAllWindows().length === 0) createWindow();
  });
});

app.on('window-all-closed', () => {
  stopBackend();
  if (process.platform !== 'darwin') {
    app.quit();
  }
});

app.on('before-quit', () => {
  stopBackend();
});
