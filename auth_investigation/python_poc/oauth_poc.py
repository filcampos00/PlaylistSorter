"""
Proof of Concept: Test if Web OAuth tokens work with ytmusicapi

This script tests two approaches:
1. TV Device Flow (documented approach)
2. Web OAuth Flow (better UX, but untested with ytmusicapi)

Run with: python oauth_poc.py
"""

import os
import time
import json
import asyncio
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Check which credentials are available
print("=" * 60)
print("AVAILABLE CREDENTIALS CHECK")
print("=" * 60)

tv_client_id = os.getenv("Google_Tv_Client_ID")
tv_client_secret = os.getenv("Google_Tv_Client_Secret")
web_client_id = os.getenv("Google_Web_Client_ID")
web_client_secret = os.getenv("Google_Web_Client_Secret")

print(f"TV Client ID: {'✅ Found' if tv_client_id else '❌ Missing'}")
print(f"TV Client Secret: {'✅ Found' if tv_client_secret else '❌ Missing'}")
print(f"Web Client ID: {'✅ Found' if web_client_id else '❌ Missing'}")
print(f"Web Client Secret: {'✅ Found' if web_client_secret else '❌ Missing'}")
print()


def test_tv_device_flow():
    """
    Test 1: TV Device Flow (official ytmusicapi approach)
    Uses: ytmusicapi's built-in OAuth setup
    """
    print("=" * 60)
    print("TEST 1: TV Device Flow (ytmusicapi native)")
    print("=" * 60)
    
    try:
        from ytmusicapi import YTMusic, OAuthCredentials
        from ytmusicapi.auth.oauth.credentials import OAuthCredentials as OAuthCreds
        from ytmusicapi.auth.oauth.token import RefreshingToken
        
        if not tv_client_id or not tv_client_secret:
            print("❌ TV credentials not found in .env")
            return None
        
        credentials = OAuthCreds(
            client_id=tv_client_id,
            client_secret=tv_client_secret
        )
        
        # Step 1: Get device code
        print("\n1. Requesting device code from Google...")
        code_response = credentials.get_code()
        
        print(f"\n   Device Code: {code_response.get('device_code', 'N/A')[:20]}...")
        print(f"   User Code: {code_response.get('user_code', 'N/A')}")
        print(f"   Verification URL: {code_response.get('verification_url', 'N/A')}")
        print(f"   Expires in: {code_response.get('expires_in', 'N/A')} seconds")
        
        # Step 2: User must visit URL and enter code
        verification_url = code_response.get('verification_url', 'https://www.google.com/device')
        user_code = code_response.get('user_code', '')
        
        print(f"\n   👉 Go to: {verification_url}")
        print(f"   👉 Enter code: {user_code}")
        
        input("\n   Press Enter after you've completed the authorization...")
        
        # Step 3: Exchange device code for tokens
        print("\n2. Exchanging device code for tokens...")
        token_response = credentials.token_from_code(code_response['device_code'])
        
        print(f"\n   ✅ TV Device Flow SUCCESS!")
        print(f"   Access Token: {token_response.get('access_token', 'N/A')[:30]}...")
        print(f"   Refresh Token: {token_response.get('refresh_token', 'N/A')[:20]}...")
        print(f"   Expires In: {token_response.get('expires_in', 'N/A')} seconds")
        
        # Step 4: Test with YTMusic
        print("\n3. Testing YTMusic API call...")
        
        # Format token for ytmusicapi
        oauth_token = {
            "access_token": token_response["access_token"],
            "refresh_token": token_response["refresh_token"],
            "token_type": token_response.get("token_type", "Bearer"),
            "expires_at": int(time.time()) + token_response.get("expires_in", 3600),
            "expires_in": token_response.get("expires_in", 3600),
            "scope": "https://www.googleapis.com/auth/youtube"
        }
        
        ytmusic = YTMusic(oauth_token, oauth_credentials=OAuthCredentials(
            client_id=tv_client_id,
            client_secret=tv_client_secret
        ))
        
        # Try a simple API call
        playlists = ytmusic.get_library_playlists(limit=3)
        print(f"   ✅ API call successful! Found {len(playlists)} playlists")
        for p in playlists[:3]:
            print(f"      - {p.get('title', 'Unknown')}")
        
        # Save token for later use
        token_file = Path(__file__).parent / "oauth_tv_test.json"
        with open(token_file, "w") as f:
            json.dump(oauth_token, f, indent=2)
        print(f"\n   Token saved to: {token_file}")
        
        return oauth_token
        
    except Exception as e:
        print(f"\n   ❌ TV Device Flow FAILED: {e}")
        import traceback
        traceback.print_exc()
        return None


