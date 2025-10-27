// Price Monitor Pro - Frontend Logic
class PriceMonitorApp {
    constructor() {
        this.currentView = 'grid';
        this.products = [];
        this.stats = {
            totalProducts: 0,
            totalSavings: 0,
            activeTargets: 0,
            lastUpdate: null
        };
        
        this.init();
    }

    async init() {
        try {
            console.log('Initializing Price Monitor App...');
            await this.loadProducts();
            this.setupEventListeners();
            this.updateStats();
            this.renderProducts();
            this.setupAutoRefresh();
            console.log('Price Monitor App initialized successfully');
        } catch (error) {
            console.error('Error initializing app:', error);
            // Show a basic error message if possible
            document.body.innerHTML = `
                <div style="padding: 20px; text-align: center;">
                    <h2>Error Loading Application</h2>
                    <p>Please restart the application</p>
                    <pre>${error.message}</pre>
                </div>
            `;
        }
    }

    setupEventListeners() {
        try {
            // Header buttons
            const addProductBtn = document.getElementById('addProductBtn');
            if (addProductBtn) {
                addProductBtn.addEventListener('click', () => this.showAddProductModal());
            }
            const testProductBtn = document.getElementById('testProductBtn');
            if (testProductBtn) {
                testProductBtn.addEventListener('click', () => this.testAddProduct());
            }
            const autoCheckBtn = document.getElementById('autoCheckBtn');
            if (autoCheckBtn) {
                autoCheckBtn.addEventListener('click', () => this.showAutoCheckModal());
            }
            const clearAllBtn = document.getElementById('clearAllBtn');
            if (clearAllBtn) {
                clearAllBtn.addEventListener('click', () => this.clearAllProducts());
            }
            const findDealsBtn = document.getElementById('findDealsBtn');
            if (findDealsBtn) {
                findDealsBtn.addEventListener('click', () => this.showDealFinderModal());
            }

            // View controls
            document.getElementById('gridView').addEventListener('click', () => this.setView('grid'));
            document.getElementById('listView').addEventListener('click', () => this.setView('list'));

            // Modal controls
            document.querySelectorAll('.close-btn').forEach(btn => {
                btn.addEventListener('click', (e) => this.closeModal(e.target.closest('.modal-overlay')));
            });

            // Form submissions
            const addProductForm = document.getElementById('addProductForm');
            if (addProductForm) {
                addProductForm.addEventListener('submit', (e) => this.handleAddProduct(e));
            }

            const dealFinderForm = document.getElementById('dealFinderForm');
            if (dealFinderForm) {
                dealFinderForm.addEventListener('submit', (e) => this.handleDealFinder(e));
            }

            const autoCheckForm = document.getElementById('autoCheckForm');
            if (autoCheckForm) {
                autoCheckForm.addEventListener('submit', (e) => this.handleAutoCheckSettings(e));
            }
        } catch (error) {
            console.error('Error setting up event listeners:', error);
        }

                    // IPC listeners for backend communication
            if (window.electronAPI) {
                window.electronAPI.onProductAdded((product) => {
                    this.products.push(product);
                    this.renderProducts();
                    this.updateStats();
                    this.showToast('Product added successfully!', 'success');
                });

                window.electronAPI.onProductUpdated((updatedProduct) => {
                    const index = this.products.findIndex(p => p.id === updatedProduct.id);
                    if (index !== -1) {
                        this.products[index] = updatedProduct;
                        this.renderProducts();
                        this.updateStats();
                        
                        // Check if target was reached
                        if (updatedProduct.currentPrice <= updatedProduct.targetPrice) {
                            this.showToast(`Target price reached for ${updatedProduct.name}!`, 'success');
                        }
                    }
                });

                window.electronAPI.onError((error) => {
                    this.showToast(error, 'error');
                });

                // Price update notifications
                window.electronAPI.onPriceUpdate((data) => {
                    const { productName, oldPrice, newPrice, targetPrice } = data;
                    const change = newPrice - oldPrice;
                    const changePercent = ((change / oldPrice) * 100).toFixed(1);
                    
                    if (change < 0) {
                        this.showToast(`Price drop: ${productName} is now $${newPrice} (${changePercent}%)`, 'success');
                    } else if (change > 0) {
                        this.showToast(`Price increase: ${productName} is now $${newPrice} (+${changePercent}%)`, 'warning');
                    }
                });
            } else {
                console.error('electronAPI not available - check preload script');
            }
    }

