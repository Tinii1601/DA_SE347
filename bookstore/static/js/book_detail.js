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

    // Real-time Stock Enforcement on Quantity Input
    const qtyInput = document.getElementById('quantity-input');
    if (qtyInput) {
        const maxStock = parseInt(qtyInput.getAttribute('max')) || 9999;
        
        function enforceStockLimit() {
            let val = parseInt(qtyInput.value);
            if (!isNaN(val) && val > maxStock) {
                qtyInput.value = maxStock;
                if (window.showToast) {
                    window.showToast(`Sản phẩm chỉ còn tối đa ${maxStock} cuốn trong kho! Đã tự động điều chỉnh về mức tối đa.`, 'warning');
                }
            }
        }

        qtyInput.addEventListener('input', enforceStockLimit);
        qtyInput.addEventListener('change', function() {
            let val = parseInt(this.value);
            if (isNaN(val) || val < 1) {
                this.value = 1;
            } else if (val > maxStock) {
                enforceStockLimit();
            }
        });
    }

    const addToCartForm = document.getElementById('add-to-cart-form');
    if (addToCartForm) {
        addToCartForm.addEventListener('submit', (e) => {
            e.preventDefault();
            const url = addToCartForm.action;
            const formData = new FormData(addToCartForm);
            const submitBtn = addToCartForm.querySelector('button[type="submit"]');

            if (submitBtn) submitBtn.disabled = true;

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
                    if (submitBtn) submitBtn.disabled = false;

                    if (data.success) {
                        // Cập nhật số lượng trên icon giỏ hàng header
                        document.querySelectorAll('.cart-badge').forEach(badge => {
                            badge.textContent = data.cart_length;
                            badge.classList.remove('d-none');
                        });

                        const toastType = data.adjusted ? 'warning' : 'success';
                        if (window.showToast) {
                            window.showToast(data.message || 'Đã thêm vào giỏ hàng thành công!', toastType);
                        }
                    } else {
                        // Cảnh báo lỗi tồn kho ngay trên trang, KHÔNG bao giờ dùng alert thô hay chuyển trang
                        const errorMsg = data.error || 'Không thể thêm sản phẩm vào giỏ hàng.';
                        if (window.showToast) {
                            window.showToast(errorMsg, 'warning');
                        }
                    }
                })
                .catch(err => {
                    if (submitBtn) submitBtn.disabled = false;
                    console.error('Lỗi thêm giỏ hàng:', err);
                    if (window.showToast) {
                        window.showToast('Có lỗi xảy ra khi kết nối máy chủ.', 'danger');
                    }
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

    // Interactive Star Rating for Review Form
    const starContainer = document.getElementById('star-rating-picker');
    const ratingInput = document.getElementById('selected-rating-val');
    const ratingLabel = document.getElementById('selected-rating-label');

    if (starContainer && ratingInput && ratingLabel) {
        const starItems = starContainer.querySelectorAll('.star-item');
        const labels = {
            1: 'Rất tệ (1 sao)',
            2: 'Chưa hài lòng (2 sao)',
            3: 'Bình thường (3 sao)',
            4: 'Hài lòng (4 sao)',
            5: 'Tuyệt vời (5 sao)'
        };

        function updateStars(val) {
            starItems.forEach(star => {
                const starVal = parseInt(star.getAttribute('data-value'));
                if (starVal <= val) {
                    star.classList.remove('bi-star');
                    star.classList.add('bi-star-fill', 'active');
                } else {
                    star.classList.remove('bi-star-fill', 'active');
                    star.classList.add('bi-star');
                }
            });
            if (labels[val]) {
                ratingLabel.textContent = labels[val];
            }
        }

        starItems.forEach(star => {
            star.addEventListener('mouseenter', () => {
                const val = parseInt(star.getAttribute('data-value'));
                updateStars(val);
            });

            star.addEventListener('click', () => {
                const val = parseInt(star.getAttribute('data-value'));
                ratingInput.value = val;
                updateStars(val);
            });
        });

        starContainer.addEventListener('mouseleave', () => {
            const currentVal = parseInt(ratingInput.value) || 5;
            updateStars(currentVal);
        });

        // Initialize with default value (5)
        updateStars(parseInt(ratingInput.value) || 5);
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
