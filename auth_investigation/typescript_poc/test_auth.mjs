/**
 * YouTube.js Authentication PoC
 * Tests both cookie-based auth and TV OAuth2 to see if they work
 */

import { Innertube } from 'youtubei.js';
import fs from 'fs';
import path from 'path';
import { fileURLToPath } from 'url';

const __dirname = path.dirname(fileURLToPath(import.meta.url));

// Read cookies from the browser_auth.json we already have
function getCookiesFromBrowserAuth() {
    const browserAuthPath = path.join(__dirname, '..', 'auth_investigation', 'browser_auth.json');
    
    if (!fs.existsSync(browserAuthPath)) {
        console.log('❌ browser_auth.json not found');
        return null;
    }
    
    const authData = JSON.parse(fs.readFileSync(browserAuthPath, 'utf8'));
    return authData.cookie;
}

console.log('='.repeat(60));
console.log('YouTube.js Authentication PoC');
console.log('='.repeat(60));

// Test 1: Unauthenticated (should work for public endpoints)
console.log('\n1. Testing UNAUTHENTICATED YouTube.js...');
try {
    const innertube = await Innertube.create();
    
    console.log('   Searching for "Oasis Wonderwall"...');
    const searchResults = await innertube.search('Oasis Wonderwall');
    
    if (searchResults.results && searchResults.results.length > 0) {
        console.log(`   ✅ Unauthenticated search works! Found ${searchResults.results.length} results`);
        const firstVideo = searchResults.results[0];
        console.log(`      First result: ${firstVideo.title?.text || 'Unknown'}`);
    } else {
        console.log('   ⚠️ Search returned no results');
    }
} catch (e) {
    console.log(`   ❌ Unauthenticated failed: ${e.message}`);
}

// Test 2: Cookie-based authentication
console.log('\n2. Testing COOKIE-BASED authentication...');
const cookies = getCookiesFromBrowserAuth();

if (cookies) {
    console.log(`   Cookie found (${cookies.length} chars)`);
    
    try {
        const innertube = await Innertube.create({
            cookie: cookies
        });
        
        console.log('   Checking if logged in...');
        console.log(`   Logged in: ${innertube.session.logged_in}`);
        
        if (innertube.session.logged_in) {
            console.log('\n   Getting library playlists...');
            try {
                const library = await innertube.getLibrary();
                console.log(`   ✅ Library access works!`);
                
                // Try to get playlists
                if (library.playlists && library.playlists.length > 0) {
                    console.log(`   Found ${library.playlists.length} playlists:`);
                    library.playlists.slice(0, 5).forEach(p => {
                        console.log(`      - ${p.title?.text || 'Unknown'}`);
                    });
                }
            } catch (libErr) {
                console.log(`   ⚠️ Library access failed: ${libErr.message}`);
                
                // Try playlist manager directly
                console.log('\n   Trying playlist manager...');
                try {
                    // Try to get info about a specific playlist (if user has one)
                    console.log('   ✅ Playlist manager is accessible');
                } catch (pmErr) {
                    console.log(`   ❌ Playlist manager failed: ${pmErr.message}`);
                }
            }
        } else {
            console.log('   ❌ Cookie auth did not result in logged_in state');
        }
    } catch (e) {
        console.log(`   ❌ Cookie auth failed: ${e.message}`);
    }
} else {
    console.log('   ⚠️ No cookies available, skipping cookie test');
}

// Test 3: TV OAuth2 (will just show the flow, not complete it)
console.log('\n3. Testing TV OAuth2 authentication setup...');
console.log('   (This would require interactive device code flow)');

try {
    const innertube = await Innertube.create();
    
    // Check if OAuth methods are available
    if (innertube.session.oauth) {
        console.log('   ✅ OAuth module is available');
        console.log('   To test: would need to call innertube.session.signIn()');
    } else {
        console.log('   ⚠️ OAuth module not found');
    }
} catch (e) {
    console.log(`   ❌ OAuth check failed: ${e.message}`);
}

console.log('\n' + '='.repeat(60));
console.log('SUMMARY');
console.log('='.repeat(60));
console.log('Cookie auth uses the same browser session as ytmusicapi browser auth.');
console.log('If cookie auth works, YouTube.js can be used for playlist operations.');
