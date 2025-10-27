// Test scraping functionality for all supported platforms
const https = require('https');
const zlib = require('zlib');
const { URL } = require('url');

// Test configuration
const TEST_CONFIG = {
    platforms: [
        {
            name: 'Amazon',
            searchUrl: 'https://www.amazon.com/s?k=apple+iphone+13+mini+128gb+unlocked',
            patterns: [
                /<span class="a-price-whole">(\d+)<\/span>/gi,
                /<span[^>]*class="[^"]*a-price[^"]*"[^>]*>\$?(\d+\.?\d*)<\/span>/gi,
                />\$(\d{2,4}\.?\d{0,2})</gi
            ]
        },
        {
            name: 'eBay',
            searchUrl: 'https://www.ebay.com/sch/i.html?_nkw=apple+iphone+13+mini+128gb+unlocked',
            patterns: [
                /<span class="s-item__price"[^>]*>\$(\d+\.?\d*)<\/span>/gi,
                /<span class="notranslate">\$(\d+\.?\d*)<\/span>/gi,
                /\$(\d{2,4}\.?\d{0,2})<\/span>/gi
            ]
        },
        {
            name: 'Walmart',
            searchUrl: 'https://www.walmart.com/search?q=apple+iphone+13+mini',
            patterns: [
                /<span[^>]*class="[^"]*price-main[^"]*"[^>]*>[\s\S]*?\$(\d+)\.(\d{2})/gi,
                /"priceInfo":\{"linePrice":"(\d+\.?\d*)"/gi,
                /\$(\d+)\.(\d{2})/gi
            ]
        },
        {
            name: 'Best Buy',
            searchUrl: 'https://www.bestbuy.com/site/searchpage.jsp?st=apple+iphone+13+mini',
            patterns: [
                /<span[^>]*class="[^"]*priceView-hero-price[^"]*"[^>]*>[\s\S]*?\$(\d+)\.(\d{2})/gi,
                /"salePrice":(\d+\.?\d*)/gi,
                /\$(\d+)\.(\d{2})/gi
            ]
        },
        {
            name: 'Target',
            searchUrl: 'https://www.target.com/s?searchTerm=apple+iphone+13+mini',
            patterns: [
                /<span[^>]*data-test="[^"]*product-price[^"]*"[^>]*>[\s\S]*?\$(\d+)\.(\d{2})/gi,
                /"price":\{"current_retail":(\d+\.?\d*)/gi,
                /\$(\d+)\.(\d{2})/gi
            ]
        }
    ]
};

async function testPlatform(platform) {
    console.log(`\n${'='.repeat(60)}`);
    console.log(`🧪 Testing: ${platform.name}`);
    console.log(`URL: ${platform.searchUrl}`);
    console.log('='.repeat(60));

    return new Promise((resolve) => {
        try {
            const urlObj = new URL(platform.searchUrl);

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
                timeout: 20000
            };

            const req = https.request(options, (res) => {
                console.log(`📡 Response: ${res.statusCode} from ${urlObj.hostname}`);

                if (res.statusCode !== 200) {
                    console.log(`❌ HTTP ${res.statusCode} - Failed`);
                    resolve({ platform: platform.name, success: false, error: `HTTP ${res.statusCode}` });
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

                        // Try to extract prices using platform-specific patterns
                        let prices = [];

                        platform.patterns.forEach((pattern, index) => {
                            let match;
                            const patternPrices = [];
                            while ((match = pattern.exec(html)) !== null) {
                                let price;
                                if (match[2] && !isNaN(match[2])) {
                                    price = parseFloat(`${match[1]}.${match[2]}`);
                                } else {
                                    price = parseFloat(match[1]);
                                }
                                if (price >= 50 && price <= 1500) {
                                    patternPrices.push(price);
                                }
                            }
                            if (patternPrices.length > 0) {
                                console.log(`  Pattern ${index + 1}: Found ${patternPrices.length} prices`);
                                prices.push(...patternPrices);
                            }
                        });

                        prices = [...new Set(prices)].sort((a, b) => a - b);

                        if (prices.length > 0) {
                            console.log(`💰 Found ${prices.length} unique prices: [${prices.slice(0, 10).join(', ')}${prices.length > 10 ? '...' : ''}]`);
                            const iPhonePrices = prices.filter(p => p >= 200 && p <= 800);
                            const selectedPrice = iPhonePrices.length > 0 ? iPhonePrices[0] : prices[0];
                            console.log(`✅ Selected price: $${selectedPrice}`);
                            resolve({ platform: platform.name, success: true, price: selectedPrice, totalFound: prices.length });
                        } else {
                            console.log(`⚠️  No prices found`);
                            resolve({ platform: platform.name, success: false, error: 'No prices extracted' });
                        }
                    } catch (parseError) {
                        console.error('❌ Parse error:', parseError.message);
                        resolve({ platform: platform.name, success: false, error: parseError.message });
                    }
                });

                stream.on('error', (streamError) => {
                    console.error('❌ Stream error:', streamError.message);
                    resolve({ platform: platform.name, success: false, error: streamError.message });
                });
            });

            req.on('timeout', () => {
                console.log('⏱️  Request timeout');
                req.destroy();
                resolve({ platform: platform.name, success: false, error: 'Timeout' });
            });

            req.on('error', (error) => {
                console.error('❌ Request error:', error.message);
                resolve({ platform: platform.name, success: false, error: error.message });
            });

            req.end();

        } catch (error) {
            console.error('❌ Test error:', error.message);
            resolve({ platform: platform.name, success: false, error: error.message });
        }
    });
}

async function runTests() {
    console.log('\n🚀 Starting Platform Scraping Tests...');
    console.log('Testing all supported e-commerce platforms\n');

    const results = [];

    // Test each platform sequentially with delays to avoid rate limiting
    for (const platform of TEST_CONFIG.platforms) {
        const result = await testPlatform(platform);
        results.push(result);

        // Wait 3 seconds between tests to avoid rate limiting
        if (platform !== TEST_CONFIG.platforms[TEST_CONFIG.platforms.length - 1]) {
            console.log('\n⏳ Waiting 3 seconds before next test...');
            await new Promise(resolve => setTimeout(resolve, 3000));
        }
    }

    // Print summary
    console.log('\n' + '='.repeat(60));
    console.log('📊 TEST SUMMARY');
    console.log('='.repeat(60));

    const successful = results.filter(r => r.success);
    const failed = results.filter(r => !r.success);

    console.log(`\n✅ Successful: ${successful.length}/${results.length}`);
    successful.forEach(r => {
        console.log(`   • ${r.platform}: $${r.price} (${r.totalFound} prices found)`);
    });

    if (failed.length > 0) {
        console.log(`\n❌ Failed: ${failed.length}/${results.length}`);
        failed.forEach(r => {
            console.log(`   • ${r.platform}: ${r.error}`);
        });
    }

    console.log('\n' + '='.repeat(60));
    console.log(`Overall Success Rate: ${Math.round((successful.length / results.length) * 100)}%`);
    console.log('='.repeat(60) + '\n');
}

// Run the tests
runTests().catch(console.error);
