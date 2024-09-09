document.addEventListener('DOMContentLoaded', function() {
    // Получаем элементы формы
    var form = document.getElementById('registrationForm');
    var username = document.getElementById('username');
    var password = document.getElementById('password');
    var usernameError = document.getElementById('usernameError');
    var passwordError = document.getElementById('passwordError');

    form.addEventListener('submit', function(event) {
        usernameError.textContent = '';
        passwordError.textContent = '';
        username.classList.remove('error');
        password.classList.remove('error');

        var valid = true;

        if (username.value.length < 5) {
            usernameError.textContent = 'Username must be at least 5 characters long.';
            username.classList.add('error');
            valid = false;
        }

        var passwordRegex = /^(?=.*[A-Z])(?=.*\d)(?=.*[@$!%*?&])[A-Za-z\d@$!%*?&]{8,}$/;
        if (!passwordRegex.test(password.value)) {
            passwordError.textContent = 'Password must be at least 8 characters long, contain one uppercase letter, one digit, and one special character.';
            password.classList.add('error');
            valid = false;
        }

        if (!valid) {
            event.preventDefault();
        }
    });
});
