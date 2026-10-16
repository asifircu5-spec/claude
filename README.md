# Little Learners 🔺🔢🐝🖍️

A playful learning web app for **3-year-olds**, built as a single `index.html` with no installs or build step.

It has four areas, each with a **Play** game and a **Watch** tab of real videos from public YouTube channels:

| Area | Skill | Game |
|---|---|---|
| 🔺 Think | Qualitative: shapes, colors, big & small | Tap the right shape, color or size |
| 🔢 Count | Quantitative: numbers 1–10 | Tap-and-count, then "How many?" (gets harder as the child succeeds) |
| 🐝 Code | Early coding: sequencing & planning | Plan arrow moves, press **Go**, and watch the bee fly to the flower (7 levels, rocks appear later) |
| 🖍️ Draw | Drawing & fine motor | Finger painting with big brushes, or trace a circle, square, triangle, house or sun |

Instructions are read aloud (🔊) using the browser's built-in speech, so the child doesn't need to read. Correct answers earn ⭐ stars.

## Videos used

Each video was checked on its YouTube page for title and uploading channel (October 2026). Videos play through YouTube's privacy-enhanced embed (`youtube-nocookie.com`). If a channel disables embedding, a link to open it on YouTube is shown under the player.

- **Think:** Sesame Street — *Let's Find Shapes with Elmo!*, *Songs About Colors with Elmo & Friends*; Takalani Sesame — *Zoe and Elmo Learn About Circle Shapes*; Dream English Kids — *Big Small Action Song*
- **Count:** Blocks Universe — *Numberblocks: Numbers 1 to 10!*; Sesame Street — *Time to Count with Elmo and Friends*
- **Code:** CodeMonkey — *Sequencing: Coding Concepts Explained for Kids*; EdThings — *An Introduction to Coding with Bee-Bot*; It Starts at Home by Sonali Kapoor — *Kids Coding Activities Without Computer: Sequencing (3–6 yrs)*
- **Draw:** Art for Kids Hub — *How To Draw A Turtle / A Funny Monster / A Bee / Pizza — Preschool*

Note: the CodeMonkey and Bee-Bot videos are aimed at slightly older children or at grown-ups introducing coding; they work best watched together.

## Run it

- **Locally:** open `index.html` in any modern browser (phone or computer).
- **Online for free:** in this repo go to **Settings → Pages**, set *Source* to `main` branch, `/ (root)`, and save. The app will appear at `https://<your-username>.github.io/claude/`.

## For grown-ups

Short sessions (10–15 minutes) with an adult nearby work best at this age. Stars and coding-level progress are saved only in the browser on your device; nothing is sent anywhere.

## Android app (APK)

The `android/` folder wraps the app in an Android WebView. Every push to `main` runs the **Build Android APK** workflow, which builds `little-learners.apk` and attaches it to a new release under **Releases**. Download it on an Android phone, open it, and allow installing from this source when asked. The APK is signed with a development key, so it is for personal use, not the Play Store.
