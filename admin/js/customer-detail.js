/* Customer Detail — profile, inquiries, follow-up log */
AdminApp.mount('customer-detail.html', 'Customer Detail', async function (content) {
  var A = AdminApp;
  var params = new URLSearchParams(window.location.search);
  var customerId = params.get('id');
  if (!customerId) { content.innerHTML = '<div class="empty"><p>No customer selected. <a href="customers.html">← Back to list</a></p></div>'; return; }

  content.innerHTML = '<div class="loading"><div class="spinner"></div>Loading customer…</div>';

  try {
    var r = await A.DB.getCustomer(customerId);
    if (r.error || !r.data) { content.innerHTML = '<div class="empty"><p>Customer not found. <a href="customers.html">← Back</a></p></div>'; return; }
    var c = r.data;
    document.title = (c.contact_name || 'Customer') + ' — Woneng Admin';

    var initial = (c.contact_name || c.company_name || '?').charAt(0).toUpperCase();
    content.innerHTML =
      '<div class="detail-head">' +
        '<div class="avatar">' + A.escapeHtml(initial) + '</div>' +
        '<div><h2>' + A.escapeHtml(c.contact_name || 'Unknown') + '</h2>' +
        '<div class="meta">' + A.escapeHtml(c.company_name || '') + ' · ' + A.badge(c.status) + ' · ' + A.fmtDate(c.created_at) + '</div></div>' +
        '<div style="margin-left:auto;display:flex;gap:10px">' +
          '<button class="btn btn-outline" id="btnEdit">✏️ Edit</button>' +
          '<a href="customers.html" class="btn btn-gray">← Back</a></div>' +
      '</div>' +
      '<div class="detail-grid">' +
        '<div class="card card-pad"><h3 style="margin-bottom:14px">Contact Info</h3>' +
          detailRow('Email', c.email) + detailRow('Phone', c.phone) + detailRow('WhatsApp', c.whatsapp) +
          detailRow('Country', c.country) + detailRow('Type', '<span class="badge badge-gray">' + A.escapeHtml(c.customer_type) + '</span>') +
          detailRow('Source', c.source) + detailRow('Tags', (c.tags || []).join(', ') || '—') +
        '</div>' +
        '<div class="card card-pad"><h3 style="margin-bottom:14px">Notes</h3>' +
          '<div style="white-space:pre-wrap;color:var(--muted);font-size:14px;min-height:60px">' + A.escapeHtml(c.notes || 'No notes yet.') + '</div>' +
        '</div>' +
      '</div>' +
      '<div style="display:grid;grid-template-columns:1fr 1fr;gap:20px">' +
        '<div class="card"><div class="card-head"><h3>Follow-up History</h3><button class="btn btn-sm" id="btnAddFollow">+ Add</button></div>' +
          '<div id="followArea" class="card-pad" style="padding-top:8px"><div class="loading"><div class="spinner"></div></div></div></div>' +
        '<div class="card"><div class="card-head"><h3>Linked Inquiries</h3></div>' +
          '<div id="inqArea" class="card-pad" style="padding-top:8px"><div class="loading"><div class="spinner"></div></div></div></div>' +
      '</div>' +
      // Edit Modal
      '<div class="modal-back" id="editModal">' +
        '<div class="modal"><div class="modal-head"><h3>Edit Customer</h3><button class="modal-close" id="editClose">×</button></div>' +
        '<div class="modal-body"><form id="editForm">' +
          '<div class="form-grid">' +
            '<div class="field"><label>Company Name</label><input type="text" id="e_company"></div>' +
            '<div class="field"><label>Contact Name</label><input type="text" id="e_name"></div>' +
            '<div class="field"><label>Email</label><input type="email" id="e_email"></div>' +
            '<div class="field"><label>Phone</label><input type="text" id="e_phone"></div>' +
            '<div class="field"><label>WhatsApp</label><input type="text" id="e_whatsapp"></div>' +
            '<div class="field"><label>Country</label><input type="text" id="e_country"></div>' +
            '<div class="field"><label>Type</label><select id="e_type"><option value="lead">Lead</option><option value="distributor">Distributor</option><option value="wholesaler">Wholesaler</option><option value="retailer">Retailer</option><option value="project">Project</option><option value="other">Other</option></select></div>' +
            '<div class="field"><label>Status</label><select id="e_status"><option value="new">New</option><option value="contacted">Contacted</option><option value="quoted">Quoted</option><option value="negotiating">Negotiating</option><option value="won">Won</option><option value="lost">Lost</option></select></div>' +
            '<div class="field"><label>Tags</label><input type="text" id="e_tags"></div>' +
            '<div class="field"><label>Source</label><select id="e_source"><option value="website">Website</option><option value="email">Email</option><option value="whatsapp">WhatsApp</option><option value="exhibition">Exhibition</option><option value="referral">Referral</option></select></div>' +
            '<div class="field full"><label>Notes</label><textarea id="e_notes"></textarea></div>' +
          '</div>' +
        '</form></div>' +
        '<div class="modal-foot"><button class="btn btn-gray" id="editCancel">Cancel</button> <button class="btn" id="editSave">Save Changes</button></div></div>' +
      '</div>' +
      // Follow-up Modal
      '<div class="modal-back" id="followModal">' +
        '<div class="modal"><div class="modal-head"><h3>Add Follow-up</h3><button class="modal-close" id="followClose">×</button></div>' +
        '<div class="modal-body"><form id="followForm">' +
          '<div class="form-grid">' +
            '<div class="field"><label>Contact Date</label><input type="date" id="fu_date" required></div>' +
            '<div class="field"><label>Method</label><select id="fu_method"><option value="email">Email</option><option value="whatsapp">WhatsApp</option><option value="phone">Phone</option><option value="wechat">WeChat</option><option value="other">Other</option></select></div>' +
            '<div class="field full"><label>Communication Content <span class="req">*</span></label><textarea id="fu_content" required placeholder="What was discussed?"></textarea></div>' +
            '<div class="field"><label>Next Action</label><input type="text" id="fu_next"></div>' +
            '<div class="field"><label>Next Follow-up Date</label><input type="date" id="fu_nextdate"></div>' +
          '</div>' +
        '</form></div>' +
        '<div class="modal-foot"><button class="btn btn-gray" id="followCancel">Cancel</button> <button class="btn" id="followSave">Save</button></div></div>' +
      '</div>';

    // Fill edit form
    document.getElementById('e_company').value = c.company_name || '';
    document.getElementById('e_name').value = c.contact_name || '';
    document.getElementById('e_email').value = c.email || '';
    document.getElementById('e_phone').value = c.phone || '';
    document.getElementById('e_whatsapp').value = c.whatsapp || '';
    document.getElementById('e_country').value = c.country || '';
    document.getElementById('e_type').value = c.customer_type || 'lead';
    document.getElementById('e_status').value = c.status || 'new';
    document.getElementById('e_tags').value = (c.tags || []).join(', ');
    document.getElementById('e_source').value = c.source || 'website';
    document.getElementById('e_notes').value = c.notes || '';

    // Bind events
    document.getElementById('btnEdit').addEventListener('click', function () { document.getElementById('editModal').classList.add('show'); });
    document.getElementById('editClose').addEventListener('click', function () { document.getElementById('editModal').classList.remove('show'); });
    document.getElementById('editCancel').addEventListener('click', function () { document.getElementById('editModal').classList.remove('show'); });
    document.getElementById('editSave').addEventListener('click', saveEdit);
    document.getElementById('btnAddFollow').addEventListener('click', function () {
      document.getElementById('fu_date').value = A.fmtDate(new Date());
      document.getElementById('followModal').classList.add('show');
    });
    document.getElementById('followClose').addEventListener('click', function () { document.getElementById('followModal').classList.remove('show'); });
    document.getElementById('followCancel').addEventListener('click', function () { document.getElementById('followModal').classList.remove('show'); });
    document.getElementById('followSave').addEventListener('click', saveFollow);

    loadFollowUps();
    loadInquiries();

    async function saveEdit() {
      var tagsRaw = document.getElementById('e_tags').value;
      var tags = tagsRaw ? tagsRaw.split(',').map(function (t) { return t.trim(); }).filter(Boolean) : [];
      var data = {
        company_name: document.getElementById('e_company').value.trim(),
        contact_name: document.getElementById('e_name').value.trim(),
        email: document.getElementById('e_email').value.trim(),
        phone: document.getElementById('e_phone').value.trim(),
        whatsapp: document.getElementById('e_whatsapp').value.trim(),
        country: document.getElementById('e_country').value.trim(),
        customer_type: document.getElementById('e_type').value,
        status: document.getElementById('e_status').value,
        tags: tags,
        source: document.getElementById('e_source').value,
        notes: document.getElementById('e_notes').value.trim(),
      };
      var btn = document.getElementById('editSave');
      btn.disabled = true; btn.textContent = 'Saving…';
      try {
        var r = await A.DB.updateCustomer(customerId, data);
        if (r.error) throw r.error;
        A.ok('Saved');
        location.reload();
      } catch (err) { A.err(err.message); }
      btn.disabled = false; btn.textContent = 'Save Changes';
    }

    async function saveFollow() {
      var form = document.getElementById('followForm');
      if (!form.checkValidity()) { form.reportValidity(); return; }
      var data = {
        customer_id: customerId,
        contact_date: document.getElementById('fu_date').value,
        contact_method: document.getElementById('fu_method').value,
        content: document.getElementById('fu_content').value.trim(),
        next_action: document.getElementById('fu_next').value.trim(),
        next_date: document.getElementById('fu_nextdate').value || null,
      };
      var btn = document.getElementById('followSave');
      btn.disabled = true; btn.textContent = 'Saving…';
      try {
        var r = await A.DB.addFollowUp(data);
        if (r.error) throw r.error;
        A.ok('Follow-up added');
        document.getElementById('followModal').classList.remove('show');
        form.reset();
        loadFollowUps();
      } catch (err) { A.err(err.message); }
      btn.disabled = false; btn.textContent = 'Save';
    }

    async function loadFollowUps() {
      var area = document.getElementById('followArea');
      try {
        var r = await A.DB.listFollowUps(customerId);
        var rows = r.data || [];
        if (!rows.length) { area.innerHTML = '<div class="empty" style="padding:24px"><p>No follow-ups yet.</p></div>'; return; }
        area.innerHTML = rows.map(function (f) {
          return '<div style="padding:14px 0;border-bottom:1px solid var(--line)">' +
            '<div style="display:flex;justify-content:space-between;align-items:center">' +
              '<strong>' + A.escapeHtml(f.contact_method) + '</strong> ' +
              '<span class="badge badge-blue">' + A.fmtDate(f.contact_date) + '</span>' +
              '<button class="icon-btn danger" data-fdel="' + f.id + '">🗑</button>' +
            '</div>' +
            '<p style="margin:8px 0;color:var(--muted)">' + A.escapeHtml(f.content).replace(/\n/g, '<br>') + '</p>' +
            (f.next_action ? '<div class="small muted">Next: ' + A.escapeHtml(f.next_action) + (f.next_date ? ' (' + A.fmtDate(f.next_date) + ')' : '') + '</div>' : '') +
          '</div>';
        }).join('');
        area.querySelectorAll('[data-fdel]').forEach(function (b) {
          b.addEventListener('click', async function () {
            if (!confirm('Delete this follow-up?')) return;
            var r = await A.DB.deleteFollowUp(this.getAttribute('data-fdel'));
            if (r.error) { A.err(r.error.message); return; }
            A.ok('Deleted'); loadFollowUps();
          });
        });
      } catch (e) { area.innerHTML = '<p class="err">' + A.escapeHtml(e.message) + '</p>'; }
    }

    async function loadInquiries() {
      var area = document.getElementById('inqArea');
      try {
        var r = await A.client().from('inquiries').select('*').eq('customer_id', customerId).order('created_at', { ascending: false });
        var rows = r.data || [];
        if (!rows.length) { area.innerHTML = '<div class="empty" style="padding:24px"><p>No linked inquiries.</p></div>'; return; }
        area.innerHTML = rows.map(function (q) {
          return '<div style="padding:14px 0;border-bottom:1px solid var(--line)">' +
            '<div style="display:flex;justify-content:space-between"><strong>' + A.escapeHtml(q.product_interest || 'Inquiry') + '</strong>' + A.badge(q.status) + '</div>' +
            '<p class="small muted" style="margin:6px 0">' + A.escapeHtml((q.message || '').substring(0, 120)) + (q.message && q.message.length > 120 ? '…' : '') + '</p>' +
            '<div class="small muted">' + A.timeAgo(q.created_at) + '</div>' +
          '</div>';
        }).join('');
      } catch (e) { area.innerHTML = '<p class="err">' + A.escapeHtml(e.message) + '</p>'; }
    }
  } catch (e) {
    content.innerHTML = '<div class="empty"><p>Error: ' + A.escapeHtml(e.message) + '</p></div>';
  }

  function detailRow(k, v) {
    return '<div class="detail-row"><span class="k">' + k + '</span><span class="v">' + (v != null ? (typeof v === 'string' ? A.escapeHtml(v) : v) : '—') + '</span></div>';
  }
});
