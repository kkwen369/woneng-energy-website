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

  // Forms (client-side demo submit)
  document.querySelectorAll('form[data-demo]').forEach(function (form) {
    form.addEventListener('submit', function (e) {
      e.preventDefault();
      var ok = form.querySelector('.form-ok');
      if (ok) ok.classList.add('show');
      form.reset();
      if (form.closest('.modal-back')) setTimeout(closeModal, 1600);
      if (ok) setTimeout(function () { ok.classList.remove('show'); }, 5000);
    });
  });
})();
