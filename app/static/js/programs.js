document.addEventListener('DOMContentLoaded', function() {
  const form = document.getElementById('programForm');
  const tbody = document.getElementById('programs-table-body');
  const searchInput = document.getElementById('program-search');
  let programs = window.INIT_PROGRAMS || [];
  let editIndex = null;

  function renderTable(list = programs) {
    tbody.innerHTML = '';
    if (list.length === 0) {
      tbody.innerHTML = `<tr><td colspan="4" class="text-center text-muted">No programs found.</td></tr>`;
      return;
    }
    list.forEach((p, i) => {
      const tr = document.createElement('tr');
      tr.innerHTML = `
        <td>${p.code}</td>
        <td>${p.name}</td>
        <td>${p.college}</td>
        <td>
          <button class="btn btn-sm btn-outline-primary me-1" data-index="${i}" data-action="edit">Edit</button>
          <button class="btn btn-sm btn-outline-danger" data-index="${i}" data-action="delete">Delete</button>
        </td>`;
      tbody.appendChild(tr);
    });
  }

  function resetForm() {
    form.reset();
    editIndex = null;
    if (form.elements['id']) form.elements['id'].value = '';
  }

  // Let the form submit normally to server (server handles create/edit).

  tbody.addEventListener('click', function(e) {
    const btn = e.target.closest('button');
    if (!btn) return;
    const index = btn.dataset.index;
    const action = btn.dataset.action;
    if (action === 'delete') {
      const prog = programs[index];
      if (!prog) return;
      if (!confirm(`Delete program ${prog.name}?`)) return;
      const csrfToken = document.querySelector('input[name="csrf_token"]')?.value;
      fetch(`/user/programs/delete/${prog.id}`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'X-CSRFToken': csrfToken || ''
        }
      }).then(r => r.json()).then(data => {
        if (data && data.success) {
          programs.splice(index, 1);
          renderTable();
          showAlert('success', data.message || 'Program deleted');
        } else {
          showAlert('danger', (data && data.message) || 'Failed to delete program');
        }
      }).catch(err => {
        console.error(err);
        showAlert('danger', 'Failed to delete program');
      });
    } else if (action === 'edit') {
      const program = programs[index];
      if (form) {
        if (form.elements['id']) form.elements['id'].value = program.id || '';
        if (form.elements['code']) form.elements['code'].value = program.code || '';
        if (form.elements['name']) form.elements['name'].value = program.name || '';
        if (form.elements['college_id']) form.elements['college_id'].value = program.college_id || '';
      }
      new bootstrap.Modal(document.querySelector('#programModal')).show();
    }
  });

  searchInput.addEventListener('input', function() {
    const q = this.value.toLowerCase();
    const filtered = programs.filter(p =>
      p.name.toLowerCase().includes(q) ||
      p.code.toLowerCase().includes(q) ||
      p.college.toLowerCase().includes(q)
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

