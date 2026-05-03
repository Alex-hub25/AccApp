// app.js — Global JS for TradApp
// Configures HTMX to send the CSRF token on every request.

document.addEventListener('htmx:configRequest', function (evt) {
  const csrfToken = document.cookie
    .split('; ')
    .find(row => row.startsWith('csrftoken='))
    ?.split('=')[1];
  if (csrfToken) {
    evt.detail.headers['X-CSRFToken'] = csrfToken;
  }
});

// Auto-dismiss Bootstrap alerts after 4 seconds
document.addEventListener('DOMContentLoaded', function () {
  document.querySelectorAll('.alert-dismissible').forEach(function (alert) {
    setTimeout(function () {
      const bsAlert = bootstrap.Alert.getOrCreateInstance(alert);
      bsAlert.close();
    }, 4000);
  });
});
