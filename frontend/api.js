const API_BASE = window.location.origin;

const RESTAURANT_IMAGES = {
    'Пицца плюс': 'pizzaplus.png',
    'Тануки': 'tanuki.png',
    'FoodBand': 'foodband.png',
    'Жадина-пицца': 'zhadina.png',
    'Точка еды': 'tochka.png',
    'PizzaBurger': 'pizzaburger.png',
};

const DELIVERY_TIMES = {
    'Пицца плюс': 50,
    'Тануки': 60,
    'FoodBand': 40,
    'Жадина-пицца': 35,
    'Точка еды': 45,
    'PizzaBurger': 65,
};

function getRestaurantImage(name) {
    return `Картинки/${RESTAURANT_IMAGES[name] || 'tanuki.png'}`;
}

function getDeliveryTime(name) {
    return DELIVERY_TIMES[name] || 45;
}

function getSessionId() {
    let sessionId = sessionStorage.getItem('delivery-session-id');

    if (!sessionId) {
        sessionId = crypto.randomUUID();
        sessionStorage.setItem('delivery-session-id', sessionId);
    }

    return sessionId;
}

async function apiFetch(path, options = {}) {
    const response = await fetch(`${API_BASE}${path}`, {
        headers: {
            'Content-Type': 'application/json',
            ...(options.headers || {}),
        },
        ...options,
    });

    if (!response.ok) {
        let message = 'Ошибка сервера';

        try {
            const data = await response.json();
            const detail = data.detail;

            if (Array.isArray(detail)) {
                message = detail.map((item) => item.msg || String(item)).join(', ');
            } else if (typeof detail === 'string') {
                message = detail;
            }
        } catch {
            message = response.statusText || message;
        }

        throw new Error(message);
    }

    if (response.status === 204) {
        return null;
    }

    return response.json();
}

window.DeliveryAPI = {
    getRestaurants() {
        return apiFetch('/api/restaurants');
    },

    search(query) {
        return apiFetch(`/api/search?query=${encodeURIComponent(query)}`);
    },

    getMenu(restaurantId) {
        return apiFetch(`/api/restaurants/${restaurantId}/menu`);
    },

    getCart() {
        return apiFetch(`/api/cart/${getSessionId()}`);
    },

    addToCart(menuItemId, quantity = 1) {
        return apiFetch(
            `/api/cart/${getSessionId()}/add/${menuItemId}?quantity=${quantity}`,
            { method: 'POST' }
        );
    },

    removeFromCart(menuItemId) {
        return apiFetch(
            `/api/cart/${getSessionId()}/remove/${menuItemId}`,
            { method: 'DELETE' }
        );
    },

    checkout(deliveryAddress, userId = null) {
        return apiFetch(`/api/cart/${getSessionId()}/checkout`, {
            method: 'POST',
            body: JSON.stringify({
                delivery_address: deliveryAddress,
                user_id: userId,
            }),
        });
    },

    register(userData) {
        return apiFetch('/api/auth/register', {
            method: 'POST',
            body: JSON.stringify(userData),
        });
    },

    login(email) {
        return apiFetch('/api/auth/login', {
            method: 'POST',
            body: JSON.stringify({ email }),
        });
    },

    getRestaurantImage,
    getDeliveryTime,
    getSessionId,
};
