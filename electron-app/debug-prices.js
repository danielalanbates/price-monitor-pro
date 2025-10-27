// Debug price extraction - test what's actually in the HTML
const https = require('https');
const zlib = require('zlib');
const { URL } = require('url');

async function debugPriceExtraction() {
    const searchUrl = 'https://www.amazon.com/s?k=macbook%20pro%2014%20inch%20m3&ref=sr_pg_1';
    
    console.log('🔍 Testing:', searchUrl);
    
    const urlObj = new URL(searchUrl);
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
    
    return new Promise((resolve) => {
        const req = https.request(options, (res) => {
            console.log(`Response: ${res.statusCode}`);
            
            let chunks = [];
            let stream = res;
            
            if (res.headers['content-encoding'] === 'gzip') {
                stream = zlib.createGunzip();
                res.pipe(stream);
            }
            
            stream.on('data', (chunk) => {
                chunks.push(chunk);
            });
            
            stream.on('end', () => {
                const html = Buffer.concat(chunks).toString('utf8');
                console.log(`📄 HTML length: ${html.length}`);
                
                // Find all price-like patterns
                const pricePatterns = [
                    /\$(\d{3,4})/g,  // $999, $1999 etc.
                    /<span[^>]*class="[^"]*a-price[^"]*"[^>]*>([^<]*)<\/span>/gi,
                    /<span class="a-price-whole">(\d+)<\/span>/gi,
                    /<span class="a-price-symbol">\$<\/span><span class="a-price-whole">(\d+)<\/span>/gi
                ];
                
                console.log('\n💰 All prices found:');
                pricePatterns.forEach((pattern, index) => {
                    const matches = [...html.matchAll(pattern)];
                    if (matches.length > 0) {
                        console.log(`\nPattern ${index + 1}: ${pattern}`);
                        matches.slice(0, 10).forEach((match, i) => {
                            console.log(`  ${i + 1}. ${match[1]}`);
                        });
                        if (matches.length > 10) {
                            console.log(`  ... and ${matches.length - 10} more`);
                        }
                    }
                });
                
                // Look for data-component-type="s-search-result"
                const searchResults = html.match(/<div[^>]*data-component-type="s-search-result"[^>]*>[\s\S]*?<\/div>/gi);
                if (searchResults) {
                    console.log(`\n📦 Found ${searchResults.length} search result containers`);
                    
                    // Check first result for prices
                    if (searchResults[0]) {
                        console.log('\n🎯 First search result:');
                        const firstResult = searchResults[0];
                        const pricesInFirst = [...firstResult.matchAll(/\$(\d{3,4})/g)];
                        console.log(`Prices in first result: ${pricesInFirst.map(m => '$' + m[1]).join(', ')}`);
                    }
                }
                
                resolve();
            });
        });
        
        req.on('error', (error) => {
            console.error('Request error:', error.message);
            resolve();
        });
        
        req.end();
    });
}

debugPriceExtraction().catch(console.error);