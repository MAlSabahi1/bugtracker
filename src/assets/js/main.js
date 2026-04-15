/**
 * Main
 */

'use strict';

let menu,
  animate;
document.addEventListener('DOMContentLoaded', function () {
  // class for ios specific styles
  if (navigator.userAgent.match(/iPhone|iPad|iPod/i)) {
    document.body.classList.add('ios');
  }
});

(function () {
  // Gracefully handle resizing from desktop to mobile
  window.matchMedia('(max-width: 1199.98px)').addEventListener('change', (e) => {
    if (e.matches) {
      document.documentElement.classList.remove('layout-menu-collapsed');
    } else {
      if (localStorage.getItem('layout-menu-collapsed') === 'true') {
        document.documentElement.classList.add('layout-menu-collapsed');
      }
    }
  });

  // Initialize menu
  //-----------------

  let layoutMenuEl = document.querySelectorAll('#layout-menu');
  layoutMenuEl.forEach(function (element) {
    menu = new Menu(element, {
      orientation: 'vertical',
      closeChildren: false
    });
    // Change parameter to true if you want scroll animation
    window.Helpers.scrollToActive((animate = false));
    window.Helpers.mainMenu = menu;
  });

  let wasCollapsedOnHover = false;

  // Initialize menu togglers and bind click on each
  let menuToggler = document.querySelectorAll('.layout-menu-toggle');
  menuToggler.forEach(item => {
    item.addEventListener('click', event => {
      event.preventDefault();
      
      // On mobile (window < 1200px), use the built-in helper to expand/collapse offcanvas
      if (window.Helpers.isSmallScreen()) {
        window.Helpers.toggleCollapsed();
      } else {
        // On desktop, act as a Pin/Unpin
        if (wasCollapsedOnHover) {
          // Disable the mouseleave auto-collapse (Pin it permanently open)
          wasCollapsedOnHover = false;
          document.documentElement.classList.remove('layout-menu-hover');
          document.documentElement.classList.remove('layout-menu-collapsed');
          localStorage.setItem('layout-menu-collapsed', 'false');
        } else {
          // Normal toggle
          document.documentElement.classList.toggle('layout-menu-collapsed');
          document.documentElement.classList.remove('layout-menu-hover');
          
          let isCollapsed = document.documentElement.classList.contains('layout-menu-collapsed');
          localStorage.setItem('layout-menu-collapsed', isCollapsed);
        }
        
        // Update circular icon purely based on final pinned state
        let toggleIcon = document.querySelector('#layout-menu .layout-menu-toggle i');
        if (toggleIcon) {
          if (document.documentElement.classList.contains('layout-menu-collapsed')) {
            toggleIcon.className = 'icon-base bx bx-circle bx-sm align-middle'; // Empty circle when Unpinned
          } else {
            toggleIcon.className = 'icon-base bx bx-radio-circle-marked bx-sm align-middle'; // Checked circle when Pinned
          }
        }
      }
    });

    // Native hover fix for desktop collapsed menu: temporarily restore full menu natively
    let layoutMenu = document.getElementById('layout-menu');
    if (layoutMenu) {
      layoutMenu.addEventListener('mouseenter', () => {
        if (!window.Helpers.isSmallScreen() && document.documentElement.classList.contains('layout-menu-collapsed')) {
          wasCollapsedOnHover = true;
          document.documentElement.classList.add('layout-menu-hover');
          // Temporarily drop collapsed class so dropdowns and texts natively work!
          document.documentElement.classList.remove('layout-menu-collapsed');
        }
      });
      layoutMenu.addEventListener('mouseleave', () => {
        if (wasCollapsedOnHover) {
          document.documentElement.classList.remove('layout-menu-hover');
          document.documentElement.classList.add('layout-menu-collapsed');
          wasCollapsedOnHover = false;
        }
      });
    }
  });

  // Display menu toggle permanently shown, flip icon via manual fix if necessary
  let toggleButton = document.querySelector('.layout-menu-toggle');
  if (toggleButton) {
    toggleButton.classList.add('d-block');
  }

  // Display in main menu when menu scrolls
  let menuInnerContainer = document.getElementsByClassName('menu-inner'),
    menuInnerShadow = document.getElementsByClassName('menu-inner-shadow')[0];
  if (menuInnerContainer.length > 0 && menuInnerShadow) {
    menuInnerContainer[0].addEventListener('ps-scroll-y', function () {
      if (this.querySelector('.ps__thumb-y').offsetTop) {
        menuInnerShadow.style.display = 'block';
      } else {
        menuInnerShadow.style.display = 'none';
      }
    });
  }

  // Init helpers & misc
  // --------------------

  // Init BS Tooltip
  const tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
  tooltipTriggerList.map(function (tooltipTriggerEl) {
    return new bootstrap.Tooltip(tooltipTriggerEl);
  });

  // Accordion active class
  const accordionActiveFunction = function (e) {
    if (e.type == 'show.bs.collapse' || e.type == 'show.bs.collapse') {
      e.target.closest('.accordion-item').classList.add('active');
    } else {
      e.target.closest('.accordion-item').classList.remove('active');
    }
  };

  const accordionTriggerList = [].slice.call(document.querySelectorAll('.accordion'));
  const accordionList = accordionTriggerList.map(function (accordionTriggerEl) {
    accordionTriggerEl.addEventListener('show.bs.collapse', accordionActiveFunction);
    accordionTriggerEl.addEventListener('hide.bs.collapse', accordionActiveFunction);
  });

  // Auto update layout based on screen size
  window.Helpers.setAutoUpdate(true);

  // Toggle Password Visibility
  window.Helpers.initPasswordToggle();

  // Speech To Text
  window.Helpers.initSpeechToText();

  // Manage menu expanded/collapsed with templateCustomizer & local storage
  //------------------------------------------------------------------

  // If current layout is horizontal OR current window screen is small (overlay menu) than return from here
  if (window.Helpers.isSmallScreen()) {
    return;
  }

  // If current layout is vertical and current window screen is > small

  // Auto update menu collapsed/expanded based on local storage
  if (!window.Helpers.isSmallScreen()) {
    let savedCollapsed = localStorage.getItem('layout-menu-collapsed');
    if (savedCollapsed === 'true') {
      document.documentElement.classList.add('layout-menu-collapsed');
    } else {
      document.documentElement.classList.remove('layout-menu-collapsed');
    }
    
    // Set initial icon on load correctly
    let initialToggleIcon = document.querySelector('#layout-menu .layout-menu-toggle i');
    if (initialToggleIcon) {
        if (document.documentElement.classList.contains('layout-menu-collapsed')) {
            initialToggleIcon.className = 'icon-base bx bx-circle bx-sm align-middle';
        } else {
            initialToggleIcon.className = 'icon-base bx bx-radio-circle-marked bx-sm align-middle';
        }
    }
  }
})();
// Utils
function isMacOS() {
  return /Mac|iPod|iPhone|iPad/.test(navigator.userAgent);
}
