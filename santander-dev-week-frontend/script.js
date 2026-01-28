// Configuration
const API_BASE_URL = 'http://localhost:8000';
let currentUserData = null;
let transactionHistory = [];

// Initialize App
document.addEventListener('DOMContentLoaded', function() {
    initializeApp();
    setupTabNavigation();
    checkAPIStatus();
    loadInitialData();
});

// Initialize Application
function initializeApp() {
    updateConnectionStatus('Conectando...', 'warning');
    
    fetch(`${API_BASE_URL}/health`)
        .then(response => {
            if (response.ok) {
                updateConnectionStatus('Conectado', 'connected');
                return response.json();
            }
            throw new Error('API não respondendo');
        })
        .then(data => {
            document.getElementById('apiStatus').textContent = '✅ Online';
            getUser(1);
        })
        .catch(error => {
            console.error('Erro:', error);
            updateConnectionStatus('Desconectado', 'error');
            document.getElementById('apiStatus').textContent = '❌ Offline';
            showNotification('Não foi possível conectar à API. Verifique se o servidor está rodando.', 'error');
        });
}

// Tab Navigation
function setupTabNavigation() {
    const tabItems = document.querySelectorAll('.sidebar li');
    
    tabItems.forEach(item => {
        item.addEventListener('click', function() {
            const tabId = this.getAttribute('data-tab');
            
            tabItems.forEach(i => i.classList.remove('active'));
            this.classList.add('active');
            
            document.querySelectorAll('.tab-content').forEach(content => {
                content.classList.remove('active');
            });
            document.getElementById(tabId).classList.add('active');
            
            switch(tabId) {
                case 'users':
                    getAllUsers();
                    break;
                case 'features':
                    loadFeatures();
                    break;
                case 'news':
                    loadNews();
                    break;
            }
        });
    });
}

// Update Connection Status
function updateConnectionStatus(message, type) {
    const statusElement = document.getElementById('connectionStatus');
    statusElement.innerHTML = `<i class="fas fa-circle"></i> ${message}`;
    statusElement.className = `status ${type}`;
}

// Show Notification
function showNotification(message, type = 'info') {
    const oldNotification = document.querySelector('.notification');
    if (oldNotification) oldNotification.remove();
    
    const notification = document.createElement('div');
    notification.className = `notification ${type}`;
    notification.innerHTML = `
        <p>${message}</p>
        <button onclick="this.parentElement.remove()">×</button>
    `;
    
    notification.style.cssText = `
        position: fixed;
        top: 20px;
        right: 20px;
        padding: 15px 20px;
        background: ${type === 'error' ? '#e74c3c' : type === 'success' ? '#27ae60' : '#3498db'};
        color: white;
        border-radius: 8px;
        box-shadow: 0 5px 15px rgba(0,0,0,0.2);
        z-index: 1000;
        display: flex;
        justify-content: space-between;
        align-items: center;
        min-width: 300px;
        animation: slideIn 0.3s ease;
    `;
    
    document.body.appendChild(notification);
    
    setTimeout(() => {
        if (notification.parentElement) {
            notification.remove();
        }
    }, 5000);
}

// Get User by ID
async function getUser(id) {
    try {
        showLoading('usersTableBody', 'Carregando usuário...');
        
        const response = await fetch(`${API_BASE_URL}/users/${id}`);
        
        if (!response.ok) {
            throw new Error(`Usuário ${id} não encontrado`);
        }
        
        const user = await response.json();
        currentUserData = user;
        updateUserDisplay(user);
        showUserDetails(user);
        showNotification(`Usuário ${user.name} carregado com sucesso!`, 'success');
        
    } catch (error) {
        console.error('Erro ao buscar usuário:', error);
        showNotification(error.message, 'error');
        document.getElementById('usersTableBody').innerHTML = 
            `<tr><td colspan="6" class="error">${error.message}</td></tr>`;
    }
}

// Get User by Input
function getUserById() {
    const userId = document.getElementById('userIdInput').value;
    if (!userId || userId < 1) {
        showNotification('Digite um ID válido (maior que 0)', 'error');
        return;
    }
    getUser(userId);
}

// Get All Users
async function getAllUsers() {
    try {
        showLoading('usersTableBody', 'Carregando usuários...');
        
        const response = await fetch(`${API_BASE_URL}/users`);
        
        if (!response.ok) {
            throw new Error('Erro ao carregar usuários');
        }
        
        const users = await response.json();
        displayUsersTable(users);
        
    } catch (error) {
        console.error('Erro ao listar usuários:', error);
        showNotification(error.message, 'error');
        document.getElementById('usersTableBody').innerHTML = 
            `<tr><td colspan="6" class="error">${error.message}</td></tr>`;
    }
}

