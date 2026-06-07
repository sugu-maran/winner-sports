// Mobile menu toggle
function toggleMenu() {
    const menu = document.getElementById('mobileMenu');
    menu.classList.toggle('open');
}

// Update cart count on page load
document.addEventListener('DOMContentLoaded', function () {
    fetch('/cart')
        .then(r => r.text())
        .then(html => {
            const parser = new DOMParser();
            const doc = parser.parseFromString(html, 'text/html');
            const items = doc.querySelectorAll('.cart-item');
            const countEl = document.getElementById('cart-count');
            if (countEl) countEl.textContent = items.length;
        })
        .catch(() => {});
});