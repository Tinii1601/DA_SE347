document.addEventListener('DOMContentLoaded', function () {
    const pwd1 = document.getElementById('id_new_password1');
    const pwd2 = document.getElementById('id_new_password2');

    const ruleBox = document.getElementById('password-rules');
    const matchBox = document.getElementById('password-match');

    if (!pwd1 || !pwd2 || !ruleBox || !matchBox) return;

    pwd1.addEventListener('input', function () {
        const value = pwd1.value;
        let errors = [];

        if (value.length < 8) {
            errors.push('Mật khẩu phải có ít nhất 8 ký tự.');
        }
        if (/^\d+$/.test(value)) {
            errors.push('Mật khẩu không được chỉ bao gồm chữ số.');
        }
        if (['12345678', 'password', 'qwerty'].includes(value.toLowerCase())) {
            errors.push('Mật khẩu này quá phổ biến.');
        }

        ruleBox.innerHTML = errors.length
            ? errors.map(e => `<div>• ${e}</div>`).join('')
            : '';
    });

    pwd2.addEventListener('input', function () {
        if (pwd2.value && pwd1.value !== pwd2.value) {
            matchBox.innerHTML = 'Mật khẩu xác nhận không khớp.';
        } else {
            matchBox.innerHTML = '';
        }
    });
});
