import yt_dlp
import json

def get_real_mp4_url(youtube_url):
    ydl_opts = {
        # On cherche le meilleur format MP4 contenant Vidéo ET Audio (vcodec/acodec != none)
        # On exclut explicitement m3u8 et dash pour garantir un lien direct utilisable
        'format': 'best[ext=mp4][vcodec!=none][acodec!=none][protocol!*=m3u8][protocol!*=dash]', 
        'quiet': True,
        'simulate': True,
        'forceurl': True,
        # Force le tri par résolution décroissante pour obtenir la meilleure qualité possible
        'format_sort': ['res'],
        # On ajoute iOS qui peut parfois offrir des variantes intéressantes, en plus d'Android (top pour le mp4)
        'extractor_args': {'youtube': {'player_client': ['android', 'web', 'ios']}},
    }

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            print(f"Extraction des infos pour : {youtube_url}...")
            info = ydl.extract_info(youtube_url, download=False)
            
            # Vérification rigoureuse
            if 'url' in info:
                # On vérifie si c'est bien un mp4 et pas un m3u8
                url = info['url']
                if ".m3u8" in url:
                    return "ÉCHEC: YouTube force le HLS (m3u8) pour cette vidéo. Impossible d'avoir un mp4 direct simple."
                
                print(f"Titre : {info.get('title', 'Inconnu')}")
                print(f"\nQualité trouvée : {info.get('resolution', 'N/A')}")
                print(f"Format ID : {info.get('format_id', 'N/A')}")
                return url
            else:
                return "Aucune URL directe trouvée."

    except Exception as e:
        return f"Erreur critique : {e}"

# Test avec ta vidéo
# Note : Pour que ça marche parfaitement, installe Node.js sur ton PC pour supprimer l'avertissement JS
video_url = "https://www.youtube.com/watch?v=7V5jdOjWVU4" 
mp4_link = get_real_mp4_url(video_url)

print(f"\nL'URL finale MP4 est :\n{mp4_link}")