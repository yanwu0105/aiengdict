// Authentication JavaScript

// Show message function
function showAuthMessage(message, isError = false) {
    const messageDiv = document.getElementById('authMessage');
    messageDiv.textContent = message;
    messageDiv.className = `auth-message ${isError ? 'error' : 'success'}`;
    messageDiv.classList.remove('hidden');

    // Auto hide success messages after 3 seconds
    if (!isError) {
        setTimeout(() => {
            messageDiv.classList.add('hidden');
        }, 3000);
    }
}

// Hide message function
function hideAuthMessage() {
    const messageDiv = document.getElementById('authMessage');
    messageDiv.classList.add('hidden');
}

// Show loading state
function showAuthLoading(formType) {
    const btn = document.getElementById(`${formType}Btn`);
    const btnText = document.getElementById(`${formType}BtnText`);
    const loading = document.getElementById(`${formType}Loading`);

    btn.disabled = true;
    btnText.classList.add('hidden');
    loading.classList.remove('hidden');
}

// Hide loading state
function hideAuthLoading(formType) {
    const btn = document.getElementById(`${formType}Btn`);
    const btnText = document.getElementById(`${formType}BtnText`);
    const loading = document.getElementById(`${formType}Loading`);

    btn.disabled = false;
    btnText.classList.remove('hidden');
    loading.classList.add('hidden');
}

// Login form handler
if (document.getElementById('loginForm')) {
    document.getElementById('loginForm').addEventListener('submit', async function(e) {
        e.preventDefault();
        hideAuthMessage();

        const formData = new FormData(this);
        const data = {
            username: formData.get('username').trim(),
            password: formData.get('password')
        };

        if (!data.username || !data.password) {
            showAuthMessage('請填寫所有欄位', true);
            return;
        }

        showAuthLoading('login');

        try {
            const response = await fetch('/login', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify(data)
            });

            const result = await response.json();

            if (response.ok) {
                showAuthMessage(result.message);
                setTimeout(() => {
                    window.location.href = '/';
                }, 1500);
            } else {
                showAuthMessage(result.error, true);
            }
        } catch (error) {
            console.error('Login error:', error);
            showAuthMessage('網路連線錯誤，請稍後再試', true);
        } finally {
            hideAuthLoading('login');
        }
    });
}

// Register form handler
if (document.getElementById('registerForm')) {
    document.getElementById('registerForm').addEventListener('submit', async function(e) {
        e.preventDefault();
        hideAuthMessage();

        const formData = new FormData(this);
        const data = {
            username: formData.get('username').trim(),
            email: formData.get('email').trim(),
            password: formData.get('password'),
            display_name: formData.get('displayName').trim(),
            confirmPassword: formData.get('confirmPassword')
        };

        // Validation
        if (!data.username || !data.email || !data.password || !data.confirmPassword) {
            showAuthMessage('請填寫所有必填欄位', true);
            return;
        }

        if (data.password !== data.confirmPassword) {
            showAuthMessage('密碼確認不一致', true);
            return;
        }

        if (data.password.length < 6) {
            showAuthMessage('密碼長度至少6個字符', true);
            return;
        }

        // Email validation
        const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
        if (!emailRegex.test(data.email)) {
            showAuthMessage('請輸入有效的電子郵件地址', true);
            return;
        }

        showAuthLoading('register');

        try {
            const response = await fetch('/register', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify(data)
            });

            const result = await response.json();

            if (response.ok) {
                showAuthMessage(result.message + '，即將跳轉至登入頁面...');
                setTimeout(() => {
                    window.location.href = '/login';
                }, 2000);
            } else {
                showAuthMessage(result.error, true);
            }
        } catch (error) {
            console.error('Register error:', error);
            showAuthMessage('網路連線錯誤，請稍後再試', true);
        } finally {
            hideAuthLoading('register');
        }
    });
}

// Focus on first input when page loads
document.addEventListener('DOMContentLoaded', function() {
    const firstInput = document.querySelector('input[type="text"], input[type="email"]');
    if (firstInput) {
        firstInput.focus();
    }
});
