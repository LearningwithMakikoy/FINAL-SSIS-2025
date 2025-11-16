document.addEventListener('DOMContentLoaded', function() {
  const form = document.getElementById('programForm');
  const tbody = document.getElementById('programs-table-body');
  const searchInput = document.getElementById('program-search');
  const paginationEl = document.querySelector('.pagination');
  let programs = window.INIT_PROGRAMS || [];
  let filteredPrograms = programs.slice();
  let editIndex = null;
  
  // Sorting state
  let sortColumn = null;
  let sortDirection = 'asc'; // 'asc' or 'desc'
  
  // Pagination state
  const pageSize = 10;
  let currentPage = 1;

  function sortData(data, column, direction) {
    if (!column) return data;
    
    return [...data].sort((a, b) => {
      let aVal, bVal;
      
      switch(column) {
        case 'code':
          aVal = (a.code || '').toLowerCase();
          bVal = (b.code || '').toLowerCase();
          break;
        case 'name':
          aVal = (a.name || '').toLowerCase();
          bVal = (b.name || '').toLowerCase();
          break;
        case 'college':
          aVal = (a.college || '').toLowerCase();
          bVal = (b.college || '').toLowerCase();
          break;
        default:
          return 0;
      }
      
      return direction === 'asc' ? aVal.localeCompare(bVal) : bVal.localeCompare(aVal);
    });
  }

  function renderTable(list = filteredPrograms) {
    if (!tbody) return;
    
    // Sort the data
    const sortedData = sortData(list, sortColumn, sortDirection);
    
    // Paginate
    const totalPages = Math.max(1, Math.ceil(sortedData.length / pageSize));
    const start = (currentPage - 1) * pageSize;
    const end = start + pageSize;
    const pageData = sortedData.slice(start, end);
    
    tbody.innerHTML = '';
    if (pageData.length === 0) {
      tbody.innerHTML = `<tr><td colspan="4" class="text-center text-muted">No programs found.</td></tr>`;
      renderPagination(sortedData.length, totalPages);
      return;
    }
    
    // Find original indices for edit/delete buttons
    pageData.forEach((p, i) => {
      const originalIndex = filteredPrograms.findIndex(pr => pr.code === p.code);
      const tr = document.createElement('tr');
      tr.innerHTML = `
        <td>${p.code}</td>
        <td>${p.name}</td>
        <td>${p.college || ''}</td>
        <td>
          <button class="btn btn-sm btn-outline-primary me-1" data-index="${originalIndex}" data-action="edit">Edit</button>
          <button class="btn btn-sm btn-outline-danger" data-index="${originalIndex}" data-action="delete">Delete</button>
        </td>`;
      tbody.appendChild(tr);
    });
    
    renderPagination(sortedData.length, totalPages);
  }

  function renderPagination(totalItems, totalPages) {
    if (!paginationEl) return;
    paginationEl.innerHTML = '';
    
    if (totalPages <= 1) return;
    
    const createPageItem = (label, page, disabled = false, active = false) => {
      const li = document.createElement('li');
      li.className = 'page-item' + (disabled ? ' disabled' : '') + (active ? ' active' : '');
      const a = document.createElement('a');
      a.className = 'page-link';
      a.href = '#';
      a.textContent = label;
      if (!disabled) {
        a.addEventListener('click', (e) => {
          e.preventDefault();
          currentPage = page;
          renderTable();
          window.scrollTo({ top: 0, behavior: 'smooth' });
        });
      }
      li.appendChild(a);
      return li;
    };
    
    // Previous button
    const prev = createPageItem('Previous', currentPage - 1, currentPage === 1);
    paginationEl.appendChild(prev);
    
    // Page numbers
    const maxVisiblePages = 5;
    let startPage = Math.max(1, currentPage - Math.floor(maxVisiblePages / 2));
    let endPage = Math.min(totalPages, startPage + maxVisiblePages - 1);
    
    if (endPage - startPage < maxVisiblePages - 1) {
      startPage = Math.max(1, endPage - maxVisiblePages + 1);
    }
    
    if (startPage > 1) {
      paginationEl.appendChild(createPageItem('1', 1));
      if (startPage > 2) {
        const ellipsis = document.createElement('li');
        ellipsis.className = 'page-item disabled';
        ellipsis.innerHTML = '<span class="page-link">...</span>';
        paginationEl.appendChild(ellipsis);
      }
    }
    
    for (let i = startPage; i <= endPage; i++) {
      paginationEl.appendChild(createPageItem(String(i), i, false, i === currentPage));
    }
    
    if (endPage < totalPages) {
      if (endPage < totalPages - 1) {
        const ellipsis = document.createElement('li');
        ellipsis.className = 'page-item disabled';
        ellipsis.innerHTML = '<span class="page-link">...</span>';
        paginationEl.appendChild(ellipsis);
      }
      paginationEl.appendChild(createPageItem(String(totalPages), totalPages));
    }
    
    // Next button
    const next = createPageItem('Next', currentPage + 1, currentPage === totalPages);
    paginationEl.appendChild(next);
  }

  // Add sorting to table headers
  const table = tbody ? tbody.closest('table') : null;
  const tableHeaders = table ? table.querySelectorAll('thead th') : [];
  if (tableHeaders.length > 0) {
    const sortableColumns = ['code', 'name', 'college'];
    tableHeaders.forEach((th, index) => {
      if (index < sortableColumns.length) {
        th.style.cursor = 'pointer';
        th.style.userSelect = 'none';
        th.setAttribute('data-column', sortableColumns[index]);
        
        // Add sort indicators
        const sortIcon = document.createElement('span');
        sortIcon.className = 'sort-icon ms-1';
        sortIcon.innerHTML = '↕';
        sortIcon.style.fontSize = '0.9em';
        th.appendChild(sortIcon);
        
        th.addEventListener('click', function() {
          const column = this.getAttribute('data-column');
          
          // Toggle sort direction if clicking the same column
          if (sortColumn === column) {
            sortDirection = sortDirection === 'asc' ? 'desc' : 'asc';
          } else {
            sortColumn = column;
            sortDirection = 'asc';
          }
          
          currentPage = 1; // Reset to first page when sorting
          
          // Update sort indicators
          tableHeaders.forEach((header, idx) => {
            if (idx < sortableColumns.length) {
              const icon = header.querySelector('.sort-icon');
              if (icon) {
                if (header.getAttribute('data-column') === column) {
                  icon.textContent = sortDirection === 'asc' ? '↑' : '↓';
                  icon.style.color = '#0d6efd';
                  icon.style.fontWeight = 'bold';
                } else {
                  icon.textContent = '↕';
                  icon.style.color = '#6c757d';
                  icon.style.fontWeight = 'normal';
                }
              }
            }
          });
          
          renderTable();
        });
      }
    });
  }

  function resetForm() {
    form.reset();
    editIndex = null;
    if (form.elements['id']) form.elements['id'].value = '';
  }

  // Handle edit/delete buttons
  tbody.addEventListener('click', function(e) {
    const btn = e.target.closest('button');
    if (!btn) return;
    const index = parseInt(btn.dataset.index);
    const action = btn.dataset.action;
    
    if (action === 'delete') {
      const prog = filteredPrograms[index];
      if (!prog) return;
      if (!confirm(`Delete program ${prog.name}?`)) return;
      const csrfToken = document.querySelector('input[name="csrf_token"]')?.value;
      fetch(`/user/programs/delete/${prog.code}`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'X-CSRFToken': csrfToken || ''
        }
      }).then(r => r.json()).then(data => {
        if (data && data.success) {
          const programIndex = programs.findIndex(p => p.code === prog.code);
          if (programIndex !== -1) {
            programs.splice(programIndex, 1);
          }
          const filteredIndex = filteredPrograms.findIndex(p => p.code === prog.code);
          if (filteredIndex !== -1) {
            filteredPrograms.splice(filteredIndex, 1);
          }
          currentPage = 1; // Reset to first page
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
      const program = filteredPrograms[index];
      if (form) {
        if (form.elements['id']) form.elements['id'].value = program.code || '';
        if (form.elements['code']) form.elements['code'].value = program.code || '';
        if (form.elements['name']) form.elements['name'].value = program.name || '';
        if (form.elements['college_id']) form.elements['college_id'].value = program.college || '';
      }
      new bootstrap.Modal(document.querySelector('#programModal')).show();
    }
  });

  // Handle search
  searchInput.addEventListener('input', function() {
    const q = this.value.toLowerCase();
    filteredPrograms = programs.filter(p =>
      (p.name || '').toLowerCase().includes(q) ||
      (p.code || '').toLowerCase().includes(q) ||
      (p.college || '').toLowerCase().includes(q)
    );
    currentPage = 1; // Reset to first page when searching
    renderTable();
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

  // Initialize filtered programs and render
  filteredPrograms = programs.slice();
  renderTable();
});