    async loadProducts() {
        try {
            if (window.electronAPI && window.electronAPI.getProducts) {
                this.products = await window.electronAPI.getProducts();
                console.log('Loaded products:', this.products);
            } else {
                console.error('electronAPI.getProducts not available');
                this.products = [];
            }
        } catch (error) {
            console.error('Error loading products:', error);
            this.showToast('Error loading products', 'error');
            this.products = [];
        }
    }

    updateStats() {
        this.stats.totalProducts = this.products.length;
        this.stats.activeTargets = this.products.filter(p => p.currentPrice > p.targetPrice).length;
        
        // Sum up individual product savings
        this.stats.totalSavings = this.products.reduce((total, product) => {
            return total + this.calculateProductSavings(product);
        }, 0);
        
        this.stats.lastUpdate = new Date();

        // Update DOM
        document.getElementById('totalProducts').textContent = this.stats.totalProducts;
        document.getElementById('totalSavings').textContent = `$${this.stats.totalSavings.toFixed(2)}`;
        document.getElementById('activeTargets').textContent = this.stats.activeTargets;
        document.getElementById('lastUpdate').textContent = this.stats.lastUpdate 
            ? this.stats.lastUpdate.toLocaleTimeString() 
            : 'Never';
    }

    setView(view) {
        this.currentView = view;
        
        // Update active button
        document.querySelectorAll('.view-btn').forEach(btn => btn.classList.remove('active'));
        document.getElementById(`${view}View`).classList.add('active');
        
        this.renderProducts();
    }

    renderProducts() {
        const container = document.getElementById('productsContainer');
        
        if (this.products.length === 0) {
            container.innerHTML = `
                <div class="empty-state">
                    <div class="empty-icon">📦</div>
                    <h3>No products yet</h3>
                    <p>Add your first product to start monitoring prices</p>
                    <button class="btn btn-primary" onclick="app.showAddProductModal()">
                        <span class="icon">➕</span>
                        Add Product
                    </button>
                </div>
            `;
            return;
        }

        const productsHtml = this.products.map(product => this.renderProductCard(product)).join('');
        
        container.innerHTML = `
            <div class="products-${this.currentView}">
                ${productsHtml}
            </div>
        `;

        // Product cards are now handled by individual buttons
        // No need for general card click listeners
    }

