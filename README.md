# Watch Calendar — Full Setup Guide (no GitHub experience needed)

This builds a Google Calendar subscription feed containing:
1. **Upcoming episodes** for TV shows you list, pulled from TVMaze (free, no signup).
2. **Upcoming US movie releases with a Metacritic score above 80**, pulled from TMDB (release dates) + OMDb (Metascore — there's no public Metacritic API, so OMDb is the closest legitimate substitute).

Everything below uses GitHub's **website only** — no command line, no installing git, no coding required from you. You'll just create accounts, upload files by dragging them into a browser window, and click a few buttons. It takes about 15–20 minutes the first time.

---

## Part 1: Get your two free API keys

You need these before anything else — they're what let the script actually fetch movie/TV data.

### 1a. TMDB key
1. Go to https://www.themoviedb.org/ and click **Join TMDB** (top right) to create a free account. Verify your email if asked.
2. Once logged in, click your profile icon (top right) → **Settings**.
3. In the left sidebar, click **API**.
4. Click **Create** (or "Request an API Key"), choose **Developer**, and fill in the short form (you can put "personal calendar project" for the app name/URL/description — it's just for your own use).
5. Once approved (usually instant), you'll see a field called **API Key (v3 auth)**. Copy that string somewhere safe (e.g., a notes app) — it looks like a random string of letters and numbers.

### 1b. OMDb key
1. Go to https://www.omdbapi.com/apikey.aspx
2. Select the **FREE (1,000 daily limit)** option, enter your email, and submit.
3. Check your email — OMDb sends an activation link. Click it to activate your key.
4. Save the key (it's a short string, also emailed to you).

You should now have two keys saved somewhere: one from TMDB, one from OMDb.

---

## Part 2: Create your GitHub account

1. Go to https://github.com and click **Sign up**.
2. Enter an email, password, and username, and follow the verification steps.
3. Once you're logged in, you'll land on your GitHub homepage.

---

## Part 3: Create the repository (this just means "project folder on GitHub")

1. Click the **+** icon in the top-right corner of any GitHub page → **New repository**.
2. **Repository name**: type something like `watch-calendar` (no spaces).
3. Leave it set to **Public** (this is required for the free version of the feature we'll use later — your calendar events will only be visible to people who have your exact private feed URL, which is long and unguessable).
4. Do **not** check "Add a README file" — leave everything else default.
5. Click **Create repository**.

You'll land on an empty repo page with some setup instructions on it — ignore those, we're going to upload files directly.

---

## Part 4: Upload the project files

You should have unzipped the `watch-calendar.zip` file I gave you on your computer first (double-click it, or right-click → Extract All on Windows / just double-click on Mac). You should now have a folder called `watch-calendar` containing:
- `generate_calendar.py`
- `config.yaml`
- `requirements.txt`
- `README.md`
- a `docs` folder (containing `calendar.ics`)
- a `.github` folder (containing a `workflows` folder, containing `update-calendar.yml`)

**Important:** folders starting with a dot (like `.github`) are often hidden by your operating system. If you don't see it:
- **Mac**: in Finder, press `Cmd + Shift + .` (period) to reveal hidden files.
- **Windows**: in File Explorer, go to the **View** tab → check **Hidden items**.

Now, on your empty GitHub repo page:
1. Click **uploading an existing file** (a link in the setup instructions), or click **Add file → Upload files**.
2. Open your `watch-calendar` folder in a separate File Explorer/Finder window, select **everything inside it** (all files and both folders), and drag the whole selection into the GitHub upload box in your browser.
3. GitHub will show a list of files being staged for upload — double check you see `.github/workflows/update-calendar.yml` and `docs/calendar.ics` listed (not just the top-level files). If the `.github` folder didn't upload, drag it in separately.
4. Scroll down, and click the green **Commit changes** button (default settings are fine).

Your repo should now show all the files and folders.

---

## Part 5: Add your API keys as "secrets"

Secrets are how you give the script your API keys without them being visible to anyone browsing your repo.

1. On your repo page, click **Settings** (top menu bar of the repo, not your account settings — it has a gear icon).
2. In the left sidebar, click **Secrets and variables** → **Actions**.
3. Click the green **New repository secret** button.
4. **Name**: type exactly `TMDB_API_KEY` (all caps, exact spelling matters).
5. **Secret**: paste your TMDB key.
6. Click **Add secret**.
7. Repeat steps 3–6 for a second secret: **Name** `OMDB_API_KEY`, **Secret** = your OMDb key.

You should now see two secrets listed (their values are hidden — that's expected).

---

## Part 6: Tell the script which shows you watch

1. On your repo's main page, click on `config.yaml`.
2. Click the pencil icon (✏️) near the top right of the file view to edit it.
3. Replace the example show names with the actual shows you watch, one per line, keeping the same `- "Show Name"` format. Use the show's common title, adding the year in parentheses if it's a remake/reboot with an ambiguous name (e.g. `- "Suits (2011)"`).
4. Optionally adjust `min_metascore` (default 80) or `lookahead_days`.
5. Scroll down, click **Commit changes**.

---

## Part 7: Turn on GitHub Pages (this is what makes your file publicly fetchable by URL)

1. Repo page → **Settings** → in the left sidebar, click **Pages**.
2. Under **Build and deployment** → **Source**, choose **Deploy from a branch**.
3. Under **Branch**, choose `main` from the first dropdown, and `/docs` from the second dropdown (it defaults to `/root` — change it to `/docs`).
4. Click **Save**.
5. Wait about a minute, then refresh the page. Near the top you should see a green box saying your site is live at a URL like:
   ```
   https://your-username.github.io/watch-calendar/
   ```
   Keep this tab open — you'll need this URL in Part 9.

---

## Part 8: Run the script for the first time

1. On your repo page, click the **Actions** tab (top menu).
2. If prompted with "Workflows aren't being run on this forked repository" or similar, click **I understand my workflows, go ahead and enable them**.
3. In the left sidebar, click **Update Watch Calendar**.
4. Click the **Run workflow** dropdown button (right side) → **Run workflow** (green button in the little popup).
5. Refresh the page after a few seconds — you'll see a run appear with a yellow dot (in progress), then a green checkmark (success) after roughly 30–90 seconds depending on how many shows/movies it processes.
   - If you instead see a red ❌, click into the run to view the log — the most common cause is a typo in one of the secret names (must be exactly `TMDB_API_KEY` and `OMDB_API_KEY`) or an unactivated OMDb key (check your email).
6. Once it's green, go back to the **Code** tab → open `docs/calendar.ics` → click it and confirm it now contains real `BEGIN:VEVENT` entries with show/movie names, not just the empty placeholder.

---

## Part 9: Subscribe in Google Calendar

Your feed URL is the Pages URL from Part 7, with `calendar.ics` on the end:
```
https://your-username.github.io/watch-calendar/calendar.ics
```

1. Open Google Calendar in a browser (calendar.google.com) — this must be done on desktop; the mobile app doesn't support adding by URL.
2. On the left sidebar, next to **Other calendars**, click the **+**.
3. Click **From URL**.
4. Paste your feed URL and click **Add calendar**.
5. It may take a minute or two for Google to do its first fetch. Your events will then appear, and it'll re-check periodically on its own (Google decides the exact frequency — usually every 12–24 hours — this can't be forced faster from our side, but the daily Action keeps the file itself fresh so whenever Google does check, it gets current data).

---

## Ongoing maintenance

- **Adding/removing shows**: go back to `config.yaml` in your repo (Part 6) and edit it anytime — no need to touch anything else. The next scheduled run (daily) will pick up the change automatically, or you can force it immediately via Actions → Update Watch Calendar → Run workflow (Part 8).
- **Checking it's still working**: the Actions tab will show a red ❌ if a run ever fails — worth a glance every so often. Common cause is an API key expiring or a service being temporarily down.
- **Nothing to install or renew**: GitHub Actions' free tier easily covers one run a day for a personal project like this indefinitely.

## Two honest limitations, explained

1. **Refresh timing**: Google Calendar — not this script — decides how often it re-polls your subscribed URL, typically every 12–24 hours. Running the Action daily is the correct and sufficient thing to do on your end; there's no setting anywhere that forces Google to check faster.
2. **Movies "showing up late"**: Metacritic scores are usually only assigned once critics review a film, often right around its release date rather than months ahead. So a movie won't appear on your calendar until it actually has a Metascore — the script also re-checks the last couple weeks of releases (`lookback_days` in config) to catch scores that land a few days after release.
