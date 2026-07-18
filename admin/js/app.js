/* ============================================================
   Woneng Admin — Core Application Logic
   Handles: Supabase init, auth, layout, API wrappers, utilities
   ============================================================ */
(function () {
  'use strict';

  /* ---------- Supabase client ---------- */
  var _client = null;

  function initClient() {
    if (_client) return _client;
    if (typeof window.supabase === 'undefined') return null;
    var cfg = window.SUPABASE_CONFIG;
    if (!cfg || !cfg.url || cfg.url.indexOf('YOUR_') === 0) return null;
    _client = window.supabase.createClient(cfg.url, cfg.anonKey);
    return _client;
  }

  function client() { return initClient(); }

  function isConfigured() { return client() !== null; }

  /* ---------- Auth ---------- */
  async function getSession() {
    var c = client();
    if (!c) return null;
    var r = await c.auth.getSession();
    return r.data.session;
  }

  async function requireAuth() {
    var session = await getSession();
    if (!session) { window.location.href = 'index.html'; return null; }
    return session;
  }

  async function login(email, password) {
    var c = client();
    if (!c) return { error: 'Supabase not configured. Edit admin/js/config.js first.' };
    var r = await c.auth.signInWithPassword({ email: email, password: password });
    if (r.error) return { error: r.error.message };
    return { data: r.data };
  }

  async function logout() {
    var c = client();
    if (c) await c.auth.signOut();
    window.location.href = 'index.html';
  }

  async function currentUser() {
    var c = client();
    if (!c) return null;
    var r = await c.auth.getUser();
    return r.data.user;
  }

  /* ---------- UI helpers ---------- */
  function toast(msg, type) {
    var t = document.createElement('div');
    t.className = 'toast toast-' + (type || 'info');
    t.innerHTML = msg;
    document.body.appendChild(t);
    requestAnimationFrame(function () { t.classList.add('show'); });
    setTimeout(function () {
      t.classList.remove('show');
      setTimeout(function () { if (t.parentNode) t.remove(); }, 300);
    }, 3500);
  }
  function ok(m) { toast(m, 'ok'); }
  function err(m) { toast(m, 'err'); }
  function info(m) { toast(m, 'info'); }

  function fmtDate(d) {
    if (!d) return '-';
    var dt = new Date(d);
    if (isNaN(dt)) return '-';
    return dt.getFullYear() + '-' + String(dt.getMonth() + 1).padStart(2, '0') + '-' + String(dt.getDate()).padStart(2, '0');
  }
  function fmtDateTime(d) {
    if (!d) return '-';
    var dt = new Date(d);
    if (isNaN(dt)) return '-';
    return fmtDate(d) + ' ' + String(dt.getHours()).padStart(2, '0') + ':' + String(dt.getMinutes()).padStart(2, '0');
  }
  function timeAgo(d) {
    if (!d) return '-';
    var dt = new Date(d), now = new Date();
    var diff = (now - dt) / 1000;
    if (diff < 60) return 'just now';
    if (diff < 3600) return Math.floor(diff / 60) + 'm ago';
    if (diff < 86400) return Math.floor(diff / 3600) + 'h ago';
    if (diff < 604800) return Math.floor(diff / 86400) + 'd ago';
    return fmtDate(d);
  }

  function escapeHtml(s) {
    if (s == null) return '';
    return String(s).replace(/[&<>"']/g, function (c) {
      return { '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' }[c];
    });
  }

  function debounce(fn, wait) {
    var t;
    return function () {
      var ctx = this, args = arguments;
      clearTimeout(t);
      t = setTimeout(function () { fn.apply(ctx, args); }, wait || 300);
    };
  }

  /* ---------- Status badges ---------- */
  var STATUS_COLORS = {
    new: 'blue', contacted: 'cyan', quoted: 'amber', negotiating: 'purple', won: 'green', lost: 'red',
    pending: 'amber', replied: 'blue', closed: 'gray',
    draft: 'gray', published: 'green'
  };
  function badge(status) {
    var c = STATUS_COLORS[status] || 'gray';
    return '<span class="badge badge-' + c + '">' + escapeHtml(status) + '</span>';
  }

  /* ---------- Sidebar layout ---------- */
  var NAV = [
    { href: 'dashboard.html', icon: 'M3 13h8V3H3v10zm0 8h8v-6H3v6zm10 0h8V11h-8v10zm0-18v6h8V3h-8z', label: 'Dashboard' },
    { href: 'customers.html', icon: 'M16 11c1.66 0 2.99-1.34 2.99-3S17.66 5 16 5c-1.66 0-3 1.34-3 3s1.34 3 3 3zm-8 0c1.66 0 2.99-1.34 2.99-3S9.66 5 8 5C6.34 5 5 6.34 5 8s1.34 3 3 3zm0 2c-2.33 0-7 1.17-7 3.5V19h14v-2.5c0-2.33-4.67-3.5-7-3.5zm8 0c-.29 0-.62.02-.97.05 1.16.84 1.97 1.97 1.97 3.45V19h6v-2.5c0-2.33-4.67-3.5-7-3.5z', label: 'Customers' },
    { href: 'inquiries.html', icon: 'M20 4H4c-1.1 0-1.99.9-1.99 2L2 18c0 1.1.9 2 2 2h16c1.1 0 2-.9 2-2V6c0-1.1-.9-2-2-2zm0 4l-8 5-8-5V6l8 5 8-5v2z', label: 'Inquiries' },
    { href: 'news.html', icon: 'M4 3h16a1 1 0 0 1 1 1v16a1 1 0 0 1-1 1H4a1 1 0 0 1-1-1V4a1 1 0 0 1 1-1zm2 4v2h12V7H6zm0 4v2h8v-2H6zm0 4v2h12v-2H6z', label: 'News & Blog' },
    { href: 'seo.html', icon: 'M15.5 14h-.79l-.28-.27a6.5 6.5 0 1 0-.7.7l.27.28v.79l5 4.99L20.49 19l-4.99-5zm-6 0A4.5 4.5 0 1 1 14 9.5 4.5 4.5 0 0 1 9.5 14z', label: 'SEO Settings' },
  ];

  function renderLayout(activePage, pageTitle) {
    var navHtml = NAV.map(function (item) {
      var active = item.href === activePage ? ' active' : '';
      return '<a href="' + item.href + '" class="nav-item' + active + '">' +
        '<svg class="nav-icon" viewBox="0 0 24 24" fill="currentColor"><path d="' + item.icon + '"/></svg>' +
        '<span>' + item.label + '</span></a>';
    }).join('');

    return '<div class="admin-shell">' +
      '<aside class="sidebar">' +
        '<div class="sidebar-brand"><span class="logo">W</span><div><strong>Woneng</strong><small>Admin Panel</small></div></div>' +
        '<nav class="sidebar-nav">' + navHtml + '</nav>' +
        '<div class="sidebar-foot"><button class="btn-logout" id="btnLogout">Logout</button></div>' +
      '</aside>' +
      '<main class="admin-main">' +
        '<header class="topbar"><h1 class="page-title">' + escapeHtml(pageTitle || '') + '</h1>' +
        '<div class="topbar-right"><a href="../index.html" target="_blank" class="link-view">View Site ↗</a></div></header>' +
        '<div class="admin-content" id="adminContent"></div>' +
      '</main>' +
    '</div>';
  }

  async function mount(pageName, pageTitle, initFn) {
    document.title = pageTitle + ' — Woneng Admin';
    var session = await requireAuth();
    if (!session) return;

    // check config
    if (!isConfigured()) {
      document.body.innerHTML = '<div class="config-warning"><h2>⚠️ Supabase Not Configured</h2>' +
        '<p>Edit <code>admin/js/config.js</code> and fill in your Supabase URL &amp; anon key, then reload.</p>' +
        '<p>See <code>admin/database/schema.sql</code> for database setup instructions.</p></div>';
      return;
    }

    document.body.innerHTML = renderLayout(pageName, pageTitle);
    var btn = document.getElementById('btnLogout');
    if (btn) btn.addEventListener('click', function () { logout(); });

    var content = document.getElementById('adminContent');
    if (initFn) await initFn(content, session);
  }

  /* ---------- CSV export ---------- */
  function exportCSV(filename, rows, headers) {
    if (!rows || !rows.length) { err('No data to export'); return; }
    headers = headers || Object.keys(rows[0]);
    var csv = headers.join(',') + '\n';
    rows.forEach(function (row) {
      csv += headers.map(function (h) {
        var v = row[h];
        if (v == null) v = '';
        v = String(v).replace(/"/g, '""');
        if (/[",\n]/.test(v)) v = '"' + v + '"';
        return v;
      }).join(',') + '\n';
    });
    var blob = new Blob([csv], { type: 'text/csv;charset=utf-8;' });
    var url = URL.createObjectURL(blob);
    var a = document.createElement('a');
    a.href = url; a.download = filename;
    document.body.appendChild(a); a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(url);
    ok('Exported ' + rows.length + ' rows');
  }

  /* ---------- DB API wrappers ---------- */
  var DB = {
    /* Customers */
    async listCustomers(filters) {
      var c = client();
      var q = c.from('customers').select('*', { count: 'exact' }).order('created_at', { ascending: false });
      if (filters) {
        if (filters.search) q = q.or('company_name.ilike.%' + filters.search + '%,contact_name.ilike.%' + filters.search + '%,email.ilike.%' + filters.search + '%');
        if (filters.status && filters.status !== 'all') q = q.eq('status', filters.status);
        if (filters.type && filters.type !== 'all') q = q.eq('customer_type', filters.type);
      }
      if (filters && filters.limit) q = q.range(filters.offset || 0, (filters.offset || 0) + filters.limit - 1);
      return await q;
    },
    async getCustomer(id) {
      var c = client();
      var r = await c.from('customers').select('*').eq('id', id).single();
      return r;
    },
    async createCustomer(data) {
      var c = client();
      return await c.from('customers').insert(data).select().single();
    },
    async updateCustomer(id, data) {
      var c = client();
      return await c.from('customers').update(data).eq('id', id).select().single();
    },
    async deleteCustomer(id) {
      var c = client();
      return await c.from('customers').delete().eq('id', id);
    },

    /* Inquiries */
    async listInquiries(filters) {
      var c = client();
      var q = c.from('inquiries').select('*', { count: 'exact' }).order('created_at', { ascending: false });
      if (filters) {
        if (filters.search) q = q.or('contact_name.ilike.%' + filters.search + '%,company_name.ilike.%' + filters.search + '%,email.ilike.%' + filters.search + '%,product_interest.ilike.%' + filters.search + '%');
        if (filters.status && filters.status !== 'all') q = q.eq('status', filters.status);
      }
      return await q;
    },
    async getInquiry(id) {
      var c = client();
      return await c.from('inquiries').select('*').eq('id', id).single();
    },
    async updateInquiry(id, data) {
      var c = client();
      return await c.from('inquiries').update(data).eq('id', id).select().single();
    },
    async deleteInquiry(id) {
      var c = client();
      return await c.from('inquiries').delete().eq('id', id);
    },
    async inquiryToCustomer(inquiryId) {
      // Convert inquiry to a customer record
      var c = client();
      var iq = await c.from('inquiries').select('*').eq('id', inquiryId).single();
      if (iq.error) return iq;
      var d = iq.data;
      var cust = await c.from('customers').insert({
        company_name: d.company_name, contact_name: d.contact_name, email: d.email,
        phone: d.phone, whatsapp: d.whatsapp, country: d.country,
        status: 'new', source: 'website', notes: 'Converted from inquiry. Product: ' + (d.product_interest || '')
      }).select().single();
      if (cust.error) return cust;
      await c.from('inquiries').update({ customer_id: cust.data.id, status: 'replied' }).eq('id', inquiryId);
      return cust;
    },

    /* Follow-ups */
    async listFollowUps(customerId) {
      var c = client();
      return await c.from('follow_ups').select('*').eq('customer_id', customerId).order('contact_date', { ascending: false });
    },
    async addFollowUp(data) {
      var c = client();
      return await c.from('follow_ups').insert(data).select().single();
    },
    async deleteFollowUp(id) {
      var c = client();
      return await c.from('follow_ups').delete().eq('id', id);
    },

    /* News */
    async listNews(filters) {
      var c = client();
      var q = c.from('news').select('*', { count: 'exact' }).order('created_at', { ascending: false });
      if (filters) {
        if (filters.search) q = q.or('title.ilike.%' + filters.search + '%');
        if (filters.status && filters.status !== 'all') q = q.eq('status', filters.status);
        if (filters.category && filters.category !== 'all') q = q.eq('category', filters.category);
      }
      return await q;
    },
    async getNews(id) {
      var c = client();
      return await c.from('news').select('*').eq('id', id).single();
    },
    async createNews(data) {
      var c = client();
      return await c.from('news').insert(data).select().single();
    },
    async updateNews(id, data) {
      var c = client();
      return await c.from('news').update(data).eq('id', id).select().single();
    },
    async deleteNews(id) {
      var c = client();
      return await c.from('news').delete().eq('id', id);
    },

    /* SEO */
    async listSeo() {
      var c = client();
      return await c.from('seo_pages').select('*').order('page_path', { ascending: true });
    },
    async getSeoByPath(path) {
      var c = client();
      return await c.from('seo_pages').select('*').eq('page_path', path).maybeSingle();
    },
    async upsertSeo(data) {
      var c = client();
      return await c.from('seo_pages').upsert(data, { onConflict: 'page_path' }).select().single();
    },
    async deleteSeo(id) {
      var c = client();
      return await c.from('seo_pages').delete().eq('id', id);
    },

    /* Dashboard stats */
    async dashboardStats() {
      var c = client();
      var now = new Date();
      var monthAgo = new Date(now.getTime() - 30 * 86400000).toISOString();
      var results = {};
      var r;
      r = await c.from('customers').select('id', { count: 'exact', head: true }); results.totalCustomers = r.count || 0;
      r = await c.from('customers').select('id', { count: 'exact', head: true }).eq('status', 'new'); results.newLeads = r.count || 0;
      r = await c.from('customers').select('id', { count: 'exact', head: true }).eq('status', 'won'); results.wonCustomers = r.count || 0;
      r = await c.from('inquiries').select('id', { count: 'exact', head: true }); results.totalInquiries = r.count || 0;
      r = await c.from('inquiries').select('id', { count: 'exact', head: true }).eq('status', 'pending'); results.pendingInquiries = r.count || 0;
      r = await c.from('inquiries').select('id', { count: 'exact', head: true }).gte('created_at', monthAgo); results.recentInquiries = r.count || 0;
      r = await c.from('news').select('id', { count: 'exact', head: true }).eq('status', 'published'); results.publishedNews = r.count || 0;
      r = await c.from('news').select('id', { count: 'exact', head: true }).eq('status', 'draft'); results.draftNews = r.count || 0;
      return results;
    }
  };

  /* ---------- Expose ---------- */
  window.AdminApp = {
    client: client,
    isConfigured: isConfigured,
    getSession: getSession,
    requireAuth: requireAuth,
    login: login,
    logout: logout,
    currentUser: currentUser,
    mount: mount,
    toast: toast, ok: ok, err: err, info: info,
    fmtDate: fmtDate, fmtDateTime: fmtDateTime, timeAgo: timeAgo,
    escapeHtml: escapeHtml, debounce: debounce,
    badge: badge,
    exportCSV: exportCSV,
    DB: DB,
  };
})();