    renderProductCard(product) {
        const priceChange = this.calculatePriceChange(product);
        const targetReached = product.currentPrice <= product.targetPrice;
        const savings = this.calculateProductSavings(product);
        
        // Build platform results display
        let platformResultsHtml = '';
        if (product.platformResults && product.platformResults.length > 0) {
            platformResultsHtml = product.platformResults.map(result => {
                const platformIcon = result.platform === 'amazon' ? '🟠' : result.platform === 'ebay' ? '🔵' : '🌐';
                const platformName = result.platform.charAt(0).toUpperCase() + result.platform.slice(1);
                return `
                    <div class="platform-result" style="margin: 8px 0; padding: 8px; background: #f8f9fa; border-radius: 4px;">
                        <div style="font-weight: 600; font-size: 0.9rem; margin-bottom: 4px;">
                            ${platformIcon} <strong>${result.title || product.name}</strong>
                        </div>
                        <div style="display: flex; justify-content: space-between; align-items: center;">
                            <a href="#" onclick="openExternalLink('${result.url}'); return false;" 
                               style="color: #0066cc; text-decoration: none; font-size: 0.85rem;">
                                ${platformName} Link →
                            </a>
                            <span style="font-weight: bold; color: #28a745;">$${result.price.toFixed(2)}</span>
                        </div>
                    </div>
                `;
            }).join('');
        }

        return `
            <div class="product-card" data-product-id="${product.id}">
                <div class="product-header">
                    <div>
                        <div class="product-name">${product.name}</div>
                    </div>
                    <button class="btn btn-danger btn-sm" onclick="app.removeProduct('${product.id}', event)">
                        <span class="icon">🗑️</span>
                    </button>
                </div>
                
                <div class="product-price">
                    <span class="current-price">$${product.currentPrice ? product.currentPrice.toFixed(2) : '0.00'}</span>
                    ${priceChange ? `<span class="price-change ${priceChange.direction}">${priceChange.text}</span>` : ''}
                </div>
                
                ${savings > 0 ? `<div class="product-savings" style="
                    color: #28a745; 
                    font-weight: bold; 
                    font-size: 14px;
                    margin: 8px 0; 
                    padding: 5px 8px; 
                    background-color: #d4edda; 
                    border-radius: 4px; 
                    border-left: 3px solid #28a745;
                ">
                    💰 You've saved: $${savings.toFixed(2)}
                </div>` : product.priceHistory && product.priceHistory.length > 0 && product.priceHistory[0].price ? `<div class="product-original" style="
                    color: #6c757d; 
                    font-size: 12px;
                    margin: 5px 0; 
                ">
                    Original price: $${product.priceHistory[0].price.toFixed(2)}
                </div>` : ''}
                
                <div class="product-stats">
                    <span>Target: $${product.targetPrice ? product.targetPrice.toFixed(2) : 'None'}</span>
                    <span>Last checked: ${this.getTimeAgo(product.lastChecked)}</span>
                </div>
                
                <div class="target-indicator ${targetReached ? 'reached' : 'pending'}">
                    <span class="icon">${targetReached ? '✅' : '⏳'}</span>
                    ${targetReached ? 'Target reached!' : 'Monitoring...'}
                </div>
                
                ${platformResultsHtml}
                
                <div class="product-actions" style="margin-top: 10px;">
                    <button class="btn btn-secondary btn-sm" onclick="app.showProductDetail('${product.id}'); event.stopPropagation();">
                        <span class="icon">📊</span> Details
                    </button>
                </div>
            </div>
        `;
    }

    calculatePriceChange(product) {
        if (!product.priceHistory || product.priceHistory.length < 2) return null;
        
        const current = product.currentPrice;
        const previous = product.priceHistory[product.priceHistory.length - 2].price;
        const change = current - previous;
        const changePercent = ((change / previous) * 100).toFixed(1);
        
        if (Math.abs(change) < 0.01) return null;
        
        return {
            direction: change > 0 ? 'positive' : 'negative',
            text: `${change > 0 ? '+' : ''}${changePercent}%`
        };
    }

    calculateProductSavings(product) {
        // Calculate savings for this specific product only
        if (!product.priceHistory || product.priceHistory.length < 1) return 0;
        
        const originalPrice = product.priceHistory[0].price; // First price when added
        const currentPrice = product.currentPrice;          // Latest price
        
        // Only return positive savings (when current price is lower than original)
        return Math.max(0, originalPrice - currentPrice);
    }

    getDomainFromUrl(url) {
        try {
            return new URL(url).hostname.replace('www.', '');
        } catch {
            return 'Unknown';
        }
    }

    getTimeAgo(timestamp) {
        if (!timestamp) return 'Never';
        
        const now = new Date();
        const date = new Date(timestamp);
        const diffMs = now - date;
        const diffMins = Math.floor(diffMs / 60000);
        const diffHours = Math.floor(diffMins / 60);
        const diffDays = Math.floor(diffHours / 24);
        
        if (diffMins < 1) return 'Just now';
        if (diffMins < 60) return `${diffMins}m ago`;
        if (diffHours < 24) return `${diffHours}h ago`;
        return `${diffDays}d ago`;
    }

