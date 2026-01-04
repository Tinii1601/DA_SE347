document.addEventListener('DOMContentLoaded', function () {
    const forms = document.querySelectorAll('.add-to-cart-form');
    forms.forEach(form => {
        form.addEventListener('submit', function (e) {
            e.preventDefault();
            const url = this.action;
            const formData = new FormData(this);

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
                        const cartIcon = document.querySelector('.cart-icon');
                        let badge = cartIcon.querySelector('.cart-badge');
                        if (!badge) {
                            badge = document.createElement('span');
                            badge.className = 'cart-badge';
                            cartIcon.appendChild(badge);
                        }
                        badge.textContent = data.cart_length;
                    }
                })
                .catch(error => console.error('Error:', error));
        });
    });
});