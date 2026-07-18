/* Inquiries — list, search, view, update status, convert to customer, export */
AdminApp.mount('inquiries.html', 'Inquiries', async function (content) {
  var A = AdminApp;
  var state = { search: '', status: 'all' };

  content.innerHTML = renderShell();

  document.getElementById('searchInput').addEventListener('input', A.debounce(function () {
    state.search = this.value.trim(); loadList();
  }, 300));
  document.getElementById('statusFilter').addEventListener('change', function () {
    state.status = this.value; loadList();
  });
  document.getElementById('btnExport').addEventListener('click', doExport);
  document.getElementById('modalClose').addEventListener('click', closeModal);
  document.getElementById('modalBack').addEventListener('click', function (e) { if (e.target === this) closeModal(); });

  loadList();

  function renderShell() {
    return '' +
      '<div class="toolbar"><div class="left"><button class="btn btn-outline" id="btnExport">⬇ Export CSV</button></div>' +
        '<div class="right"><a href="dashboard.html" class="btn btn-gray">← Dashboard</a></div></div>' +
      '<div class="filters">' +
        '<div class="search"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="11" cy="11" r="8"/><path d="m21 21-4.3-4.3"/></svg>' +
        '<input type="text" id="searchInput" placeholder="Search name, company, product…"></div>' +
        '<select id="statusFilter"><option value="all">All Status</option>' +
          '<option value="pending">Pending</option><option value="replied">Replied</option>' +
          '<option value="quoted">Quoted</option><option value="closed">Closed</option></select>' +
      '</div>' +
      '<div id="listArea"><div class="loading"><div class="spinner"></div>Loading inquiries…</div></div>' +
      '<div class="modal-back" id="modalBack">' +
        '<div class="modal"><div class="modal-head"><h3>Inquiry Detail</h3><button class="modal-close" id="modalClose">×</button></div>' +
        '<div class="modal-body" id="modalBody"></div>' +
        '<div class="modal-foot" id="modalFoot"></div></div>' +
      '</div>';
  }

  async function loadList() {
    var area = document.getElementById('listArea');
    area.innerHTML = '<div class="loading"><div class="spinner"></div>Loading…</div>';
    try {
      var r = await A.DB.listInquiries(state);
      var rows = r.data || [];
      if (!rows.length) {
        area.innerHTML = '<div class="card"><div class="empty"><svg viewBox="0 0 24 24" fill="currentColor"><path d="M20 4H4c-1.1 0-1.99.9-1.99 2L2 18c0 1.1.9 2 2 2h16c1.1 0 2-.9 2-2V6c0-1.1-.9-2-2-2zm0 4l-8 5-8-5V6l8 5 8-5v2z"/></svg><p>No inquiries yet. New inquiries from your website forms will appear here automatically.</p></div></div>';
        return;
      }
      var html = '<div class="card"><div class="table-wrap"><table class="data"><thead><tr>' +
        '<th>Customer</th><th>Product Interest</th><th>Country</th><th>Status</th><th>Received</th><th></th></tr></thead><tbody>';
      html += rows.map(function (q) {
        return '<tr>' +
          '<td><strong>' + A.escapeHtml(q.contact_name || 'Unknown') + '</strong><br><span class="muted">' + A.escapeHtml(q.company_name || q.email || '') + '</span></td>' +
          '<td>' + A.escapeHtml(q.product_interest || '—') + '</td>' +
          '<td>' + A.escapeHtml(q.country || '—') + '</td>' +
          '<td>' + A.badge(q.status) + '</td>' +
          '<td class="muted">' + A.timeAgo(q.created_at) + '</td>' +
          '<td class="actions"><button class="icon-btn" data-view="' + q.id + '" title="View">👁</button>' +
            (q.status === 'pending' ? '<button class="icon-btn" data-conv="' + q.id + '" title="Convert to Customer">👤+</button>' : '') +
            '<button class="icon-btn danger" data-del="' + q.id + '" title="Delete">🗑</button></td></tr>';
      }).join('');
      html += '</tbody></table></div></div>';
      area.innerHTML = html;

      area.querySelectorAll('[data-view]').forEach(function (b) {
        b.addEventListener('click', function () { viewInquiry(this.getAttribute('data-view')); });
      });
      area.querySelectorAll('[data-conv]').forEach(function (b) {
        b.addEventListener('click', function () { convertInquiry(this.getAttribute('data-conv')); });
      });
      area.querySelectorAll('[data-del]').forEach(function (b) {
        b.addEventListener('click', function () { delInquiry(this.getAttribute('data-del')); });
      });
    } catch (e) {
      area.innerHTML = '<div class="empty"><p>Error: ' + A.escapeHtml(e.message) + '</p></div>';
    }
  }

  async function viewInquiry(id) {
    var body = document.getElementById('modalBody');
    var foot = document.getElementById('modalFoot');
    body.innerHTML = '<div class="loading"><div class="spinner"></div></div>';
    foot.innerHTML = '';
    document.getElementById('modalBack').classList.add('show');
    try {
      var r = await A.DB.getInquiry(id);
      if (r.error) throw r.error;
      var q = r.data;
      body.innerHTML =
        '<div class="detail-grid">' +
          field('Contact Name', q.contact_name) +
          field('Company', q.company_name) +
          field('Email', q.email) +
          field('Phone', q.phone) +
          field('WhatsApp', q.whatsapp) +
          field('Country', q.country) +
          field('Product Interest', q.product_interest) +
          field('Quantity', q.quantity) +
          field('Target Market', q.target_market) +
          field('Source Page', q.source_page) +
        '</div>' +
        '<div class="card card-pad" style="margin-top:16px"><strong>Message:</strong><br>' + A.escapeHtml(q.message || 'No message').replace(/\n/g, '<br>') + '</div>';
      foot.innerHTML = '<button class="btn btn-gray" onclick="document.getElementById(\'modalClose\').click()">Close</button>' +
        statusBtns(q.id, q.status) +
        (q.status === 'pending' ? '<button class="btn" id="btnConvert">👤 Convert to Customer</button>' : '');
      var cb = document.getElementById('btnConvert');
      if (cb) cb.addEventListener('click', function () { closeModal(); convertInquiry(id); });
    } catch (e) { body.innerHTML = '<p class="err">Error: ' + A.escapeHtml(e.message) + '</p>'; }
  }

  function field(k, v) {
    return '<div class="detail-row"><span class="k">' + k + '</span><span class="v">' + A.escapeHtml(v || '—') + '</span></div>';
  }

  function statusBtns(id, current) {
    var statuses = ['pending', 'replied', 'quoted', 'closed'];
    return '<div style="margin-left:auto;display:flex;gap:6px">' + statuses.map(function (s) {
      var cls = s === current ? 'btn btn-sm' : 'btn btn-sm btn-gray';
      return '<button class="' + cls + '" data-status="' + s + '" data-id="' + id + '">' + s + '</button>';
    }).join('') + '</div>';
  }

  document.addEventListener('click', async function (e) {
    var t = e.target;
    if (t.hasAttribute('data-status') && t.hasAttribute('data-id')) {
      try {
        var r = await A.DB.updateInquiry(t.getAttribute('data-id'), { status: t.getAttribute('data-status') });
        if (r.error) throw r.error;
        A.ok('Status updated');
        closeModal();
        loadList();
      } catch (err) { A.err(err.message); }
    }
  });

  async function convertInquiry(id) {
    if (!confirm('Convert this inquiry to a customer record? This will create a new customer and link the inquiry.')) return;
    try {
      var r = await A.DB.inquiryToCustomer(id);
      if (r.error) throw r.error;
      A.ok('Converted to customer');
      loadList();
    } catch (err) { A.err(err.message || 'Conversion failed'); }
  }

  async function delInquiry(id) {
    if (!confirm('Delete this inquiry permanently?')) return;
    try {
      var r = await A.DB.deleteInquiry(id);
      if (r.error) throw r.error;
      A.ok('Inquiry deleted');
      loadList();
    } catch (err) { A.err(err.message); }
  }

  function closeModal() { document.getElementById('modalBack').classList.remove('show'); }

  async function doExport() {
    try {
      var r = await A.DB.listInquiries(state);
      var rows = (r.data || []).map(function (q) {
        return {
          contact: q.contact_name, company: q.company_name, email: q.email, phone: q.phone,
          whatsapp: q.whatsapp, country: q.country, product: q.product_interest, quantity: q.quantity,
          market: q.target_market, message: q.message, status: q.status, received: A.fmtDate(q.created_at)
        };
      });
      A.exportCSV('woneng-inquiries-' + A.fmtDate(new Date()) + '.csv', rows);
    } catch (err) { A.err('Export failed'); }
  }
});
