const CART_STORAGE_KEY = 'delivery-cart';

let cart = loadCart();

function loadCart() {
    try {
        const saved = localStorage.getItem(CART_STORAGE_KEY);
        return saved ? JSON.parse(saved) : [];
    } catch {
        return [];
    }
}

function saveCart() {
    localStorage.setItem(CART_STORAGE_KEY, JSON.stringify(cart));
}

function updateCartUI() {
    const cartCount = document.getElementById('cart-count');
    const cartItemsList = document.getElementById('cart-items-list');
    const cartTotalPrice = document.getElementById('cart-total-price');

    if (!cartItemsList || !cartTotalPrice) {
        return;
    }

    const totalCount = cart.reduce((sum, item) => sum + item.count, 0);
    if (cartCount) {
        if (totalCount > 0) {
            cartCount.textContent = totalCount;
            cartCount.style.display = 'inline-block';
        } else {
            cartCount.style.display = 'none';
        }
    }

    cartItemsList.innerHTML = '';

    if (cart.length === 0) {
        cartItemsList.innerHTML = '<div style="color: #8c8c8c; text-align: center; padding: 40px 0; font-size: 18px;">Корзина пуста</div>';
        cartTotalPrice.textContent = '0';
        return;
    }

    let totalSum = 0;

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

window.refreshCartUI = updateCartUI;

window.changeCount = function(index, direction) {
    if (!cart[index]) {
        return;
    }

    cart[index].count += direction;

    if (cart[index].count <= 0) {
        cart.splice(index, 1);
    }

    saveCart();
    updateCartUI();
};

window.addToCart = function(title, price) {
    const existingItem = cart.find(item => item.title === title);

    if (existingItem) {
        existingItem.count += 1;
    } else {
        cart.push({ title, price, count: 1 });
    }

    saveCart();
    updateCartUI();
};

function initCartModal() {
    const cartBtn = document.getElementById('cart-btn');
    const cartModal = document.getElementById('cart-modal');
    const modalClose = document.getElementById('modal-close');

    if (!cartModal) {
        return;
    }

    if (cartBtn) {
        cartBtn.addEventListener('click', () => {
            cartModal.style.display = 'flex';
            updateCartUI();
        });
    }

    if (modalClose) {
        modalClose.addEventListener('click', () => {
            cartModal.style.display = 'none';
        });
    }

    cartModal.addEventListener('click', (event) => {
        if (event.target === cartModal) {
            cartModal.style.display = 'none';
        }
    });

    updateCartUI();
}

document.addEventListener('DOMContentLoaded', initCartModal);
