"""
Debug test to determine if the problem is:
1. Authentication (invalid/expired token)
2. Request format (ytmusicapi sending bad request body)
"""
import os
import json
import httpx
from dotenv import load_dotenv
from ytmusicapi import YTMusic, OAuthCredentials

load_dotenv()

# Load the official oauth.json
oauth_file = "backend/oauth_official.json"
with open(oauth_file) as f:
    oauth_data = json.load(f)

access_token = oauth_data.get("access_token")
print("=" * 60)
print("DEBUG: Token Validation")
print("=" * 60)
print(f"Access Token (truncated): {access_token[:50]}...")

# Test 1: Validate token with Google's tokeninfo endpoint
print("\n1. Validating token with Google's tokeninfo endpoint...")
try:
    response = httpx.get(
        f"https://oauth2.googleapis.com/tokeninfo?access_token={access_token}"
    )
    if response.status_code == 200:
        info = response.json()
        print(f"   ✅ Token is VALID!")
        print(f"   - Scope: {info.get('scope')}")
        print(f"   - Expires in: {info.get('expires_in')} seconds")
        print(f"   - Audience: {info.get('aud', 'N/A')[:50]}...")
    else:
        print(f"   ❌ Token is INVALID: {response.status_code}")
        print(f"   Response: {response.text}")
except Exception as e:
    print(f"   ❌ Error validating token: {e}")

# Test 2: Make a direct API call to YouTube Data API (not YouTube Music internal API)
print("\n2. Testing YouTube Data API directly with token...")
try:
    response = httpx.get(
        "https://www.googleapis.com/youtube/v3/channels",
        params={"part": "snippet", "mine": "true"},
        headers={"Authorization": f"Bearer {access_token}"}
    )
    if response.status_code == 200:
        data = response.json()
        channels = data.get("items", [])
        if channels:
            print(f"   ✅ YouTube Data API works! Channel: {channels[0]['snippet']['title']}")
        else:
            print(f"   ✅ YouTube Data API works! (no channels found)")
    else:
        print(f"   ❌ YouTube Data API failed: {response.status_code}")
        print(f"   Response: {response.text[:500]}")
except Exception as e:
    print(f"   ❌ Error: {e}")

# Test 3: Try the internal YouTube Music API endpoint directly
print("\n3. Testing YouTube Music internal API directly...")
print("   (This is what ytmusicapi calls internally)")

# This is the endpoint ytmusicapi uses for get_library_playlists
YTM_API_URL = "https://music.youtube.com/youtubei/v1/browse"
YTM_PARAMS = "?alt=json&key=AIzaSyC9XL3ZjWddXya6X74dJoCTL-WEYFDNX30"

# Build request similar to what ytmusicapi does
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:88.0) Gecko/20100101 Firefox/88.0",
    "Accept": "*/*",
    "Content-Type": "application/json",
    "Authorization": f"Bearer {access_token}",
    "X-Goog-AuthUser": "0",
    "Origin": "https://music.youtube.com",
    "Referer": "https://music.youtube.com/",
}

# Minimal body for browse request (library playlists)
body = {
    "context": {
        "client": {
            "clientName": "WEB_REMIX",
            "clientVersion": "1.20231204.01.00",
            "hl": "en",
            "gl": "US",
        }
    },
    "browseId": "FEmusic_liked_playlists"
}

try:
    response = httpx.post(
        YTM_API_URL + YTM_PARAMS,
        headers=headers,
        json=body
    )
    print(f"   Status: {response.status_code}")
    if response.status_code == 200:
        print(f"   ✅ Internal API works!")
        print(f"   Response (first 300 chars): {response.text[:300]}...")
    else:
        print(f"   ❌ Internal API failed!")
        print(f"   Response: {response.text[:500]}")
except Exception as e:
    print(f"   ❌ Error: {e}")

# Test 4: Now test through ytmusicapi to compare
print("\n4. Testing through ytmusicapi library...")
try:
    ytmusic = YTMusic(
        oauth_file,
        oauth_credentials=OAuthCredentials(
            client_id=os.getenv("Google_Tv_Client_ID"),
            client_secret=os.getenv("Google_Tv_Client_Secret")
        )
    )
    playlists = ytmusic.get_library_playlists(limit=3)
    print(f"   ✅ ytmusicapi works! Found {len(playlists)} playlists")
except Exception as e:
    print(f"   ❌ ytmusicapi failed: {e}")

print("\n" + "=" * 60)
print("CONCLUSION")
print("=" * 60)
