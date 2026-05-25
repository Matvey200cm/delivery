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

let toastIdCounter = 0;
const TOAST_LIFETIME_MS = 3000;
const MAX_VISIBLE_TOASTS = 5;

function initCartToastStack() {
    let stack = document.getElementById('cart-toast-stack');

    if (!stack) {
        stack = document.createElement('div');
        stack.id = 'cart-toast-stack';
        stack.className = 'cart-toast-stack';
        stack.setAttribute('role', 'status');
        stack.setAttribute('aria-live', 'polite');
        document.body.appendChild(stack);
    }

    return stack;
}

function createToastElement() {
    const toast = document.createElement('div');
    toast.className = 'cart-toast';
    toast.dataset.toastId = String(++toastIdCounter);
    toast.innerHTML = `
        <span class="cart-toast_icon" aria-hidden="true"></span>
        <span class="cart-toast_text">Товар добавлен в корзину</span>
    `;
    return toast;
}

function animateToastsDown(existingToasts, previousRects) {
    existingToasts.forEach((toast, index) => {
        const previousTop = previousRects[index].top;
        const currentTop = toast.getBoundingClientRect().top;
        const offset = previousTop - currentTop;

        if (Math.abs(offset) < 1) {
            return;
        }

        toast.style.transform = `translateY(${offset}px)`;
        toast.style.transition = 'none';

        requestAnimationFrame(() => {
            toast.style.transition = 'transform 0.35s ease';
            toast.style.transform = '';
        });
    });
}

function hideToast(stack, toast) {
    if (!toast.isConnected) {
        return;
    }

    toast.classList.remove('cart-toast_enter');
    toast.classList.add('cart-toast_exit');

    toast.addEventListener('animationend', () => {
        toast.remove();

        if (stack.children.length === 0) {
            stack.remove();
        }
    }, { once: true });
}

function showCartToast() {
    const stack = initCartToastStack();
    const existingToasts = [...stack.querySelectorAll('.cart-toast:not(.cart-toast_exit)')];
    const previousRects = existingToasts.map(toast => toast.getBoundingClientRect());

    const toast = createToastElement();
    stack.prepend(toast);

    requestAnimationFrame(() => {
        toast.classList.add('cart-toast_enter');
        animateToastsDown(existingToasts, previousRects);
    });

    while (stack.querySelectorAll('.cart-toast:not(.cart-toast_exit)').length > MAX_VISIBLE_TOASTS) {
        const oldest = stack.querySelector('.cart-toast:not(.cart-toast_exit):last-child');
        hideToast(stack, oldest);
    }

    const toastId = toast.dataset.toastId;

    setTimeout(() => {
        const toastEl = stack.querySelector(`[data-toast-id="${toastId}"]`);
        if (toastEl) {
            hideToast(stack, toastEl);
        }
    }, TOAST_LIFETIME_MS);
}

window.addToCart = function(title, price) {
    const existingItem = cart.find(item => item.title === title);

    if (existingItem) {
        existingItem.count += 1;
    } else {
        cart.push({ title, price, count: 1 });
    }

    saveCart();
    updateCartUI();
    showCartToast();
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
