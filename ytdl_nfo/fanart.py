import json
import os
import urllib.parse
import urllib.request


def clean_artist_name(name):
    if not name:
        return ""
    import re
    name = re.sub(r"VEVO$", "", name, flags=re.IGNORECASE)
    name = re.sub(r"-?\s*Topic$", "", name, flags=re.IGNORECASE)
    name = re.sub(r"-?\s*Official$", "", name, flags=re.IGNORECASE)
    name = re.sub(r"([a-z])([A-Z])", r"\1 \2", name)
    return name.strip()


def fetch_fanart_data(artist_name, api_key=None, client_key=None):
    """
    Fetches artist artwork URLs from Fanart.tv via MusicBrainz MBID lookup.
    """
    if not api_key:
        api_key = os.environ.get("FANART_API_KEY")

    if not api_key:
        return {}

    artist_name = clean_artist_name(artist_name)
    if not artist_name:
        return {}

    # 1. Lookup MBID on MusicBrainz
    mbid = None
    try:
        mb_url = (
            "https://musicbrainz.org/ws/2/artist/?query=artist:"
            + urllib.parse.quote(artist_name)
            + "&fmt=json&limit=1"
        )
        req = urllib.request.Request(
            mb_url,
            headers={
                "User-Agent": "ytdl-nfo/0.5.1 ( https://github.com/exyron/ytdl-nfo )"
            },
        )
        with urllib.request.urlopen(req, timeout=10) as resp:
            data = json.loads(resp.read().decode("utf-8"))
            artists = data.get("artists", [])
            if artists:
                mbid = artists[0].get("id")
    except Exception as e:
        print(f"⚠️ Error al consultar MusicBrainz: {e}")
        mbid = None

    if not mbid:
        return {}

    # 2. Query Fanart.tv API
    result = {}
    try:
        fanart_url = f"https://webservice.fanart.tv/v3/music/{mbid}?api_key={api_key}"
        if client_key:
            fanart_url += f"&client_key={client_key}"

        req = urllib.request.Request(
            fanart_url, headers={"User-Agent": "ytdl-nfo/0.5.1"}
        )
        with urllib.request.urlopen(req, timeout=10) as resp:
            fanart_data = json.loads(resp.read().decode("utf-8"))

            if "hdmusiclogo" in fanart_data and fanart_data["hdmusiclogo"]:
                result["clearlogo"] = fanart_data["hdmusiclogo"][0].get("url", "")
            elif "musiclogo" in fanart_data and fanart_data["musiclogo"]:
                result["clearlogo"] = fanart_data["musiclogo"][0].get("url", "")

            if "artistthumb" in fanart_data and fanart_data["artistthumb"]:
                result["artist_thumb"] = fanart_data["artistthumb"][0].get("url", "")

            if "musicbanner" in fanart_data and fanart_data["musicbanner"]:
                result["banner"] = fanart_data["musicbanner"][0].get("url", "")

            if "artistbackground" in fanart_data and fanart_data["artistbackground"]:
                result["fanart"] = fanart_data["artistbackground"][0].get("url", "")
    except Exception as e:
        print(f"⚠️ Error al consultar Fanart.tv: {e}")

    return result
