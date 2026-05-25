function getRestaurantIdFromUrl() {
    const params = new URLSearchParams(window.location.search);
    const id = Number(params.get('id'));
    return Number.isInteger(id) && id > 0 ? id : 2;
}

function getMenuImage(index) {
    return `Картинки/карточка ${(index % 6) + 1}.jpg`;
}

function renderMenuCard(item, index) {
    const card = document.createElement('div');
    card.className = 'card';
    card.dataset.menuItemId = String(item.id);

    card.innerHTML = `
        <img src="${getMenuImage(index)}" alt="${item.name}" class="card-image">
        <div class="card-text">
            <h3 class="card-title">${item.name}</h3>
            <div class="card-ingredients">${item.description || ''}</div>
            <div class="card-buttons">
                <button type="button" class="btn-buy" data-menu-item-id="${item.id}">В корзину</button>
                <span class="card-price">${item.price} ₽</span>
            </div>
        </div>
    `;

    return card;
}

function renderRestaurantHeader(restaurant) {
    const title = document.querySelector('.restaurant-title-section .title');
    const rating = document.querySelector('.restaurant-title-section .rating');
    const meta = document.querySelector('.restaurant-title-section .meta-info');

    if (title) {
        title.textContent = restaurant.name;
    }

    if (rating) {
        rating.innerHTML = `★ ${restaurant.rating.toFixed(1)}`;
    }

    if (meta) {
        const category = restaurant.category ? ` • ${restaurant.category}` : '';
        meta.textContent = `От ${restaurant.min_price} ₽${category}`;
    }

    document.title = `Delivery Food — ${restaurant.name}`;
}

async function loadMenu() {
    const restaurantId = getRestaurantIdFromUrl();
    const cardsSection = document.querySelector('.cards');

    if (!cardsSection) {
        return;
    }

    cardsSection.innerHTML = '<p class="cards_loading">Загрузка меню...</p>';

    try {
        const data = await DeliveryAPI.getMenu(restaurantId);
        renderRestaurantHeader(data.restaurant);

        cardsSection.innerHTML = '';

        data.menu.forEach((item, index) => {
            cardsSection.appendChild(renderMenuCard(item, index));
        });

        cardsSection.addEventListener('click', (event) => {
            const button = event.target.closest('.btn-buy[data-menu-item-id]');

            if (!button) {
                return;
            }

            addToCart(Number(button.dataset.menuItemId));
        });
    } catch (error) {
        cardsSection.innerHTML = `<p class="cards_loading">${error.message}</p>`;
    }
}

document.addEventListener('DOMContentLoaded', loadMenu);