    showAddProductModal() {
        this.showModal('addProductModal');
        const searchInput = document.getElementById('searchTerms');
        if (searchInput) {
            searchInput.focus();
        }
    }

    showDealFinderModal() {
        this.showModal('dealFinderModal');
        document.getElementById('dealSearchTerms').focus();
    }

    hideDealFinderModal() {
        this.closeModal('dealFinderModal');
        this.hideDealsResults();
    }

    showSettingsModal() {
        this.showModal('settingsModal');
        this.loadSettings();
    }

    showAutoCheckModal() {
        this.showModal('autoCheckModal');
        this.loadAutoCheckSettings();
    }

    hideAutoCheckModal() {
        this.closeModal('autoCheckModal');
    }

    async loadAutoCheckSettings() {
        if (!window.electronAPI?.getSettings) {
            return;
        }

        try {
            const settings = await window.electronAPI.getSettings();
            const intervalInput = document.getElementById('checkInterval');
            const autoCheckEnabled = document.getElementById('autoCheckEnabled');
            const enableNotifications = document.getElementById('enableNotifications');

            if (intervalInput && settings.checkInterval) {
                intervalInput.value = settings.checkInterval;
            }

            if (autoCheckEnabled) {
                autoCheckEnabled.checked = settings.autoCheck !== false;
            }

            if (enableNotifications) {
                enableNotifications.checked = settings.enableNotifications !== false;
            }
        } catch (error) {
            console.error('Error loading auto-check settings:', error);
        }
    }

    async handleAutoCheckSettings(event) {
        event.preventDefault();

        const formData = new FormData(event.target);
        const checkInterval = parseInt(formData.get('checkInterval') || '60', 10);
        const autoCheckEnabled = formData.get('autoCheckEnabled') === 'on';
        const enableNotifications = formData.get('enableNotifications') === 'on';

        if (isNaN(checkInterval) || checkInterval < 1) {
            this.showToast('Check interval must be at least 1 minute.', 'error');
            return;
        }

        try {
            await window.electronAPI.updateSettings({
                checkInterval,
                autoCheck: autoCheckEnabled,
                enableNotifications
            });

            this.hideAutoCheckModal();
            this.showToast('Auto-check preferences saved!', 'success');
        } catch (error) {
            console.error('Error saving auto-check settings:', error);
            this.showToast('Error saving preferences.', 'error');
        }
    }

