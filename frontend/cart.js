let cart = { items: [], total: 0 };

async function syncCart() {
    try {
        cart = await DeliveryAPI.getCart();
        updateCartUI();
    } catch (error) {
        console.error(error);
    }
}

function updateCartUI() {
    const cartCount = document.getElementById('cart-count');
    const cartItemsList = document.getElementById('cart-items-list');
    const cartTotalPrice = document.getElementById('cart-total-price');

    if (!cartItemsList || !cartTotalPrice) {
        return;
    }

    const items = cart.items || [];
    const totalCount = items.reduce((sum, item) => sum + item.quantity, 0);

    if (cartCount) {
        if (totalCount > 0) {
            cartCount.textContent = totalCount;
            cartCount.style.display = 'inline-block';
        } else {
            cartCount.style.display = 'none';
        }
    }

    cartItemsList.innerHTML = '';

    if (items.length === 0) {
        cartItemsList.innerHTML = '<div style="color: #8c8c8c; text-align: center; padding: 40px 0; font-size: 18px;">Корзина пуста</div>';
        cartTotalPrice.textContent = '0';
        return;
    }

    items.forEach((item) => {
        const row = document.createElement('div');
        row.className = 'cart-item-row';
        row.innerHTML = `
            <div class="cart-item-title">${item.name}</div>
            <div class="cart-item-price">${item.price} ₽</div>
            <div class="cart-counter-block">
                <button type="button" data-action="decrease" data-menu-item-id="${item.menu_item_id}" class="counter-btn">-</button>
                <span class="counter-value">${item.quantity}</span>
                <button type="button" data-action="increase" data-menu-item-id="${item.menu_item_id}" class="counter-btn">+</button>
            </div>
        `;
        cartItemsList.appendChild(row);
    });

    cartTotalPrice.textContent = cart.total || 0;
}

window.refreshCartUI = syncCart;

async function changeCount(menuItemId, direction) {
    try {
        if (direction > 0) {
            await DeliveryAPI.addToCart(menuItemId, 1);
        } else {
            await DeliveryAPI.removeFromCart(menuItemId);
        }

        await syncCart();
    } catch (error) {
        alert(error.message);
    }
}

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

window.addToCart = async function(menuItemId) {
    try {
        await DeliveryAPI.addToCart(menuItemId, 1);
        await syncCart();
        showCartToast();
    } catch (error) {
        alert(error.message);
    }
};

function getDeliveryAddress() {
    const input = document.querySelector('.delivery_address input, .search-input');
    return input ? input.value.trim() : '';
}

async function checkoutOrder() {
    const address = getDeliveryAddress();

    if (!address) {
        alert('Укажите адрес доставки');
        return;
    }

    if (!cart.items || cart.items.length === 0) {
        alert('Корзина пуста');
        return;
    }

    const user = typeof getStoredUser === 'function' ? getStoredUser() : null;

    try {
        const result = await DeliveryAPI.checkout(address, user ? user.id : null);
        alert(`${result.message}\nНомер заказа: ${result.order_id}`);
        await syncCart();

        const cartModal = document.getElementById('cart-modal');
        if (cartModal) {
            cartModal.style.display = 'none';
        }
    } catch (error) {
        alert(error.message);
    }
}

function initCartModal() {
    const cartBtn = document.getElementById('cart-btn');
    const cartModal = document.getElementById('cart-modal');
    const modalClose = document.getElementById('modal-close');
    const checkoutBtn = document.querySelector('.btn-checkout');

    if (!cartModal) {
        return;
    }

    if (cartBtn) {
        cartBtn.addEventListener('click', async () => {
            cartModal.style.display = 'flex';
            await syncCart();
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

    if (checkoutBtn) {
        checkoutBtn.addEventListener('click', checkoutOrder);
    }

    document.getElementById('cart-items-list')?.addEventListener('click', (event) => {
        const button = event.target.closest('[data-menu-item-id]');

        if (!button) {
            return;
        }

        const menuItemId = Number(button.dataset.menuItemId);
        const direction = button.dataset.action === 'increase' ? 1 : -1;
        changeCount(menuItemId, direction);
    });

    syncCart();
}

document.addEventListener('DOMContentLoaded', initCartModal);