// Update User Display
function updateUserDisplay(user) {
    document.getElementById('userName').textContent = user.name;
    document.getElementById('userBalance').textContent = formatCurrency(user.account.balance);
    document.getElementById('currentUser').textContent = user.name;
    document.getElementById('cardLimit').textContent = formatCurrency(user.card.limit);
    document.getElementById('accountNumber').textContent = `${user.account.number} / ${user.account.agency}`;
}

// Show User Details
function showUserDetails(user) {
    const detailsElement = document.getElementById('userDetails');
    
    detailsElement.innerHTML = `
        <div class="user-detail-card">
            <h3><i class="fas fa-id-card"></i> Detalhes do Usuário</h3>
            <div class="user-info-grid">
                <div class="info-item">
                    <label><i class="fas fa-user"></i> Nome:</label>
                    <span>${user.name}</span>
                </div>
                <div class="info-item">
                    <label><i class="fas fa-envelope"></i> Email:</label>
                    <span>${user.email || 'Não informado'}</span>
                </div>
                <div class="info-item">
                    <label><i class="fas fa-calendar"></i> Criado em:</label>
                    <span>${formatDate(user.created_at)}</span>
                </div>
                <div class="info-item">
                    <label><i class="fas fa-wallet"></i> Saldo:</label>
                    <span class="balance">${formatCurrency(user.account.balance)}</span>
                </div>
                <div class="info-item">
                    <label><i class="fas fa-credit-card"></i> Limite do Cartão:</label>
                    <span>${formatCurrency(user.card.limit)}</span>
                </div>
                <div class="info-item">
                    <label><i class="fas fa-university"></i> Conta:</label>
                    <span>${user.account.number} / ${user.account.agency}</span>
                </div>
            </div>
            
            <div class="user-actions">
                <button class="btn btn-primary" onclick="openModal('${user.id}')">
                    <i class="fas fa-eye"></i> Ver Completo
                </button>
                <button class="btn btn-success" onclick="copyUserData('${user.id}')">
                    <i class="fas fa-copy"></i> Copiar Dados
                </button>
            </div>
        </div>
    `;
}

// Display Users Table
function displayUsersTable(users) {
    const tbody = document.getElementById('usersTableBody');
    
    if (!users || users.length === 0) {
        tbody.innerHTML = `
            <tr>
                <td colspan="6" style="text-align: center; padding: 40px;">
                    <i class="fas fa-users" style="font-size: 3rem; color: #ddd; margin-bottom: 15px;"></i>
                    <p style="color: #666;">Nenhum usuário encontrado</p>
                </td>
            </tr>
        `;
        return;
    }
    
    tbody.innerHTML = users.map(user => `
        <tr>
            <td><strong>#${user.id}</strong></td>
            <td>
                <div class="user-cell">
                    <i class="fas fa-user-circle"></i>
                    <span>${user.name}</span>
                </div>
            </td>
            <td>${user.email || '-'}</td>
            <td>
                <span class="balance-badge ${user.account.balance >= 0 ? 'positive' : 'negative'}">
                    ${formatCurrency(user.account.balance)}
                </span>
            </td>
            <td>
                <div class="card-cell">
                    <i class="fas fa-credit-card"></i>
                    <span>${user.card.number}</span>
                </div>
            </td>
            <td>
                <button class="btn btn-sm btn-primary" onclick="getUser(${user.id})">
                    <i class="fas fa-eye"></i>
                </button>
                <button class="btn btn-sm btn-success" onclick="copyUserData('${user.id}')">
                    <i class="fas fa-copy"></i>
                </button>
            </td>
        </tr>
    `).join('');
}

// Load Features
async function loadFeatures() {
    if (!currentUserData) {
        document.getElementById('featuresList').innerHTML = `
            <div class="empty-state">
                <i class="fas fa-star" style="font-size: 3rem; color: #ddd;"></i>
                <p>Carregue um usuário primeiro</p>
            </div>
        `;
        return;
    }
    
    const featuresList = document.getElementById('featuresList');
    featuresList.innerHTML = '';
    
    if (currentUserData.features && currentUserData.features.length > 0) {
        currentUserData.features.forEach(feature => {
            const featureElement = document.createElement('div');
            featureElement.className = 'feature-item';
            featureElement.innerHTML = `
                <div class="feature-icon">
                    <span style="font-size: 2rem;">${feature.icon}</span>
                </div>
                <div class="feature-content">
                    <h4>${feature.description}</h4>
                </div>
            `;
            featuresList.appendChild(featureElement);
        });
    } else {
        featuresList.innerHTML = `
            <div class="empty-state">
                <i class="fas fa-star" style="font-size: 3rem; color: #ddd;"></i>
                <p>Nenhuma feature disponível</p>
            </div>
        `;
    }
}