    async showProductDetail(productId) {
        const product = this.products.find(p => p.id === productId);
        if (!product) {
            console.error('Product not found:', productId);
            return;
        }

        console.log('Showing detail for product:', product);

        document.getElementById('detailProductName').textContent = product.name;
        document.getElementById('detailCurrentPrice').textContent = `$${product.currentPrice ? product.currentPrice.toFixed(2) : '0.00'}`;
        document.getElementById('detailTargetPrice').textContent = `$${product.targetPrice ? product.targetPrice.toFixed(2) : 'None'}`;

        // Display platform results in detail modal
        const detailUrl = document.getElementById('detailProductUrl');
        if (detailUrl && product.platformResults && product.platformResults.length > 0) {
            const platformLinksHtml = product.platformResults.map(result => {
                const platformIcon = result.platform === 'amazon' ? '🟠' : result.platform === 'ebay' ? '🔵' : '🌐';
                return `<div style="margin: 4px 0;">
                    ${platformIcon} <a href="#" onclick="openExternalLink('${result.url}'); return false;" 
                       style="color: #0066cc; text-decoration: underline;">${result.title || product.name}</a> - $${result.price.toFixed(2)}
                </div>`;
            }).join('');
            detailUrl.innerHTML = platformLinksHtml;
        } else if (detailUrl) {
            const productUrl = product.url || product.primaryUrl || '';
            detailUrl.textContent = productUrl ? this.getDomainFromUrl(productUrl) : 'N/A';
            detailUrl.dataset.url = productUrl;
            detailUrl.onclick = () => {
                if (productUrl) {
                    openExternalLink(productUrl);
                }
            };
        }

        document.getElementById('detailLastChecked').textContent = product.lastChecked ? new Date(product.lastChecked).toLocaleString() : 'Never';
        document.getElementById('detailCreated').textContent = product.createdAt ? new Date(product.createdAt).toLocaleDateString() : 'Unknown';

        // Stats and history
        document.getElementById('detailLowestPrice').textContent = product.priceHistory && product.priceHistory.length ? `$${Math.min(...product.priceHistory.map(p => p.price || 0)).toFixed(2)}` : '-';
        document.getElementById('detailHighestPrice').textContent = product.priceHistory && product.priceHistory.length ? `$${Math.max(...product.priceHistory.map(p => p.price || 0)).toFixed(2)}` : '-';
        document.getElementById('detailAveragePrice').textContent = product.priceHistory && product.priceHistory.length
            ? `$${(product.priceHistory.reduce((sum, entry) => sum + (entry.price || 0), 0) / product.priceHistory.length).toFixed(2)}`
            : '-';
        document.getElementById('detailPriceChecks').textContent = product.priceHistory ? product.priceHistory.length : 0;

        this.renderPriceHistory(product.priceHistory || []);

        const openButton = document.getElementById('openProductUrl');
        if (openButton) {
            openButton.onclick = () => {
                if (productUrl) {
                    openExternalLink(productUrl);
                }
            };
        }

        const removeButton = document.getElementById('removeProductBtn');
        if (removeButton) {
            removeButton.onclick = (event) => this.removeProduct(product.id, event);
        }

        this.showModal('productDetailModal');
    }

    renderPriceHistory(history) {
        const container = document.getElementById('priceHistoryList');

        if (!container) {
            return;
        }

        if (!history.length) {
            container.innerHTML = '<p>No price history available</p>';
            return;
        }

        const historyHtml = history
            .slice()
            .sort((a, b) => new Date(b.timestamp) - new Date(a.timestamp))
            .slice(0, 10)
            .map(entry => `
                <div class="history-item">
                    <span class="history-price">$${entry.price ? entry.price.toFixed(2) : '0.00'}</span>
                    <span class="history-date">${entry.timestamp ? new Date(entry.timestamp).toLocaleString() : 'Unknown'}</span>
                </div>
            `)
            .join('');

        container.innerHTML = historyHtml;
    }

    async handleAddProduct(event) {
        event.preventDefault();
        
        const formData = new FormData(event.target);
        const searchTerms = formData.get('searchTerms')?.trim() || '';
        const productName = formData.get('productName')?.trim() || '';
        const targetPrice = parseFloat(formData.get('targetPrice') || '0');
        const searchAmazon = document.getElementById('searchAmazon').checked;
        const searchEbay = document.getElementById('searchEbay').checked;
        const searchGoogle = document.getElementById('searchGoogle').checked;

        console.log('Frontend validation - productData:', { searchTerms, productName, targetPrice, searchAmazon, searchEbay, searchGoogle });

        // Validate input
        if (!searchTerms || !productName) {
            this.showToast('Please fill in search terms and product name', 'error');
            return;
        }

        if (!searchAmazon && !searchEbay && !searchGoogle) {
            this.showToast('Please select at least one platform to search', 'error');
            return;
        }

        if (targetPrice && (isNaN(targetPrice) || targetPrice <= 0)) {
            this.showToast('Target price must be a valid number greater than 0', 'error');
            return;
        }

        // Validate search terms (basic sanity check)
        if (searchTerms.length < 3) {
            this.showToast('Search terms must be at least 3 characters long', 'error');
            return;
        }

        if (searchTerms.length > 200) {
            this.showToast('Search terms are too long. Please use shorter terms.', 'error');
            return;
        }

        try {
            this.showLoading(true);
            
            const productData = {
                searchTerms,
                name: productName,
                targetPrice: targetPrice || null,
                platforms: {
                    amazon: searchAmazon,
                    ebay: searchEbay,
                    google: searchGoogle
                }
            };
            
            const result = await window.electronAPI.addProduct(productData);
            
            if (result.success) {
                this.closeModal(document.getElementById('addProductModal'));
                event.target.reset();
                this.showToast('Product added successfully!', 'success');
                
                // Refresh the products list
                await this.loadProducts();
                this.renderProducts();
                this.updateStats();
            } else {
                this.showToast(result.error || 'Error adding product', 'error');
            }
        } catch (error) {
            console.error('Error adding product:', error);
            this.showToast('Error adding product. Please try again.', 'error');
        } finally {
            this.showLoading(false);
        }
    }

