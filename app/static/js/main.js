// app/static/js/main.js
(() => {
  const DATA_URL = '/static/data/students.json'; // relative to app static root
  let students = [];           // in-memory dataset
  let currentEditId = null;    // null => new, else edit
  const pageSize = 8;
  let currentPage = 1;
  let filtered = [];

  // DOM refs
  const tbody = document.querySelector('#students-table-body');
  const form = document.getElementById('studentForm');
  const modalEl = document.getElementById('studentModal');
  const searchInput = document.getElementById('student-search');
  const paginationEl = document.querySelector('.pagination');

  // Bootstrap modal helper
  let bsModal = null;
  if (modalEl) bsModal = new bootstrap.Modal(modalEl);

  async function loadData() {
    try {
      // prefer server-provided initial data injected into the page
      if (window.INIT_STUDENTS) {
        students = window.INIT_STUDENTS.slice();
      } else {
        const res = await fetch(DATA_URL);
        students = await res.json();
      }
      filtered = students.slice();
      renderTable();
      renderPagination();
    } catch (err) {
      console.error('Failed to fetch students.json', err);
      // fallback: empty array
      students = [];
      filtered = [];
      renderTable();
      renderPagination();
    }
  }

  function renderTable() {
    if (!tbody) return;
    tbody.innerHTML = '';

    const start = (currentPage - 1) * pageSize;
    const pageItems = filtered.slice(start, start + pageSize);

    if (pageItems.length === 0) {
      tbody.innerHTML = `<tr><td colspan="6" class="text-center small text-muted">No students found</td></tr>`;
      return;
    }

    for (const s of pageItems) {
      const tr = document.createElement('tr');

      // show id_number, first_name, last_name, program, year, gender
      tr.innerHTML = `
        <td><a href="#" class="student-roll-link" data-id="${s.id}">${escapeHtml(s.id_number || '')}</a></td>
        <td>${escapeHtml(s.first_name || '')}</td>
        <td>${escapeHtml(s.last_name || '')}</td>
        <td>${escapeHtml(s.program || '')}</td>
        <td>${escapeHtml(String(s.year || ''))}</td>
        <td>${escapeHtml(s.gender || '')}</td>
        <td>
          <button class="btn btn-sm btn-outline-primary btn-edit" data-id="${s.id}">Edit</button>
          <button class="btn btn-sm btn-outline-danger btn-delete" data-id="${s.id}">Delete</button>
        </td>
      `;
      tbody.appendChild(tr);
    }

    // wire buttons
    tbody.querySelectorAll('.btn-edit').forEach(btn => btn.addEventListener('click', onEdit));
    tbody.querySelectorAll('.btn-delete').forEach(btn => btn.addEventListener('click', onDelete));
  }

  function renderPagination() {
    if (!paginationEl) return;
    paginationEl.innerHTML = '';

    const pages = Math.max(1, Math.ceil(filtered.length / pageSize));
    const createPageItem = (label, pg, disabled=false, active=false) => {
      const li = document.createElement('li');
      li.className = 'page-item' + (disabled ? ' disabled' : '') + (active ? ' active' : '');
      const a = document.createElement('a');
      a.className = 'page-link';
      a.href = '#';
      a.dataset.page = pg;
      a.textContent = label;
      a.addEventListener('click', (e) => {
        e.preventDefault();
        if (!disabled) {
          currentPage = pg;
          renderTable();
          renderPagination();
          window.scrollTo({top: 0, behavior: 'smooth'});
        }
      });
      li.appendChild(a);
      return li;
    };

    // prev
    const prev = createPageItem('<', Math.max(1, currentPage - 1), currentPage === 1);
    paginationEl.appendChild(prev);

    for (let i = 1; i <= pages; i++) {
      const li = createPageItem(String(i), i, false, i === currentPage);
      paginationEl.appendChild(li);
    }

    // next
    const next = createPageItem('>', Math.min(pages, currentPage + 1), currentPage === pages);
    paginationEl.appendChild(next);
  }

  // Edit handler
  function onEdit(e) {
    const id = Number(e.currentTarget.dataset.id);
    const student = students.find(s => s.id === id);
    if (!student) return;
    currentEditId = id;
    // fill form
    form.reset();
    setFormValue('id', student.id || '');
    setFormValue('id_number', student.id_number || '');
    setFormValue('first_name', student.first_name || '');
    setFormValue('last_name', student.last_name || '');
    setFormValue('program_id', student.program_id || '');
    setFormValue('year', student.year || '');
    setFormValue('gender', student.gender || '');
    if (bsModal) bsModal.show();
  }

  // Delete handler
  function onDelete(e) {
    const id = Number(e.currentTarget.dataset.id);
    const student = students.find(s => s.id === id);
    if (!student) return;
    if (!confirm(`Delete ${student.first_name} ${student.last_name} (${student.id_number})?`)) return;
    // call server delete endpoint (uses CSRF token from the page)
    const csrfToken = document.querySelector('input[name="csrf_token"]')?.value;
    fetch(`/user/students/delete/${id}`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'X-CSRFToken': csrfToken || ''
      }
    }).then(r => r.json()).then(data => {
      if (data && data.success) {
        // remove locally and refresh UI
        students = students.filter(s => s.id !== id);
        filtered = filtered.filter(s => s.id !== id);
        const maxPage = Math.max(1, Math.ceil(filtered.length / pageSize));
        if (currentPage > maxPage) currentPage = maxPage;
        renderTable();
        renderPagination();
        showAlert('success', data.message || 'Student deleted');
      } else {
        showAlert('danger', (data && data.message) || 'Failed to delete student');
      }
    }).catch(err => {
      console.error(err);
      showAlert('danger', 'Failed to delete student');
    });
  }

  // Form helpers
  function setFormValue(name, value) {
    const el = form.elements[name];
    if (!el) return;
    el.value = value;
  }
 
  // We no longer intercept form submit; forms post to the server for create/edit.

  // Search
  function applySearch() {
    const q = searchInput ? (searchInput.value || '').toLowerCase().trim() : '';
    if (!q) {
      filtered = students.slice();
    } else {
      filtered = students.filter(s =>
        (s.first_name && s.first_name.toLowerCase().includes(q)) ||
        (s.last_name && s.last_name.toLowerCase().includes(q)) ||
        (s.id_number && s.id_number.toLowerCase().includes(q)) ||
        (s.program && s.program.toLowerCase().includes(q))
      );
    }
    currentPage = 1;
    renderTable();
    renderPagination();
  }

  if (searchInput) {
    searchInput.addEventListener('input', () => {
      applySearch();
    });
  }

  // escape html (basic)
  function escapeHtml(str) {
    if (!str) return '';
    return String(str)
      .replaceAll('&', '&amp;')
      .replaceAll('<', '&lt;')
      .replaceAll('>', '&gt;')
      .replaceAll('"', '&quot;')
      .replaceAll("'", '&#39;');
  }

  function showAlert(type, message) {
    try {
      const container = document.querySelector('.container') || document.body;
      const existing = document.querySelector('.dynamic-alert');
      if (existing) existing.remove();
      const div = document.createElement('div');
      div.className = `alert alert-${type} alert-dismissible dynamic-alert`;
      div.role = 'alert';
      div.innerHTML = `${escapeHtml(message)}<button type="button" class="btn-close" data-bs-dismiss="alert" aria-label="Close"></button>`;
      container.insertBefore(div, container.firstChild);
      // auto-dismiss after 4s
      setTimeout(() => div.remove(), 4000);
    } catch (e) {
      console.warn('showAlert failed', e);
    }
  }

  // init on DOMContentLoaded
  document.addEventListener('DOMContentLoaded', () => {
    loadData();
  });

})();
