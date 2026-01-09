/**
 * YouTube.js - Test with YouTube Music client
 */

import { Innertube } from 'youtubei.js';
import fs from 'fs';
import path from 'path';
import { fileURLToPath } from 'url';

const __dirname = path.dirname(fileURLToPath(import.meta.url));

function getCookiesFromBrowserAuth() {
    const browserAuthPath = path.join(__dirname, '..', 'auth_investigation', 'browser_auth.json');
    if (!fs.existsSync(browserAuthPath)) return null;
    const authData = JSON.parse(fs.readFileSync(browserAuthPath, 'utf8'));
    return authData.cookie;
}

console.log('='.repeat(60));
console.log('YouTube.js - Music Client Test');
console.log('='.repeat(60));

const cookies = getCookiesFromBrowserAuth();

try {
    // Try with YouTube Music client type
    const innertube = await Innertube.create({ 
        cookie: cookies,
        // Try to force music client
        client_type: 'MUSIC'
    });
    
    console.log(`\nLogged in: ${innertube.session.logged_in}`);
    console.log(`Client type: ${innertube.session.client_name}`);

    // Check if music property exists
    console.log(`\nHas music property: ${!!innertube.music}`);
    
    if (innertube.music) {
        console.log('\n1. Testing YouTube Music library...');
        try {
            const musicLibrary = await innertube.music.getLibrary();
            console.log(`   ✅ Music library accessible!`);
            console.log(`   Type: ${musicLibrary.constructor.name}`);
            console.log(`   Keys: ${Object.keys(musicLibrary).join(', ')}`);
        } catch (e) {
            console.log(`   ❌ Music library failed: ${e.message}`);
        }

        console.log('\n2. Testing liked songs...');
        try {
            const likedSongs = await innertube.music.getLikedSongs();
            console.log(`   ✅ Liked songs accessible!`);
            if (likedSongs.contents && likedSongs.contents.length > 0) {
                console.log(`   Found ${likedSongs.contents.length} songs`);
            }
        } catch (e) {
            console.log(`   ❌ Liked songs failed: ${e.message}`);
        }
    } else {
        console.log('   No music client available');
    }

} catch (e) {
    console.log(`\n❌ Error: ${e.message}`);
    console.log(e.stack);
}
