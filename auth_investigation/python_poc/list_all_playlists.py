"""
Compare playlists found by ytmusicapi vs YouTube.js
"""
import os
from ytmusicapi import YTMusic

script_dir = os.path.dirname(os.path.abspath(__file__))
auth_file = os.path.join(script_dir, "..", "temp_browser_auth.json")

print("=" * 60)
print("ytmusicapi - All Library Playlists")
print("=" * 60)

try:
    ytmusic = YTMusic(auth_file)
    
    # Get ALL playlists, not just 5
    playlists = ytmusic.get_library_playlists(limit=100)
    
    print(f"\nTotal playlists found: {len(playlists)}\n")
    
    for i, p in enumerate(playlists, 1):
        title = p.get('title', 'Unknown')
        playlist_id = p.get('playlistId', 'N/A')
        count = p.get('count', '?')
        print(f"{i:2}. {title} ({count} tracks) - ID: {playlist_id}")
        
except Exception as e:
    print(f"Error: {e}")
    import traceback
    traceback.print_exc()
