"""
Test: Try unauthenticated YTMusic to see if basic API calls work
"""
from ytmusicapi import YTMusic

print("Testing UNAUTHENTICATED YTMusic...")
print("(No OAuth, no browser auth - just public data)")

try:
    ytmusic = YTMusic()  # No auth
    
    print("\n1. Searching for 'Oasis Wonderwall'...")
    results = ytmusic.search("Oasis Wonderwall", limit=2)
    print(f"   ✅ Search works! Found {len(results)} results")
    for r in results[:2]:
        print(f"      - {r.get('title', 'N/A')} by {r.get('artists', [{}])[0].get('name', 'N/A') if r.get('artists') else 'N/A'}")
    
    print("\n2. Getting charts...")
    charts = ytmusic.get_charts(country="US")
    if charts:
        print(f"   ✅ Charts works!")
    
except Exception as e:
    print(f"   ❌ FAILED: {e}")
    import traceback
    traceback.print_exc()
