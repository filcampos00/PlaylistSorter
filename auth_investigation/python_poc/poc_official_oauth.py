"""
Minimal test using the official oauth.json created by ytmusicapi CLI
"""
import os
from dotenv import load_dotenv
from ytmusicapi import YTMusic, OAuthCredentials

load_dotenv()

# Use the official oauth.json file
oauth_file = "backend/oauth_official.json"

print(f"Testing with: {oauth_file}")
print(f"Client ID: {os.getenv('Google_Tv_Client_ID')[:30]}...")

try:
    ytmusic = YTMusic(
        oauth_file,
        oauth_credentials=OAuthCredentials(
            client_id=os.getenv("Google_Tv_Client_ID"),
            client_secret=os.getenv("Google_Tv_Client_Secret")
        )
    )
    
    print("\n1. Testing get_library_playlists()...")
    playlists = ytmusic.get_library_playlists(limit=3)
    print(f"   ✅ SUCCESS! Found {len(playlists)} playlists:")
    for p in playlists[:3]:
        print(f"      - {p.get('title', 'Unknown')}")

except Exception as e:
    print(f"\n   ❌ FAILED: {e}")
    import traceback
    traceback.print_exc()
