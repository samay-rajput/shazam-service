import requests
import json

RAPIDAPI_KEY = "1c324420b5msh29a97c2f356f964p1370f0jsneec2c6ac2a8c"

def search_spotify(query, type="tracks", limit=1):
    url = "https://spotify23.p.rapidapi.com/search/"
    
    querystring = {
        "q": query,
        "type": type,
        "offset": "0",
        "limit": str(limit),
        "numberOfTopResults": "1"
    }
    
    headers = {
        "x-rapidapi-key": RAPIDAPI_KEY,
        "x-rapidapi-host": "spotify23.p.rapidapi.com"
    }
    
    response = requests.get(url, headers=headers, params=querystring)
    
    if response.status_code == 200:
        data = response.json()
        return data
    else:
        print(f"Error: {response.status_code} - {response.text}")
        return None

def parse_spotify_results(results):
    """Extract song title, artists, album, duration, cover art from API response"""

    tracks = results.get('tracks', {}).get('items', [])
    songs = []
    
    for track in tracks:
        data = track.get('data', {})
        
        # Main song info
        song_info = {
            'id': data.get('id'),
            'name': data.get('name'),
            'duration_ms': data.get('duration', {}).get('totalMilliseconds'),
            'playable': data.get('playability', {}).get('playable', False),
            'explicit': data.get('contentRating', {}).get('label') == 'EXPLICIT'
        }
        
        # Album info
        album = data.get('albumOfTrack', {})
        song_info['album'] = album.get('name')
        song_info['album_id'] = album.get('id')
        
        # Cover art (largest available)
        cover_sources = album.get('coverArt', {}).get('sources', [])
        if cover_sources:
            song_info['cover_art'] = max(cover_sources, key=lambda x: x.get('width', 0))['url']
        
        # Multiple artists (join them)
        artists = []
        for artist_item in data.get('artists', {}).get('items', []):
            artist_data = artist_item.get('profile', {})
            artists.append(artist_data.get('name', 'Unknown'))
        
        song_info['artists'] = ', '.join(artists)  # "Artist1, Artist2"
        
        songs.append(song_info)
    
    return songs


#use
if __name__ == "__main__":
    data = search_spotify("that shit hard vichaar")

    songs = parse_spotify_results(data)

    print(songs)
