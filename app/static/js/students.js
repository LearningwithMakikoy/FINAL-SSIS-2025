document.addEventListener('DOMContentLoaded', function() {
  const form = document.getElementById('studentForm');
  const tbody = document.getElementById('students-table-body');
  const searchInput = document.getElementById('student-search');
  let students = window.INIT_STUDENTS || [];
  let editIndex = null;

  function escapeHtml(text) {
    if (text == null) return '';
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
  }

  function renderTable(list = students) {
    if (!tbody) return;
    tbody.innerHTML = '';
    if (list.length === 0) {
      tbody.innerHTML = `<tr><td colspan="7" class="text-center text-muted">No students found.</td></tr>`;
      return;
    }
    list.forEach((s, i) => {
      const tr = document.createElement('tr');
      tr.innerHTML = `
        <td>${escapeHtml(s.id_number || s.id || '')}</td>
        <td>${escapeHtml(s.first_name || '')}</td>
        <td>${escapeHtml(s.last_name || '')}</td>
        <td>${escapeHtml(s.program || s.course || '')}</td>
        <td>${escapeHtml(String(s.year || ''))}</td>
        <td>${escapeHtml(s.gender || '')}</td>
        <td>
          <button class="btn btn-sm btn-outline-primary me-1" data-index="${i}" data-action="edit">Edit</button>
          <button class="btn btn-sm btn-outline-danger" data-index="${i}" data-action="delete">Delete</button>
        </td>`;
      tbody.appendChild(tr);
    });
  }

  function resetForm() {
    if (form) {
      form.reset();
      editIndex = null;
      if (form.elements['id']) form.elements['id'].value = '';
    }
  }

  // Handle edit/delete buttons
  tbody.addEventListener('click', function(e) {
    const btn = e.target.closest('button');
    if (!btn) return;
    const index = parseInt(btn.dataset.index);
    const action = btn.dataset.action;

    if (action === 'delete') {
      const student = students[index];
      if (!student) return;
      if (!confirm(`Delete student ${student.first_name} ${student.last_name}?`)) return;
      const csrfToken = document.querySelector('input[name="csrf_token"]')?.value;
      fetch(`/user/students/delete/${student.id}`, {
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
      const student = students[index];
      if (form && student) {
        if (form.elements['id']) form.elements['id'].value = student.id || '';
        if (form.elements['id_number']) form.elements['id_number'].value = student.id_number || student.id || '';
        if (form.elements['first_name']) form.elements['first_name'].value = student.first_name || '';
        if (form.elements['last_name']) form.elements['last_name'].value = student.last_name || '';
        if (form.elements['program_id']) form.elements['program_id'].value = student.course || '';
        if (form.elements['year']) form.elements['year'].value = student.year || '';
        if (form.elements['gender']) form.elements['gender'].value = student.gender || '';
      }
      editIndex = index;
      new bootstrap.Modal(document.querySelector('#studentModal')).show();
    }
  });

  // Handle search
  if (searchInput) {
    searchInput.addEventListener('input', function() {
      const q = this.value.toLowerCase();
      const filtered = students.filter(s => {
        const firstName = (s.first_name || '').toLowerCase();
        const lastName = (s.last_name || '').toLowerCase();
        const idNumber = (s.id_number || s.id || '').toLowerCase();
        const program = (s.program || s.course || '').toLowerCase();
        return firstName.includes(q) || 
               lastName.includes(q) || 
               idNumber.includes(q) ||
               program.includes(q);
      });
      renderTable(filtered);
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

  renderTable();
});

