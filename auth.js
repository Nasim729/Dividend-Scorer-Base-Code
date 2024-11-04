document.addEventListener('DOMContentLoaded', function() {
    const loginOverlay = document.getElementById('login-overlay');
    const signupOverlay = document.getElementById('signup-overlay');
    const mainContent = document.getElementById('main-content');
    const loginForm = document.getElementById('login-form');
    const signupForm = document.getElementById('signup-form');
    const switchToSignupBtn = document.getElementById('switch-to-signup');
    const switchToLoginBtn = document.getElementById('switch-to-login');
    const logoutBtn = document.getElementById('logout-btn');

    // Check if user is logged in
    function checkAuth() {
        const currentUser = localStorage.getItem('currentUser');
        if (currentUser) {
            loginOverlay.style.display = 'none';
            signupOverlay.style.display = 'none';
            mainContent.style.display = 'block';
        } else {
            loginOverlay.style.display = 'flex';
            signupOverlay.style.display = 'none';
            mainContent.style.display = 'none';
        }
    }

    // Switch between login and signup forms
    switchToSignupBtn.addEventListener('click', function(e) {
        e.preventDefault();
        loginOverlay.style.display = 'none';
        signupOverlay.style.display = 'flex';
    });

    switchToLoginBtn.addEventListener('click', function(e) {
        e.preventDefault();
        signupOverlay.style.display = 'none';
        loginOverlay.style.display = 'flex';
    });

    // Handle login
    loginForm.addEventListener('submit', function(e) {
        e.preventDefault();
        const username = document.getElementById('login-username').value;
        const password = document.getElementById('login-password').value;

        // Get users from local storage
        const users = JSON.parse(localStorage.getItem('users') || '{}');

        if (users[username] && users[username].password === password) {
            localStorage.setItem('currentUser', username);
            checkAuth();
        } else {
            alert('Invalid username or password');
        }
    });

    // Handle signup
    signupForm.addEventListener('submit', function(e) {
        e.preventDefault();
        const username = document.getElementById('signup-username').value;
        const password = document.getElementById('signup-password').value;
        const confirmPassword = document.getElementById('confirm-password').value;

        if (password !== confirmPassword) {
            alert('Passwords do not match');
            return;
        }

        // Get existing users or initialize empty object
        const users = JSON.parse(localStorage.getItem('users') || '{}');

        if (users[username]) {
            alert('Username already exists');
            return;
        }

        // Add new user
        users[username] = { password: password };
        localStorage.setItem('users', JSON.stringify(users));
        localStorage.setItem('currentUser', username);
        checkAuth();
    });

    // Handle logout
    logoutBtn.addEventListener('click', function() {
        localStorage.removeItem('currentUser');
        checkAuth();
    });

    // Initial auth check
    checkAuth();
});
