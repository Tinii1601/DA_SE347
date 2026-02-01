document.addEventListener('DOMContentLoaded', () => {
    const page = document.getElementById('cart-page');
    if (!page) return;

    const updateUrl = page.dataset.updateUrl;

    function getCookie(name) {
        let cookieValue = null;
        if (document.cookie && document.cookie !== '') {
            const cookies = document.cookie.split(';');
            for (let i = 0; i < cookies.length; i++) {
                const cookie = cookies[i].trim();
                if (cookie.substring(0, name.length + 1) === (name + '=')) {
                    cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                    break;
                }
            }
        }
        return cookieValue;
    }

    function formatVND(value) {
        if (value === null || value === undefined) return '';
        return new Intl.NumberFormat('vi-VN', { style: 'currency', currency: 'VND' }).format(value);
    }

    async function updateSelection(formData) {
        if (!updateUrl) return;
        const response = await fetch(updateUrl, {
            method: 'POST',
            headers: {
                'X-Requested-With': 'XMLHttpRequest',
                'X-CSRFToken': getCookie('csrftoken')
            },
            body: formData
        });

        if (response.ok) {
            const data = await response.json();
            const selectedTotalEl = document.getElementById('selected-total-amount');
            const cartTotalEl = document.getElementById('cart-total-amount');
            if (selectedTotalEl) selectedTotalEl.textContent = formatVND(data.selected_total);
            if (cartTotalEl) cartTotalEl.textContent = formatVND(data.cart_total);
        }
    }

    const selectAll = document.getElementById('select-all');
    const itemCheckboxes = document.querySelectorAll('.cart-item-checkbox');

    function syncSelectAll() {
        if (!selectAll) return;
        const checkedCount = Array.from(itemCheckboxes).filter(cb => cb.checked).length;
        if (checkedCount === 0) {
            selectAll.checked = false;
            selectAll.indeterminate = false;
        } else if (checkedCount === itemCheckboxes.length) {
            selectAll.checked = true;
            selectAll.indeterminate = false;
        } else {
            selectAll.checked = false;
            selectAll.indeterminate = true;
        }
    }

    if (selectAll) {
        selectAll.addEventListener('change', () => {
            itemCheckboxes.forEach(cb => { cb.checked = selectAll.checked; });
            const formData = new FormData();
            formData.append('csrfmiddlewaretoken', getCookie('csrftoken'));
            formData.append('select_all', selectAll && selectAll.checked ? '1' : '0');
            updateSelection(formData);
        });
    }

    itemCheckboxes.forEach(cb => {
        cb.addEventListener('change', () => {
            syncSelectAll();
            const formData = new FormData();
            formData.append('csrfmiddlewaretoken', getCookie('csrftoken'));
            itemCheckboxes.forEach(itemCb => {
                if (itemCb.checked) {
                    formData.append('selected_items', itemCb.value);
                }
            });
            updateSelection(formData);
        });
    });

    syncSelectAll();
});
