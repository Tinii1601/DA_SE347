document.addEventListener('DOMContentLoaded', function () {
    const toggleCheckboxes = document.querySelectorAll('.password-toggle-checkbox');

    toggleCheckboxes.forEach((checkbox) => {
        checkbox.addEventListener('change', function () {
            const targetId = checkbox.getAttribute('data-target');
            const input = targetId
                ? document.getElementById(targetId)
                : checkbox.closest('.password-field')?.querySelector('input');

            if (!input) return;

            input.type = checkbox.checked ? 'text' : 'password';
        });
    });
});