def test_web_oauth_flow():
    """
    Test 2: Web OAuth Flow (custom implementation)
    Uses: Standard web OAuth with redirect
    """
    print("\n" + "=" * 60)
    print("TEST 2: Web OAuth Flow (custom)")
    print("=" * 60)
    
    try:
        import httpx
        from urllib.parse import urlencode, parse_qs, urlparse
        from ytmusicapi import YTMusic, OAuthCredentials
        
        if not web_client_id or not web_client_secret:
            print("❌ Web credentials not found in .env")
            return None
        
        redirect_uri = os.getenv("OAUTH_REDIRECT_URI", "http://localhost:5182/callback")
        
        # Step 1: Generate authorization URL
        print("\n1. Generating authorization URL...")
        
        auth_params = {
            "client_id": web_client_id,
            "redirect_uri": redirect_uri,
            "response_type": "code",
            "scope": "https://www.googleapis.com/auth/youtube",
            "access_type": "offline",
            "prompt": "consent",
            "state": "test_state_123"
        }
        auth_url = f"https://accounts.google.com/o/oauth2/v2/auth?{urlencode(auth_params)}"
        
        print(f"\n   👉 Open this URL in your browser:")
        print(f"   {auth_url}")
        print(f"\n   After authorization, Google will redirect to: {redirect_uri}")
        print(f"   Copy the FULL redirect URL (including the ?code=... parameter)")
        
        redirect_response = input("\n   Paste the full redirect URL here: ").strip()
        
        # Extract authorization code from redirect URL
        parsed = urlparse(redirect_response)
        query_params = parse_qs(parsed.query)
        
        if "code" not in query_params:
            print("   ❌ No authorization code found in URL")
            return None
        
        auth_code = query_params["code"][0]
        print(f"\n   Authorization code: {auth_code[:30]}...")
        
        # Step 2: Exchange code for tokens
        print("\n2. Exchanging authorization code for tokens...")
        
        with httpx.Client() as client:
            token_response = client.post(
                "https://oauth2.googleapis.com/token",
                data={
                    "client_id": web_client_id,
                    "client_secret": web_client_secret,
                    "code": auth_code,
                    "grant_type": "authorization_code",
                    "redirect_uri": redirect_uri
                }
            )
        
        if token_response.status_code != 200:
            print(f"   ❌ Token exchange failed: {token_response.status_code}")
            print(f"   Response: {token_response.text}")
            return None
        
        tokens = token_response.json()
        print(f"\n   ✅ Token exchange SUCCESS!")
        print(f"   Access Token: {tokens.get('access_token', 'N/A')[:30]}...")
        print(f"   Refresh Token: {tokens.get('refresh_token', 'N/A')[:20] if tokens.get('refresh_token') else '❌ NOT PROVIDED'}...")
        print(f"   Expires In: {tokens.get('expires_in', 'N/A')} seconds")
        print(f"   Scope: {tokens.get('scope', 'N/A')}")
        
        if not tokens.get("refresh_token"):
            print("\n   ⚠️  No refresh token! This may be because:")
            print("      - User previously authorized this app")
            print("      - 'prompt=consent' wasn't used")
            print("      - This is a second authorization attempt")
        
        # Step 3: Format for ytmusicapi and test
        print("\n3. Testing with YTMusic API...")
        
        oauth_token = {
            "access_token": tokens["access_token"],
            "refresh_token": tokens.get("refresh_token", ""),
            "token_type": tokens.get("token_type", "Bearer"),
            "expires_at": int(time.time()) + tokens.get("expires_in", 3600),
            "expires_in": tokens.get("expires_in", 3600),
            "scope": tokens.get("scope", "https://www.googleapis.com/auth/youtube")
        }
        
        try:
            ytmusic = YTMusic(oauth_token, oauth_credentials=OAuthCredentials(
                client_id=web_client_id,
                client_secret=web_client_secret
            ))
            
            # Try a simple API call
            playlists = ytmusic.get_library_playlists(limit=3)
            print(f"   ✅ WEB OAUTH WORKS WITH YTMUSICAPI!")
            print(f"   Found {len(playlists)} playlists:")
            for p in playlists[:3]:
                print(f"      - {p.get('title', 'Unknown')}")
            
            # Save token for later use
            token_file = Path(__file__).parent / "oauth_web_test.json"
            with open(token_file, "w") as f:
                json.dump(oauth_token, f, indent=2)
            print(f"\n   Token saved to: {token_file}")
            
            return oauth_token
            
        except Exception as api_error:
            print(f"\n   ❌ YTMusic API call FAILED with Web OAuth tokens: {api_error}")
            import traceback
            traceback.print_exc()
            return None
        
    except Exception as e:
        print(f"\n   ❌ Web OAuth Flow FAILED: {e}")
        import traceback
        traceback.print_exc()
        return None


def main():
    print("\n" + "=" * 60)
    print("YTMUSICAPI OAUTH PROOF OF CONCEPT")
    print("=" * 60)
    print("\nThis script will test both OAuth approaches:")
    print("1. TV Device Flow (ytmusicapi's documented method)")
    print("2. Web OAuth Flow (standard web redirect)")
    print()
    
    choice = input("Which test to run? (1=TV, 2=Web, 3=Both): ").strip()
    
    results = {}
    
    if choice in ["1", "3"]:
        results["tv"] = test_tv_device_flow()
    
    if choice in ["2", "3"]:
        results["web"] = test_web_oauth_flow()
    
    # Summary
    print("\n" + "=" * 60)
    print("SUMMARY")
    print("=" * 60)
    
    if "tv" in results:
        print(f"TV Device Flow: {'✅ SUCCESS' if results['tv'] else '❌ FAILED'}")
    
    if "web" in results:
        print(f"Web OAuth Flow: {'✅ SUCCESS' if results['web'] else '❌ FAILED'}")
    
    print()


if __name__ == "__main__":
    main()
