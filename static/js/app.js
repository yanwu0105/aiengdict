// DOM Elements
const wordInput = document.getElementById('wordInput');
const searchBtn = document.getElementById('searchBtn');
const btnText = document.getElementById('btnText');
const loading = document.getElementById('loading');
const languageDetected = document.getElementById('languageDetected');
const resultContainer = document.getElementById('resultContainer');
const errorContainer = document.getElementById('errorContainer');
const resultWord = document.getElementById('resultWord');
const resultLanguage = document.getElementById('resultLanguage');
const resultDefinition = document.getElementById('resultDefinition');
const errorText = document.getElementById('errorText');
const historyContainer = document.getElementById('historyContainer');
const refreshIcon = document.getElementById('refreshIcon');
const userSection = document.getElementById('userSection');
const authSection = document.getElementById('authSection');
const userAvatar = document.getElementById('userAvatar');
const userDisplayName = document.getElementById('userDisplayName');
const userEmail = document.getElementById('userEmail');

// Language detection function
function detectLanguage(text) {
    const chinesePattern = /[\u4e00-\u9fff]/;
    return chinesePattern.test(text) ? 'chinese' : 'english';
}

// Update language indicator
function updateLanguageIndicator() {
    const text = wordInput.value.trim();
    if (text) {
        const language = detectLanguage(text);
        const languageText = language === 'chinese' ? '中文' : 'English';
        languageDetected.textContent = `偵測語言: ${languageText}`;
    } else {
        languageDetected.textContent = '';
    }
}

// Show loading state
function showLoading() {
    searchBtn.disabled = true;
    btnText.classList.add('hidden');
    loading.classList.remove('hidden');
}

// Hide loading state
function hideLoading() {
    searchBtn.disabled = false;
    btnText.classList.remove('hidden');
    loading.classList.add('hidden');
}

// Clean up excessive whitespace and line breaks
function cleanDefinitionText(text) {
    return text
        .replace(/\n\s*\n\s*\n+/g, '\n\n')  // Replace multiple line breaks with double line breaks
        .replace(/【例句】\s*:\s*\n+/g, '【例句】:\n')  // Clean up after 【例句】:
        .replace(/【.*?】\s*:\s*\n+/g, (match) => match.replace(/\n+/g, '\n'))  // Clean up after any 【】: pattern
        .replace(/^\s+|\s+$/g, '')          // Trim leading and trailing whitespace
        .replace(/[ \t]+/g, ' ')            // Replace multiple spaces/tabs with single space
        .replace(/\n{3,}/g, '\n\n');        // Replace 3+ line breaks with just 2
}

// Clean up HTML to reduce spacing
function cleanHtml(html) {
    return html
        .replace(/<p><\/p>/g, '')           // Remove empty paragraphs
        .replace(/<p>\s*<\/p>/g, '')        // Remove paragraphs with only whitespace
        .replace(/<p>\s*&nbsp;\s*<\/p>/g, '') // Remove paragraphs with only &nbsp;
        .replace(/(<\/li>)\s*<p>/g, '$1')   // Remove paragraph tags after list items
        .replace(/<\/p>\s*(<li>)/g, '$1')   // Remove paragraph tags before list items
        .replace(/(<br\s*\/?>){2,}/g, '<br>') // Replace multiple <br> tags with single one
        .replace(/\s{2,}/g, ' ')            // Replace multiple spaces with single space
        .replace(/>\s+</g, '><');           // Remove whitespace between tags
}

// Show result
function showResult(data) {
    hideContainers();
    resultWord.textContent = data.word;
    resultLanguage.textContent = data.language === 'chinese' ? '中文' : 'English';

    // Parse markdown and convert to HTML
    try {
        // Check if marked library is available
        if (typeof marked !== 'undefined') {
            const cleanedText = cleanDefinitionText(data.definition);
            console.log('Original text:', data.definition);
            console.log('Cleaned text:', cleanedText);
            let parsedHtml = marked.parse(cleanedText);
            parsedHtml = cleanHtml(parsedHtml);
            console.log('Final HTML:', parsedHtml);
            resultDefinition.innerHTML = parsedHtml;
        } else {
            console.error('Marked library not loaded, falling back to plain text');
            resultDefinition.textContent = data.definition;
        }
    } catch (error) {
        // Fallback to plain text if markdown parsing fails
        console.error('Markdown parsing failed:', error);
        resultDefinition.textContent = data.definition;
    }

    resultContainer.classList.remove('hidden');
}