    async handleDealFinder(event) {
        event.preventDefault();

        const formData = new FormData(event.target);
        let searchTerms = formData.get('dealSearchTerms')?.trim() || '';
        const maxPrice = parseFloat(formData.get('maxPrice') || '50');
        const minBids = parseInt(formData.get('minBids') || '0');
        const endingSoon = parseInt(formData.get('endingSoon') || '24');

        // Default to searching everything if no search terms provided or only whitespace
        if (!searchTerms || searchTerms.trim() === '') {
            searchTerms = '*';
            console.log('No search terms provided, searching for everything');
        }

        if (isNaN(maxPrice) || maxPrice <= 0) {
            this.showToast('Maximum price must be a valid number greater than 0', 'error');
            return;
        }

        if (isNaN(minBids) || minBids < 0) {
            this.showToast('Minimum bids must be a valid number', 'error');
            return;
        }

        if (isNaN(endingSoon) || endingSoon < 1 || endingSoon > 72) {
            this.showToast('Ending soon must be between 1 and 72 hours', 'error');
            return;
        }

        try {
            this.showLoading(true);

            const searchParams = {
                search: searchTerms,
                maxPrice: maxPrice,
                minBids: minBids,
                endingSoon: endingSoon
            };

            console.log('Searching for deals with params:', searchParams);
            const result = await window.electronAPI.findEbayDeals(searchParams);

            if (result.success) {
                this.displayDeals(result.deals);
                this.showToast(`Found ${result.deals.length} potential deals!`, 'success');
            } else {
                this.showToast(result.error || 'Error finding deals', 'error');
                this.hideDealsResults();
            }
        } catch (error) {
            console.error('Error finding deals:', error);
            this.showToast('Error finding deals. Please try again.', 'error');
            this.hideDealsResults();
        } finally {
            this.showLoading(false);
        }
    }

    displayDeals(deals) {
        const resultsContainer = document.getElementById('dealsResults');
        const dealsList = document.getElementById('dealsList');

        if (deals.length === 0) {
            dealsList.innerHTML = '<p>No deals found matching your criteria. Try adjusting your search terms or filters.</p>';
        } else {
            const dealsHtml = deals.map((deal, index) => `
                <div class="deal-item">
                    <div class="deal-header">
                        <span class="deal-number">${index + 1}.</span>
                        <span class="deal-title">${deal.title}</span>
                        <span class="deal-price">$${deal.price.toFixed(2)}</span>
                    </div>
                    <div class="deal-details">
                        <span class="deal-bids">${deal.bid_count} bids</span>
                        ${deal.end_time ? `<span class="deal-time">Ends: ${new Date(deal.end_time).toLocaleString()}</span>` : ''}
                    </div>
                    <div class="deal-actions">
                        <button class="btn btn-primary btn-sm" onclick="openExternalLink('${deal.url}')">
                            <span class="icon">🛒</span> View on eBay
                        </button>
                    </div>
                </div>
            `).join('');

            dealsList.innerHTML = dealsHtml;
        }

        resultsContainer.style.display = 'block';
    }

