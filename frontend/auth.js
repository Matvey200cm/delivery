const AUTH_USER_KEY = 'delivery-user';

function getAuthModal() {
    let modal = document.getElementById('auth-modal');

    if (!modal) {
        modal = document.createElement('div');
        modal.id = 'auth-modal';
        modal.className = 'modal-overlay auth-modal';
        modal.innerHTML = `
            <div class="modal-container auth-container">
                <div class="modal-header">
                    <h2 class="modal-title" id="auth-modal-title">Вход</h2>
                    <button type="button" id="auth-modal-close" class="modal-close-btn">&times;</button>
                </div>
                <div class="auth-tabs">
                    <button type="button" class="auth-tab auth-tab_active" data-tab="login">Вход</button>
                    <button type="button" class="auth-tab" data-tab="register">Регистрация</button>
                </div>
                <form id="auth-form-login" class="auth-form">
                    <div class="auth-field">
                        <label class="auth-label" for="login-email">Email</label>
                        <input class="auth-input" type="email" id="login-email" placeholder="example@mail.ru" required>
                    </div>
                    <p class="auth-error" id="auth-error-login"></p>
                    <button type="submit" class="auth-submit">Войти</button>
                </form>
                <form id="auth-form-register" class="auth-form auth-form_hidden">
                    <div class="auth-field">
                        <label class="auth-label" for="register-email">Email</label>
                        <input class="auth-input" type="email" id="register-email" placeholder="example@mail.ru" required>
                    </div>
                    <div class="auth-field">
                        <label class="auth-label" for="register-name">Имя</label>
                        <input class="auth-input" type="text" id="register-name" placeholder="Ваше имя" required>
                    </div>
                    <div class="auth-field">
                        <label class="auth-label" for="register-address">Адрес доставки</label>
                        <input class="auth-input" type="text" id="register-address" placeholder="Улица, дом, квартира" required>
                    </div>
                    <p class="auth-error" id="auth-error-register"></p>
                    <button type="submit" class="auth-submit">Зарегистрироваться</button>
                </form>
            </div>
        `;
        document.body.appendChild(modal);
        bindAuthModalEvents(modal);
    }

    return modal;
}

function setAuthTab(tabName) {
    const loginForm = document.getElementById('auth-form-login');
    const registerForm = document.getElementById('auth-form-register');
    const tabs = document.querySelectorAll('.auth-tab');
    const title = document.getElementById('auth-modal-title');

    tabs.forEach((tab) => {
        tab.classList.toggle('auth-tab_active', tab.dataset.tab === tabName);
    });

    if (tabName === 'login') {
        loginForm.classList.remove('auth-form_hidden');
        registerForm.classList.add('auth-form_hidden');
        title.textContent = 'Вход';
    } else {
        loginForm.classList.add('auth-form_hidden');
        registerForm.classList.remove('auth-form_hidden');
        title.textContent = 'Регистрация';
    }

    document.getElementById('auth-error-login').textContent = '';
    document.getElementById('auth-error-register').textContent = '';
}

function openAuthModal(tab = 'login') {
    const modal = getAuthModal();
    setAuthTab(tab);
    modal.style.display = 'flex';
}

function closeAuthModal() {
    const modal = document.getElementById('auth-modal');
    if (modal) {
        modal.style.display = 'none';
    }
}

function saveUser(user) {
    localStorage.setItem(AUTH_USER_KEY, JSON.stringify(user));
    updateAuthUI();
    fillDeliveryAddress(user.delivery_address);
}

function getStoredUser() {
    try {
        const raw = localStorage.getItem(AUTH_USER_KEY);
        return raw ? JSON.parse(raw) : null;
    } catch {
        return null;
    }
}

function clearUser() {
    localStorage.removeItem(AUTH_USER_KEY);
    updateAuthUI();
}

function fillDeliveryAddress(address) {
    if (!address) {
        return;
    }

    document.querySelectorAll('.delivery_address input, .search-input, #delivery-address').forEach((input) => {
        input.value = address;
    });
}

function updateAuthUI() {
    const user = getStoredUser();
    const authButtons = document.querySelectorAll('.auth-open');

    authButtons.forEach((button) => {
        if (user) {
            button.classList.add('auth-open_logged-in');
            button.innerHTML = `
                <img src="Картинки/login2.png" alt="Профиль ${user.name}" class="auth-profile-img">
            `;
            button.title = `${user.name} — нажмите, чтобы выйти`;
            button.dataset.loggedIn = 'true';
        } else {
            button.classList.remove('auth-open_logged-in');
            button.innerHTML = '<span>Войти</span>';
            button.title = '';
            button.dataset.loggedIn = 'false';
        }
    });
}

async function handleLogin(event) {
    event.preventDefault();

    const email = document.getElementById('login-email').value.trim();
    const errorEl = document.getElementById('auth-error-login');

    try {
        const user = await DeliveryAPI.login(email);
        saveUser(user);
        closeAuthModal();
    } catch (error) {
        errorEl.textContent = error.message;
    }
}

async function handleRegister(event) {
    event.preventDefault();

    const email = document.getElementById('register-email').value.trim();
    const name = document.getElementById('register-name').value.trim();
    const deliveryAddress = document.getElementById('register-address').value.trim();
    const errorEl = document.getElementById('auth-error-register');

    try {
        const user = await DeliveryAPI.register({ email, name, delivery_address: deliveryAddress });
        saveUser(user);
        closeAuthModal();
    } catch (error) {
        errorEl.textContent = error.message;
    }
}

function bindAuthModalEvents(modal) {
    document.getElementById('auth-modal-close').addEventListener('click', closeAuthModal);

    modal.addEventListener('click', (event) => {
        if (event.target === modal) {
            closeAuthModal();
        }
    });

    document.querySelectorAll('.auth-tab').forEach((tab) => {
        tab.addEventListener('click', () => setAuthTab(tab.dataset.tab));
    });

    document.getElementById('auth-form-login').addEventListener('submit', handleLogin);
    document.getElementById('auth-form-register').addEventListener('submit', handleRegister);
}

function initAuthButtons() {
    document.querySelectorAll('.auth-open').forEach((button) => {
        button.addEventListener('click', (event) => {
            event.preventDefault();

            if (button.dataset.loggedIn === 'true') {
                if (confirm('Выйти из аккаунта?')) {
                    clearUser();
                }
                return;
            }

            openAuthModal('login');
        });
    });

    updateAuthUI();

    const user = getStoredUser();
    if (user) {
        fillDeliveryAddress(user.delivery_address);
    }
}

document.addEventListener('DOMContentLoaded', initAuthButtons);

window.getStoredUser = getStoredUser;
window.openAuthModal = openAuthModal;
