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
    let duration = 15 * 60; // 15 minutes
    const display = document.querySelector('#countdown');

    if (display) {
        startTimer(duration, display);
    }

    // Poll for payment status
    const orderIdElement = document.getElementById('order-id-data');
    if (orderIdElement) {
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
    let timer = duration, minutes, seconds;
    setInterval(function () {
        minutes = parseInt(timer / 60, 10);
        seconds = parseInt(timer % 60, 10);

        minutes = minutes < 10 ? "0" + minutes : minutes;
        seconds = seconds < 10 ? "0" + seconds : seconds;

        display.textContent = minutes + ":" + seconds;

        if (--timer < 0) {
            timer = 0;
            // Handle timeout (e.g., disable payment or refresh)
        }
    }, 1000);
}