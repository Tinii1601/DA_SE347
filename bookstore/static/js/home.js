function scrollSlider(id, direction) {
    const container = document.getElementById(id);
    if (container) {
        const scrollAmount = container.clientWidth * 0.8;
        container.scrollBy({
            left: direction * scrollAmount,
            behavior: 'smooth'
        });
    }
}
