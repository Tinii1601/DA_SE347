document.addEventListener('DOMContentLoaded', function () {
    const input = document.getElementById('id_avatar');
    if (!input) return;
    input.addEventListener('change', function (e) {
        const file = e.target.files[0];
        if (!file) return;
        const validTypes = ['jpg', 'jpeg', 'png', 'gif', 'webp'];
        const ext = file.name.split('.').pop().toLowerCase();
        if (!validTypes.includes(ext)) {
            alert('Vui lòng chọn file ảnh (jpg, png, jpeg, webp)');
            input.value = '';
            return;
        }
        const reader = new FileReader();
        reader.onload = function (ev) {
            let avatar = document.getElementById('avatarPreview');
            if (!avatar) return;
            if (avatar.tagName === 'DIV') {
                const img = document.createElement('img');
                img.id = 'avatarPreview';
                img.src = ev.target.result;
                img.className = 'rounded-circle mb-2';
                img.width = 120;
                img.height = 120;
                img.style.objectFit = 'cover';
                avatar.replaceWith(img);
            } else {
                avatar.src = ev.target.result;
            }
        };
        reader.readAsDataURL(file);
    });
});
