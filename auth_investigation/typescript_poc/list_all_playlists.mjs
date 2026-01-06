/**
 * List all playlists with YouTube.js for comparison
 */

import { Innertube } from 'youtubei.js';
import fs from 'fs';
import path from 'path';
import { fileURLToPath } from 'url';

const __dirname = path.dirname(fileURLToPath(import.meta.url));

function getCookies() {
    const authPath = path.join(__dirname, '..', 'temp_browser_auth.json');
    if (!fs.existsSync(authPath)) return null;
    const authData = JSON.parse(fs.readFileSync(authPath, 'utf8'));
    return authData.cookie;
}

console.log('='.repeat(60));
console.log('YouTube.js - All Library Playlists');
console.log('='.repeat(60));

const cookies = getCookies();

try {
    const innertube = await Innertube.create({ cookie: cookies });
    
    console.log(`\nLogged in: ${innertube.session.logged_in}`);
    
    // Get library
    const library = await innertube.getLibrary();
    
    console.log(`\nLibrary sections: ${library.sections?.length || 0}`);
    
    // Explore the library structure to find playlists
    if (library.sections) {
        for (const section of library.sections) {
            console.log(`\nSection type: ${section.type}`);
            if (section.contents) {
                console.log(`  Contents: ${section.contents.length} items`);
                for (let i = 0; i < Math.min(section.contents.length, 15); i++) {
                    const item = section.contents[i];
                    // Try to get title from various possible locations
                    const title = item.title?.text || 
                                  item.metadata?.title?.text || 
                                  item.content_id ||
                                  JSON.stringify(Object.keys(item)).slice(0, 50);
                    console.log(`    ${i+1}. ${title} (type: ${item.type})`);
                }
            }
        }
    }
    
    // Also try the playlists property directly
    console.log(`\n\nDirect playlists property: ${library.playlists?.length || 0} items`);
    if (library.playlists) {
        library.playlists.forEach((p, i) => {
            const title = p.title?.text || p.metadata?.title?.text || 'Unknown';
            console.log(`  ${i+1}. ${title}`);
        });
    }
    
} catch (e) {
    console.log(`Error: ${e.message}`);
    console.log(e.stack);
}