// Load News
async function loadNews() {
    if (!currentUserData) {
        document.getElementById('newsList').innerHTML = `
            <div class="empty-state">
                <i class="fas fa-newspaper" style="font-size: 3rem; color: #ddd;"></i>
                <p>Carregue um usuário primeiro</p>
            </div>
        `;
        return;
    }
    
    const newsList = document.getElementById('newsList');
    newsList.innerHTML = '';
    
    if (currentUserData.news && currentUserData.news.length > 0) {
        currentUserData.news.forEach(news => {
            const newsElement = document.createElement('div');
            newsElement.className = 'news-item';
            newsElement.innerHTML = `
                <div class="news-icon">
                    <span style="font-size: 2rem;">${news.icon}</span>
                </div>
                <div class="news-content">
                    <h4>${news.description}</h4>
                </div>
            `;
            newsList.appendChild(newsElement);
        });
    } else {
        newsList.innerHTML = `
            <div class="empty-state">
                <i class="fas fa-newspaper" style="font-size: 3rem; color: #ddd;"></i>
                <p>Nenhuma notícia disponível</p>
            </div>
        `;
    }
}

// Create Mock User
async function createMockUser() {
    try {
        const mockUser = {
            name: `Usuário ${Date.now().toString().slice(-4)}`,
            email: `user${Date.now().toString().slice(-6)}@example.com`,
            initial_balance: 1000.00
        };
        
        showNotification('Criando usuário...', 'info');
        
        const response = await fetch(`${API_BASE_URL}/users/simple`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(mockUser)
        });
        
        if (response.ok) {
            const newUser = await response.json();
            showNotification(`Usuário ${newUser.name} criado com sucesso!`, 'success');
            getAllUsers();
            getUser(newUser.id);
        } else {
            throw new Error('Erro ao criar usuário');
        }
        
    } catch (error) {
        console.error('Erro ao criar usuário:', error);
        showNotification(error.message, 'error');
    }
}

// Make Deposit
async function makeDeposit() {
    const userId = document.getElementById('transactionUser').value;
    const amount = parseFloat(document.getElementById('depositAmount').value);
    
    if (!userId || userId < 1) {
        showNotification('ID do usuário inválido', 'error');
        return;
    }
    
    if (!amount || amount <= 0) {
        showNotification('Valor de depósito inválido', 'error');
        return;
    }
    
    try {
        const response = await fetch(`${API_BASE_URL}/users/${userId}/deposit`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ amount: amount })
        });
        
        if (response.ok) {
            const result = await response.json();
            addTransactionLog(result);
            getUser(userId);
            showNotification(`Depósito de ${formatCurrency(amount)} realizado!`, 'success');
            document.getElementById('depositAmount').value = '';
        } else {
            const error = await response.json();
            throw new Error(error.detail || 'Erro ao realizar depósito');
        }
    } catch (error) {
        console.error('Erro:', error);
        showNotification(error.message, 'error');
    }
}

// Make Withdraw
async function makeWithdraw() {
    const userId = document.getElementById('transactionUser').value;
    const amount = parseFloat(document.getElementById('withdrawAmount').value);
    
    if (!userId || userId < 1) {
        showNotification('ID do usuário inválido', 'error');
        return;
    }
    
    if (!amount || amount <= 0) {
        showNotification('Valor de saque inválido', 'error');
        return;
    }
    
    try {
        const response = await fetch(`${API_BASE_URL}/users/${userId}/withdraw`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ amount: amount })
        });
        
        if (response.ok) {
            const result = await response.json();
            addTransactionLog(result);
            getUser(userId);
            showNotification(`Saque de ${formatCurrency(amount)} realizado!`, 'success');
            document.getElementById('withdrawAmount').value = '';
        } else {
            const error = await response.json();
            throw new Error(error.detail || 'Erro ao realizar saque');
        }
    } catch (error) {
        console.error('Erro:', error);
        showNotification(error.message, 'error');
    }
}

