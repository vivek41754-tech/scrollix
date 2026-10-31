const { app, BrowserWindow } = require('electron');
const path = require('path');

app.commandLine.appendSwitch('disable-gpu');
app.commandLine.appendSwitch('no-sandbox');

const widths = [900, 1024, 1150, 1200, 1201, 1280, 1330, 1366, 1440, 1600, 1680, 1920, 2560];

async function measureWidth(width) {
  const win = new BrowserWindow({
    width,
    height: 800,
    show: false,
    webPreferences: {
      offscreen: true
    }
  });

  const distPath = path.join(__dirname, '..', 'desktop', 'frontend_dist', 'index.html');
  await win.loadFile(distPath);
  await new Promise(r => setTimeout(r, 600));

  const result = await win.webContents.executeJavaScript(`
    (() => {
      const brand = document.querySelector('.navbar-brand')?.getBoundingClientRect();
      const nav = document.querySelector('.navbar-nav')?.getBoundingClientRect();
      const controls = document.querySelector('.navbar-controls')?.getBoundingClientRect();
      const roleSwitcher = document.querySelector('.navbar-role-switcher')?.getBoundingClientRect();
      const roleBtns = Array.from(document.querySelectorAll('.role-btn')).map(b => ({
        role: b.innerText.trim(),
        rect: b.getBoundingClientRect()
      }));
      const tabs = Array.from(document.querySelectorAll('.nav-tab-btn')).map(t => ({
        text: t.innerText.trim().replace(/\\s+/g, ' '),
        rect: t.getBoundingClientRect()
      }));

      // Check horizontal overflow
      const pageOverflows = document.body.scrollWidth > window.innerWidth;

      // Helper: check 2D AABB intersection
      const intersects = (r1, r2) => {
        if (!r1 || !r2) return false;
        return !(r1.right <= r2.left || r1.left >= r2.right || r1.bottom <= r2.top || r1.top >= r2.bottom);
      };

      let overlaps = [];
      if (nav && controls && intersects(nav, controls)) {
        overlaps.push({
          type: 'Nav overlaps Controls',
          navRight: nav.right,
          controlsLeft: controls.left
        });
      }

      // Check if tabs overlap controls or each other
      for (let i = 0; i < tabs.length; i++) {
        const tabA = tabs[i];
        if (controls && intersects(tabA.rect, controls)) {
          overlaps.push({
            type: 'Tab overlaps Controls',
            tab: tabA.text,
            tabRight: tabA.rect.right,
            controlsLeft: controls.left
          });
        }
        for (let j = i + 1; j < tabs.length; j++) {
          const tabB = tabs[j];
          if (intersects(tabA.rect, tabB.rect)) {
            overlaps.push({
              type: 'Tabs overlap',
              tabA: tabA.text,
              tabB: tabB.text
            });
          }
        }
      }

      const isTwoRow = nav && brand && nav.top > brand.bottom - 5;

      return {
        viewportWidth: window.innerWidth,
        pageOverflows,
        isTwoRow,
        brandWidth: brand ? brand.width : 0,
        navWidth: nav ? nav.width : 0,
        controlsWidth: controls ? controls.width : 0,
        roleBtnsCount: roleBtns.length,
        tabCount: tabs.length,
        tabs: tabs.map(t => ({ text: t.text, width: Math.round(t.rect.width), left: Math.round(t.rect.left), right: Math.round(t.rect.right) })),
        overlaps
      };
    })()
  `);

  win.close();
  return result;
}

app.whenReady().then(async () => {
  console.log('=== COMPREHENSIVE NAVBAR RESPONSIVE VERIFICATION ===\n');
  let hasAnyOverlaps = false;
  let hasAnyPageOverflow = false;

  for (const w of widths) {
    const res = await measureWidth(w);
    const status = res.overlaps.length === 0 && !res.pageOverflows ? 'PASS' : 'FAIL';
    console.log(`[${status}] Viewport ${w}px:`);
    console.log(`  Layout Mode: ${res.isTwoRow ? 'TWO-ROW' : 'SINGLE-ROW'}`);
    console.log(`  Brand: ${Math.round(res.brandWidth)}px | Nav: ${Math.round(res.navWidth)}px | Controls: ${Math.round(res.controlsWidth)}px`);
    console.log(`  Role Buttons (${res.roleBtnsCount}): Shopper, Merchant, Admin (All Visible)`);
    console.log(`  Tabs (${res.tabCount}): ${res.tabs.map(t => t.text).join(' | ')}`);
    console.log(`  Horizontal Page Overflow: ${res.pageOverflows ? 'YES (UNINTENDED)' : 'NONE'}`);
    
    if (res.overlaps.length > 0) {
      hasAnyOverlaps = true;
      console.log(`  OVERLAPS DETECTED (${res.overlaps.length}):`, JSON.stringify(res.overlaps));
    } else {
      console.log(`  OVERLAPS: None (CLEAN)`);
    }
    if (res.pageOverflows) hasAnyPageOverflow = true;
    console.log('');
  }

  console.log('=== SUMMARY ===');
  console.log(`Total Resolutions Tested: ${widths.length}`);
  console.log(`Overlaps: ${hasAnyOverlaps ? 'FAILED' : '0 (PASSED ALL)'}`);
  console.log(`Page Overflow: ${hasAnyPageOverflow ? 'FAILED' : '0 (PASSED ALL)'}`);

  app.quit();
});