// Show error
function showError(message) {
    hideContainers();
    errorText.textContent = message;
    errorContainer.classList.remove('hidden');
}

// Hide all containers
function hideContainers() {
    resultContainer.classList.add('hidden');
    errorContainer.classList.add('hidden');
}

// Main lookup function
async function lookupWord() {
    const word = wordInput.value.trim();

    if (!word) {
        showError('請輸入要查詢的單詞');
        return;
    }

    showLoading();

    try {
        const response = await fetch('/lookup', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ word: word })
        });

        const data = await response.json();

        if (response.ok) {
            showResult(data);
            // Refresh history after successful query
            loadQueryHistory();
        } else {
            showError(data.error || '查詢失敗，請稍後再試');
        }
    } catch (error) {
        console.error('Error:', error);
        showError('網路連線錯誤，請檢查網路連線後再試');
    } finally {
        hideLoading();
    }
}

// Event listeners
wordInput.addEventListener('input', updateLanguageIndicator);

wordInput.addEventListener('keypress', function(e) {
    if (e.key === 'Enter') {
        lookupWord();
    }
});

searchBtn.addEventListener('click', lookupWord);

// Load query history
async function loadQueryHistory() {
    const refreshBtn = document.getElementById('refreshHistoryBtn');

    try {
        // Show loading state
        refreshIcon.classList.add('loading');
        refreshBtn.disabled = true;

        const response = await fetch('/history');
        const data = await response.json();

        if (response.ok && data.history) {
            displayQueryHistory(data.history);
        } else {
            historyContainer.innerHTML = '<div class="no-history">載入歷史記錄失敗</div>';
        }
    } catch (error) {
        console.error('Error loading history:', error);
        historyContainer.innerHTML = '<div class="no-history">網路連線錯誤</div>';
    } finally {
        // Hide loading state
        refreshIcon.classList.remove('loading');
        refreshBtn.disabled = false;
    }
}

// Display query history
function displayQueryHistory(history) {
    if (!history || history.length === 0) {
        historyContainer.innerHTML = '<div class="no-history">尚無查詢記錄</div>';
        return;
    }

    const historyHtml = history.map(item => `
        <div class="history-item" onclick="searchHistoryWord('${item.word}')">
            <div class="history-word">
                <span class="word">${item.word}</span>
                <span class="language-tag ${item.language}">${item.language === 'chinese' ? '中' : 'EN'}</span>
            </div>
            <div class="history-info">
                <span class="query-count">查詢 ${item.query_times} 次</span>
                <span class="last-query">${item.updated_on}</span>
            </div>
            <div class="history-preview">${item.definition}</div>
        </div>
    `).join('');

    historyContainer.innerHTML = historyHtml;
}

// Search word from history
function searchHistoryWord(word) {
    wordInput.value = word;
    updateLanguageIndicator();
    lookupWord();
}

// Check user authentication status
async function checkUserAuth() {
    try {
        const response = await fetch('/user/info');
        const data = await response.json();

        if (data.authenticated) {
            showUserSection(data.user);
        } else {
            showAuthSection();
        }
    } catch (error) {
        console.error('Auth check error:', error);
        showAuthSection();
    }
}

// Show user section for authenticated users
function showUserSection(user) {
    userAvatar.textContent = user.display_name.charAt(0).toUpperCase();
    userDisplayName.textContent = user.display_name;
    userEmail.textContent = user.email;

    userSection.classList.remove('hidden');
    authSection.classList.add('hidden');
}

// Show auth section for non-authenticated users
function showAuthSection() {
    userSection.classList.add('hidden');
    authSection.classList.remove('hidden');
}

// Logout function
async function logout() {
    try {
        const response = await fetch('/logout', {
            method: 'POST'
        });

        if (response.ok) {
            showAuthSection();
            // Reload history to show anonymous history
            loadQueryHistory();
        }
    } catch (error) {
        console.error('Logout error:', error);
    }
}

// Focus on input when page loads
document.addEventListener('DOMContentLoaded', function() {
    wordInput.focus();
    // Check authentication status
    checkUserAuth();
    // Load initial history
    loadQueryHistory();
});
