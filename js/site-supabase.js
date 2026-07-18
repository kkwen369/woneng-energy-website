/* ============================================================
   Woneng Energy — Frontend Supabase Integration
   Handles: inquiry form submission, news listing/detail, SEO enhancement
   ============================================================ */
(function () {
  'use strict';

  var _client = null;

  function init() {
    if (_client) return _client;
    if (typeof window.supabase === 'undefined') return null;
    var cfg = window.SUPABASE_CONFIG;
    if (!cfg || !cfg.url || cfg.url.indexOf('YOUR_') === 0) return null;
    _client = window.supabase.createClient(cfg.url, cfg.anonKey);
    return _client;
  }

  function client() { return init(); }
  function isConfigured() { return client() !== null; }

  /* ---------- Get current page path ---------- */
  function currentPagePath() {
    var path = window.location.pathname.split('/').pop() || 'index.html';
    return path;
  }

  /* ---------- Submit inquiry to Supabase ---------- */
  async function submitInquiry(formData, form) {
    var c = client();
    if (!c) return false;
    try {
      // Build source page from current URL
      var sourcePage = window.location.pathname.split('/').pop() || 'index.html';
      var data = {
        contact_name: (formData.get('name') || '').toString(),
        company_name: (formData.get('company') || '').toString(),
        email: (formData.get('email') || '').toString(),
        phone: (formData.get('phone') || '').toString(),
        whatsapp: (formData.get('phone') || '').toString(),
        country: (formData.get('market') || '').toString(),
        product_interest: (formData.get('product') || '').toString(),
        target_market: (formData.get('market') || '').toString(),
        message: (formData.get('message') || '').toString(),
        source_page: sourcePage,
        status: 'pending',
      };
      var r = await c.from('inquiries').insert(data).select().single();
      if (r.error) throw r.error;
      return true;
    } catch (e) {
      console.warn('[Woneng] Inquiry submission to Supabase failed, falling back:', e.message);
      return false;
    }
  }

  /* ---------- SEO Enhancement ---------- */
  async function enhanceSEO() {
    var c = client();
    if (!c) return;
    var pagePath = currentPagePath();
    try {
      var r = await c.from('seo_pages').select('*').eq('page_path', pagePath).maybeSingle();
      if (r.error || !r.data) return;
      var s = r.data;
      // Update meta tags if configured
      if (s.meta_title) { document.title = s.meta_title; setMeta('name', 'description', s.meta_description); }
      if (s.meta_description) setMeta('name', 'description', s.meta_description);
      if (s.meta_keywords) setMeta('name', 'keywords', s.meta_keywords);
      if (s.og_title) setMeta('property', 'og:title', s.og_title);
      if (s.og_description) setMeta('property', 'og:description', s.og_description);
      if (s.og_image) setMeta('property', 'og:image', s.og_image);
      if (s.canonical_url) {
        var link = document.querySelector('link[rel="canonical"]');
        if (link) link.href = s.canonical_url;
      }
    } catch (e) { /* silent fail — SEO enhancement is progressive */ }
  }

  function setMeta(attr, name, content) {
    if (!content) return;
    var el = document.querySelector('meta[' + attr + '="' + name + '"]');
    if (el) { el.setAttribute('content', content); }
    else {
      el = document.createElement('meta');
      el.setAttribute(attr, name);
      el.setAttribute('content', content);
      document.head.appendChild(el);
    }
  }

  /* ---------- News: list & detail ---------- */
  async function loadNewsList(container) {
    var c = client();
    if (!c) { showNewsDisabled(container); return; }
    try {
      var r = await c.from('news').select('*').eq('status', 'published').order('published_at', { ascending: false });
      var articles = r.data || [];
      if (!articles.length) {
        container.innerHTML = '<div class="news-empty"><p>No articles published yet. Check back soon!</p></div>';
        return;
      }
      var catLabels = { 'company-news': 'Company News', 'industry': 'Industry', 'exhibition': 'Exhibition', 'tech': 'Technology', 'case-study': 'Case Study' };
      container.innerHTML = articles.map(function (n) {
        var date = n.published_at ? formatDate(n.published_at) : '';
        var img = n.cover_image
          ? '<div class="news-card-img" style="background-image:url(\'' + esc(n.cover_image) + '\')"></div>'
          : '<div class="news-card-img news-card-placeholder"><span>' + esc((n.title || '').charAt(0)) + '</span></div>';
        return '<article class="news-card">' +
          '<a href="news.html?slug=' + encodeURIComponent(n.slug) + '" class="news-card-link">' + img +
          '<div class="news-card-body">' +
            '<div class="news-card-meta"><span class="news-cat">' + esc(catLabels[n.category] || n.category) + '</span>' +
            '<span class="news-date">' + date + '</span></div>' +
            '<h2 class="news-card-title">' + esc(n.title) + '</h2>' +
            '<p class="news-card-summary">' + esc(n.summary || '') + '</p>' +
            '<span class="news-read-more">Read more →</span>' +
          '</div></a></article>';
      }).join('');
    } catch (e) {
      container.innerHTML = '<div class="news-empty"><p>Unable to load news. Please try again later.</p></div>';
    }
  }

  async function loadNewsDetail(container, slug) {
    var c = client();
    if (!c) { showNewsDisabled(container); return; }
    try {
      var r = await c.from('news').select('*').eq('slug', slug).eq('status', 'published').maybeSingle();
      if (r.error || !r.data) {
        container.innerHTML = '<div class="news-empty"><h1>Article Not Found</h1><p>The article you are looking for does not exist or has been removed.</p><a href="news.html" class="btn">← Back to News</a></div>';
        return;
      }
      var n = r.data;
      // Increment view count
      c.from('news').update({ view_count: (n.view_count || 0) + 1 }).eq('id', n.id).then(function () {});

      var catLabels = { 'company-news': 'Company News', 'industry': 'Industry', 'exhibition': 'Exhibition', 'tech': 'Technology', 'case-study': 'Case Study' };
      var date = n.published_at ? formatDate(n.published_at) : '';

      // Update page SEO if configured
      if (n.meta_title) document.title = n.meta_title;
      else document.title = n.title + ' — Woneng';
      if (n.meta_description) setMeta('name', 'description', n.meta_description);
      else setMeta('name', 'description', n.summary || '');

      container.innerHTML =
        '<article class="news-article">' +
          '<a href="news.html" class="news-back">← All News</a>' +
          (n.cover_image ? '<div class="news-hero" style="background-image:url(\'' + esc(n.cover_image) + '\')"></div>' : '') +
          '<div class="news-article-head">' +
            '<div class="news-card-meta"><span class="news-cat">' + esc(catLabels[n.category] || n.category) + '</span>' +
            '<span class="news-date">' + date + '</span>' +
            '<span class="news-author">by ' + esc(n.author || 'Woneng') + '</span></div>' +
            '<h1>' + esc(n.title) + '</h1>' +
            (n.summary ? '<p class="news-article-summary">' + esc(n.summary) + '</p>' : '') +
          '</div>' +
          '<div class="news-content">' + (n.content || '') + '</div>' +
          '<div class="news-share"><a href="news.html" class="btn">← Back to All News</a></div>' +
        '</article>';
      window.scrollTo(0, 0);
    } catch (e) {
      container.innerHTML = '<div class="news-empty"><p>Unable to load article.</p></div>';
    }
  }

  function showNewsDisabled(container) {
    container.innerHTML = '<div class="news-empty"><p>News feature is not yet configured.</p></div>';
  }

  function formatDate(d) {
    var dt = new Date(d);
    if (isNaN(dt)) return '';
    var months = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'];
    return months[dt.getMonth()] + ' ' + dt.getDate() + ', ' + dt.getFullYear();
  }

  function esc(s) {
    if (s == null) return '';
    return String(s).replace(/[&<>"']/g, function (c) {
      return { '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' }[c];
    });
  }

  /* ---------- Auto-init on DOM ready ---------- */
  function autoInit() {
    // SEO enhancement on every page
    enhanceSEO();

    // News page detection
    var newsContainer = document.getElementById('newsContainer');
    if (newsContainer) {
      var params = new URLSearchParams(window.location.search);
      var slug = params.get('slug');
      if (slug) loadNewsDetail(newsContainer, slug);
      else loadNewsList(newsContainer);
    }
  }

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', autoInit);
  } else {
    autoInit();
  }

  /* ---------- Expose ---------- */
  window.WonengSupabase = {
    client: client,
    isConfigured: isConfigured,
    submitInquiry: submitInquiry,
    enhanceSEO: enhanceSEO,
    loadNewsList: loadNewsList,
    loadNewsDetail: loadNewsDetail,
  };
})();
