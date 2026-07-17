/* Woneng Energy — site interactions */
(function () {
  'use strict';

  // Sticky header shadow
  var header = document.querySelector('.site-header');
  function onScroll() {
    if (!header) return;
    header.classList.toggle('scrolled', window.scrollY > 8);
  }
  window.addEventListener('scroll', onScroll, { passive: true });
  onScroll();

  // Mobile nav
  var toggle = document.querySelector('.nav-toggle');
  var links = document.querySelector('.nav-links');
  if (toggle && links) {
    toggle.addEventListener('click', function () {
      links.classList.toggle('show');
      toggle.classList.toggle('open');
    });
    links.addEventListener('click', function (e) {
      if (e.target.tagName === 'A') links.classList.remove('show');
    });
  }

  // Year
  var y = document.getElementById('year');
  if (y) y.textContent = new Date().getFullYear();

  // Accordions
  document.querySelectorAll('.acc button').forEach(function (b) {
    b.addEventListener('click', function () {
      b.parentElement.classList.toggle('open');
    });
  });

  // Inquiry modal
  var modal = document.getElementById('inquiryModal');
  var modalTitle = document.getElementById('inquiryModalTitle');
  function openModal(title, product) {
    if (!modal) return;
    if (modalTitle && title) modalTitle.textContent = title;
    var pf = document.getElementById('f-product');
    if (pf && product) pf.value = product;
    modal.classList.add('show');
    document.body.style.overflow = 'hidden';
  }
  function closeModal() {
    if (!modal) return;
    modal.classList.remove('show');
    document.body.style.overflow = '';
  }
  document.querySelectorAll('[data-inquiry]').forEach(function (el) {
    el.addEventListener('click', function (e) {
      e.preventDefault();
      openModal(el.getAttribute('data-inquiry-title') || 'Request a Quote', el.getAttribute('data-inquiry') || '');
    });
  });
  var closeBtn = document.querySelector('.modal-close');
  if (closeBtn) closeBtn.addEventListener('click', closeModal);
  if (modal) modal.addEventListener('click', function (e) { if (e.target === modal) closeModal(); });
  document.addEventListener('keydown', function (e) { if (e.key === 'Escape') closeModal(); });

  // Forms — Web3Forms submit with validation + mailto fallback (no backend needed)
  function showOk(form) {
    var ok = form.querySelector('.form-ok');
    if (ok) { ok.classList.add('show'); setTimeout(function () { ok.classList.remove('show'); }, 6000); }
  }
  function mailtoFallback(form) {
    var d = new FormData(form);
    var lines = 'Name: ' + (d.get('name') || '') + '\n' +
                'Company: ' + (d.get('company') || '') + '\n' +
                'Email: ' + (d.get('email') || '') + '\n' +
                'WhatsApp/Phone: ' + (d.get('phone') || '') + '\n' +
                'Product/Category: ' + (d.get('product') || '') + '\n' +
                'Target Market: ' + (d.get('market') || '') + '\n' +
                'Need: ' + (d.get('message') || '');
    var subj = 'Woneng Inquiry — ' + (d.get('product') || 'Website');
    window.location.href = 'mailto:sales@entelechyenergy.com?subject=' +
      encodeURIComponent(subj) + '&body=' + encodeURIComponent(lines);
  }
  document.querySelectorAll('form[data-web3]').forEach(function (form) {
    form.addEventListener('submit', function (e) {
      e.preventDefault();
      if (!form.checkValidity()) { form.reportValidity(); return; }
      var btn = form.querySelector('button[type="submit"]');
      var orig = btn ? btn.textContent : '';
      if (btn) { btn.disabled = true; btn.textContent = 'Sending…'; }
      var data = new FormData(form);
      // Honeypot — if filled, treat as bot and silently "succeed" without sending.
      if (data.get('company_website')) {
        showOk(form); form.reset();
        if (form.closest('.modal-back')) setTimeout(closeModal, 1400);
        if (btn) { btn.disabled = false; btn.textContent = orig; }
        return;
      }
      fetch(form.action, { method: 'POST', body: data, headers: { 'Accept': 'application/json' } })
        .then(function (r) { return r.json(); })
        .then(function (j) {
          if (j && j.success) { showOk(form); form.reset(); }
          else { mailtoFallback(form); showOk(form); }
        })
        .catch(function () { mailtoFallback(form); showOk(form); })
        .finally(function () {
          if (btn) { btn.disabled = false; btn.textContent = orig; }
          if (form.closest('.modal-back')) setTimeout(closeModal, 1400);
        });
    });
  });

  // Product center — category filter
  var filterWrap = document.querySelector('.cat-filter');
  if (filterWrap) {
    filterWrap.querySelectorAll('.chip-filter').forEach(function (btn) {
      btn.addEventListener('click', function () {
        filterWrap.querySelectorAll('.chip-filter').forEach(function (b) { b.classList.remove('active'); });
        btn.classList.add('active');
        var cat = btn.getAttribute('data-cat');
        document.querySelectorAll('.series').forEach(function (s) {
          s.style.display = (cat === 'all' || s.getAttribute('data-cat') === cat) ? '' : 'none';
        });
      });
    });
  }
})();
