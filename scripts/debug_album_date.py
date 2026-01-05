from ytmusicapi import YTMusic
import json

def debug_album_dates():
    yt = YTMusic()
    
    # Search for a few popular albums to verify
    queries = ["Thriller Michael Jackson", "Random Access Memories Daft Punk"]
    
    for q in queries:
        print(f"\n{'='*50}")
        print(f"Searching for: {q}")
        search_results = yt.search(q, filter="albums")
        if not search_results:
            print("No results found.")
            continue
            
        album_id = search_results[0]['browseId']
        print(f"Found album ID: {album_id}")
        
        album_details = yt.get_album(album_id)
        
        print(f"Album: {album_details.get('title')}")
        print("Release Date Raw Info:")
        if 'releaseDate' in album_details:
             print(f"  DTO['releaseDate']: {album_details['releaseDate']}")
        else:
             print("  DTO['releaseDate'] is MISSING")
            
        print(f"  DTO['year']: {album_details.get('year')}")
        
        # Check description for date patterns
        desc = album_details.get('description', '')
        print(f"  Description snippet: {desc[:100]}...")
        
        # Check first track
        tracks = album_details.get('tracks', [])
        if tracks:
            first_track = tracks[0]
            print(f"  First Track: {first_track.get('title')} ({first_track.get('videoId')})")
            # Try to get song details if we have videoId
            if 'videoId' in first_track:
                try:
                    song_details = yt.get_song(first_track['videoId'])
                    # 'videoDetails' usually contains date?
                    video_details = song_details.get('videoDetails', {})
                    print(f"  Song VideoDetails keys: {list(video_details.keys())}")
                    # check for usage of microformat?
                    microformat = song_details.get('microformat', {}).get('microformatDataRenderer', {})
                    print(f"  Microformat uploadDate: {microformat.get('uploadDate')}")
                except Exception as e:
                    print(f"  Failed to get song details: {e}")

if __name__ == "__main__":
    debug_album_dates()