    hideDealsResults() {
        const resultsContainer = document.getElementById('dealsResults');
        resultsContainer.style.display = 'none';
    }

    async handleSettings(event) {
        event.preventDefault();
        
        const formData = new FormData(event.target);
        const settings = {
            checkInterval: parseInt(formData.get('checkInterval')),
            enableNotifications: formData.get('enableNotifications') === 'on',
            autoStart: formData.get('autoStart') === 'on'
        };

        try {
            await window.electronAPI.updateSettings(settings);
            this.closeModal(document.getElementById('settingsModal'));
            this.showToast('Settings saved successfully!', 'success');
        } catch (error) {
            console.error('Error saving settings:', error);
            this.showToast('Error saving settings', 'error');
        }
    }

    async loadSettings() {
        try {
            const settings = await window.electronAPI.getSettings();
            document.getElementById('checkInterval').value = settings.checkInterval || 60;
            document.getElementById('enableNotifications').checked = settings.enableNotifications !== false;
            document.getElementById('autoStart').checked = settings.autoStart !== false;
        } catch (error) {
            console.error('Error loading settings:', error);
        }
    }

    async removeProduct(productId, event) {
        event.stopPropagation(); // Prevent card click
        
        if (!confirm('Are you sure you want to remove this product?')) {
            return;
        }

        try {
            await window.electronAPI.removeProduct(productId);
            this.products = this.products.filter(p => p.id !== productId);
            this.renderProducts();
            this.updateStats();
            this.showToast('Product removed successfully!', 'success');
        } catch (error) {
            console.error('Error removing product:', error);
            this.showToast('Error removing product', 'error');
        }
    }

    async refreshAllProducts() {
        try {
            this.showLoading(true);
            await window.electronAPI.refreshAllProducts();
            await this.loadProducts();
            this.renderProducts();
            this.updateStats();
            this.showToast('All products refreshed!', 'success');
        } catch (error) {
            console.error('Error refreshing products:', error);
            this.showToast('Error refreshing products', 'error');
        } finally {
            this.showLoading(false);
        }
    }

    async testAddProduct() {
        console.log('Test search: iPhone 13 Mini');
        try {
            this.showLoading(true);
            
            const testProductData = {
                searchTerms: 'apple iphone 13 mini 128gb unlocked',
                name: 'Apple iPhone 13 Mini 128GB',
                targetPrice: 400,
                platforms: {
                    amazon: true,
                    ebay: true,
                    google: true
                }
            };
            
            console.log('Testing search with:', testProductData);
            const result = await window.electronAPI.addProduct(testProductData);
            console.log('Search result:', result);
            
            if (result.success) {
                this.showToast('iPhone 13 Mini search completed successfully!', 'success');
                await this.loadProducts();
                this.renderProducts();
                this.updateStats();
            } else {
                this.showToast(result.error || 'Error searching for iPhone 13 Mini', 'error');
            }
        } catch (error) {
            console.error('Error testing iPhone search:', error);
            this.showToast('Error testing iPhone search: ' + error.message, 'error');
        } finally {
            this.showLoading(false);
        }
    }

    async testAddEbayProduct() {
        console.log('Test search: MacBook Pro');
        try {
            this.showLoading(true);
            
            const testProductData = {
                searchTerms: 'macbook pro 14 inch m3',
                name: 'MacBook Pro 14" M3',
                targetPrice: 1800,
                platforms: {
                    amazon: true,
                    ebay: true,
                    google: true
                }
            };
            
            console.log('Testing MacBook search with:', testProductData);
            const result = await window.electronAPI.addProduct(testProductData);
            console.log('MacBook search result:', result);
            
            if (result.success) {
                this.showToast('MacBook Pro search completed successfully!', 'success');
                await this.loadProducts();
                this.renderProducts();
                this.updateStats();
            } else {
                this.showToast(result.error || 'Error searching for MacBook Pro', 'error');
            }
        } catch (error) {
            console.error('Error testing MacBook search:', error);
            this.showToast('Error testing MacBook search: ' + error.message, 'error');
        } finally {
            this.showLoading(false);
        }
    }

