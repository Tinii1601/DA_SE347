(function () {
    const dataEl = document.getElementById('revenue-data');
    if (!dataEl || !dataEl.textContent) return;

    let data;
    try {
        data = JSON.parse(dataEl.textContent);
    } catch (err) {
        return;
    }

    function renderChart(canvasId, labels, values, label) {
        const ctx = document.getElementById(canvasId);
        if (!ctx || !window.Chart) return;
        new Chart(ctx, {
            type: 'line',
            data: {
                labels: labels,
                datasets: [{
                    label: label,
                    data: values,
                    borderColor: '#22c55e',
                    backgroundColor: 'rgba(34, 197, 94, 0.15)',
                    tension: 0.3,
                    fill: true,
                    pointRadius: 3,
                    pointHoverRadius: 5,
                }]
            },
            options: {
                plugins: { legend: { display: false } },
                scales: {
                    y: {
                        ticks: {
                            callback: function (value) {
                                return new Intl.NumberFormat('vi-VN').format(value) + ' đ';
                            }
                        }
                    }
                }
            }
        });
    }

    renderChart('revenueDailyChart', data.daily.labels, data.daily.data, 'Doanh thu ngày');
    renderChart('revenueWeeklyChart', data.weekly.labels, data.weekly.data, 'Doanh thu tuần');
    renderChart('revenueMonthlyChart', data.monthly.labels, data.monthly.data, 'Doanh thu tháng');
})();
