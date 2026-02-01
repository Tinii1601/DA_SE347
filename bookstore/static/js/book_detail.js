document.addEventListener('DOMContentLoaded', () => {
    const wrapper = document.getElementById('description-wrapper');
    const content = document.getElementById('description-content');
    const btn = document.getElementById('toggle-desc-btn');
    const fade = document.getElementById('fade-overlay');

    if (wrapper && content && btn && fade) {
        if (content.scrollHeight > 150) {
            btn.classList.remove('d-none');
        } else {
            wrapper.style.maxHeight = 'none';
            fade.style.display = 'none';
        }
    }

    const addToCartForm = document.getElementById('add-to-cart-form');
    if (addToCartForm) {
        addToCartForm.addEventListener('submit', (e) => {
            e.preventDefault();
            const url = addToCartForm.action;
            const formData = new FormData(addToCartForm);
            const cartDetailUrl = addToCartForm.dataset.cartDetailUrl || '/orders/cart/';

            fetch(url, {
                method: 'POST',
                body: formData,
                headers: {
                    'X-Requested-With': 'XMLHttpRequest',
                    'X-CSRFToken': formData.get('csrfmiddlewaretoken')
                }
            })
                .then(response => response.json())
                .then(data => {
                    if (data.cart_length !== undefined) {
                        const badge = document.querySelector('.bi-cart-fill')?.nextElementSibling;
                        if (badge) {
                            badge.textContent = data.cart_length;
                            badge.classList.remove('d-none');
                        } else {
                            location.reload();
                        }
                        alert('Đã thêm vào giỏ hàng!');
                    } else {
                        window.location.href = cartDetailUrl;
                    }
                })
                .catch(() => {
                    window.location.href = cartDetailUrl;
                });
        });
    }

    const imageModal = document.getElementById('imageModal');
    if (imageModal) {
        imageModal.addEventListener('show.bs.modal', () => {
            const mainImg = document.getElementById('main-product-img');
            const modalImg = document.getElementById('modal-img-content');
            if (mainImg && modalImg) {
                modalImg.src = mainImg.src;
            }
        });
    }
});

window.toggleDescription = function toggleDescription() {
    const wrapper = document.getElementById('description-wrapper');
    const btn = document.getElementById('toggle-desc-btn');
    const fade = document.getElementById('fade-overlay');

    if (!wrapper || !btn || !fade) return;

    if (wrapper.style.maxHeight !== 'none') {
        wrapper.style.maxHeight = 'none';
        btn.innerHTML = 'Thu gọn <i class="bi bi-chevron-up"></i>';
        btn.classList.replace('btn-primary', 'btn-outline-primary');
        fade.style.display = 'none';
    } else {
        wrapper.style.maxHeight = '150px';
        btn.innerHTML = 'Xem thêm <i class="bi bi-chevron-down"></i>';
        btn.classList.replace('btn-outline-primary', 'btn-primary');
        fade.style.display = 'block';
        wrapper.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
    }
};

window.updateMainImage = function updateMainImage(thumb) {
    const mainImg = document.getElementById('main-product-img');
    if (mainImg) {
        mainImg.src = thumb.src;

        document.querySelectorAll('.thumbnail-img').forEach(el => {
            el.style.opacity = '0.6';
            el.style.border = '1px solid #dee2e6';
        });

        thumb.style.opacity = '1';
        thumb.style.border = '2px solid #0d6efd';
    }
};
