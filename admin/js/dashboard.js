/* Dashboard — overview stats & recent activity */
AdminApp.mount('dashboard.html', 'Dashboard', async function (content) {
  var A = AdminApp;
  content.innerHTML =
    '<div class="loading"><div class="spinner"></div>Loading dashboard…</div>';

  try {
    var s = await A.DB.dashboardStats();
    var recent = await A.client().from('inquiries').select('*').order('created_at', { ascending: false }).limit(8);
    var recentList = recent.data || [];

    var stats = [
      { label: 'Total Customers', value: s.totalCustomers || 0, icon: '👥', cls: 'icon-blue' },
      { label: 'New Leads', value: s.newLeads || 0, icon: '✨', cls: 'icon-amber' },
      { label: 'Total Inquiries', value: s.totalInquiries || 0, icon: '📩', cls: 'icon-purple' },
      { label: 'Pending Inquiries', value: s.pendingInquiries || 0, icon: '⏳', cls: 'icon-amber' },
      { label: 'Won Customers', value: s.wonCustomers || 0, icon: '🏆', cls: 'icon-green' },
      { label: 'Published News', value: s.publishedNews || 0, icon: '📰', cls: 'icon-green' },
    ];

    var statHtml = stats.map(function (st) {
      return '<div class="stat-card"><div class="stat-icon ' + st.cls + '">' + st.icon + '</div>' +
        '<div class="stat-label">' + st.label + '</div><div class="stat-value">' + st.value + '</div></div>';
    }).join('');

    var inquiryRows = recentList.length ? recentList.map(function (q) {
      return '<tr><td><strong>' + A.escapeHtml(q.contact_name || 'Unknown') + '</strong><br><span class="muted">' +
        A.escapeHtml(q.company_name || '-') + '</span></td>' +
        '<td>' + A.escapeHtml(q.product_interest || '-') + '</td>' +
        '<td>' + A.escapeHtml(q.country || '-') + '</td>' +
        '<td>' + A.badge(q.status) + '</td>' +
        '<td class="muted">' + A.timeAgo(q.created_at) + '</td>' +
        '<td><a href="inquiries.html" class="btn btn-sm btn-outline">View</a></td></tr>';
    }).join('') : '<tr><td colspan="6"><div class="empty">No inquiries yet</div></td></tr>';

    content.innerHTML =
      statHtml ?
        '<div class="stat-grid">' + statHtml + '</div>' +
        '<div style="display:grid;grid-template-columns:2fr 1fr;gap:20px">' +
          '<div class="card"><div class="card-head"><h3>Recent Inquiries</h3><a href="inquiries.html" class="btn btn-sm btn-outline">View All</a></div>' +
            '<div class="table-wrap"><table class="data"><thead><tr><th>Customer</th><th>Product</th><th>Country</th><th>Status</th><th>Received</th><th></th></tr></thead>' +
            '<tbody>' + inquiryRows + '</tbody></table></div></div>' +
          '<div class="card card-pad"><h3 style="margin-bottom:16px">Quick Actions</h3>' +
            '<div style="display:flex;flex-direction:column;gap:10px">' +
              '<a href="customers.html" class="btn">👥 Manage Customers</a>' +
              '<a href="inquiries.html" class="btn btn-outline">📩 Review Inquiries</a>' +
              '<a href="news-edit.html" class="btn btn-outline">✍️ Write News Article</a>' +
              '<a href="seo.html" class="btn btn-outline">🔍 Edit SEO Settings</a>' +
              '<a href="../news.html" target="_blank" class="btn btn-gray">🌐 View News Page</a>' +
            '</div>' +
            '<div style="margin-top:20px;padding:14px;background:var(--blue-soft);border-radius:10px;font-size:13px;color:var(--muted)">' +
              '<strong>💡 Tip:</strong> Update news articles regularly to improve SEO ranking and keep your site fresh for search engines.</div>' +
          '</div>' +
        '</div>'
      : '<div class="empty"><p>Dashboard is ready. Start by adding customers or waiting for inquiries.</p></div>';
  } catch (e) {
    content.innerHTML = '<div class="empty"><p>Failed to load: ' + A.escapeHtml(e.message) + '</p></div>';
  }
});
