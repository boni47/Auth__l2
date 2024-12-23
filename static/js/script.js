const apiUrl = "http://localhost:5000"; // URL вашего бэкенда

// Функция для регистрации пользователя
document.getElementById("registerForm")?.addEventListener("submit", async (e) => {
    e.preventDefault();
    
    const username = document.getElementById("username").value;
    const password = document.getElementById("password").value;
    const confirmPassword = document.getElementById("confirmPassword").value;
    const email = document.getElementById("email").value;

    const response = await fetch(`${apiUrl}/register`, {
        method: "POST",
        headers: {
            "Content-Type": "application/json",
        },
        body: JSON.stringify({ username, password, confirmPassword, email })
    });

    const data = await response.json();
    
    if (response.ok) {
        window.location.href = "/login.html"; // Перенаправление на страницу входа
    } else {
        document.getElementById("registerErrorMessage").innerText = data.message;
    }
});

// Функция для входа пользователя
document.getElementById("loginForm")?.addEventListener("submit", async (e) => {
    e.preventDefault();

    const username = document.getElementById("username").value;
    const password = document.getElementById("password").value;

    const response = await fetch(`${apiUrl}/login`, {
        method: "POST",
        headers: {
            "Content-Type": "application/json",
        },
        body: JSON.stringify({ username, password })
    });

    const data = await response.json();

    if (response.ok) {
        localStorage.setItem("token", data.token); // Сохраняем токен
        window.location.href = "/user_profile.html"; // Перенаправление на профиль
    } else {
        document.getElementById("errorMessage").innerText = data.message;
    }
});

// Загрузка данных пользователя на странице профиля
if (window.location.pathname === "/user_profile.html") {
    const token = localStorage.getItem("token");
    
    if (token) {
        const response = await fetch(`${apiUrl}/user`, {
            method: "GET",
            headers: {
                "Authorization": `Bearer ${token}`
            }
        });

        const user = await response.json();
        
        if (response.ok) {
            document.getElementById("userData").innerHTML = `
                <h2>Привет, ${user.username}</h2>
                <p>Email: ${user.email}</p>
                <p>Телефон: ${user.phone || "Не указан"}</p>
                <p>Никнейм: ${user.nickname || "Не указан"}</p>
                <p>Пол: ${user.gender || "Не указан"}</p>
            `;
        } else {
            window.location.href = "/login.html"; // Перенаправление на страницу входа, если нет токена
        }
    } else {
        window.location.href = "/login.html"; // Перенаправление на страницу входа, если нет токена
    }
}
