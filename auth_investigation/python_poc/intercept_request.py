"""
Debug: Intercept and log the EXACT request ytmusicapi sends
"""
import os
import json
from dotenv import load_dotenv
from ytmusicapi import YTMusic, OAuthCredentials
import requests

load_dotenv()

oauth_file = "backend/oauth_official.json"

# Patch requests.Session.post to intercept the request
original_post = requests.Session.post

def intercepting_post(self, url, *args, **kwargs):
    print("\n" + "=" * 60)
    print("INTERCEPTED REQUEST")
    print("=" * 60)
    print(f"URL: {url}")
    print(f"\nHEADERS:")
    for k, v in kwargs.get('headers', {}).items():
        # Truncate long values
        v_str = str(v)
        if len(v_str) > 80:
            v_str = v_str[:80] + "..."
        print(f"  {k}: {v_str}")
    print(f"\nBODY (first 500 chars):")
    body = kwargs.get('json', {})
    print(json.dumps(body, indent=2)[:500])
    print("=" * 60 + "\n")
    
    # Call original
    return original_post(self, url, *args, **kwargs)

# Apply patch
requests.Session.post = intercepting_post

try:
    ytmusic = YTMusic(
        oauth_file,
        oauth_credentials=OAuthCredentials(
            client_id=os.getenv("Google_Tv_Client_ID"),
            client_secret=os.getenv("Google_Tv_Client_Secret")
        )
    )
    
    print("Calling get_library_playlists...")
    playlists = ytmusic.get_library_playlists(limit=1)
    print(f"✅ SUCCESS: {len(playlists)} playlists")
except Exception as e:
    print(f"❌ FAILED: {e}")
finally:
    # Restore original
    requests.Session.post = original_post
