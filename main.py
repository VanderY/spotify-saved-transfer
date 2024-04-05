import spotipy
from spotipy.oauth2 import SpotifyOAuth, SpotifyOauthError
from dotenv import load_dotenv
from rich.console import Console
from rich.pretty import pprint
from rich.progress import Progress, TextColumn, BarColumn, TaskProgressColumn, TimeRemainingColumn, MofNCompleteColumn
from rich.prompt import Confirm
from rich.text import Text

load_dotenv()

console = Console()


def login(scope):
    cache_handler = spotipy.CacheFileHandler()
    cache_handler.save_token_to_cache(None)
    return spotipy.Spotify(auth_manager=SpotifyOAuth(scope=scope, show_dialog=True))


def pull_tracks():
    scope = "user-library-read"

    sp = login(scope)
    pull_user_id: str = sp.me()['id']
    saved_tracks = sp.current_user_saved_tracks(limit=50)

    with Progress(
            TextColumn("[progress.description]{task.description}"),
            BarColumn(),
            TaskProgressColumn(),
            MofNCompleteColumn(),
            TimeRemainingColumn(),
            transient=True,
    ) as progress:
        total_saved_tracks = saved_tracks['total']
        fetch_tracks_task = progress.add_task("[green]Fetching all your tracks...", total=int(total_saved_tracks))

        fetched_tracks = []

        def fetch_tracks(tracks):
            track_ids_chunk = []
            for item in tracks['items']:
                track = item['track']
                track_ids_chunk.append(track['id'])
                print("\t\t\t%s - %s" % (track['artists'][0]['name'], track['name']))

                progress.update(fetch_tracks_task, advance=1)
            fetched_tracks.append(track_ids_chunk)

        fetch_tracks(saved_tracks)

        while saved_tracks['next']:
            saved_tracks = sp.next(saved_tracks)
            fetch_tracks(saved_tracks)

        print(f"Fetched {total_saved_tracks} tracks from {sp.me()['display_name']} account!")

        return fetched_tracks, pull_user_id


def push_login(pull_user_id):
    scope = "user-read-private user-read-email user-library-modify"

    console.print(Text(
        "Please make sure you are not logged in account which you just pulled tracks of",
        style="bold yellow"))

    sp = login(scope)
    try:
        me = sp.me()
        pprint(pull_user_id)
        pprint(me['id'])

        if pull_user_id == me['id']:
            retry_choice = Confirm.ask(f"Do you want to login to another account?")
            if retry_choice:
                console.print(Text(
                    "To login to another account you need to click 'Not you?' link",
                    style="bold yellow"))
                return push_login(pull_user_id)
            return None
        me = sp.me()
        continue_choice = Confirm.ask(
            f"Do you want to push tracks to account {me['display_name']} with url {me['external_urls']['spotify']}?")
        if not continue_choice:
            return push_login(pull_user_id)
        return sp
    except SpotifyOauthError:
        console.print(f"You probably denied access to application. Sad :((")
        return None


def push_tracks(tracks, sp):
    with Progress(
            TextColumn("[progress.description]{task.description}"),
            BarColumn(),
            TaskProgressColumn(),
            MofNCompleteColumn(),
            TimeRemainingColumn(),
            transient=True,
    ) as progress:
        tracks_count = 0
        for tracks_chunk in tracks:
            tracks_count += len(tracks_chunk)

        push_tracks_task = progress.add_task(f"[green]Pushing tracks...",
                                             total=tracks_count)
        for tracks_chunk in tracks:
            sp.current_user_saved_tracks_add(tracks_chunk)
            progress.update(push_tracks_task, advance=len(tracks_chunk))
    console.print(Text(f"Successfully pushed {tracks_count} tracks to your second account!"))


if __name__ == "__main__":
    pulled_tracks, user_id = pull_tracks()

    console.print(Text(
        "To push tracks to another account, please go to your browser and logout from spotify",
        style="bold yellow"))

    input("Press ENTER to continue...")
    user = push_login(user_id)
    if not user:
        console.print("Login failed. Aborting....")
        exit(1)

    push_tracks(pulled_tracks, user)
