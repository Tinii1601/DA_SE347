document.addEventListener('DOMContentLoaded', function () {
    const citySelect = document.querySelector('select[name="city"]');
    const districtSelect = document.querySelector('select[name="district"]');
    const wardSelect = document.querySelector('select[name="ward"]');

    // Load Provinces
    fetch('https://provinces.open-api.vn/api/?depth=1')
        .then(response => response.json())
        .then(data => {
            data.forEach(item => {
                const option = new Option(item.name, item.name);
                option.dataset.code = item.code;
                citySelect.add(option);
            });

            // Pre-select if value exists
            if (citySelect.dataset.default) {
                citySelect.value = citySelect.dataset.default;
                // Trigger change only if value was set successfully (exists in options)
                if (citySelect.value) {
                    citySelect.dispatchEvent(new Event('change'));
                }
            }
        })
        .catch(error => console.error('Error loading provinces:', error));

    // City Change
    citySelect.addEventListener('change', function () {
        districtSelect.length = 1; // Clear
        wardSelect.length = 1; // Clear
        districtSelect.disabled = true;
        wardSelect.disabled = true;

        const selectedOption = this.options[this.selectedIndex];
        const code = selectedOption.dataset.code;

        if (code) {
            fetch(`https://provinces.open-api.vn/api/p/${code}?depth=2`)
                .then(response => response.json())
                .then(data => {
                    districtSelect.disabled = false;
                    data.districts.forEach(item => {
                        const option = new Option(item.name, item.name);
                        option.dataset.code = item.code;
                        districtSelect.add(option);
                    });

                    // Pre-select district
                    if (districtSelect.dataset.default && !districtSelect.dataset.loaded) {
                        districtSelect.value = districtSelect.dataset.default;
                        if (districtSelect.value) {
                            districtSelect.dataset.loaded = true;
                            districtSelect.dispatchEvent(new Event('change'));
                        }
                    }
                })
                .catch(error => console.error('Error loading districts:', error));
        }
    });

    // District Change
    districtSelect.addEventListener('change', function () {
        wardSelect.length = 1;
        wardSelect.disabled = true;

        const selectedOption = this.options[this.selectedIndex];
        const code = selectedOption.dataset.code;

        if (code) {
            fetch(`https://provinces.open-api.vn/api/d/${code}?depth=2`)
                .then(response => response.json())
                .then(data => {
                    wardSelect.disabled = false;
                    data.wards.forEach(item => {
                        const option = new Option(item.name, item.name);
                        wardSelect.add(option);
                    });

                    // Pre-select ward
                    if (wardSelect.dataset.default && !wardSelect.dataset.loaded) {
                        wardSelect.value = wardSelect.dataset.default;
                        if (wardSelect.value) {
                            wardSelect.dataset.loaded = true;
                        }
                    }
                })
                .catch(error => console.error('Error loading wards:', error));
        }
    });

    // Coupon Application
    const applyCouponBtn = document.getElementById('apply-coupon-btn');
    const couponInput = document.getElementById('coupon-input');
    const couponMessage = document.getElementById('coupon-message');
    const discountAmount = document.getElementById('discount-amount');
    const totalAmount = document.getElementById('total-amount');

    if (applyCouponBtn) {
        applyCouponBtn.addEventListener('click', function (e) {
            e.preventDefault();
            const code = couponInput.value.trim();
            if (!code) {
                couponMessage.innerHTML = '<span class="text-danger">Vui lòng nhập mã giảm giá</span>';
                return;
            }

            // Show loading state
            const originalText = applyCouponBtn.textContent;
            applyCouponBtn.textContent = 'Đang xử lý...';
            applyCouponBtn.disabled = true;

            const csrfToken = document.querySelector('[name=csrfmiddlewaretoken]').value;

            fetch('/orders/apply-coupon/', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': csrfToken
                },
                body: JSON.stringify({ code: code })
            })
                .then(response => response.json())
                .then(data => {
                    if (data.success) {
                        couponMessage.innerHTML = `<span class="text-success">${data.message}</span>`;
                        discountAmount.textContent = data.discount.toLocaleString('vi-VN') + ' VNĐ';
                        totalAmount.textContent = data.total.toLocaleString('vi-VN') + ' VNĐ';
                    } else {
                        couponMessage.innerHTML = `<span class="text-danger">${data.message}</span>`;
                        discountAmount.textContent = '0 VNĐ';
                    }
                })
                .catch(error => {
                    console.error('Error:', error);
                    couponMessage.innerHTML = '<span class="text-danger">Có lỗi xảy ra. Vui lòng thử lại.</span>';
                })
                .finally(() => {
                    applyCouponBtn.textContent = originalText;
                    applyCouponBtn.disabled = false;
                });
        });
    }

    if (couponInput) {
        couponInput.addEventListener('keypress', function (e) {
            if (e.key === 'Enter') {
                e.preventDefault();
                if (applyCouponBtn) {
                    applyCouponBtn.click();
                }
            }
        });
    }
});