    async clearAllProducts() {
        try {
            // Ask for confirmation
            const confirmed = confirm('Are you sure you want to clear all products? This action cannot be undone.');
            if (!confirmed) return;
            
            this.showLoading(true);
            const result = await window.electronAPI.clearAllProducts();
            
            if (result.success) {
                this.showToast('All products cleared successfully!', 'success');
                await this.loadProducts();
                this.renderProducts();
                this.updateStats();
            } else {
                this.showToast('Error clearing products', 'error');
            }
        } catch (error) {
            console.error('Error clearing products:', error);
            this.showToast('Error clearing products: ' + error.message, 'error');
        } finally {
            this.showLoading(false);
        }
    }

    setupAutoRefresh() {
        // Refresh product data every 5 minutes
        setInterval(async () => {
            await this.loadProducts();
            this.renderProducts();
            this.updateStats();
        }, 5 * 60 * 1000);
    }

    showModal(modalId) {
        const modal = document.getElementById(modalId);
        modal.classList.add('show');
        
        // Focus first input
        const firstInput = modal.querySelector('input');
        if (firstInput) {
            setTimeout(() => firstInput.focus(), 100);
        }
    }

    closeModal(modal) {
        if (typeof modal === 'string') {
            modal = document.getElementById(modal);
        }
        modal.classList.remove('show');
    }

    showLoading(show) {
        const overlay = document.getElementById('loadingOverlay');
        if (show) {
            overlay.classList.add('show');
        } else {
            overlay.classList.remove('show');
        }
    }

    showToast(message, type = 'info') {
        const toast = document.createElement('div');
        toast.className = `toast ${type}`;
        toast.textContent = message;
        
        const container = document.getElementById('toastContainer');
        container.appendChild(toast);
        
        // Show toast
        setTimeout(() => toast.classList.add('show'), 100);
        
        // Remove toast after 5 seconds
        setTimeout(() => {
            toast.classList.remove('show');
            setTimeout(() => container.removeChild(toast), 300);
        }, 5000);
    }
}

// Initialize app when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    window.app = new PriceMonitorApp();
});

// Utility functions for inline handlers
function openExternalLink(url) {
    window.electronAPI.openExternal(url);
}

function hideAddProductModal() {
    window.app?.closeModal('addProductModal');
}

function hideProductDetailModal() {
    window.app?.closeModal('productDetailModal');
}

function hideAutoCheckModal() {
    window.app?.hideAutoCheckModal();
}

function hideDealFinderModal() {
    window.app?.closeModal('dealFinderModal');
}

// Handle keyboard shortcuts
document.addEventListener('keydown', (e) => {
    // Escape to close modals
    if (e.key === 'Escape') {
        const openModal = document.querySelector('.modal-overlay.show');
        if (openModal) {
            window.app.closeModal(openModal);
        }
    }
    
    // Cmd/Ctrl + N to add new product
    if ((e.metaKey || e.ctrlKey) && e.key === 'n') {
        e.preventDefault();
        window.app.showAddProductModal();
    }
    
    // Cmd/Ctrl + R to refresh
    if ((e.metaKey || e.ctrlKey) && e.key === 'r') {
        e.preventDefault();
        window.app.refreshAllProducts();
    }
    
    // Cmd/Ctrl + , to open settings
    if ((e.metaKey || e.ctrlKey) && e.key === ',') {
        e.preventDefault();
        window.app.showSettingsModal();
    }
});
