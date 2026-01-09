/**
 * ytmusic-api (zS1L3NT) Authentication PoC
 * 
 * This library is a TypeScript YouTube Music API wrapper.
 * Testing to see if it has the same OAuth/InnerTube limitations as:
 * - ytmusicapi (Python)
 * - YouTube.js
 * 
 * Based on GitHub: https://github.com/zS1L3NT/ts-npm-ytmusic-api
 */

import YTMusic from 'ytmusic-api';

console.log('='.repeat(60));
console.log('ytmusic-api (zS1L3NT) Authentication PoC');
console.log('='.repeat(60));

// Test 1: Basic initialization without cookies (unauthenticated)
console.log('\n1. Testing UNAUTHENTICATED access...');
try {
    const ytmusic = new YTMusic();
    await ytmusic.initialize();
    
    console.log('   ✅ Initialized successfully without cookies');
    
    // Try a simple search
    console.log('   Searching for "Never gonna give you up"...');
    const results = await ytmusic.searchSongs('Never gonna give you up');
    
    if (results && results.length > 0) {
        console.log(`   ✅ Search works! Found ${results.length} songs`);
        console.log(`      First result: ${results[0].name} by ${results[0].artist?.name || 'Unknown'}`);
    } else {
        console.log('   ⚠️ Search returned no results');
    }
} catch (e) {
    console.log(`   ❌ Unauthenticated test failed: ${e.message}`);
}

// Test 2: Check what methods/features are available
console.log('\n2. Checking available API methods...');
try {
    const ytmusic = new YTMusic();
    await ytmusic.initialize();
    
    // List available methods
    const methods = Object.getOwnPropertyNames(Object.getPrototypeOf(ytmusic))
        .filter(m => m !== 'constructor' && typeof ytmusic[m] === 'function');
    
    console.log('   Available methods:');
    methods.forEach(m => console.log(`      - ${m}`));
    
    // Check for any authentication-related methods
    const authMethods = methods.filter(m => 
        m.toLowerCase().includes('auth') || 
        m.toLowerCase().includes('login') ||
        m.toLowerCase().includes('playlist') ||
        m.toLowerCase().includes('library')
    );
    
    if (authMethods.length > 0) {
        console.log('\n   Auth/Playlist related methods:');
        authMethods.forEach(m => console.log(`      - ${m} ⚠️`));
    } else {
        console.log('\n   ⚠️ No auth/playlist methods found');
    }
} catch (e) {
    console.log(`   ❌ Method check failed: ${e.message}`);
}

// Test 3: Test with cookies (if available)
console.log('\n3. Testing WITH COOKIES (for authenticated access)...');
console.log('   Note: This library supports custom cookies via initialize()');

// Try to get a playlist (this usually requires auth)
try {
    const ytmusic = new YTMusic();
    await ytmusic.initialize();
    
    // Try to get a public playlist
    console.log('   Trying to get a public playlist...');
    const playlist = await ytmusic.getPlaylist('RDCLAK5uy_n9Fbdw7e6ap-98_A-8JYBmPv64v-Uaq1M');
    
    if (playlist) {
        console.log(`   ✅ Public playlist access works!`);
        console.log(`      Playlist: ${playlist.name || 'Unknown'}`);
        console.log(`      Tracks: ${playlist.videoCount || 'Unknown'}`);
    }
} catch (e) {
    console.log(`   ❌ Playlist access failed: ${e.message}`);
}

// Test 4: Test search for different content types
console.log('\n4. Testing various search endpoints...');
try {
    const ytmusic = new YTMusic();
    await ytmusic.initialize();
    
    const testQuery = 'Daft Punk';
    
    // Search songs
    try {
        const songs = await ytmusic.searchSongs(testQuery);
        console.log(`   ✅ searchSongs: ${songs?.length || 0} results`);
    } catch (e) {
        console.log(`   ❌ searchSongs failed: ${e.message}`);
    }
    
    // Search artists
    try {
        const artists = await ytmusic.searchArtists(testQuery);
        console.log(`   ✅ searchArtists: ${artists?.length || 0} results`);
    } catch (e) {
        console.log(`   ❌ searchArtists failed: ${e.message}`);
    }
    
    // Search albums
    try {
        const albums = await ytmusic.searchAlbums(testQuery);
        console.log(`   ✅ searchAlbums: ${albums?.length || 0} results`);
    } catch (e) {
        console.log(`   ❌ searchAlbums failed: ${e.message}`);
    }
    
    // Search playlists
    try {
        const playlists = await ytmusic.searchPlaylists(testQuery);
        console.log(`   ✅ searchPlaylists: ${playlists?.length || 0} results`);
    } catch (e) {
        console.log(`   ❌ searchPlaylists failed: ${e.message}`);
    }
    
} catch (e) {
    console.log(`   ❌ Search tests failed: ${e.message}`);
}

// Summary
console.log('\n' + '='.repeat(60));
console.log('SUMMARY - ytmusic-api Library Analysis');
console.log('='.repeat(60));
console.log(`
Key findings about ytmusic-api:
1. This library is primarily a DATA SCRAPER for public YouTube Music content
2. It does NOT appear to support authenticated user operations like:
   - Getting user's library/playlists  
   - Creating/editing playlists
   - Adding/removing songs from playlists
3. Authentication via cookies is for accessing the API, not for user-specific data
4. This is fundamentally different from ytmusicapi/YouTube.js which support
   user account operations

CONCLUSION: This library is NOT suitable for playlist sorting because:
- It can only READ public content (search, public playlists)
- It CANNOT access user's private playlists
- It CANNOT modify playlists (no edit_playlist, no moveVideo methods)

For our PlaylistSorter app, we still need ytmusicapi or YouTube.js with
browser cookie authentication.
`);
