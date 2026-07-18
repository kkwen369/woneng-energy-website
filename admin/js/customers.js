/* Customers — list, search, filter, add, edit, delete, export */
AdminApp.mount('customers.html', 'Customers', async function (content) {
  var A = AdminApp;
  var state = { search: '', status: 'all', type: 'all' };

  content.innerHTML = renderShell();

  // Bind events
  document.getElementById('searchInput').addEventListener('input', A.debounce(function () {
    state.search = this.value.trim();
    loadList();
  }, 300));
  document.getElementById('statusFilter').addEventListener('change', function () {
    state.status = this.value; loadList();
  });
  document.getElementById('typeFilter').addEventListener('change', function () {
    state.type = this.value; loadList();
  });
  document.getElementById('btnAdd').addEventListener('click', function () { openModal(); });
  document.getElementById('btnExport').addEventListener('click', function () { doExport(); });
  document.getElementById('modalClose').addEventListener('click', closeModal);
  document.getElementById('modalBack').addEventListener('click', function (e) { if (e.target === this) closeModal(); });
  document.getElementById('custForm').addEventListener('submit', saveCustomer);

  loadList();

  function renderShell() {
    return '' +
      '<div class="toolbar">' +
        '<div class="left"><button class="btn" id="btnAdd">+ Add Customer</button>' +
        '<button class="btn btn-outline" id="btnExport">⬇ Export CSV</button></div>' +
        '<div class="right"><a href="dashboard.html" class="btn btn-gray">← Dashboard</a></div>' +
      '</div>' +
      '<div class="filters">' +
        '<div class="search"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="11" cy="11" r="8"/><path d="m21 21-4.3-4.3"/></svg>' +
        '<input type="text" id="searchInput" placeholder="Search name, company, email…"></div>' +
        '<select id="statusFilter"><option value="all">All Status</option>' +
          '<option value="new">New</option><option value="contacted">Contacted</option>' +
          '<option value="quoted">Quoted</option><option value="negotiating">Negotiating</option>' +
          '<option value="won">Won</option><option value="lost">Lost</option></select>' +
        '<select id="typeFilter"><option value="all">All Types</option>' +
          '<option value="lead">Lead</option><option value="distributor">Distributor</option>' +
          '<option value="wholesaler">Wholesaler</option><option value="retailer">Retailer</option>' +
          '<option value="project">Project</option><option value="other">Other</option></select>' +
      '</div>' +
      '<div id="listArea"><div class="loading"><div class="spinner"></div>Loading customers…</div></div>' +
      // Modal
      '<div class="modal-back" id="modalBack">' +
        '<div class="modal">' +
          '<div class="modal-head"><h3 id="modalTitle">Add Customer</h3><button class="modal-close" id="modalClose">×</button></div>' +
          '<div class="modal-body"><form id="custForm"><input type="hidden" id="custId">' +
            '<div class="form-grid">' +
              '<div class="field"><label>Company Name</label><input type="text" id="f_company" placeholder="Acme Solar Ltd"></div>' +
              '<div class="field"><label>Contact Name <span class="req">*</span></label><input type="text" id="f_name" required></div>' +
              '<div class="field"><label>Email</label><input type="email" id="f_email" placeholder="contact@acme.com"></div>' +
              '<div class="field"><label>Phone / WhatsApp</label><input type="text" id="f_phone" placeholder="+234 800 000 0000"></div>' +
              '<div class="field"><label>Country</label><input type="text" id="f_country" placeholder="Nigeria"></div>' +
              '<div class="field"><label>Customer Type</label><select id="f_type">' +
                '<option value="lead">Lead</option><option value="distributor">Distributor</option>' +
                '<option value="wholesaler">Wholesaler</option><option value="retailer">Retailer</option>' +
                '<option value="project">Project</option><option value="other">Other</option></select></div>' +
              '<div class="field"><label>Status</label><select id="f_status">' +
                '<option value="new">New</option><option value="contacted">Contacted</option>' +
                '<option value="quoted">Quoted</option><option value="negotiating">Negotiating</option>' +
                '<option value="won">Won</option><option value="lost">Lost</option></select></div>' +
              '<div class="field"><label>Source</label><select id="f_source">' +
                '<option value="website">Website</option><option value="email">Email</option>' +
                '<option value="whatsapp">WhatsApp</option><option value="exhibition">Exhibition</option>' +
                '<option value="referral">Referral</option></select></div>' +
              '<div class="field"><label>Tags (comma separated)</label><input type="text" id="f_tags" placeholder="VIP, Africa, Bulk"></div>' +
              '<div class="field full"><label>Notes</label><textarea id="f_notes" placeholder="Customer requirements, preferences…"></textarea></div>' +
            '</div>' +
          '</form></div>' +
          '<div class="modal-foot"><button class="btn btn-gray" id="btnCancel">Cancel</button> ' +
            '<button class="btn" id="btnSave">Save</button></div>' +
        '</div>' +
      '</div>';
  }

  async function loadList() {
    var area = document.getElementById('listArea');
    area.innerHTML = '<div class="loading"><div class="spinner"></div>Loading…</div>';
    try {
      var r = await A.DB.listCustomers(state);
      var rows = r.data || [];
      if (!rows.length) {
        area.innerHTML = '<div class="card"><div class="empty"><svg viewBox="0 0 24 24" fill="currentColor"><path d="M16 11c1.66 0 2.99-1.34 2.99-3S17.66 5 16 5c-1.66 0-3 1.34-3 3s1.34 3 3 3zm-8 0c1.66 0 2.99-1.34 2.99-3S9.66 5 8 5C6.34 5 5 6.34 5 8s1.34 3 3 3zm0 2c-2.33 0-7 1.17-7 3.5V19h14v-2.5c0-2.33-4.67-3.5-7-3.5zm8 0c-.29 0-.62.02-.97.05 1.16.84 1.97 1.97 1.97 3.45V19h6v-2.5c0-2.33-4.67-3.5-7-3.5z"/></svg><p>No customers found. Click "Add Customer" to create one.</p></div></div>';
        return;
      }
      var html = '<div class="card"><div class="table-wrap"><table class="data"><thead><tr>' +
        '<th>Company / Contact</th><th>Email</th><th>Country</th><th>Type</th><th>Status</th><th>Created</th><th></th></tr></thead><tbody>';
      html += rows.map(function (c) {
        return '<tr>' +
          '<td><strong>' + A.escapeHtml(c.contact_name || '—') + '</strong><br><span class="muted">' + A.escapeHtml(c.company_name || '') + '</span></td>' +
          '<td>' + A.escapeHtml(c.email || '—') + '</td>' +
          '<td>' + A.escapeHtml(c.country || '—') + '</td>' +
          '<td><span class="badge badge-gray">' + A.escapeHtml(c.customer_type) + '</span></td>' +
          '<td>' + A.badge(c.status) + '</td>' +
          '<td class="muted">' + A.fmtDate(c.created_at) + '</td>' +
          '<td class="actions">' +
            '<a href="customer-detail.html?id=' + c.id + '" class="icon-btn" title="View">👁</a>' +
            '<button class="icon-btn" data-edit="' + c.id + '" title="Edit">✏️</button>' +
            '<button class="icon-btn danger" data-del="' + c.id + '" title="Delete">🗑</button>' +
          '</td></tr>';
      }).join('');
      html += '</tbody></table></div></div>';
      area.innerHTML = html;

      // Bind row actions
      area.querySelectorAll('[data-edit]').forEach(function (b) {
        b.addEventListener('click', function () { openModal(this.getAttribute('data-edit')); });
      });
      area.querySelectorAll('[data-del]').forEach(function (b) {
        b.addEventListener('click', function () { delCustomer(this.getAttribute('data-del')); });
      });
    } catch (e) {
      area.innerHTML = '<div class="empty"><p>Error: ' + A.escapeHtml(e.message) + '</p></div>';
    }
  }

  function openModal(id) {
    var form = document.getElementById('custForm');
    form.reset();
    document.getElementById('custId').value = '';
    document.getElementById('modalTitle').textContent = id ? 'Edit Customer' : 'Add Customer';
    if (id) {
      // find from loaded data — but we need to fetch fresh
      A.DB.getCustomer(id).then(function (r) {
        if (r.data) {
          var c = r.data;
          document.getElementById('custId').value = c.id;
          document.getElementById('f_company').value = c.company_name || '';
          document.getElementById('f_name').value = c.contact_name || '';
          document.getElementById('f_email').value = c.email || '';
          document.getElementById('f_phone').value = c.phone || c.whatsapp || '';
          document.getElementById('f_country').value = c.country || '';
          document.getElementById('f_type').value = c.customer_type || 'lead';
          document.getElementById('f_status').value = c.status || 'new';
          document.getElementById('f_source').value = c.source || 'website';
          document.getElementById('f_tags').value = (c.tags || []).join(', ');
          document.getElementById('f_notes').value = c.notes || '';
        }
      });
    }
    document.getElementById('modalBack').classList.add('show');
  }

  function closeModal() { document.getElementById('modalBack').classList.remove('show'); }

  async function saveCustomer(e) {
    e.preventDefault();
    var id = document.getElementById('custId').value;
    var tagsRaw = document.getElementById('f_tags').value;
    var tags = tagsRaw ? tagsRaw.split(',').map(function (t) { return t.trim(); }).filter(Boolean) : [];
    var data = {
      company_name: document.getElementById('f_company').value.trim(),
      contact_name: document.getElementById('f_name').value.trim(),
      email: document.getElementById('f_email').value.trim(),
      phone: document.getElementById('f_phone').value.trim(),
      country: document.getElementById('f_country').value.trim(),
      customer_type: document.getElementById('f_type').value,
      status: document.getElementById('f_status').value,
      source: document.getElementById('f_source').value,
      tags: tags,
      notes: document.getElementById('f_notes').value.trim(),
    };
    var btn = document.getElementById('btnSave');
    btn.disabled = true; btn.textContent = 'Saving…';
    try {
      var r = id ? await A.DB.updateCustomer(id, data) : await A.DB.createCustomer(data);
      if (r.error) throw r.error;
      A.ok(id ? 'Customer updated' : 'Customer added');
      closeModal();
      loadList();
    } catch (err) {
      A.err(err.message || 'Save failed');
    }
    btn.disabled = false; btn.textContent = 'Save';
  }

  async function delCustomer(id) {
    if (!confirm('Delete this customer? This cannot be undone.')) return;
    try {
      var r = await A.DB.deleteCustomer(id);
      if (r.error) throw r.error;
      A.ok('Customer deleted');
      loadList();
    } catch (err) { A.err(err.message || 'Delete failed'); }
  }

  async function doExport() {
    try {
      var r = await A.DB.listCustomers({ search: state.search, status: state.status, type: state.type });
      var rows = (r.data || []).map(function (c) {
        return {
          company: c.company_name, contact: c.contact_name, email: c.email, phone: c.phone,
          country: c.country, type: c.customer_type, status: c.status, source: c.source,
          tags: (c.tags || []).join(';'), notes: c.notes, created: A.fmtDate(c.created_at)
        };
      });
      A.exportCSV('woneng-customers-' + A.fmtDate(new Date()) + '.csv', rows);
    } catch (err) { A.err('Export failed'); }
  }
});
