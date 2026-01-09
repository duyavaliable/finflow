// Auto-hide flash messages
document.addEventListener('DOMContentLoaded', function() {
    const alerts = document.querySelectorAll('.alert');
    alerts.forEach(alert => {
        setTimeout(() => {
            alert.style.transition = 'opacity 0.3s';
            alert.style.opacity = '0';
            setTimeout(() => alert.remove(), 300);
        }, 5000);
    });
});

// Confirm delete
function confirmDelete(message) {
    return confirm(message || 'Bạn có chắc muốn xóa?');
}

// Format number input with thousand separators
function formatNumberInput(input) {
    let value = input.value.replace(/[^0-9]/g, '');
    if (value) {
        input.value = parseInt(value).toLocaleString('vi-VN');
    }
}
