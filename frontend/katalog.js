document.addEventListener('DOMContentLoaded', () => {
    document.querySelectorAll('.card').forEach(card => {
        const buyBtn = card.querySelector('.btn-buy');
        const titleEl = card.querySelector('.card-title');
        const priceEl = card.querySelector('.card-price');

        if (buyBtn && titleEl && priceEl) {
            const title = titleEl.textContent.trim();
            const price = parseInt(priceEl.textContent, 10);

            buyBtn.addEventListener('click', () => {
                addToCart(title, price);
            });
        }
    });
});