// Make Transfer
async function makeTransfer() {
    const fromUserId = document.getElementById('transactionUser').value;
    const toUserId = document.getElementById('transferToUser').value;
    const amount = parseFloat(document.getElementById('transferAmount').value);
    
    if (!fromUserId || fromUserId < 1 || !toUserId || toUserId < 1) {
        showNotification('IDs de usuário inválidos', 'error');
        return;
    }
    
    if (!amount || amount <= 0) {
        showNotification('Valor de transferência inválido', 'error');
        return;
    }
    
    try {
        const response = await fetch(`${API_BASE_URL}/users/${fromUserId}/transfer`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ 
                to_user_id: parseInt(toUserId), 
                amount: amount 
            })
        });
        
        if (response.ok) {
            const result = await response.json();
            addTransactionLog(result);
            getUser(fromUserId);
            showNotification(`Transferência de ${formatCurrency(amount)} realizada!`, 'success');
            document.getElementById('transferAmount').value = '';
            document.getElementById('transferToUser').value = '';
        } else {
            const error = await response.json();
            throw new Error(error.detail || 'Erro ao realizar transferência');
        }
    } catch (error) {
        console.error('Erro:', error);
        showNotification(error.message, 'error');
    }
}

// Add Transaction to Log
function addTransactionLog(transaction) {
    transactionHistory.unshift({
        ...transaction,
        timestamp: new Date().toLocaleTimeString()
    });
    
    if (transactionHistory.length > 10) {
        transactionHistory = transactionHistory.slice(0, 10);
    }
    
    updateTransactionLog();
}

// Update Transaction Log
function updateTransactionLog() {
    const logElement = document.getElementById('transactionLog');
    
    if (transactionHistory.length === 0) {
        logElement.innerHTML = '<p>Nenhuma transação realizada.</p>';
        return;
    }
    
    logElement.innerHTML = transactionHistory.map(tx => `
        <div class="transaction-item">
            <div class="tx-header">
                <strong>${tx.transaction_id}</strong>
                <span class="tx-time">${tx.timestamp}</span>
            </div>
            <div class="tx-body">
                ${tx.message}
                <div class="tx-details">
                    ${tx.amount ? `Valor: ${formatCurrency(tx.amount)}` : ''}
                    ${tx.new_balance ? ` | Novo saldo: ${formatCurrency(tx.new_balance)}` : ''}
                </div>
            </div>
        </div>
    `).join('');
}

// Test API
async function testAPI() {
    const endpoints = ['/', '/health', '/users', '/users/1'];
    const results = [];
    
    for (const endpoint of endpoints) {
        try {
            const startTime = Date.now();
            const response = await fetch(`${API_BASE_URL}${endpoint}`);
            const endTime = Date.now();
            
            results.push({
                endpoint,
                status: response.status,
                ok: response.ok,
                time: endTime - startTime
            });
        } catch (error) {
            results.push({
                endpoint,
                status: 'ERROR',
                ok: false,
                time: null,
                error: error.message
            });
        }
    }
    
    displayTestResults(results);
}

// Display Test Results
function displayTestResults(results) {
    const apiResponse = document.getElementById('apiResponse');
    
    const html = results.map(result => `
        <div class="test-result ${result.ok ? 'success' : 'error'}">
            <div class="test-endpoint">
                <strong>${result.endpoint}</strong>
                <span class="status-badge ${result.ok ? 'success' : 'error'}">
                    ${result.ok ? '✅ OK' : '❌ ERROR'} ${result.status}
                </span>
            </div>
            ${result.time ? `<div class="test-time">Tempo: ${result.time}ms</div>` : ''}
            ${result.error ? `<div class="test-error">${result.error}</div>` : ''}
        </div>
    `).join('');
    
    apiResponse.innerHTML = html;
}

// Fetch API Endpoint
async function fetchAPI(endpoint) {
    try {
        const response = await fetch(`${API_BASE_URL}${endpoint}`);
        const data = await response.json();
        
        const apiResponse = document.getElementById('apiResponse');
        apiResponse.textContent = JSON.stringify(data, null, 2);
        
        showNotification(`Endpoint ${endpoint} testado!`, 'success');
    } catch (error) {
        console.error('Erro:', error);
        showNotification(`Erro ao testar ${endpoint}`, 'error');
        document.getElementById('apiResponse').textContent = `Erro: ${error.message}`;
    }
}

// Utility Functions
function formatCurrency(value) {
    return new Intl.NumberFormat('pt-BR', {
        style: 'currency',
        currency: 'BRL'
    }).format(value);
}

function formatDate(dateString) {
    if (!dateString) return 'Não disponível';
    const date = new Date(dateString);
    return date.toLocaleDateString('pt-BR') + ' ' + date.toLocaleTimeString('pt-BR');
}

