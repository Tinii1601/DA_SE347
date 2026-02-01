window.closeModal = function closeModal() {
    const modal = document.getElementById('resetModal');
    if (modal) {
        modal.style.display = 'none';
    }
    const backdrop = document.querySelector('.modal-backdrop');
    if (backdrop) {
        backdrop.remove();
    }
};
