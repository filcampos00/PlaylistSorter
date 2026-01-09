"""
Test browser authentication with ytmusicapi
"""
import os
import sys

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from ytmusicapi import YTMusic

print("Testing BROWSER authentication...")

# Use path relative to this script's location
script_dir = os.path.dirname(os.path.abspath(__file__))
auth_file = os.path.join(script_dir, "browser_auth.json")

print(f"Using auth file: {auth_file}")
print(f"File exists: {os.path.exists(auth_file)}")

try:
    ytmusic = YTMusic(auth_file)

    
    print("\n1. Getting library playlists...")
    playlists = ytmusic.get_library_playlists(limit=5)
    print(f"   ✅ SUCCESS! Found {len(playlists)} playlists:")
    for p in playlists[:5]:
        print(f"      - {p.get('title', 'Unknown')}")
    
    print("\n2. Getting liked songs...")
    liked = ytmusic.get_liked_songs(limit=3)
    if liked and liked.get('tracks'):
        print(f"   ✅ SUCCESS! Found {len(liked['tracks'])} liked songs (showing 3)")
        for t in liked['tracks'][:3]:
            print(f"      - {t.get('title', 'Unknown')} by {t.get('artists', [{}])[0].get('name', 'Unknown') if t.get('artists') else 'Unknown'}")
    
    print("\n✅ BROWSER AUTHENTICATION WORKS!")
    
except Exception as e:
    print(f"\n   ❌ FAILED: {e}")
    import traceback
    traceback.print_exc()
