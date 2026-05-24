
    // Хранилище для товаров в корзине
    let cart = [];

    // Элементы интерфейса
    const cartBtn = document.getElementById('cart-btn');
    const cartCount = document.getElementById('cart-count');
    const cartModal = document.getElementById('cart-modal');
    const modalClose = document.getElementById('modal-close');
    const cartItemsList = document.getElementById('cart-items-list');
    const cartTotalPrice = document.getElementById('cart-total-price');

    // 1. Сбор данных из карточек и добавление в корзину
    document.querySelectorAll('.card').forEach(card => {
        const buyBtn = card.querySelector('.btn-buy');
        const title = card.querySelector('.card-title').textContent;
        const price = parseInt(card.querySelector('.card-price').textContent);

        buyBtn.addEventListener('click', () => {
            // Проверяем, есть ли уже такой товар в корзине
            const existingItem = cart.find(item => item.title === title);

            if (existingItem) {
                existingItem.count += 1;
            } else {
                cart.push({ title, price, count: 1 });
            }

            updateCartUI();
        });
    });

    // 2. Обновление счетчиков и интерфейса корзины
    function updateCartUI() {
        // Обновление красного счетчика на кнопке в шапке
        const totalCount = cart.reduce((sum, item) => sum + item.count, 0);
        if (totalCount > 0) {
            cartCount.textContent = totalCount;
            cartCount.style.display = 'inline-block';
        } else {
            cartCount.style.display = 'none';
        }

        // Очищаем старый список в модальном окне
        cartItemsList.innerHTML = '';

        if (cart.length === 0) {
            cartItemsList.innerHTML = '<div style="color: #8c8c8c; text-align: center; padding: 20px;">Корзина пуста</div>';
            cartTotalPrice.textContent = '0';
            return;
        }

        // Рендерим актуальные строки товаров
        let totalSum = 0;
        cart.forEach((item, index) => {
            totalSum += item.price * item.count;

            const row = document.createElement('div');
            row.style.cssText = 'display: flex; justify-content: space-between; align-items: center; padding: 10px 0; border-bottom: 1px solid #f0f0f0;';
            row.innerHTML = `
                <div style="font-size: 16px; flex-grow: 1;">${item.title}</div>
                <div style="font-weight: 700; margin-right: 30px;">${item.price} ₽</div>
                <div style="display: flex; align-items: center; gap: 10px;">
                    <button onclick="changeCount(${index}, -1)" style="width: 24px; height: 24px; background: white; border: 1px solid #d9d9d9; cursor: pointer;">-</button>
                    <span>${item.count}</span>
                    <button onclick="changeCount(${index}, 1)" style="width: 24px; height: 24px; background: white; border: 1px solid #d9d9d9; cursor: pointer;">+</button>
                </div>
            `;
            cartItemsList.appendChild(row);
        });

        cartTotalPrice.textContent = totalSum;
    }

    // 3. Изменение количества товара (+ / -) внутри корзины
    window.changeCount = function(index, direction) {
        cart[index].count += direction;

        // Если количество стало 0 — удаляем товар
        if (cart[index].count <= 0) {
            cart.splice(index, 1);
        }

        updateCartUI();
    };

    // 4. Открытие и закрытие модального окна
    cartBtn.addEventListener('click', () => {
        cartModal.style.display = 'flex';
    });

    modalClose.addEventListener('click', () => {
        cartModal.style.display = 'none';
    });

    // Закрытие окна при клике на темную область вокруг него
    cartModal.addEventListener('click', (event) => {
        if (event.target === cartModal) {
            cartModal.style.display = 'none';
        }
    });
