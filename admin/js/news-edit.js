/* News Editor — create/edit articles with SEO metadata */
AdminApp.mount('news-edit.html', 'Edit Article', async function (content) {
  var A = AdminApp;
  var params = new URLSearchParams(window.location.search);
  var articleId = params.get('id');
  var editing = !!articleId;

  content.innerHTML = renderForm();

  // Auto-generate slug from title
  document.getElementById('f_title').addEventListener('input', function () {
    if (!editing || !document.getElementById('f_slug').dataset.touched) {
      var slug = this.value.toLowerCase().replace(/[^a-z0-9]+/g, '-').replace(/^-+|-+$/g, '');
      document.getElementById('f_slug').value = slug;
    }
  });
  document.getElementById('f_slug').addEventListener('input', function () { this.dataset.touched = '1'; });

  // Toolbar buttons for content
  document.querySelectorAll('[data-insert]').forEach(function (btn) {
    btn.addEventListener('click', function () {
      var ta = document.getElementById('f_content');
      var tag = this.getAttribute('data-insert');
      var sel = ta.selectionStart, end = ta.selectionEnd;
      var selected = ta.value.substring(sel, end);
      var wrap = { h2: '<h2>', h3: '<h3>', p: '<p>', b: '<strong>', i: '<em>', a: '<a href="#">', ul: '<ul><li>', li: '<li>' };
      var close = { h2: '</h2>', h3: '</h3>', p: '</p>', b: '</strong>', i: '</em>', a: '</a>', ul: '</li></ul>', li: '</li>' };
      var text = (wrap[tag] || '') + (selected || 'Text') + (close[tag] || '');
      ta.value = ta.value.substring(0, sel) + text + ta.value.substring(end);
      ta.focus();
      ta.selectionStart = sel + text.length;
    });
  });

  document.getElementById('btnCancel').addEventListener('click', function () { window.location.href = 'news.html'; });
  document.getElementById('btnDraft').addEventListener('click', function () { save('draft'); });
  document.getElementById('btnPublish').addEventListener('click', function () { save('published'); });

  if (editing) loadArticle();

  function renderForm() {
    return '' +
      '<div class="toolbar"><div class="left"><a href="news.html" class="btn btn-gray">← Back to Articles</a></div>' +
        '<div class="right"><button class="btn btn-gray" id="btnCancel">Cancel</button> ' +
        '<button class="btn btn-outline" id="btnDraft">💾 Save Draft</button> ' +
        '<button class="btn" id="btnPublish">🚀 Publish</button></div></div>' +
      '<div style="display:grid;grid-template-columns:1fr 320px;gap:20px">' +
        '<div class="card card-pad news-editor">' +
          '<div class="field"><label>Article Title <span class="req">*</span></label><input type="text" id="f_title" required placeholder="e.g. Woneng Showcases New Solar Street Light at Exhibition"></div>' +
          '<div class="field"><label>URL Slug</label><input type="text" id="f_slug" placeholder="auto-generated-from-title"><div class="field-hint">URL: /news/your-slug.html</div></div>' +
          '<div class="field"><label>Summary</label><textarea id="f_summary" style="min-height:70px" placeholder="Brief excerpt shown in news listings and search results…"></textarea></div>' +
          '<div class="field"><label>Content (HTML)</label>' +
            '<div style="display:flex;gap:4px;margin-bottom:8px;flex-wrap:wrap">' +
              '<button type="button" class="btn btn-sm btn-gray" data-insert="h2">H2</button>' +
              '<button type="button" class="btn btn-sm btn-gray" data-insert="h3">H3</button>' +
              '<button type="button" class="btn btn-sm btn-gray" data-insert="p">¶</button>' +
              '<button type="button" class="btn btn-sm btn-gray" data-insert="b"><strong>B</strong></button>' +
              '<button type="button" class="btn btn-sm btn-gray" data-insert="i"><em>I</em></button>' +
              '<button type="button" class="btn btn-sm btn-gray" data-insert="a">Link</button>' +
              '<button type="button" class="btn btn-sm btn-gray" data-insert="ul">• List</button>' +
            '</div>' +
            '<textarea id="f_content" placeholder="<h2>Heading</h2>&#10;<p>Write your article content here in HTML format…</p>"></textarea>' +
            '<div class="field-hint">Tip: Use HTML tags. The content renders on the public news page.</div>' +
          '</div>' +
        '</div>' +
        '<div>' +
          '<div class="card card-pad" style="margin-bottom:20px">' +
            '<h3 style="margin-bottom:14px">Publish Settings</h3>' +
            '<div class="field"><label>Category</label><select id="f_category">' +
              '<option value="company-news">Company News</option><option value="industry">Industry</option>' +
              '<option value="exhibition">Exhibition</option><option value="tech">Technology</option>' +
              '<option value="case-study">Case Study</option></select></div>' +
            '<div class="field"><label>Author</label><input type="text" id="f_author" value="Woneng"></div>' +
            '<div class="field"><label>Cover Image URL</label><input type="text" id="f_cover" placeholder="https://…/image.webp"></div>' +
            '<div class="field"><label>Status</label><select id="f_status"><option value="draft">Draft</option><option value="published">Published</option></select></div>' +
          '</div>' +
          '<div class="card card-pad">' +
            '<h3 style="margin-bottom:14px">🔍 SEO Settings</h3>' +
            '<div class="field"><label>Meta Title</label><input type="text" id="f_meta_title" placeholder="SEO title (50-60 chars)"><div class="field-hint">Optimal: 50-60 characters</div></div>' +
            '<div class="field"><label>Meta Description</label><textarea id="f_meta_desc" style="min-height:70px" placeholder="SEO description (150-160 chars)"></textarea><div class="field-hint">Optimal: 150-160 characters</div></div>' +
            '<div class="field"><label>Meta Keywords</label><input type="text" id="f_meta_kw" placeholder="solar street light, Nigeria, B2B"></div>' +
            '<div style="margin-top:14px;padding:12px;background:var(--blue-soft);border-radius:8px;font-size:12px;color:var(--muted)">' +
              '<strong>💡 SEO Tip:</strong> If meta fields are left empty, the article title and summary will be used automatically.</div>' +
          '</div>' +
        '</div>' +
      '</div>';
  }

  async function loadArticle() {
    try {
      var r = await A.DB.getNews(articleId);
      if (r.error || !r.data) { A.err('Article not found'); window.location.href = 'news.html'; return; }
      var n = r.data;
      ['title', 'slug', 'summary', 'content', 'cover_image', 'author', 'meta_title', 'meta_keywords'].forEach(function (k) {
        var el = document.getElementById('f_' + k.replace('meta_keywords', 'meta_kw').replace('meta_description', 'meta_desc').replace('cover_image', 'cover'));
        if (el) el.value = n[k] || '';
      });
      document.getElementById('f_meta_desc').value = n.meta_description || '';
      document.getElementById('f_category').value = n.category || 'company-news';
      document.getElementById('f_status').value = n.status || 'draft';
      document.getElementById('f_slug').dataset.touched = '1';
    } catch (e) { A.err('Failed to load article'); }
  }

  async function save(targetStatus) {
    var data = {
      title: document.getElementById('f_title').value.trim(),
      slug: document.getElementById('f_slug').value.trim(),
      summary: document.getElementById('f_summary').value.trim(),
      content: document.getElementById('f_content').value.trim(),
      category: document.getElementById('f_category').value,
      author: document.getElementById('f_author').value.trim() || 'Woneng',
      cover_image: document.getElementById('f_cover').value.trim(),
      status: targetStatus,
      meta_title: document.getElementById('f_meta_title').value.trim() || null,
      meta_description: document.getElementById('f_meta_desc').value.trim() || null,
      meta_keywords: document.getElementById('f_meta_kw').value.trim() || null,
    };
    if (!data.title) { A.err('Title is required'); return; }
    if (!data.slug) data.slug = data.title.toLowerCase().replace(/[^a-z0-9]+/g, '-').replace(/^-+|-+$/g, '');
    if (targetStatus === 'published' && !editing) data.published_at = new Date().toISOString();
    else if (targetStatus === 'published') data.published_at = new Date().toISOString();

    var btn = targetStatus === 'published' ? document.getElementById('btnPublish') : document.getElementById('btnDraft');
    var orig = btn.textContent;
    btn.disabled = true; btn.textContent = 'Saving…';
    try {
      var r = editing ? await A.DB.updateNews(articleId, data) : await A.DB.createNews(data);
      if (r.error) throw r.error;
      A.ok(targetStatus === 'published' ? 'Article published!' : 'Draft saved');
      setTimeout(function () { window.location.href = 'news.html'; }, 1000);
    } catch (err) {
      A.err(err.message || 'Save failed');
      btn.disabled = false; btn.textContent = orig;
    }
  }
});
