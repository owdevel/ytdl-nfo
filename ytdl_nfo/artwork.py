import os
import urllib.request


def detect_and_download_artwork(file_path, raw_data, download=False):
    """
    Detects local image files alongside the video/info.json,
    and optionally downloads remote artwork URLs (thumbnails, fanart, clearlogos)
    to local files so Kodi can read them offline.
    """
    dir_path = os.path.dirname(file_path)

    if file_path.endswith(".info.json"):
        base_path = file_path[:-10]
    else:
        base_path = os.path.splitext(file_path)[0]

    base_name = os.path.basename(base_path)

    def download_url(url, dest_path):
        if not url or not url.startswith("http"):
            return False
        if os.path.isfile(dest_path):
            return True
        try:
            os.makedirs(os.path.dirname(dest_path), exist_ok=True)
            req = urllib.request.Request(
                url, headers={"User-Agent": "ytdl-nfo/0.4.0"}
            )
            with urllib.request.urlopen(req, timeout=10) as resp:
                with open(dest_path, "wb") as out_file:
                    out_file.write(resp.read())
            return True
        except Exception:
            return False

    # 1. Poster / Primary Thumb
    poster_candidates = [
        f"{base_name}-poster.jpg",
        f"{base_name}.jpg",
        f"{base_name}-thumb.jpg",
        f"{base_name}.png",
        f"{base_name}-poster.png",
        f"{base_name}.webp",
        "poster.jpg",
        "folder.jpg",
    ]

    local_poster = None
    for cand in poster_candidates:
        full_cand = os.path.join(dir_path, cand)
        if os.path.isfile(full_cand):
            local_poster = cand
            break

    if not local_poster and download and raw_data.get("thumbnail"):
        dest = os.path.join(dir_path, f"{base_name}-poster.jpg")
        if download_url(raw_data["thumbnail"], dest):
            local_poster = f"{base_name}-poster.jpg"

    raw_data["local_poster"] = local_poster or raw_data.get("thumbnail") or ""

    # 2. ClearLogo
    logo_candidates = [
        f"{base_name}-clearlogo.png",
        f"{base_name}-logo.png",
        f"{base_name}-clearlogo.jpg",
        "clearlogo.png",
        "logo.png",
    ]

    local_logo = None
    for cand in logo_candidates:
        full_cand = os.path.join(dir_path, cand)
        if os.path.isfile(full_cand):
            local_logo = cand
            break

    if not local_logo and download and raw_data.get("clearlogo"):
        dest = os.path.join(dir_path, f"{base_name}-clearlogo.png")
        if download_url(raw_data["clearlogo"], dest):
            local_logo = f"{base_name}-clearlogo.png"

    raw_data["local_clearlogo"] = local_logo or raw_data.get("clearlogo") or ""

    # 3. Fanart / Background
    fanart_candidates = [
        f"{base_name}-fanart.jpg",
        f"{base_name}-fanart.png",
        "fanart.jpg",
        "fanart.png",
    ]

    local_fanart = None
    for cand in fanart_candidates:
        full_cand = os.path.join(dir_path, cand)
        if os.path.isfile(full_cand):
            local_fanart = cand
            break

    if not local_fanart and download and raw_data.get("fanart"):
        dest = os.path.join(dir_path, f"{base_name}-fanart.jpg")
        if download_url(raw_data["fanart"], dest):
            local_fanart = f"{base_name}-fanart.jpg"

    raw_data["local_fanart"] = local_fanart or raw_data.get("fanart") or ""

    # 4. Banner
    banner_candidates = [
        f"{base_name}-banner.jpg",
        f"{base_name}-banner.png",
        "banner.jpg",
    ]

    local_banner = None
    for cand in banner_candidates:
        full_cand = os.path.join(dir_path, cand)
        if os.path.isfile(full_cand):
            local_banner = cand
            break

    if not local_banner and download and raw_data.get("banner"):
        dest = os.path.join(dir_path, f"{base_name}-banner.jpg")
        if download_url(raw_data["banner"], dest):
            local_banner = f"{base_name}-banner.jpg"

    raw_data["local_banner"] = local_banner or raw_data.get("banner") or ""
