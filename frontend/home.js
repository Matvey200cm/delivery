function renderRestaurantCard(restaurant) {
    const item = document.createElement('li');
    item.className = 'restouranse_item';

    const rating = restaurant.rating.toFixed(1);
    const deliveryTime = DeliveryAPI.getDeliveryTime(restaurant.name);
    const image = DeliveryAPI.getRestaurantImage(restaurant.name);
    const category = restaurant.category ? ` • ${restaurant.category}` : '';

    item.innerHTML = `
        <a class="restouranse_item_link" href="katalog.html?id=${restaurant.id}">
            <img src="${image}" alt="Блюдо из ресторана ${restaurant.name}">
            <div class="restouranse_item_header">
                <p class="restouranse_name">${restaurant.name}</p>
                <span class="delivery_time"><span>${deliveryTime} мин</span></span>
            </div>
            <div class="restouranse_meta">
                <span class="score">★ ${rating}</span>
                <span class="min_price">От ${restaurant.min_price} ₽</span>
            </div>
        </a>
    `;

    return item;
}

async function loadRestaurants() {
    const list = document.querySelector('.restouranse_list');

    if (!list) {
        return;
    }

    list.innerHTML = '<li class="restouranse_loading">Загрузка ресторанов...</li>';

    try {
        const restaurants = await DeliveryAPI.getRestaurants();
        list.innerHTML = '';

        if (!restaurants.length) {
            list.innerHTML = '<li class="restouranse_loading">Рестораны не найдены</li>';
            return;
        }

        restaurants.forEach((restaurant) => {
            list.appendChild(renderRestaurantCard(restaurant));
        });
    } catch (error) {
        list.innerHTML = `<li class="restouranse_loading">${error.message}</li>`;
    }
}

function initSearch() {
    const form = document.querySelector('.restouranse_search');
    const list = document.querySelector('.restouranse_list');

    if (!form || !list) {
        return;
    }

    form.addEventListener('submit', async (event) => {
        event.preventDefault();

        const input = form.querySelector('input');
        const query = input.value.trim();

        if (!query) {
            loadRestaurants();
            return;
        }

        list.innerHTML = '<li class="restouranse_loading">Поиск...</li>';

        try {
            const result = await DeliveryAPI.search(query);
            list.innerHTML = '';

            const hasResults = result.restaurants.length || result.menu_items.length;

            if (!hasResults) {
                list.innerHTML = '<li class="restouranse_loading">Ничего не найдено</li>';
                return;
            }

            result.restaurants.forEach((restaurant) => {
                list.appendChild(renderRestaurantCard(restaurant));
            });

            result.menu_items.forEach((item) => {
                const card = document.createElement('li');
                card.className = 'restouranse_item';
                card.innerHTML = `
                    <a class="restouranse_item_link" href="katalog.html?id=${item.restaurant_id}">
                        <img src="${DeliveryAPI.getRestaurantImage('Тануки')}" alt="${item.name}">
                        <div class="restouranse_item_header">
                            <p class="restouranse_name">${item.name}</p>
                            <span class="delivery_time"><span>Блюдо</span></span>
                        </div>
                        <div class="restouranse_meta">
                            <span class="score">★ 4.5</span>
                            <span class="min_price">${item.price} ₽</span>
                        </div>
                    </a>
                `;
                list.appendChild(card);
            });
        } catch (error) {
            list.innerHTML = `<li class="restouranse_loading">${error.message}</li>`;
        }
    });
}

document.addEventListener('DOMContentLoaded', () => {
    loadRestaurants();
    initSearch();
});
