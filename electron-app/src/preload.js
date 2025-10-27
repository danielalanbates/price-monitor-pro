const { contextBridge, ipcRenderer } = require('electron');

// Expose safe IPC methods to renderer process
contextBridge.exposeInMainWorld('electronAPI', {
    // Product management
    addProduct: (productData) => ipcRenderer.invoke('add-product', productData),
    removeProduct: (productId) => ipcRenderer.invoke('remove-product', productId),
    getProducts: () => ipcRenderer.invoke('get-products'),
    refreshAllProducts: () => ipcRenderer.invoke('refresh-all-products'),
    clearAllProducts: () => ipcRenderer.invoke('clear-all-products'),
    
    // Settings
    getSettings: () => ipcRenderer.invoke('get-settings'),
    updateSettings: (settings) => ipcRenderer.invoke('update-settings', settings),
    
    // External links
    openExternal: (url) => ipcRenderer.invoke('open-external', url),
    
    // Test methods
    testAddProduct: () => ipcRenderer.invoke('test-add-product'),
    testAddEbayProduct: () => ipcRenderer.invoke('test-add-ebay-product'),

    // Deal finder
    findEbayDeals: (searchParams) => ipcRenderer.invoke('find-ebay-deals', searchParams),

    // Event listeners for real-time updates
    onProductAdded: (callback) => ipcRenderer.on('product-added', (event, product) => callback(product)),
    onProductUpdated: (callback) => ipcRenderer.on('product-updated', (event, product) => callback(product)),
    onPriceUpdate: (callback) => ipcRenderer.on('price-update', (event, data) => callback(data)),
    onError: (callback) => ipcRenderer.on('error', (event, error) => callback(error)),
    onShowDealFinder: (callback) => ipcRenderer.on('show-deal-finder', () => callback()),

    // Remove listeners
    removeAllListeners: (channel) => ipcRenderer.removeAllListeners(channel)
});
