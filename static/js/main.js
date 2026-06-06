// ── Auto-hide alerts after 5 seconds ─────────────────────
document.addEventListener('DOMContentLoaded', function () {

    // Auto dismiss alerts
    const alerts = document.querySelectorAll('.alert');
    alerts.forEach(function (alert) {
        setTimeout(function () {
            alert.style.transition = 'opacity 0.5s ease';
            alert.style.opacity = '0';
            setTimeout(function () {
                alert.remove();
            }, 500);
        }, 5000);
    });

    // Confirm before marking notifications as read
    const notifForm = document.querySelector('form[action="/notifications/read"]');
    if (notifForm) {
        notifForm.addEventListener('submit', function (e) {
            const confirmed = confirm('Mark all notifications as read?');
            if (!confirmed) {
                e.preventDefault();
            }
        });
    }

    // Confirm before updating complaint status (admin)
    const statusForm = document.querySelector('form[action*="/update"]');
    if (statusForm) {
        statusForm.addEventListener('submit', function (e) {
            const confirmed = confirm('Are you sure you want to update this complaint status?');
            if (!confirmed) {
                e.preventDefault();
            }
        });
    }

    // Highlight active nav link
    const currentPath = window.location.pathname;
    const navLinks = document.querySelectorAll('.nav-links a');
    navLinks.forEach(function (link) {
        if (link.getAttribute('href') === currentPath) {
            link.style.color = 'white';
            link.style.fontWeight = '700';
        }
    });

});