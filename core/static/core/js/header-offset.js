// Measure the fixed header height and set --header-height CSS variable on <html>
(function () {
  function updateHeaderOffset() {
    try {
      var header = document.querySelector('header');
      if (!header) return;
      var height = header.offsetHeight;
      document.documentElement.style.setProperty('--header-height', height + 'px');
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

      // Observe header mutations (class changes or content) that may affect height
      var header = document.querySelector('header');
      if (header && window.MutationObserver) {
        var mo = new MutationObserver(function () { updateHeaderOffset(); });
        mo.observe(header, { attributes: true, childList: true, subtree: true });
      }
    });
  } else {
    updateHeaderOffset();
    window.addEventListener('resize', onResize);
    var header = document.querySelector('header');
    if (header && window.MutationObserver) {
      var mo = new MutationObserver(function () { updateHeaderOffset(); });
      mo.observe(header, { attributes: true, childList: true, subtree: true });
    }
  }
})();
