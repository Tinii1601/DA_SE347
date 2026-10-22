// Hàm cập nhật số lượng giỏ hàng trên Header (cả desktop & mobile)
function updateCartBadge(count) {
    document.querySelectorAll('.cart-badge').forEach(badge => {
        badge.textContent = count;
        if (parseInt(count) > 0) {
            badge.classList.remove('d-none');
        } else {
            badge.classList.add('d-none');
        }
    });
}

// Event Delegation: Bắt sự kiện submit của toàn bộ form .add-to-cart-form trên mọi trang (kể cả slider/carousel)
document.addEventListener('submit', function (e) {
    const form = e.target.closest('.add-to-cart-form');
    if (!form) return;

    e.preventDefault();
    e.stopPropagation();

    const url = form.action;
    const formData = new FormData(form);
    const btn = form.querySelector('button[type="submit"]');

    if (btn) btn.disabled = true;

    fetch(url, {
        method: 'POST',
        body: formData,
        headers: {
            'X-Requested-With': 'XMLHttpRequest',
            'X-CSRFToken': formData.get('csrfmiddlewaretoken')
        }
    })
    .then(response => response.json().catch(() => ({})))
    .then(data => {
        if (btn) btn.disabled = false;
        if (data.success) {
            if (data.cart_length !== undefined) {
                updateCartBadge(data.cart_length);
            }
            if (window.showToast) {
                window.showToast(data.message || 'Đã thêm vào giỏ hàng thành công!', data.adjusted ? 'warning' : 'success');
            }
        } else {
            const errMsg = data.error || 'Không thể thêm sản phẩm vào giỏ hàng.';
            if (window.showToast) {
                window.showToast(errMsg, 'warning');
            }
        }
    })
    .catch(error => {
        if (btn) btn.disabled = false;
        console.error('Error adding to cart:', error);
    });
});