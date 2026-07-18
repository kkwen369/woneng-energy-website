/* SEO Settings — manage meta tags per page */
AdminApp.mount('seo.html', 'SEO Settings', async function (content) {
  var A = AdminApp;

  // Predefined site pages for quick setup
  var KNOWN_PAGES = [
    { path: 'index.html', title: 'Home' },
    { path: 'about.html', title: 'About Us' },
    { path: 'products.html', title: 'Products' },
    { path: 'solutions.html', title: 'Solutions' },
    { path: 'projects.html', title: 'Projects' },
    { path: 'factory.html', title: 'Factory' },
    { path: 'certifications.html', title: 'Certifications' },
    { path: 'contact.html', title: 'Contact' },
    { path: 'news.html', title: 'News & Blog' },
  ];

  content.innerHTML = renderShell();
  document.getElementById('searchInput').addEventListener('input', A.debounce(function () {
    loadList(this.value.trim());
  }, 300));
  document.getElementById('btnAdd').addEventListener('click', function () { openModal(); });
  document.getElementById('modalClose').addEventListener('click', closeModal);
  document.getElementById('modalBack').addEventListener('click', function (e) { if (e.target === this) closeModal(); });
  document.getElementById('btnSave').addEventListener('click', saveSeo);
  document.getElementById('f_path').addEventListener('change', function () {
    var known = KNOWN_PAGES.find(function (p) { return p.path === this.value; });
    if (known) document.getElementById('f_title').value = known.title;
  });

  loadList('');

  function renderShell() {
    return '' +
      '<div class="toolbar"><div class="left"><button class="btn" id="btnAdd">+ Add Page SEO</button></div>' +
        '<div class="right"><a href="dashboard.html" class="btn btn-gray">← Dashboard</a></div></div>' +
      '<div class="filters"><div class="search"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="11" cy="11" r="8"/><path d="m21 21-4.3-4.3"/></svg>' +
        '<input type="text" id="searchInput" placeholder="Search pages…"></div></div>' +
      '<div id="listArea"><div class="loading"><div class="spinner"></div>Loading…</div></div>' +
      '<div class="modal-back" id="modalBack"><div class="modal" style="max-width:640px">' +
        '<div class="modal-head"><h3 id="modalTitle">Add SEO Settings</h3><button class="modal-close" id="modalClose">×</button></div>' +
        '<div class="modal-body"><form id="seoForm"><input type="hidden" id="f_id">' +
          '<div class="field"><label>Page Path <span class="req">*</span></label>' +
            '<input type="text" id="f_path" list="pageList" placeholder="index.html" required>' +
            '<datalist id="pageList">' + KNOWN_PAGES.map(function (p) { return '<option value="' + p.path + '">'; }).join('') + '</datalist>' +
            '<div class="field-hint">The page filename, e.g. index.html or products/aio-solar-street-light.html</div></div>' +
          '<div class="field"><label>Page Title (internal label)</label><input type="text" id="f_title" placeholder="Home Page"></div>' +
          '<div style="margin:16px 0 8px;font-size:12px;font-weight:700;color:var(--muted);text-transform:uppercase;letter-spacing:.05em">Meta Tags</div>' +
          '<div class="field"><label>Meta Title</label><input type="text" id="f_meta_title" placeholder="SEO title (50-60 chars)" maxlength="70">' +
            '<div class="field-hint"><span id="c_title">0</span>/70 — optimal 50-60</div></div>' +
          '<div class="field"><label>Meta Description</label><textarea id="f_meta_desc" style="min-height:60px" placeholder="SEO description (150-160 chars)" maxlength="170"></textarea>' +
            '<div class="field-hint"><span id="c_desc">0</span>/170 — optimal 150-160</div></div>' +
          '<div class="field"><label>Meta Keywords</label><input type="text" id="f_meta_kw" placeholder="solar street light, Nigeria, B2B"></div>' +
          '<div style="margin:16px 0 8px;font-size:12px;font-weight:700;color:var(--muted);text-transform:uppercase;letter-spacing:.05em">Open Graph (Social Sharing)</div>' +
          '<div class="field"><label>OG Title</label><input type="text" id="f_og_title" placeholder="Social share title"></div>' +
          '<div class="field"><label>OG Description</label><textarea id="f_og_desc" style="min-height:50px" placeholder="Social share description"></textarea></div>' +
          '<div class="field"><label>OG Image URL</label><input type="text" id="f_og_image" placeholder="https://…/image.webp"></div>' +
          '<div class="field"><label>Canonical URL</label><input type="text" id="f_canonical" placeholder="https://kkwen369.github.io/woneng-energy-website/index.html"></div>' +
        '</form></div>' +
        '<div class="modal-foot"><button class="btn btn-gray" id="btnCancel2">Cancel</button> <button class="btn" id="btnSave">Save</button></div>' +
      '</div></div>';
  }

  // Char counters
  document.getElementById('f_meta_title').addEventListener('input', function () { document.getElementById('c_title').textContent = this.value.length; });
  document.getElementById('f_meta_desc').addEventListener('input', function () { document.getElementById('c_desc').textContent = this.value.length; });
  document.getElementById('btnCancel2').addEventListener('click', closeModal);

  async function loadList(search) {
    var area = document.getElementById('listArea');
    area.innerHTML = '<div class="loading"><div class="spinner"></div>Loading…</div>';
    try {
      var r = await A.DB.listSeo();
      var rows = r.data || [];
      var filtered = search ? rows.filter(function (s) { return s.page_path.indexOf(search) >= 0 || (s.page_title || '').indexOf(search) >= 0; }) : rows;

      // Also show known pages without SEO config
      var configuredPaths = rows.map(function (r) { return r.page_path; });
      var unconfigured = KNOWN_PAGES.filter(function (p) { return configuredPaths.indexOf(p.path) < 0; });

      var html = '';

      // Configured pages
      if (filtered.length) {
        html += '<div class="card" style="margin-bottom:20px"><div class="card-head"><h3>✅ Configured Pages (' + filtered.length + ')</h3></div><div class="table-wrap"><table class="data"><thead><tr>' +
          '<th>Page</th><th>Meta Title</th><th>Meta Description</th><th>Updated</th><th></th></tr></thead><tbody>';
        html += filtered.map(function (s) {
          return '<tr>' +
            '<td><strong>' + A.escapeHtml(s.page_title || s.page_path) + '</strong><br><span class="small muted">' + A.escapeHtml(s.page_path) + '</span></td>' +
            '<td class="small">' + A.escapeHtml((s.meta_title || '').substring(0, 50)) + (s.meta_title && s.meta_title.length > 50 ? '…' : '') + '</td>' +
            '<td class="small">' + A.escapeHtml((s.meta_description || '').substring(0, 60)) + (s.meta_description && s.meta_description.length > 60 ? '…' : '') + '</td>' +
            '<td class="muted">' + A.timeAgo(s.updated_at) + '</td>' +
            '<td class="actions"><button class="icon-btn" data-edit="' + s.id + '" title="Edit">✏️</button>' +
            '<button class="icon-btn danger" data-del="' + s.id + '" title="Delete">🗑</button></td></tr>';
        }).join('');
        html += '</tbody></table></div></div>';
      }

      // Unconfigured known pages
      if (unconfigured.length) {
        html += '<div class="card"><div class="card-head"><h3>⚠️ Pages Without SEO (' + unconfigured.length + ')</h3></div><div class="table-wrap"><table class="data"><thead><tr>' +
          '<th>Page</th><th></th></tr></thead><tbody>';
        html += unconfigured.map(function (p) {
          return '<tr><td>' + A.escapeHtml(p.title) + ' <span class="small muted">(' + A.escapeHtml(p.path) + ')</span></td>' +
            '<td><button class="btn btn-sm btn-outline" data-add="' + A.escapeHtml(p.path) + '">+ Add SEO</button></td></tr>';
        }).join('');
        html += '</tbody></table></div></div>';
      }

      if (!filtered.length && !unconfigured.length) {
        html = '<div class="card"><div class="empty"><p>No SEO settings found. Click "Add Page SEO" to configure your first page.</p></div></div>';
      }

      area.innerHTML = html;
      area.querySelectorAll('[data-edit]').forEach(function (b) { b.addEventListener('click', function () { openModal(this.getAttribute('data-edit')); }); });
      area.querySelectorAll('[data-del]').forEach(function (b) { b.addEventListener('click', function () { delSeo(this.getAttribute('data-del')); }); });
      area.querySelectorAll('[data-add]').forEach(function (b) { b.addEventListener('click', function () { openModal(null, this.getAttribute('data-add')); }); });
    } catch (e) {
      area.innerHTML = '<div class="empty"><p>Error: ' + A.escapeHtml(e.message) + '</p></div>';
    }
  }

  async function openModal(id, presetPath) {
    var form = document.getElementById('seoForm');
    form.reset();
    document.getElementById('f_id').value = '';
    document.getElementById('c_title').textContent = '0';
    document.getElementById('c_desc').textContent = '0';

    if (id) {
      document.getElementById('modalTitle').textContent = 'Edit SEO Settings';
      var r = await A.DB.listSeo();
      var s = (r.data || []).find(function (x) { return x.id === id; });
      if (s) {
        document.getElementById('f_id').value = s.id;
        document.getElementById('f_path').value = s.page_path;
        document.getElementById('f_title').value = s.page_title || '';
        document.getElementById('f_meta_title').value = s.meta_title || '';
        document.getElementById('f_meta_desc').value = s.meta_description || '';
        document.getElementById('f_meta_kw').value = s.meta_keywords || '';
        document.getElementById('f_og_title').value = s.og_title || '';
        document.getElementById('f_og_desc').value = s.og_description || '';
        document.getElementById('f_og_image').value = s.og_image || '';
        document.getElementById('f_canonical').value = s.canonical_url || '';
        document.getElementById('c_title').textContent = (s.meta_title || '').length;
        document.getElementById('c_desc').textContent = (s.meta_description || '').length;
      }
    } else {
      document.getElementById('modalTitle').textContent = 'Add SEO Settings';
      if (presetPath) {
        document.getElementById('f_path').value = presetPath;
        var known = KNOWN_PAGES.find(function (p) { return p.path === presetPath; });
        if (known) document.getElementById('f_title').value = known.title;
      }
    }
    document.getElementById('modalBack').classList.add('show');
  }

  function closeModal() { document.getElementById('modalBack').classList.remove('show'); }

  async function saveSeo() {
    var path = document.getElementById('f_path').value.trim();
    if (!path) { A.err('Page path is required'); return; }
    var data = {
      page_path: path,
      page_title: document.getElementById('f_title').value.trim(),
      meta_title: document.getElementById('f_meta_title').value.trim() || null,
      meta_description: document.getElementById('f_meta_desc').value.trim() || null,
      meta_keywords: document.getElementById('f_meta_kw').value.trim() || null,
      og_title: document.getElementById('f_og_title').value.trim() || null,
      og_description: document.getElementById('f_og_desc').value.trim() || null,
      og_image: document.getElementById('f_og_image').value.trim() || null,
      canonical_url: document.getElementById('f_canonical').value.trim() || null,
    };
    var id = document.getElementById('f_id').value;
    if (id) data.id = id;
    var btn = document.getElementById('btnSave');
    btn.disabled = true; btn.textContent = 'Saving…';
    try {
      var r = await A.DB.upsertSeo(data);
      if (r.error) throw r.error;
      A.ok('SEO settings saved');
      closeModal();
      loadList('');
    } catch (err) { A.err(err.message || 'Save failed'); }
    btn.disabled = false; btn.textContent = 'Save';
  }

  async function delSeo(id) {
    if (!confirm('Delete these SEO settings?')) return;
    try {
      var r = await A.DB.deleteSeo(id);
      if (r.error) throw r.error;
      A.ok('Deleted');
      loadList('');
    } catch (err) { A.err(err.message); }
  }
});
