/* ─────────────────────────────────────────
   script.js  —  Form Logic & Validation
───────────────────────────────────────── */

// ── DOM References ────────────────────────────────────────────────────
const form        = document.getElementById('contactForm');
const submitBtn   = document.getElementById('submitBtn');
const btnLabel    = document.getElementById('btnLabel');
const btnSpinner  = document.getElementById('btnSpinner');
const btnArrow    = document.getElementById('btnArrow');
const successBox  = document.getElementById('successBox');
const successName  = document.getElementById('successName');
const successEmail = document.getElementById('successEmail');
const resetBtn    = document.getElementById('resetBtn');

// Field inputs
const fields = {
  name:  document.getElementById('name'),
  phone: document.getElementById('phone'),
  email: document.getElementById('email'),
  city:  document.getElementById('city'),
};

// ── Validation Rules ──────────────────────────────────────────────────
const rules = {
  name: {
    validate: (v) => v.trim().length >= 2,
    message:  'Please enter your full name (min. 2 characters)',
  },
  phone: {
    validate: (v) => /^\d{10}$/.test(v.trim()),
    message:  'Enter a valid 10-digit phone number',
  },
  email: {
    validate: (v) => /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(v.trim()),
    message:  'Enter a valid email address',
  },
  city: {
    validate: (v) => v.trim().length >= 2,
    message:  'Please enter your city name',
  },
};

// ── Helper: Show error on a field ─────────────────────────────────────
function showError(fieldName, message) {
  const fieldEl = document.getElementById('field-' + fieldName);
  const errEl   = document.getElementById('err-' + fieldName);

  if (fieldEl) fieldEl.classList.add('has-error');
  if (errEl)   errEl.textContent = message;
}

// ── Helper: Clear error on a field ───────────────────────────────────
function clearError(fieldName) {
  const fieldEl = document.getElementById('field-' + fieldName);
  const errEl   = document.getElementById('err-' + fieldName);

  if (fieldEl) fieldEl.classList.remove('has-error');
  if (errEl)   errEl.textContent = '';
}

// ── Helper: Clear all errors ──────────────────────────────────────────
function clearAllErrors() {
  Object.keys(rules).forEach(clearError);
}

// ── Validate a single field ───────────────────────────────────────────
function validateField(fieldName) {
  const input = fields[fieldName];
  const rule  = rules[fieldName];

  if (!input || !rule) return true;

  const value = input.value;

  if (rule.validate(value)) {
    clearError(fieldName);
    return true;
  } else {
    showError(fieldName, rule.message);
    return false;
  }
}

// ── Validate all fields, return true if all pass ──────────────────────
function validateAll() {
  let allValid = true;

  Object.keys(rules).forEach((fieldName) => {
    const valid = validateField(fieldName);
    if (!valid) allValid = false;
  });

  return allValid;
}

// ── Set button loading state ──────────────────────────────────────────
function setLoading(isLoading) {
  submitBtn.disabled        = isLoading;
  btnSpinner.style.display  = isLoading ? 'block' : 'none';
  btnArrow.style.display    = isLoading ? 'none'  : 'block';
  btnLabel.textContent      = isLoading ? 'Submitting...' : 'Submit Entry';
}

// ── Show success state ─────────────────────────────────────────────────
function showSuccess(data) {
  form.style.display        = 'none';
  successBox.classList.add('show');
  successName.textContent   = data.name;
  successEmail.textContent  = data.email;
}

// ── Reset form to initial state ────────────────────────────────────────
function resetForm() {
  form.reset();
  clearAllErrors();
  setLoading(false);
  form.style.display = 'flex';
  successBox.classList.remove('show');
}

// ── Real-time validation on blur ───────────────────────────────────────
Object.keys(fields).forEach((fieldName) => {
  const input = fields[fieldName];

  // Validate when user leaves a field
  input.addEventListener('blur', () => {
    // Only validate if the field has been touched (has a value or was focused)
    if (input.value.trim() !== '') {
      validateField(fieldName);
    }
  });

  // Clear error as soon as user starts typing again
  input.addEventListener('input', () => {
    const fieldEl = document.getElementById('field-' + fieldName);
    if (fieldEl && fieldEl.classList.contains('has-error')) {
      // Clear error only when input becomes valid
      if (rules[fieldName].validate(input.value)) {
        clearError(fieldName);
      }
    }
  });
});

// ── Form Submit Handler ───────────────────────────────────────────────
form.addEventListener('submit', async (e) => {
  e.preventDefault();

  // Run full validation
  const isValid = validateAll();
  if (!isValid) {
    // Focus the first field with an error
    const firstError = Object.keys(rules).find(
      (name) => document.getElementById('field-' + name)?.classList.contains('has-error')
    );
    if (firstError) fields[firstError].focus();
    return;
  }

  // Collect form data
  const formData = {
    name:  fields.name.value.trim(),
    phone: fields.phone.value.trim(),
    email: fields.email.value.trim(),
    city:  fields.city.value.trim(),
  };

  // Show loading
  setLoading(true);

  try {
    // ── Real Flask API call ───────────────────────────────────────────
    const response = await fetch('/api/submit', {
      method:  'POST',
      headers: { 'Content-Type': 'application/json' },
      body:    JSON.stringify(formData),
    });

    const result = await response.json();

    if (response.ok && result.success) {
      showSuccess(formData);
    } else if (result.errors) {
      // Server-side validation errors — show on fields
      Object.entries(result.errors).forEach(([field, msg]) => showError(field, msg));
    } else {
      alert(result.message || 'Something went wrong. Please try again.');
    }

  } catch (error) {
    console.error('Submission error:', error);
    alert('Network error — make sure Flask server is running on port 5000.');
  } finally {
    setLoading(false);
  }
});

// ── Reset button ──────────────────────────────────────────────────────
resetBtn.addEventListener('click', resetForm);

// ── Phone: allow only digits ──────────────────────────────────────────
fields.phone.addEventListener('keypress', (e) => {
  if (!/[0-9]/.test(e.key)) {
    e.preventDefault();
  }
});
