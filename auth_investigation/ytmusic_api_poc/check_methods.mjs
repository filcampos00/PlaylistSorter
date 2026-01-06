/**
 * Simple test to check ytmusic-api available methods
 */
import YTMusic from 'ytmusic-api';

const ytmusic = new YTMusic();
await ytmusic.initialize();

// Get all methods on the YTMusic instance
const methods = Object.getOwnPropertyNames(Object.getPrototypeOf(ytmusic))
    .filter(m => m !== 'constructor' && typeof ytmusic[m] === 'function');

console.log('Available methods in ytmusic-api:');
console.log('================================');
methods.forEach(m => console.log(`- ${m}`));
console.log('================================');
console.log(`Total methods: ${methods.length}`);

// Check specifically for user-related methods
console.log('\nLooking for auth/user/library/modify methods...');
const relevantMethods = methods.filter(m => 
    m.toLowerCase().includes('auth') ||
    m.toLowerCase().includes('user') ||
    m.toLowerCase().includes('library') ||
    m.toLowerCase().includes('create') ||
    m.toLowerCase().includes('edit') ||
    m.toLowerCase().includes('add') ||
    m.toLowerCase().includes('remove') ||
    m.toLowerCase().includes('delete') ||
    m.toLowerCase().includes('move')
);

if (relevantMethods.length > 0) {
    console.log('Found relevant methods:');
    relevantMethods.forEach(m => console.log(`  --> ${m}`));
} else {
    console.log('NO auth/user/modify methods found!');
    console.log('This library is READ-ONLY for public content.');
}
