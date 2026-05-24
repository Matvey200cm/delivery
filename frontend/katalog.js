// Инициализируем массив товаров в корзине
let cart = [];

// Работаем строго после построения DOM-дерева браузером
document.addEventListener('DOMContentLoaded', () => {
    
    // Получаем элементы интерфейса
    const cartBtn = document.getElementById('cart-btn');
    const cartCount = document.getElementById('cart-count');
    const cartModal = document.getElementById('cart-modal');
    const modalClose = document.getElementById('modal-close');
    const cartItemsList = document.getElementById('cart-items-list');
    const cartTotalPrice = document.getElementById('cart-total-price');

    // 1. Поиск карточек и отслеживание кликов добавления
    document.querySelectorAll('.card').forEach(card => {
        const buyBtn = card.querySelector('.btn-buy');
        const titleEl = card.querySelector('.card-title');
        const priceEl = card.querySelector('.card-price');

        if (buyBtn && titleEl && priceEl) {
            const title = titleEl.textContent.trim();
            const price = parseInt(priceEl.textContent);

            buyBtn.addEventListener('click', () => {
                const existingItem = cart.find(item => item.title === title);

                if (existingItem) {
                    existingItem.count += 1;
                } else {
                    cart.push({ title, price, count: 1 });
                }

                updateCartUI();
            });
        }
    });

    // 2. Функция обновления интерфейса корзины и счетчика
    function updateCartUI() {
        // Обновляем красный круг-индикатор над кнопкой
        const totalCount = cart.reduce((sum, item) => sum + item.count, 0);
        if (totalCount > 0) {
            cartCount.textContent = totalCount;
            cartCount.style.display = 'inline-block';
        } else {
            cartCount.style.display = 'none';
        }

        // Очищаем внутренности корзины для рендера свежих данных
        cartItemsList.innerHTML = '';

        if (cart.length === 0) {
            cartItemsList.innerHTML = '<div style="color: #8c8c8c; text-align: center; padding: 40px 0; font-size: 18px;">Корзина пуста</div>';
            cartTotalPrice.textContent = '0';
            return;
        }

        let totalSum = 0;
        
        // Отрисовка строк в точности по макету
        cart.forEach((item, index) => {
            totalSum += item.price * item.count;

            const row = document.createElement('div');
            row.className = 'cart-item-row';
            row.innerHTML = `
                <div class="cart-item-title">${item.title}</div>
                <div class="cart-item-price">${item.price} ₽</div>
                <div class="cart-counter-block">
                    <button onclick="changeCount(${index}, -1)" class="counter-btn">-</button>
                    <span class="counter-value">${item.count}</span>
                    <button onclick="changeCount(${index}, 1)" class="counter-btn">+</button>
                </div>
            `;
            cartItemsList.appendChild(row);
        });

        cartTotalPrice.textContent = totalSum;
    }

    // Делаем функцию рендера доступной во внешней глобальной области
    window.refreshCartUI = updateCartUI;

    // 3. Открытие и закрытие модального окна
    cartBtn.addEventListener('click', () => {
        cartModal.style.display = 'flex';
    });

    modalClose.addEventListener('click', () => {
        cartModal.style.display = 'none';
    });

    // Закрытие по клику за пределами белого окна
    cartModal.addEventListener('click', (event) => {
        if (event.target === cartModal) {
            cartModal.style.display = 'none';
        }
    });
});

// Глобальная функция инкремента/декремента (доступна для инлайнового onclick в строках)
window.changeCount = function(index, direction) {
    if (!cart[index]) return;

    cart[index].count += direction;

    // Если количество упало до 0 — удаляем блюдо из корзины
    if (cart[index].count <= 0) {
        cart.splice(index, 1);
    }

    // Вызываем перерисовку структуры
    if (typeof window.refreshCartUI === 'function') {
        window.refreshCartUI();
    }
};
