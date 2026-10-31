const { app, BrowserWindow } = require('electron');
const path = require('path');

app.commandLine.appendSwitch('disable-gpu');
app.commandLine.appendSwitch('no-sandbox');

app.whenReady().then(async () => {
  const win = new BrowserWindow({
    width: 1366,
    height: 800,
    show: false,
    webPreferences: { offscreen: true }
  });

  const distPath = path.join(__dirname, '..', 'desktop', 'frontend_dist', 'index.html');
  await win.loadFile(distPath);
  await new Promise(r => setTimeout(r, 800));

  const clickResults = await win.webContents.executeJavaScript(`
    (async () => {
      const results = {};
      
      // 1. Initial State: Video Feed should be active
      const feedBtn = Array.from(document.querySelectorAll('.nav-tab-btn')).find(b => b.innerText.includes('Video Feed'));
      results.feedInitiallyActive = feedBtn ? feedBtn.classList.contains('active') : false;

      // 2. Click 'Trust & Admin' tab
      const trustBtn = Array.from(document.querySelectorAll('.nav-tab-btn')).find(b => b.innerText.includes('Trust & Admin'));
      if (trustBtn) {
        trustBtn.click();
        await new Promise(r => setTimeout(r, 100));
        results.trustActiveAfterClick = trustBtn.classList.contains('active');
        results.feedInactiveAfterTrustClick = feedBtn ? !feedBtn.classList.contains('active') : false;
      }

      // 3. Click 'Nearby Map' tab
      const mapBtn = Array.from(document.querySelectorAll('.nav-tab-btn')).find(b => b.innerText.includes('Nearby Map'));
      if (mapBtn) {
        mapBtn.click();
        await new Promise(r => setTimeout(r, 100));
        results.mapActiveAfterClick = mapBtn.classList.contains('active');
      }

      // 4. Test Demo Role Switcher: Click Merchant
      const merchantRole = document.querySelector('.role-merchant');
      if (merchantRole) {
        merchantRole.click();
        await new Promise(r => setTimeout(r, 600));
        results.merchantRoleActive = merchantRole.classList.contains('active');
        const merchantTab = Array.from(document.querySelectorAll('.nav-tab-btn')).find(b => b.innerText.includes('Merchant Hub'));
        results.merchantTabActivated = merchantTab ? merchantTab.classList.contains('active') : false;
      }

      // 5. Test Demo Role Switcher: Click Admin
      const adminRole = document.querySelector('.role-admin');
      if (adminRole) {
        adminRole.click();
        await new Promise(r => setTimeout(r, 350));
        results.adminRoleActive = adminRole.classList.contains('active');
        results.trustTabActivatedByAdminRole = trustBtn ? trustBtn.classList.contains('active') : false;
      }

      // 6. Test Demo Role Switcher: Click Shopper
      const shopperRole = document.querySelector('.role-shopper');
      if (shopperRole) {
        shopperRole.click();
        await new Promise(r => setTimeout(r, 350));
        results.shopperRoleActive = shopperRole.classList.contains('active');
        results.feedTabActivatedByShopperRole = feedBtn ? feedBtn.classList.contains('active') : false;
      }

      return results;
    })()
  `);

  console.log('=== NAVBAR INTERACTION & DEMO ROLE SWITCHING TEST ===\n');
  console.log('Results:', JSON.stringify(clickResults, null, 2));

  const allPassed = 
    clickResults.feedInitiallyActive &&
    clickResults.trustActiveAfterClick &&
    clickResults.feedInactiveAfterTrustClick &&
    clickResults.mapActiveAfterClick &&
    clickResults.merchantRoleActive &&
    clickResults.merchantTabActivated &&
    clickResults.adminRoleActive &&
    clickResults.trustTabActivatedByAdminRole &&
    clickResults.shopperRoleActive &&
    clickResults.feedTabActivatedByShopperRole;

  console.log(`\nOverall Interaction Test: ${allPassed ? 'ALL PASSED (100%)' : 'FAILED'}`);

  win.close();
  app.quit();
});
