# Nuzaim Learns 🔺🔢🐝🖍️

A playful learning web app for **3-year-olds**, built as a single `index.html` with no installs or build step.

It has 14 sections, each switchable between **Bangla and English**: Letters (all স্বরবর্ণ, ব্যঞ্জনবর্ণ, A–Z with tracing), Numbers (1–100 in Bangla, English and Roman numerals; নামতা 1–25), Think (shapes, colors, sizes, memory, patterns), Code, Draw, Science, Travel, World (196 countries: flag, capital, currency, leaders, parliament), Explore, Move, **My Body** (tap a drawn child or face to hear each part's name; find-it game; five senses; "Touch your…"), My Day (routines, brushing and handwashing timers, safety), Stories & Rhymes, and Seasons & Festivals. A grown-ups area (press and hold 3 seconds) has a daily time limit, a lock that keeps the child inside the app, and progress.

Instructions are read aloud using the phone's text-to-speech; Bangla needs a Bangla voice installed.

## Country facts

`tools/build_countries.py` runs on every build. It fetches capitals, leaders and parliaments from Wikidata and currencies from Unicode CLDR. A leader is shown only when two Wikidata records agree; otherwise the app says to check an official source. `tools/overrides.json` holds hand-verified corrections with sources; each one expires after 180 days or as soon as Wikidata agrees. The build's release notes include a report of every disagreement.

## Videos used

All videos are live-action (real people, real animals, real places), from public YouTube channels: Blippi, Ms Rachel, Danny Go!, Dream English Kids, Nat Geo Kids, Nat Geo Animals, Art for Kids Hub, EdThings and It Starts at Home. Some presenters use on-screen graphics, but there are no cartoon shows. Every build checks each video with YouTube's embed service (see the **Check every video** step in the build log), so a removed or non-embeddable video shows up there.

## Run it

- **Locally:** open `index.html` in any modern browser (phone or computer).
- **Online for free:** in this repo go to **Settings → Pages**, set *Source* to `main` branch, `/ (root)`, and save. The app will appear at `https://<your-username>.github.io/claude/`.

## For grown-ups

Short sessions (10–15 minutes) with an adult nearby work best at this age. Stars and coding-level progress are saved only in the browser on your device; nothing is sent anywhere.

## Android app (APK)

The `android/` folder wraps the app in an Android WebView. Every push to `main` runs the **Build Android APK** workflow, which builds `nuzaim-learns.apk` and attaches it to a new release under **Releases**. Download it on an Android phone, open it, and allow installing from this source when asked. The APK is signed with a development key, so it is for personal use, not the Play Store.
