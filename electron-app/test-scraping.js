// Test real scraping functionality
const https = require('https');
const zlib = require('zlib');
const { URL } = require('url');

async function testScraping() {
    console.log('🧪 Testing real web scraping...\n');
    
    const urls = [
        'https://www.amazon.com/s?k=apple+iphone+13+mini+128gb+unlocked',
        'https://www.ebay.com/sch/i.html?_nkw=apple+iphone+13+mini+128gb+unlocked'
    ];
    
    for (const url of urls) {
        console.log(`\n🔍 Testing: ${url.includes('amazon') ? 'Amazon' : 'eBay'}`);
        console.log(`URL: ${url}`);
        
        try {
            const price = await scrapePrice(url);
            if (price) {
                console.log(`✅ Success! Extracted price: $${price}`);
            } else {
                console.log(`❌ Failed to extract price`);
            }
        } catch (error) {
            console.log(`❌ Error: ${error.message}`);
        }
    }
}

async function scrapePrice(url) {
    return new Promise((resolve) => {
        try {
            const urlObj = new URL(url);
            const isHttps = urlObj.protocol === 'https:';
            const httpModule = https;
            
            const headers = {
                'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
                'Accept-Language': 'en-US,en;q=0.5',
                'Accept-Encoding': 'gzip, deflate, br',
                'DNT': '1',
                'Connection': 'keep-alive',
                'Upgrade-Insecure-Requests': '1',
                'Cache-Control': 'max-age=0'
            };
            
            const options = {
                hostname: urlObj.hostname,
                port: 443,
                path: urlObj.pathname + urlObj.search,
                method: 'GET',
                headers: headers,
                timeout: 15000
            };
            
            const req = httpModule.request(options, (res) => {
                console.log(`📡 Response: ${res.statusCode} from ${urlObj.hostname}`);
                
                if (res.statusCode !== 200) {
                    resolve(null);
                    return;
                }
                
                let chunks = [];
                let stream = res;
                
                if (res.headers['content-encoding'] === 'gzip') {
                    stream = zlib.createGunzip();
                    res.pipe(stream);
                } else if (res.headers['content-encoding'] === 'deflate') {
                    stream = zlib.createInflate();
                    res.pipe(stream);
                }
                
                stream.on('data', (chunk) => {
                    chunks.push(chunk);
                });
                
                stream.on('end', () => {
                    try {
                        const html = Buffer.concat(chunks).toString('utf8');
                        console.log(`📄 Received ${html.length} characters`);
                        
                        const price = extractPriceFromHtml(html, url);
                        resolve(price);
                    } catch (parseError) {
                        console.error('Parse error:', parseError.message);
                        resolve(null);
                    }
                });
                
                stream.on('error', () => resolve(null));
            });
            
            req.on('timeout', () => {
                console.log('⏱️ Request timeout');
                req.destroy();
                resolve(null);
            });
            
            req.on('error', (error) => {
                console.error('Request error:', error.message);
                resolve(null);
            });
            
            req.end();
            
        } catch (error) {
            console.error('Scraping error:', error.message);
            resolve(null);
        }
    });
}

function extractPriceFromHtml(html, url) {
    try {
        let prices = [];
        
        if (url.includes('amazon.')) {
            console.log('📦 Extracting Amazon prices...');
            
            const amazonPatterns = [
                /<span class="a-price-whole">(\d+)<\/span>/gi,
                /<span[^>]*class="[^"]*a-price[^"]*"[^>]*>\$?(\d+\.?\d*)<\/span>/gi,
                />\$(\d{2,4}\.?\d{0,2})</gi
            ];
            
            amazonPatterns.forEach((pattern, index) => {
                let match;
                while ((match = pattern.exec(html)) !== null) {
                    const price = parseFloat(match[1]);
                    if (price >= 50 && price <= 1500) {
                        prices.push(price);
                    }
                }
            });
            
        } else if (url.includes('ebay.')) {
            console.log('🛒 Extracting eBay prices...');
            
            const ebayPatterns = [
                /<span class="s-item__price"[^>]*>\$(\d+\.?\d*)<\/span>/gi,
                /<span class="notranslate">\$(\d+\.?\d*)<\/span>/gi,
                /\$(\d{2,4}\.?\d{0,2})<\/span>/gi
            ];
            
            ebayPatterns.forEach((pattern, index) => {
                let match;
                while ((match = pattern.exec(html)) !== null) {
                    const price = parseFloat(match[1]);
                    if (price >= 50 && price <= 1500) {
                        prices.push(price);
                    }
                }
            });
        }
        
        prices = [...new Set(prices)].sort((a, b) => a - b);
        console.log(`💰 Found prices: [${prices.slice(0, 10).join(', ')}${prices.length > 10 ? '...' : ''}]`);
        
        if (prices.length > 0) {
            const iPhonePrices = prices.filter(p => p >= 200 && p <= 800);
            const selectedPrice = iPhonePrices.length > 0 ? iPhonePrices[0] : prices[0];
            console.log(`✅ Selected: $${selectedPrice}`);
            return selectedPrice;
        }
        
        return null;
        
    } catch (error) {
        console.error('Extraction error:', error.message);
        return null;
    }
}

// Run the test
testScraping().catch(console.error);