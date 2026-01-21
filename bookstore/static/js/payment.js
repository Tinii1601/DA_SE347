function copyToClipboard(text) {
    navigator.clipboard.writeText(text).then(function () {
        // Optional: Show a tooltip or toast
        alert('Đã sao chép: ' + text);
    }, function (err) {
        console.error('Could not copy text: ', err);
    });
}

document.addEventListener('DOMContentLoaded', function () {
    // Countdown Timer


    // Poll for payment status
    const orderIdElement = document.getElementById('order-id-data');
    if (orderIdElement) {
        const disablePolling = orderIdElement.dataset.disablePolling === '1';
        if (disablePolling) return;
        const orderId = orderIdElement.dataset.orderId;
        console.log("Start polling for Order ID:", orderId);

        const pollInterval = setInterval(() => {
            fetch(`/payment/check-status/${orderId}/`)
                .then(response => response.json())
                .then(data => {
                    console.log("Payment status:", data.status);
                    if (data.status === 'PAID') {
                        clearInterval(pollInterval);

                        // Show success modal
                        document.getElementById('successModal').style.display = 'flex';

                        // Redirect after a short delay
                        setTimeout(() => {
                            window.location.href = `/orders/success/${orderId}/`;
                        }, 2000);
                    }
                })
                .catch(err => console.error('Error checking status:', err));
        }, 3000); // Check every 3 seconds
    }
});

function closeModal(modalId) {
    document.getElementById(modalId).style.display = 'none';
}

function startTimer(duration, display) {



    // Countdown Timer logic removed
}