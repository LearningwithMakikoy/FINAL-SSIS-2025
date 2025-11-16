document.addEventListener('DOMContentLoaded', function() {
  const form = document.getElementById('collegeForm');
  const tbody = document.getElementById('colleges-table-body');
  const searchInput = document.getElementById('college-search');
  let colleges = window.INIT_COLLEGES || [];
  let editIndex = null;

  function renderTable(list = colleges) {
    tbody.innerHTML = '';
    if (list.length === 0) {
      tbody.innerHTML = `<tr><td colspan="3" class="text-center text-muted">No colleges found.</td></tr>`;
      return;
    }
    list.forEach((c, i) => {
      const tr = document.createElement('tr');
      tr.innerHTML = `
        <td>${c.code}</td>
        <td>${c.name}</td>
        <td>
          <button class="btn btn-sm btn-outline-primary me-1" data-index="${i}" data-action="edit">Edit</button>
          <button class="btn btn-sm btn-outline-danger" data-index="${i}" data-action="delete">Delete</button>
        </td>`;
      tbody.appendChild(tr);
    });
  }

  // Let the form submit normally to the server (server handles create/edit)

  tbody.addEventListener('click', function(e) {
    const btn = e.target.closest('button');
    if (!btn) return;
    const index = btn.dataset.index;
    const action = btn.dataset.action;

    if (action === 'delete') {
      const college = colleges[index];
      if (!college) return;
      if (!confirm(`Delete college ${college.name}?`)) return;
      const csrfToken = document.querySelector('input[name="csrf_token"]')?.value;
      fetch(`/user/colleges/delete/${college.id}`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'X-CSRFToken': csrfToken || ''
        }
      }).then(r => r.json()).then(data => {
        if (data && data.success) {
          colleges.splice(index, 1);
          renderTable();
          showAlert('success', data.message || 'College deleted');
        } else {
          showAlert('danger', (data && data.message) || 'Failed to delete college');
        }
      }).catch(err => {
        console.error(err);
        showAlert('danger', 'Failed to delete college');
      });
    } else if (action === 'edit') {
      const college = colleges[index];
      if (form) {
        if (form.elements['id']) form.elements['id'].value = college.id || '';
        if (form.elements['code']) form.elements['code'].value = college.code || '';
        if (form.elements['name']) form.elements['name'].value = college.name || '';
      }
      editIndex = index;
      new bootstrap.Modal(document.querySelector('#collegeModal')).show();
    }
  });

  searchInput.addEventListener('input', function() {
    const q = this.value.toLowerCase();
    const filtered = colleges.filter(c =>
      c.name.toLowerCase().includes(q) ||
      c.code.toLowerCase().includes(q)
    );
    renderTable(filtered);
  });

  function showAlert(type, message) {
    try {
      const container = document.querySelector('.container') || document.body;
      const existing = document.querySelector('.dynamic-alert');
      if (existing) existing.remove();
      const div = document.createElement('div');
      div.className = `alert alert-${type} alert-dismissible dynamic-alert`;
      div.role = 'alert';
      div.innerHTML = `${message}<button type="button" class="btn-close" data-bs-dismiss="alert" aria-label="Close"></button>`;
      container.insertBefore(div, container.firstChild);
      setTimeout(() => div.remove(), 4000);
    } catch (e) {
      console.warn('showAlert failed', e);
    }
  }

  renderTable();
});
