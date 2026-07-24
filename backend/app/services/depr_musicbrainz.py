# import requests

# song = "Anaheim"
# artist = "NIKI"

# url = "https://musicbrainz.org/ws/2/recording"

# params = {
#     "query": f'recording:"{song}" AND artist:"{artist}"',
#     "fmt": "json",
#     "limit": 10,
# }

# headers = {
#     "User-Agent": "MyMusicApp/1.0 (your_email@example.com)"
# }

# response = requests.get(url, params=params, headers=headers)
# response.raise_for_status()

# data = response.json()

# for recording in data["recordings"]:
#     print(f"Title: {recording['title']}")
#     print(f"MBID: {recording['id']}")
#     print(f"Score: {recording.get('score')}")

#     # Artist(s)
#     artists = ", ".join(
#         credit["name"] for credit in recording.get("artist-credit", [])
#     )
#     print(f"Artist: {artists}")

#     # Release(s)
#     if recording.get("releases"):
#         print("Releases:")
#         for release in recording["releases"]:
#             print(f"  - {release['title']}")

#     print("---")