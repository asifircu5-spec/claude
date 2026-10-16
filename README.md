# Nuzaim Learns 🔺🔢🐝🖍️

A playful learning web app for **3-year-olds**, built as a single `index.html` with no installs or build step.

It has four areas, each with a **Play** game and a **Watch** tab of real videos from public YouTube channels:

| Area | Skill | Game |
|---|---|---|
| 🔺 Think | Qualitative: shapes, colors, big & small | Tap the right shape, color or size |
| 🔢 Count | Quantitative: numbers 1–10 | Tap-and-count, then "How many?" (gets harder as the child succeeds) |
| 🐝 Code | Early coding: sequencing & planning | Plan arrow moves, press **Go**, and watch the bee fly to the flower |
| 🖍️ Draw | Drawing & fine motor | Finger painting, or trace a circle, square, triangle, house or sun |
| 🔬 Science | Observing & predicting | Sink or float (with a water tank), and where animals live |
| ✈️ Travel | Vehicles & places | Land, water or sky, and what to take on a trip |
| 🧭 Explore | Curiosity | Activity ideas to do together, and "Did you know?" facts read aloud |
| 🤸 Move | Exercise & body control | Follow-along moves (jump, stomp, balance) counted out loud |

Instructions are read aloud (🔊) using the browser's built-in speech, so the child doesn't need to read. Correct answers earn ⭐ stars.

## Videos used

All videos are live-action (real people, real animals, real places), from public YouTube channels: Blippi, Ms Rachel, Danny Go!, Dream English Kids, Nat Geo Kids, Nat Geo Animals, Art for Kids Hub, EdThings and It Starts at Home. Some presenters use on-screen graphics, but there are no cartoon shows. Every build checks each video with YouTube's embed service (see the **Check every video** step in the build log), so a removed or non-embeddable video shows up there.

## Run it

- **Locally:** open `index.html` in any modern browser (phone or computer).
- **Online for free:** in this repo go to **Settings → Pages**, set *Source* to `main` branch, `/ (root)`, and save. The app will appear at `https://<your-username>.github.io/claude/`.

## For grown-ups

Short sessions (10–15 minutes) with an adult nearby work best at this age. Stars and coding-level progress are saved only in the browser on your device; nothing is sent anywhere.

## Android app (APK)

The `android/` folder wraps the app in an Android WebView. Every push to `main` runs the **Build Android APK** workflow, which builds `nuzaim-learns.apk` and attaches it to a new release under **Releases**. Download it on an Android phone, open it, and allow installing from this source when asked. The APK is signed with a development key, so it is for personal use, not the Play Store.

## Nuzaim Companion (second app)

`companion/index.html` is a separate, simpler app (English, Bangla, numbers, colors, coding, drawing, science, travel, real-life habits). The same workflow builds it as `nuzaim-companion.apk` with its own app ID, so both apps can be installed side by side. In the Android app, its `speechSynthesis` calls are routed to the phone's text-to-speech engine; Bangla speech needs a Bangla voice installed on the phone.
