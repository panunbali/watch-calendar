"""
Generates docs/calendar.ics from:
  - TVMaze (free, no key) -> upcoming episodes for shows listed in config.yaml
  - TMDB (free key)       -> upcoming US theatrical movie releases
  - OMDb (free key)       -> Metascore lookup, used to filter movies

Run daily by the GitHub Action in .github/workflows/update-calendar.yml.
"""
import os
import sys
from datetime import datetime, timedelta, date

import requests
import yaml
from icalendar import Calendar, Event

TMDB_API_KEY = os.environ.get("TMDB_API_KEY")
OMDB_API_KEY = os.environ.get("OMDB_API_KEY")

if not TMDB_API_KEY or not OMDB_API_KEY:
    print("ERROR: TMDB_API_KEY and OMDB_API_KEY must be set as environment variables "
          "(GitHub Actions secrets when run in CI).")
    sys.exit(1)

with open("config.yaml", "r") as f:
    config = yaml.safe_load(f)

TV_SHOWS = config.get("tv_shows", [])
MOVIE_CFG = config.get("movies", {})
MIN_METASCORE = MOVIE_CFG.get("min_metascore", 80)
LOOKAHEAD_DAYS = MOVIE_CFG.get("lookahead_days", 120)
LOOKBACK_DAYS = MOVIE_CFG.get("lookback_days", 14)

cal = Calendar()
cal.add("prodid", "-//Personal Watch Calendar//github.com//")
cal.add("version", "2.0")
cal.add("x-wr-calname", "TV + Movies (Metascore 80+)")
cal.add("x-wr-timezone", "America/New_York")
# Tell subscribers (Google Calendar included) how often to refresh.
# Google treats this as a hint, not a guarantee, but it's the correct signal to send.
cal.add("x-published-ttl", "PT24H")
cal.add("refresh-interval;value=duration", "PT24H")


def add_event(uid, summary, day, description=""):
    event = Event()
    event.add("uid", uid)
    event.add("summary", summary)
    event.add("dtstart", day)
    event.add("dtend", day + timedelta(days=1))
    event.add("dtstamp", datetime.utcnow())
    if description:
        event.add("description", description)
    cal.add_component(event)


def fetch_tv_episodes():
    today = date.today()
    for show_name in TV_SHOWS:
        try:
            r = requests.get(
                "https://api.tvmaze.com/search/shows",
                params={"q": show_name},
                timeout=15,
            )
            r.raise_for_status()
            results = r.json()
            if not results:
                print(f"  [TV] No match found for '{show_name}'")
                continue
            show = results[0]["show"]
            show_id = show["id"]
            show_title = show["name"]
        except Exception as e:
            print(f"  [TV] Error searching for '{show_name}': {e}")
            continue

        try:
            r = requests.get(
                f"https://api.tvmaze.com/shows/{show_id}/episodes", timeout=15
            )
            r.raise_for_status()
            episodes = r.json()
        except Exception as e:
            print(f"  [TV] Error fetching episodes for '{show_title}': {e}")
            continue

        count = 0
        for ep in episodes:
            airdate = ep.get("airdate")
            if not airdate:
                continue
            ep_date = datetime.strptime(airdate, "%Y-%m-%d").date()
            if ep_date < today:
                continue
            season = ep.get("season")
            number = ep.get("number")
            ep_title = ep.get("name") or "TBA"
            uid = f"tv-{show_id}-s{season}e{number}@personal-watch-calendar"
            if season and number:
                summary = f"\U0001F4FA {show_title} S{season:02d}E{number:02d} \u2013 {ep_title}"
            else:
                summary = f"\U0001F4FA {show_title} \u2013 {ep_title}"
            add_event(
                uid,
                summary,
                ep_date,
                description=f"{show_title} on TVMaze: https://www.tvmaze.com/shows/{show_id}",
            )
            count += 1
        print(f"  [TV] '{show_title}': {count} upcoming episode(s)")


def fetch_movies():
    today = date.today()
    end_date = today + timedelta(days=LOOKAHEAD_DAYS)
    start_date = today - timedelta(days=LOOKBACK_DAYS)

    page = 1
    max_pages = 10
    checked = 0
    added = 0

    while page <= max_pages:
        params = {
            "api_key": TMDB_API_KEY,
            "region": "US",
            "sort_by": "primary_release_date.asc",
            "primary_release_date.gte": start_date.isoformat(),
            "primary_release_date.lte": end_date.isoformat(),
            # 2 = Theatrical (limited), 3 = Theatrical
            "with_release_type": "2|3",
            "page": page,
        }
        try:
            r = requests.get(
                "https://api.themoviedb.org/3/discover/movie", params=params, timeout=15
            )
            r.raise_for_status()
            data = r.json()
        except Exception as e:
            print(f"  [Movies] Error fetching TMDB page {page}: {e}")
            break

        results = data.get("results", [])
        if not results:
            break

        for movie in results:
            checked += 1
            title = movie.get("title")
            release_date = movie.get("release_date")
            if not title or not release_date:
                continue
            try:
                rel_date = datetime.strptime(release_date, "%Y-%m-%d").date()
            except ValueError:
                continue

            year = rel_date.year
            try:
                r2 = requests.get(
                    "https://www.omdbapi.com/",
                    params={"apikey": OMDB_API_KEY, "t": title, "y": year},
                    timeout=15,
                )
                r2.raise_for_status()
                omdb_data = r2.json()
            except Exception as e:
                print(f"  [Movies] OMDb error for '{title}': {e}")
                continue

            metascore_raw = omdb_data.get("Metascore")
            if not metascore_raw or metascore_raw == "N/A":
                continue
            try:
                metascore = int(metascore_raw)
            except ValueError:
                continue

            if metascore > MIN_METASCORE:
                uid = f"movie-{movie.get('id')}@personal-watch-calendar"
                summary = f"\U0001F3AC {title} (Metascore {metascore})"
                add_event(
                    uid,
                    summary,
                    rel_date,
                    description=f"TMDB: https://www.themoviedb.org/movie/{movie.get('id')}",
                )
                added += 1

        total_pages = data.get("total_pages", 1)
        page += 1
        if page > total_pages:
            break

    print(f"  [Movies] Checked {checked} movies, added {added} with Metascore > {MIN_METASCORE}")


def main():
    print("Fetching TV episodes...")
    fetch_tv_episodes()
    print("Fetching movies...")
    fetch_movies()

    os.makedirs("docs", exist_ok=True)
    with open("docs/calendar.ics", "wb") as f:
        f.write(cal.to_ical())
    print("Wrote docs/calendar.ics")


if __name__ == "__main__":
    main()