function showLoading(elementId, message = 'Carregando...') {
    const element = document.getElementById(elementId);
    if (element) {
        element.innerHTML = `
            <tr>
                <td colspan="6" style="text-align: center; padding: 40px;">
                    <div class="loading-spinner">
                        <i class="fas fa-spinner fa-spin" style="font-size: 2rem; color: #3498db;"></i>
                        <p style="margin-top: 15px; color: #666;">${message}</p>
                    </div>
                </td>
            </tr>
        `;
    }
}

function copyUserData(userId) {
    if (!currentUserData || currentUserData.id != userId) {
        showNotification('Carregue os dados do usuário primeiro', 'warning');
        return;
    }
    
    const userStr = JSON.stringify(currentUserData, null, 2);
    navigator.clipboard.writeText(userStr)
        .then(() => {
            showNotification('Dados copiados para a área de transferência!', 'success');
        })
        .catch(err => {
            console.error('Erro ao copiar:', err);
            showNotification('Erro ao copiar dados', 'error');
        });
}

function openModal(userId) {
    if (!currentUserData || currentUserData.id != userId) {
        showNotification('Carregue os dados do usuário primeiro', 'warning');
        return;
    }
    
    const modal = document.getElementById('userModal');
    const modalContent = document.getElementById('modalContent');
    
    modalContent.innerHTML = `
        <div class="modal-user-details">
            <h3>${currentUserData.name}</h3>
            <pre>${JSON.stringify(currentUserData, null, 2)}</pre>
        </div>
    `;
    
    modal.style.display = 'flex';
}

function closeModal() {
    document.getElementById('userModal').style.display = 'none';
}

// Close modal on outside click
window.onclick = function(event) {
    const modal = document.getElementById('userModal');
    if (event.target == modal) {
        modal.style.display = 'none';
    }
}

// Load Initial Data
function loadInitialData() {
    setTimeout(() => getUser(1), 1000);
    setInterval(checkAPIStatus, 30000);
}

// Check API Status
async function checkAPIStatus() {
    try {
        const response = await fetch(`${API_BASE_URL}/health`);
        if (response.ok) {
            updateConnectionStatus('Conectado', 'connected');
        } else {
            updateConnectionStatus('Problema na API', 'error');
        }
    } catch (error) {
        updateConnectionStatus('Desconectado', 'error');
    }
}

document.addEventListener('DOMContentLoaded', function() {
    transactionCharts = new TransactionCharts();
});
// Add dynamic styles
const style = document.createElement('style');
style.textContent = `
    @keyframes slideIn {
        from {
            transform: translateX(100%);
            opacity: 0;
        }
        to {
            transform: translateX(0);
            opacity: 1;
        }
    }
    
    .transaction-item {
        background: white;
        padding: 15px;
        margin: 10px 0;
        border-radius: 8px;
        border-left: 4px solid #3498db;
        box-shadow: 0 2px 5px rgba(0,0,0,0.05);
    }
    
    .tx-header {
        display: flex;
        justify-content: space-between;
        align-items: center;
        margin-bottom: 8px;
    }
    
    .tx-time {
        font-size: 0.8rem;
        color: #666;
    }
    
    .tx-details {
        font-size: 0.9rem;
        color: #666;
        margin-top: 5px;
    }
    
    .transaction-panel {
        display: grid;
        grid-template-columns: 1fr 1fr;
        gap: 30px;
        margin-top: 20px;
    }
    
    @media (max-width: 992px) {
        .transaction-panel {
            grid-template-columns: 1fr;
        }
    }
    
    .api-info {
        display: grid;
        grid-template-columns: 1fr 1fr;
        gap: 30px;
        margin-top: 20px;
    }
    
    @media (max-width: 992px) {
        .api-info {
            grid-template-columns: 1fr;
        }
    }
    
    .endpoint-card {
        background: white;
        padding: 20px;
        border-radius: 10px;
        box-shadow: 0 3px 10px rgba(0,0,0,0.08);
    }
    
    .endpoint-card ul {
        list-style: none;
        margin-top: 15px;
    }
    
    .endpoint-card li {
        padding: 8px 0;
        border-bottom: 1px solid #eee;
    }
    
    .endpoint-card li:last-child {
        border-bottom: none;
    }
    
    .endpoint-card code {
        background: #f8f9fa;
        padding: 2px 6px;
        border-radius: 4px;
        font-family: monospace;
        font-size: 0.9rem;
    }
    
    .test-buttons {
        display: flex;
        flex-wrap: wrap;
        gap: 10px;
        margin: 15px 0;
    }
`;
document.head.appendChild(style);