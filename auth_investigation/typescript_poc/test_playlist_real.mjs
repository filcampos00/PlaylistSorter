/**
 * YouTube.js - Thorough Playlist Test
 * Actually verify we can read and manipulate playlists
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
console.log('YouTube.js - Thorough Playlist Test');
console.log('='.repeat(60));

const cookies = getCookiesFromBrowserAuth();
if (!cookies) {
    console.log('❌ No cookies found. Cannot test.');
    process.exit(1);
}

try {
    const innertube = await Innertube.create({ cookie: cookies });
    
    console.log(`\nLogged in: ${innertube.session.logged_in}`);
    
    if (!innertube.session.logged_in) {
        console.log('❌ Not logged in despite cookies');
        process.exit(1);
    }

    // Test 1: Get library and inspect structure
    console.log('\n1. Getting library...');
    const library = await innertube.getLibrary();
    console.log(`   Library type: ${library.constructor.name}`);
    console.log(`   Library keys: ${Object.keys(library).slice(0, 10).join(', ')}`);
    
    // Check playlists property
    if (library.playlists) {
        console.log(`   Playlists array length: ${library.playlists.length}`);
        if (library.playlists.length > 0) {
            const firstPlaylist = library.playlists[0];
            console.log(`   First playlist type: ${firstPlaylist.constructor.name}`);
            console.log(`   First playlist keys: ${Object.keys(firstPlaylist).join(', ')}`);
            console.log(`   First playlist data: ${JSON.stringify(firstPlaylist, null, 2).slice(0, 500)}`);
        }
    }

    // Test 2: Try to get a specific playlist
    console.log('\n2. Getting liked music playlist (LM)...');
    try {
        const likedPlaylist = await innertube.getPlaylist('LM');
        console.log(`   ✅ Got liked music playlist!`);
        console.log(`   Title: ${likedPlaylist.info?.title || 'Unknown'}`);
        console.log(`   Total items: ${likedPlaylist.info?.total_items || 'Unknown'}`);
        
        if (likedPlaylist.videos && likedPlaylist.videos.length > 0) {
            console.log(`   Videos retrieved: ${likedPlaylist.videos.length}`);
            console.log(`   First 3 songs:`);
            likedPlaylist.videos.slice(0, 3).forEach((v, i) => {
                console.log(`      ${i+1}. ${v.title?.text || v.title || 'Unknown'}`);
            });
        }
    } catch (e) {
        console.log(`   ❌ Failed: ${e.message}`);
    }

    // Test 3: Try playlist manager
    console.log('\n3. Testing PlaylistManager...');
    if (innertube.playlist) {
        console.log('   ✅ PlaylistManager is accessible');
        console.log(`   Available methods: ${Object.getOwnPropertyNames(Object.getPrototypeOf(innertube.playlist)).filter(m => m !== 'constructor').join(', ')}`);
    } else {
        console.log('   ❌ PlaylistManager not found');
    }

    console.log('\n' + '='.repeat(60));
    console.log('CONCLUSION');
    console.log('='.repeat(60));
    
} catch (e) {
    console.log(`\n❌ Error: ${e.message}`);
    console.log(e.stack);
}
