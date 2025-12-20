document.addEventListener('DOMContentLoaded', function() {
  const form = document.getElementById('studentForm');
  const tbody = document.getElementById('students-table-body');
  const searchInput = document.getElementById('student-search');
  const paginationEl = document.querySelector('.pagination');
  const filterProgram = document.getElementById('filter-program');
  const filterYear = document.getElementById('filter-year');
  const filterGender = document.getElementById('filter-gender');
  const clearFiltersBtn = document.getElementById('btn-clear-filters');
  let students = window.INIT_STUDENTS || [];
  let filteredStudents = students.slice();
  let editIndex = null;
  
  // Sorting state
  let sortColumn = null;
  let sortDirection = 'asc'; // 'asc' or 'desc'
  
  // Pagination state
  const pageSize = 30;
  let currentPage = 1;

  function escapeHtml(text) {
    if (text == null) return '';
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
  }

  function sortData(data, column, direction) {
    if (!column) return data;
    
    return [...data].sort((a, b) => {
      let aVal, bVal;
      
      switch(column) {
        case 'id_number':
          // Parse ID number in format YYYY-NNNN for proper numeric sorting
          const parseIdNumber = (idStr) => {
            if (!idStr) return { year: 0, num: 0 };
            const id = (idStr || '').toString().trim();
            // Handle YYYY-NNNN format
            if (id.includes('-')) {
              const parts = id.split('-');
              const year = parseInt(parts[0]) || 0;
              const num = parseInt(parts[1]) || 0;
              return { year, num, full: year * 10000 + num }; // Combine for sorting
            }
            // Fallback: try to parse as number
            const num = parseInt(id.replace(/\D/g, '')) || 0;
            return { year: Math.floor(num / 10000), num: num % 10000, full: num };
          };
          const aId = parseIdNumber(a.id_number || a.id || '');
          const bId = parseIdNumber(b.id_number || b.id || '');
          aVal = aId.full;
          bVal = bId.full;
          break;
        case 'first_name':
          aVal = (a.first_name || '').trim().toLowerCase();
          bVal = (b.first_name || '').trim().toLowerCase();
          break;
        case 'last_name':
          aVal = (a.last_name || '').trim().toLowerCase();
          bVal = (b.last_name || '').trim().toLowerCase();
          break;
        case 'program':
          aVal = (a.program || a.course || '').trim().toLowerCase();
          bVal = (b.program || b.course || '').trim().toLowerCase();
          break;
        case 'year':
          aVal = parseInt(a.year) || 0;
          bVal = parseInt(b.year) || 0;
          break;
        case 'gender':
          aVal = (a.gender || '').trim().toLowerCase();
          bVal = (b.gender || '').trim().toLowerCase();
          break;
        default:
          return 0;
      }
      
      if (typeof aVal === 'string' && typeof bVal === 'string') {
        const comparison = aVal.localeCompare(bVal);
        return direction === 'asc' ? comparison : -comparison;
      } else {
        return direction === 'asc' ? aVal - bVal : bVal - aVal;
      }
    });
  }

  function renderTable(list = filteredStudents) {
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
      tbody.innerHTML = `<tr><td colspan="8" class="text-center text-muted">No students found.</td></tr>`;
      renderPagination(sortedData.length, totalPages);
      return;
    }
    
    // Render table rows
    pageData.forEach((s, i) => {
      const DEFAULT_PHOTO_URL = 'https://mczkesrlrwuuxyxdigvp.supabase.co/storage/v1/object/public/SSIS/default_profile.jpg';
      const photoUrl = s.photo_url || '';
      const photoId = `photo-${s.id}`;
      const placeholderId = `photo-placeholder-${s.id}`;
      const photoHtml = photoUrl 
        ? `<div style="position: relative; width: 40px; height: 40px;">
             <img id="${photoId}" src="${escapeHtml(photoUrl)}" alt="Student photo" style="width: 40px; height: 40px; object-fit: cover; border-radius: 4px;" onerror="this.style.display='none'; document.getElementById('${placeholderId}').style.display='flex';">
             <div id="${placeholderId}" style="display: none; width: 40px; height: 40px; background-color: #dee2e6; border-radius: 4px; align-items: center; justify-content: center; font-size: 0.7rem; color: #6c757d;">No photo</div>
           </div>`
        : `<div style="width: 40px; height: 40px; background-color: #dee2e6; border-radius: 4px; display: flex; align-items: center; justify-content: center; font-size: 0.7rem; color: #6c757d;"><img src="${DEFAULT_PHOTO_URL}" alt="Default photo" style="width: 40px; height: 40px; object-fit: cover; border-radius: 4px;">
           </div>`;
      
      const tr = document.createElement('tr');
      tr.innerHTML = `
        <td>${photoHtml}</td>
        <td>${escapeHtml(s.id_number || s.id || '')}</td>
        <td>${escapeHtml(s.first_name || '')}</td>
        <td>${escapeHtml(s.last_name || '')}</td>
        <td>${escapeHtml(s.program || s.course || '')}</td>
        <td>${escapeHtml(String(s.year || ''))}</td>
        <td>${escapeHtml(s.gender || '')}</td>
        <td>
          <div class="d-flex gap-2">
            <button class="btn btn-sm btn-outline-primary" data-student-id="${escapeHtml(s.id)}" data-action="edit">Edit</button>
            <button class="btn btn-sm btn-outline-danger" data-student-id="${escapeHtml(s.id)}" data-action="delete">Delete</button>
          </div>
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
    
    // Page numbers - show all pages if 20 or fewer, otherwise show window around current page
    if (totalPages <= 20) {
      // Show all pages
      for (let i = 1; i <= totalPages; i++) {
        paginationEl.appendChild(createPageItem(String(i), i, false, i === currentPage));
      }
    } else {
      // Show window of pages around current page
      const maxVisiblePages = 7;
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
    }
    
    // Next button
    const next = createPageItem('Next', currentPage + 1, currentPage === totalPages);
    paginationEl.appendChild(next);
  }

  // Add sorting to table headers (only once on page load)
  const table = tbody ? tbody.closest('table') : null;
  const tableHeaders = table ? table.querySelectorAll('thead th') : [];
  if (tableHeaders.length > 0) {
    // Map column indices to sortable column names
    // Index 0: Photo (not sortable)
    // Index 1: ID # (id_number)
    // Index 2: First Name (first_name)
    // Index 3: Last Name (last_name)
    // Index 4: Course (program)
    // Index 5: Year (year)
    // Index 6: Gender (gender)
    // Index 7: Actions (not sortable)
    const columnMapping = {
      1: 'id_number',
      2: 'first_name',
      3: 'last_name',
      4: 'program',
      5: 'year',
      6: 'gender'
    };
    
    tableHeaders.forEach((th, index) => {
      const columnName = columnMapping[index];
      
      // Only make sortable columns clickable
      if (columnName) {
        // Check if already initialized to avoid duplicate icons
        if (!th.hasAttribute('data-sort-initialized')) {
          th.style.cursor = 'pointer';
          th.style.userSelect = 'none';
          th.setAttribute('data-column', columnName);
          th.setAttribute('data-sort-initialized', 'true');
          
          // Add sort indicators (only if not already present)
          if (!th.querySelector('.sort-icon')) {
            const sortIcon = document.createElement('span');
            sortIcon.className = 'sort-icon ms-1';
            sortIcon.innerHTML = '↕';
            sortIcon.style.fontSize = '0.9em';
            th.appendChild(sortIcon);
          }
          
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
            
            // Re-query headers to ensure we have fresh references
            const currentHeaders = table ? table.querySelectorAll('thead th') : [];
            const currentMapping = {
              1: 'id_number',
              2: 'first_name',
              3: 'last_name',
              4: 'program',
              5: 'year',
              6: 'gender'
            };
            
            // Update sort indicators for all sortable columns
            currentHeaders.forEach((header, idx) => {
              const colName = currentMapping[idx];
              if (colName) {
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
      } else {
        // Non-sortable columns (Photo, Actions)
        th.style.cursor = 'default';
      }
    });
  }

  function resetForm() {
    if (form) {
      form.reset();
      editIndex = null;
      if (form.elements['id']) form.elements['id'].value = '';
      
      // Reset photo preview
      const photoPreview = document.getElementById('photo-preview');
      const photoPlaceholder = document.getElementById('photo-placeholder');
      const photoInput = document.getElementById('photo-input');
      const photoActionButtons = document.getElementById('photo-action-buttons');
      const removePhotoInput = document.getElementById('remove_photo');

      if (photoPreview && photoPlaceholder && photoInput) {
        photoPreview.src = '';
        photoPreview.style.display = 'none';
        photoPlaceholder.style.display = 'block';
        photoInput.value = '';
        
        // Hide remove button container if it exists
        if (photoActionButtons) {
          photoActionButtons.style.display = 'none';
        }
        
        // Reset remove photo flag if it exists
        if (removePhotoInput) {
          removePhotoInput.value = '0';
        }
      }
    }
  }
  
  // Handle photo preview and removal
  const photoInput = document.getElementById('photo-input');
  if (photoInput) {
    // Initialize photo removal functionality
    const photoPreview = document.getElementById('photo-preview');
    const photoPlaceholder = document.getElementById('photo-placeholder');
    const removePhotoBtn = document.getElementById('remove-photo-btn');
    const photoActionButtons = document.getElementById('photo-action-buttons');
    const removePhotoInput = document.getElementById('remove_photo');
    const previewContainer = document.getElementById('photo-preview-container');
    const defaultPhotoUrl = 'https://mczkesrlrwuuxyxdigvp.supabase.co/storage/v1/object/public/SSIS/default_profile.jpg';
    
    // Remove photo functionality
    if (removePhotoBtn) {
      removePhotoBtn.addEventListener('click', function() {
        // Reset to default
        if (photoPreview) {
          photoPreview.src = defaultPhotoUrl;
          photoPreview.style.display = 'none';
        }
        
        if (photoPlaceholder) {
          photoPlaceholder.style.display = 'block';
        }
        
        // Hide remove button container
        if (photoActionButtons) {
          photoActionButtons.style.display = 'none';
        }
        
        // Clear file input
        photoInput.value = '';
        
        // Set removed flag
        if (removePhotoInput) {
          removePhotoInput.value = '1';
        }
      });
    }
    
    // Click preview container to trigger file input
    if (previewContainer) {
      previewContainer.addEventListener('click', function() {
        photoInput.click();
      });
      
      // Add hover effect
      previewContainer.addEventListener('mouseenter', function() {
        this.style.borderColor = '#007bff';
        this.style.backgroundColor = '#e9ecef';
      });
      
      previewContainer.addEventListener('mouseleave', function() {
        this.style.borderColor = '#dee2e6';
        this.style.backgroundColor = '#f8f9fa';
      });
    }
    
    // Handle file selection
    photoInput.addEventListener('change', function(e) {
      const file = e.target.files[0];
      if (file) {
        // Validate file type
        const validTypes = ['image/jpeg', 'image/jpg', 'image/png'];
        if (!validTypes.includes(file.type)) {
          alert('Invalid file type. Please upload JPG, JPEG, or PNG.');
          e.target.value = '';
          return;
        }
        
        // Validate file size (5MB)
        if (file.size > 5 * 1024 * 1024) {
          alert('File too large. Maximum size is 5MB.');
          e.target.value = '';
          return;
        }
        
        // Show preview
        const reader = new FileReader();
        reader.onload = function(e) {
          if (photoPreview && photoPlaceholder) {
            photoPreview.src = e.target.result;
            photoPreview.style.display = 'block';
            photoPlaceholder.style.display = 'none';
            
            // Show remove button container
            if (photoActionButtons) {
              photoActionButtons.style.display = 'block';
            }
            
            // Reset removed flag
            if (removePhotoInput) {
              removePhotoInput.value = '0';
            }
          }
        };
        reader.readAsDataURL(file);
      }
    });
  }

  // Handle edit/delete buttons
  tbody.addEventListener('click', function(e) {
    const btn = e.target.closest('button');
    if (!btn) return;
    const studentId = btn.dataset.studentId;
    const action = btn.dataset.action;
    
    if (!studentId) return;

    // Find student by ID (works regardless of sorting)
    const student = students.find(s => s.id === studentId) || filteredStudents.find(s => s.id === studentId);
    if (!student) return;

    if (action === 'delete') {
      if (!confirm(`Delete student ${student.first_name} ${student.last_name}?`)) return;
      const csrfToken = document.querySelector('input[name="csrf_token"]')?.value;
      fetch(`/student/delete/${student.id}`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'X-CSRFToken': csrfToken || ''
        }
      }).then(r => r.json()).then(data => {
        if (data && data.success) {
          const studentIndex = students.findIndex(s => s.id === student.id);
          if (studentIndex !== -1) {
            students.splice(studentIndex, 1);
          }
          const filteredIndex = filteredStudents.findIndex(s => s.id === student.id);
          if (filteredIndex !== -1) {
            filteredStudents.splice(filteredIndex, 1);
          }
          currentPage = 1; // Reset to first page
          renderTable();
          showAlert('success', data.message || 'Student deleted');
        } else {
          showAlert('danger', (data && data.message) || 'Failed to delete student');
        }
      }).catch(err => {
        console.error(err);
        showAlert('danger', 'Failed to delete student');
      });
    } else if (action === 'edit') {
      if (form && student) {
        // Always set DB id (hidden) and the original id_number (so server can find the record)
        if (form.elements['id']) form.elements['id'].value = String(student.id ?? '');
        if (form.elements['original_id_number']) {
          form.elements['original_id_number'].value = student.id_number ?? String(student.id ?? '');
        } else {
          // fallback to element by id if form.elements doesn't have it
          const origEl = document.getElementById('original_id_number');
          if (origEl) origEl.value = student.id_number ?? String(student.id ?? '');
        }

        // Populate visible fields once
        if (form.elements['id_number']) form.elements['id_number'].value = student.id_number ?? String(student.id ?? '');
        if (form.elements['first_name']) form.elements['first_name'].value = student.first_name ?? '';
        if (form.elements['last_name']) form.elements['last_name'].value = student.last_name ?? '';
        if (form.elements['program_id']) form.elements['program_id'].value = student.program_id ?? student.course ?? '';
        if (form.elements['year']) form.elements['year'].value = student.year ?? '';
        if (form.elements['gender']) {
          const g = form.elements['gender'];
          g.value = student.gender ?? '';
          if (!g.value) { // fallback to match option text
            Array.from(g.options).forEach(opt => {
              if ((opt.text || '').toLowerCase() === (student.gender || '').toLowerCase()) opt.selected = true;
            });
          }
        }
        
        // Set photo preview and removal state
        const photoPreview = document.getElementById('photo-preview');
        const photoPlaceholder = document.getElementById('photo-placeholder');
        const photoInput = document.getElementById('photo-input');
        const photoActionButtons = document.getElementById('photo-action-buttons');
        const removePhotoInput = document.getElementById('remove_photo');

        if (photoPreview && photoPlaceholder && photoInput && photoActionButtons && removePhotoInput) {
          if (student.photo_url) {
            photoPreview.src = student.photo_url;
            photoPreview.style.display = 'block';
            photoPlaceholder.style.display = 'none';
            photoActionButtons.style.display = 'block';
            removePhotoInput.value = '0'; // Student has photo, not removed
          } else {
            photoPreview.style.display = 'none';
            photoPlaceholder.style.display = 'block';
            photoActionButtons.style.display = 'none';
            removePhotoInput.value = '0'; // No photo to remove
          }
          photoInput.value = ''; // Reset file input
        }
      }
      // Store student ID instead of index
      editIndex = studentId;
      new bootstrap.Modal(document.querySelector('#studentModal')).show();
    }
  });

  // Handle search
  if (searchInput) {
    searchInput.addEventListener('input', function() {
        const q = this.value.toLowerCase();
        
        if (!q) {
            // If search is empty, just apply the current filters
            applyFilters();
            return;
        }
        
        // First apply the dropdown filters to get base filtered list
        const programVal = (filterProgram?.value || "").toLowerCase();
        const yearVal = (filterYear?.value || "").toLowerCase();
        const genderVal = (filterGender?.value || "").toLowerCase();
        
        let baseFiltered = students.filter(s => {
            const program = (s.program || s.course || s.program_id || "").toLowerCase();
            const year = String(s.year || "").toLowerCase();
            const gender = (s.gender || "").toLowerCase();

            const programMatch = !programVal || program === programVal || (s.course && s.course.toLowerCase().includes(programVal));
            const yearMatch = !yearVal || year === yearVal;
            const genderMatch = !genderVal || gender === genderVal;

            return programMatch && yearMatch && genderMatch;
        });
        
        // Then search within that filtered list
        filteredStudents = baseFiltered.filter(s => {
            const firstName = (s.first_name || '').toLowerCase();
            const lastName = (s.last_name || '').toLowerCase();
            const idNumber = (s.id_number || s.id || '').toLowerCase();
            const program = (s.program || s.course || '').toLowerCase();
            return firstName.includes(q) || 
                   lastName.includes(q) || 
                   idNumber.includes(q) ||
                   program.includes(q);
        });
        
        console.log(`Searched from ${baseFiltered.length} to ${filteredStudents.length} students`);
        currentPage = 1; // Reset to first page when searching
        renderTable();
    });
  }

  // Reset form when modal is closed
  const modal = document.getElementById('studentModal');
  if (modal) {
    modal.addEventListener('hidden.bs.modal', function() {
      resetForm();
    });
  }

  // Reset form when Add button is clicked
  const addBtn = document.getElementById('btn-add');
  if (addBtn) {
    addBtn.addEventListener('click', function() {
      resetForm();
    });
  }

  // Format Student ID input to YYYY-NNNN format
  const idNumberInput = form ? form.elements['id_number'] : null;
  if (idNumberInput) {
    function formatStudentId(value) {
      // Remove all non-digits
      let digits = value.replace(/\D/g, '');
      
      // Limit to 8 digits
      if (digits.length > 8) {
        digits = digits.slice(0, 8);
      }
      
      // Format as YYYY-NNNN
      if (digits.length > 4) {
        return digits.slice(0, 4) + '-' + digits.slice(4);
      }
      
      return digits;
    }

    // Handle input event (typing, pasting, etc.)
    idNumberInput.addEventListener('input', function(e) {
      const cursorPos = e.target.selectionStart;
      const oldValue = e.target.value;
      const formattedValue = formatStudentId(e.target.value);
      e.target.value = formattedValue;
      
      // Adjust cursor position when dash is auto-inserted
      if (oldValue.length < formattedValue.length && formattedValue.length === 5 && cursorPos === 4) {
        // Dash was inserted, move cursor after it
        e.target.setSelectionRange(5, 5);
      } else {
        // Try to maintain approximate cursor position
        const digitsBeforeCursor = oldValue.substring(0, cursorPos).replace(/\D/g, '').length;
        let newCursorPos = 0;
        let digitCount = 0;
        for (let i = 0; i < formattedValue.length; i++) {
          if (/\d/.test(formattedValue[i])) {
            digitCount++;
            if (digitCount === digitsBeforeCursor) {
              newCursorPos = i + 1;
              break;
            }
          }
          newCursorPos = i + 1;
        }
        e.target.setSelectionRange(Math.min(newCursorPos, formattedValue.length), Math.min(newCursorPos, formattedValue.length));
      }
    });

    // Handle paste event
    idNumberInput.addEventListener('paste', function(e) {
      e.preventDefault();
      const pastedData = (e.clipboardData || window.clipboardData).getData('text');
      const formattedValue = formatStudentId(pastedData);
      const start = e.target.selectionStart;
      const end = e.target.selectionEnd;
      const currentValue = e.target.value;
      
      // Insert formatted value
      const newValue = currentValue.substring(0, start) + formattedValue + currentValue.substring(end);
      e.target.value = formatStudentId(newValue);
      
      // Move cursor to end of pasted content
      const newCursorPos = start + formattedValue.length;
      setTimeout(() => {
        e.target.setSelectionRange(Math.min(newCursorPos, e.target.value.length), Math.min(newCursorPos, e.target.value.length));
      }, 0);
    });

    // Prevent invalid characters on keypress
    idNumberInput.addEventListener('keypress', function(e) {
      const char = e.key || String.fromCharCode(e.which);
      const cursorPos = e.target.selectionStart;
      const currentValue = e.target.value;
      
      // Allow control keys (backspace, delete, tab, arrow keys, etc.)
      if (e.ctrlKey || e.metaKey || e.altKey || 
          ['Backspace', 'Delete', 'Tab', 'Enter', 'ArrowLeft', 'ArrowRight', 'ArrowUp', 'ArrowDown', 'Home', 'End'].includes(char)) {
        return true;
      }
      
      // Only allow digits
      if (!/\d/.test(char)) {
        e.preventDefault();
        return false;
      }
      
      // Prevent typing if already at max length (8 digits + 1 dash = 9 chars)
      const digitCount = currentValue.replace(/\D/g, '').length;
      if (digitCount >= 8 && cursorPos >= currentValue.length) {
        e.preventDefault();
        return false;
      }
    });
  }

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
  
  // FORM LOADING FUNCTIONALITY 
  const submitBtn = document.getElementById('submit-btn');
  if (form && submitBtn) {
    // Store original button HTML
    const originalBtnHtml = submitBtn.innerHTML;
    
    // Handle form submission
    form.addEventListener('submit', function() {
      // Show loading state
      submitBtn.disabled = true;
      submitBtn.innerHTML = `
        <span class="spinner-border spinner-border-sm me-2" role="status" aria-hidden="true"></span>
        Saving...
      `;
    });
    
    // Reset button when modal closes
    if (modal) {
      modal.addEventListener('hidden.bs.modal', function() {
        resetSubmitButton();
      });
      
      modal.addEventListener('show.bs.modal', function() {
        resetSubmitButton();
      });
    }
    
    // Also reset on page load in case of validation errors
    window.addEventListener('load', function() {
      resetSubmitButton();
    });
    
    function resetSubmitButton() {
      submitBtn.disabled = false;
      submitBtn.innerHTML = originalBtnHtml;
    }
  }

   
function applyFilters() {
    console.log('Applying filters...');
   
    const programVal = (filterProgram?.value || "").toLowerCase();
    const yearVal = (filterYear?.value || "").toLowerCase();
    const genderVal = (filterGender?.value || "").toLowerCase();

    console.log('Filter values:', {
        program: programVal,
        year: yearVal,
        gender: genderVal
    });

    filteredStudents = students.filter(s => {
        const program = (s.program || s.course || s.program_id || "").toLowerCase();
        const year = String(s.year || "").toLowerCase();
        const gender = (s.gender || "").toLowerCase();

        const programMatch = !programVal || program === programVal || (s.course && s.course.toLowerCase().includes(programVal));
        const yearMatch = !yearVal || year === yearVal;
        const genderMatch = !genderVal || gender === genderVal;

        return programMatch && yearMatch && genderMatch;
    });

    console.log(`Filtered from ${students.length} to ${filteredStudents.length} students`);
    currentPage = 1;
    renderTable();
}


  function clearAllFilters() {
    console.log('Clearing all filters');
   
    // Reset all filter inputs
    if (filterProgram) filterProgram.value = '';
    if (filterYear) filterYear.value = '';
    if (filterGender) filterGender.value = '';
    if (searchInput) searchInput.value = '';
   
    // Reset to show all students
    filteredStudents = students.slice();


   
    currentPage = 1;
    renderTable();




  }


  // ============ EVENT LISTENER SETUP ============

  // Setup filter event listeners
  if (filterProgram) {
    filterProgram.addEventListener("change", applyFilters);
  }


  if (filterYear) {
    filterYear.addEventListener("change", applyFilters);
  }


  if (filterGender) {
    filterGender.addEventListener("change", applyFilters);
  }


  if (clearFiltersBtn) {
    clearFiltersBtn.addEventListener("click", clearAllFilters);
    console.log('Clear Filters button event listener added');
  }



  // Initialize filtered students and render
  filteredStudents = students.slice();
  renderTable();
});