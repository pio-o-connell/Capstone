// Measure the fixed header height and set --header-height CSS variable on <html>
// Also position the login banner below the header
(function () {
  function updateHeaderOffset() {
    try {
      var header = document.querySelector('header');
      var banner = document.querySelector('.login-banner-wrapper');
      if (!header) return;
      
      var headerHeight = header.offsetHeight;
      
      // Position banner right below header
      if (banner) {
        banner.style.top = headerHeight + 'px';
        var bannerHeight = banner.offsetHeight;
        var totalHeight = headerHeight + bannerHeight;
        document.documentElement.style.setProperty('--header-height', totalHeight + 'px');
      } else {
        document.documentElement.style.setProperty('--header-height', headerHeight + 'px');
      }
    } catch (e) {
      // ignore
    }
  }

  // Debounce resize
  var resizeTimeout = null;
  function onResize() {
    clearTimeout(resizeTimeout);
    resizeTimeout = setTimeout(updateHeaderOffset, 100);
  }

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', function () {
      updateHeaderOffset();
      window.addEventListener('resize', onResize);

      // Observe header and banner mutations (class changes or content) that may affect height
      var header = document.querySelector('header');
      var banner = document.querySelector('.login-banner-wrapper');
      if (header && window.MutationObserver) {
        var mo = new MutationObserver(function () { updateHeaderOffset(); });
        mo.observe(header, { attributes: true, childList: true, subtree: true });
        if (banner) {
          mo.observe(banner, { attributes: true, childList: true, subtree: true });
        }
      }
    });
  } else {
    updateHeaderOffset();
    window.addEventListener('resize', onResize);
    var header = document.querySelector('header');
    var banner = document.querySelector('.login-banner-wrapper');
    if (header && window.MutationObserver) {
      var mo = new MutationObserver(function () { updateHeaderOffset(); });
      mo.observe(header, { attributes: true, childList: true, subtree: true });
      if (banner) {
        mo.observe(banner, { attributes: true, childList: true, subtree: true });
      }
    }
  }
})();
