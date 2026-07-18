/* News — list articles, filter, publish/unpublish, delete */
AdminApp.mount('news.html', 'News & Blog', async function (content) {
  var A = AdminApp;
  var state = { search: '', status: 'all', category: 'all' };

  content.innerHTML = renderShell();
  bindEvents();
  loadList();

  function renderShell() {
    return '' +
      '<div class="toolbar"><div class="left"><a href="news-edit.html" class="btn">+ New Article</a></div>' +
        '<div class="right"><a href="dashboard.html" class="btn btn-gray">← Dashboard</a></div></div>' +
      '<div class="filters">' +
        '<div class="search"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="11" cy="11" r="8"/><path d="m21 21-4.3-4.3"/></svg>' +
        '<input type="text" id="searchInput" placeholder="Search articles…"></div>' +
        '<select id="statusFilter"><option value="all">All Status</option><option value="draft">Draft</option><option value="published">Published</option></select>' +
        '<select id="catFilter"><option value="all">All Categories</option>' +
          '<option value="company-news">Company News</option><option value="industry">Industry</option>' +
          '<option value="exhibition">Exhibition</option><option value="tech">Technology</option>' +
          '<option value="case-study">Case Study</option></select>' +
      '</div>' +
      '<div id="listArea"><div class="loading"><div class="spinner"></div>Loading articles…</div></div>';
  }

  function bindEvents() {
    document.getElementById('searchInput').addEventListener('input', A.debounce(function () {
      state.search = this.value.trim(); loadList();
    }, 300));
    document.getElementById('statusFilter').addEventListener('change', function () { state.status = this.value; loadList(); });
    document.getElementById('catFilter').addEventListener('change', function () { state.category = this.value; loadList(); });
  }

  async function loadList() {
    var area = document.getElementById('listArea');
    area.innerHTML = '<div class="loading"><div class="spinner"></div>Loading…</div>';
    try {
      var r = await A.DB.listNews(state);
      var rows = r.data || [];
      if (!rows.length) {
        area.innerHTML = '<div class="card"><div class="empty"><p>No articles yet. Click "New Article" to write your first post.</p>' +
          '<a href="news-edit.html" class="btn" style="margin-top:12px">+ Write Article</a></div></div>';
        return;
      }
      var catLabels = { 'company-news': 'Company News', 'industry': 'Industry', 'exhibition': 'Exhibition', 'tech': 'Technology', 'case-study': 'Case Study' };
      var html = '<div class="card"><div class="table-wrap"><table class="data"><thead><tr>' +
        '<th>Title</th><th>Category</th><th>Status</th><th>Views</th><th>Updated</th><th></th></tr></thead><tbody>';
      html += rows.map(function (n) {
        return '<tr>' +
          '<td><strong>' + A.escapeHtml(n.title) + '</strong><br><span class="small muted">/' + A.escapeHtml(n.slug) + '</span></td>' +
          '<td><span class="badge badge-gray">' + A.escapeHtml(catLabels[n.category] || n.category) + '</span></td>' +
          '<td>' + A.badge(n.status) + '</td>' +
          '<td>' + (n.view_count || 0) + '</td>' +
          '<td class="muted">' + A.timeAgo(n.updated_at) + '</td>' +
          '<td class="actions">' +
            '<a href="news-edit.html?id=' + n.id + '" class="icon-btn" title="Edit">✏️</a>' +
            (n.status === 'published'
              ? '<button class="icon-btn" data-unpub="' + n.id + '" title="Unpublish">📤</button>'
              : '<button class="icon-btn" data-pub="' + n.id + '" title="Publish">✅</button>') +
            (n.status === 'published' ? '<a href="../news/' + A.escapeHtml(n.slug) + '.html" target="_blank" class="icon-btn" title="View">👁</a>' : '') +
            '<button class="icon-btn danger" data-del="' + n.id + '" title="Delete">🗑</button>' +
          '</td></tr>';
      }).join('');
      html += '</tbody></table></div></div>';
      area.innerHTML = html;

      area.querySelectorAll('[data-pub]').forEach(function (b) {
        b.addEventListener('click', function () { togglePublish(this.getAttribute('data-pub'), 'published'); });
      });
      area.querySelectorAll('[data-unpub]').forEach(function (b) {
        b.addEventListener('click', function () { togglePublish(this.getAttribute('data-unpub'), 'draft'); });
      });
      area.querySelectorAll('[data-del]').forEach(function (b) {
        b.addEventListener('click', function () { delNews(this.getAttribute('data-del')); });
      });
    } catch (e) {
      area.innerHTML = '<div class="empty"><p>Error: ' + A.escapeHtml(e.message) + '</p></div>';
    }
  }

  async function togglePublish(id, status) {
    var data = { status: status };
    if (status === 'published') data.published_at = new Date().toISOString();
    try {
      var r = await A.DB.updateNews(id, data);
      if (r.error) throw r.error;
      A.ok(status === 'published' ? 'Article published' : 'Moved to draft');
      loadList();
    } catch (err) { A.err(err.message); }
  }

  async function delNews(id) {
    if (!confirm('Delete this article permanently?')) return;
    try {
      var r = await A.DB.deleteNews(id);
      if (r.error) throw r.error;
      A.ok('Article deleted');
      loadList();
    } catch (err) { A.err(err.message); }
  }
});
