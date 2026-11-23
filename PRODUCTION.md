# Prompt to Production: lesson production guide

Channel: **Prompt to Production** (youtube.com/@prompt-production). Owner: Reza.
Course: **How to Become an AI Application Engineer**, a free course for software engineers moving into AI
application engineering and for beginners starting from scratch. The plan is in `curriculum.md`; what has been
published is in `log.md`. This file is the authoritative procedure for the daily production agent.

The channel's promise: real engineering, not vibe coding. Every lesson teaches current best practice, shows code
that actually works, and builds toward shipping production AI apps.

## 1. Daily flow (two approvals from Reza)

1. `./setup.sh` (installs packages, downloads the voice model and the code font into `.cache/`).
2. Pick the next lesson: the first row in `curriculum.md` whose status is `todo` (or `built`, see below), in order.
   If Reza asked for a different lesson, do that one.
3. **Approval 1, the lesson plan.** Research the topic (section 2), then send Reza: the YouTube title, the lesson's
   promise in one sentence, the scene outline (one line per scene: kind, title, what it teaches), the main code
   that will appear, target length, and anything he should decide. Ask him to reply "go" or to ask for changes.
   Stop and wait. Build nothing before "go".
4. Write `lessons/<slug>.py` and `code/<slug>/` (sections 3 and 4), check them, render previews, look at them.
5. Full build (section 5). Check the output.
6. **Approval 2, the preview.** Send Reza the MP4, the cover and the SRT, plus the title, description (with
   chapters), tags, and the facts or API details you verified with their sources. Say plainly that nobody listened
   to the audio. Ask him to reply "approve" or to say what to change. Stop and wait. Rebuild and re-send after changes.
7. Only after an explicit "approve" given after he received the preview: commit, push, upload (section 6),
   then update `curriculum.md` and `log.md`, push again, and send Reza the link plus any manual to-dos.

If Reza does not reply, do nothing further. Never upload without approval 2.

A row with status `built` already has a finished video in the repo (for example lesson 11, the reference lesson).
For it, skip building: check the content is still current, send the plan and the preview together, and ask for
"approve".

## 2. Research and accuracy rules

- AI tooling changes fast. Before writing any lesson, check the current official documentation for every API,
  SDK call, parameter, library and model name you will show (web search; prefer docs.anthropic.com /
  docs.claude.com, platform.openai.com/docs, ai.google.dev, the library's own docs and GitHub). Never show an API
  feature you have not confirmed in current docs. Note the sources for the preview message.
- Prefer the newest stable method, and say so in the narration when an older pattern is still common
  ("you'll still see X in tutorials; today, use Y").
- Never state prices, limits or benchmark numbers from memory. If a lesson needs them, take them from the official
  page on the day, say "at the time of recording", or use clearly labeled placeholders as lesson 11 does.
- Code shown on screen must be correct and runnable. Put the complete runnable version in `code/<slug>/` with a
  short README (setup and run commands). Check every Python file with `python3 -m py_compile`. Install the libraries
  and run whatever runs without an API key (imports, pure functions, unit tests, a fake client). If something could
  not be run, tell Reza which part was not executed.
- Default provider in examples: the Anthropic SDK with a current Claude model; mention that the same ideas work with
  other providers, and show another provider when the lesson is about comparing them.
- Teach like a senior engineer: explain why, show the failure mode, then the fix. Keep a running thread through the
  course (the same small app grows from lesson to lesson where it makes sense).

## 3. The lesson file (`lessons/<slug>.py`)

Slug: `l<number>_<short_name>`, e.g. `l12_chatbot_memory`. Copy `lessons/l11_first_llm_call.py`, the reference
that uses every scene kind. A lesson file defines:

```python
LESSON = dict(number=12, module=4, slug="l12_chatbot_memory", title="Build a Chatbot with Memory",
              cover_text="Chatbot|with memory",          # 1 to 2 short lines for the thumbnail, '|' splits lines
              next="Lesson 13: Streaming responses")    # shown on the outro
SCENES = [ dict(kind=..., title=..., chapter=..., steps=[(narration, arg), ...], ...), ... ]
```

Each scene has `steps`: a list of `(narration text, arg)`. Each step's visual change starts with its narration.
`chapter` is the YouTube chapter name (defaults to the scene title). Scene kinds:

| kind | fields | step arg |
|---|---|---|
| `title` | (none; uses LESSON) | ignored. Always the first scene. One step. |
| `bullets` | `title`, `style` goal/warn/tip, `side`: `{"terminal": [[text, color], ...]}`, `"warning"`, `"check"` or None | the new card's text (max ~40 chars), or None for a step that adds no card. Max 4 cards. |
| `code` | `title`, `code`, `lang` python/bash/json, `file` (tab name) | number of lines visible after this step (99 = all). New lines type in and get highlighted. Max ~22 lines. |
| `terminal` | `title`, `lines`: `[[text, color], ...]`, `file` | lines visible after this step |
| `flow` | `title`, `subtitle`, `boxes`: `[[title, caption, kind], ...]` (2 to 5), `callout` | boxes visible after this step |
| `rows` | `title`, `subtitle`, `headline`, `headline_sub`, `rows`: `[{"label", "chips": [[text, kind]], "arrow", "bar"}]`, `bar_label`, `callout` | stage: 1 = big headline, 2 = rows appear, 3 = bars and callout |
| `outro` | `title`, `tasks` (2 to 4 short homework items) | ignored; the second step shows the "Next" card. Always last. |

Colors for terminal/side lines: fg, muted, violet, teal, amber, red. Chip/box kinds: user, bot, tool, system, data.

Lesson shape (5 to 14 minutes, as long as the topic needs and no padding; never over 14:30, the upload limit for unverified channels is 15 min):
title (hook in the first 10 seconds: what you'll build and why it matters) → "By the end of this lesson" goals →
concept diagram (flow/rows) → code in small steps, each followed by a terminal run when useful → one "common
mistakes" bullets scene → outro with homework and the next lesson. Split long code over several code scenes
(max ~22 lines each). One idea per scene.

## 4. Narration

- Voice Kokoro `am_fenrir`, speed 1.05 (Reza's choice). Never imitate a real person's voice.
- Write for the ear: short sentences, one idea each, conversational ("you", "let's"), no hype.
- Spell out what the voice might misread: "messages dot create", "max tokens", "L L M" only if needed (LLM is fine),
  "uv" is fine, numbers as words when short ("eleven"), URLs never read aloud ("the link below").
- Code is not read aloud character by character; narrate what the highlighted lines do.
- No music for now. No burned-in subtitles; the SRT file is uploaded as captions.

## 5. Build and check

```
./setup.sh
python3 template/build.py lessons/<slug>.py --preview   # PNG per step in build/<slug>/ + preview_cover.jpg
python3 template/build.py lessons/<slug>.py             # full build (about 2 to 5 minutes per 10 minutes of video)
python3 template/build.py lessons/<slug>.py --scenes 3,4   # re-render only changed scenes (narration unchanged)
```

Look at every preview PNG before the full build: text must not overflow its box or the screen, code must fit
the window, cards must not overlap. Outputs: `videos/<slug>.mp4` (1920x1080, 30 fps), `covers/<slug>.jpg`
(1280x720), `captions/<slug>.srt`, `meta/<slug>_chapters.txt`. Check the MP4 with ffprobe (video and audio
present, durations match, under 95 MB) and look at a few frames from the finished file.

## 6. Upload (Zapier, YouTube app `YouTubeV4CLIAPI`)

**Channel safety, every time.** Reza's Zapier has more than one YouTube connection (one is Planck to Parsec).
Use only the Prompt to Production connection, passing its `connection_id` explicitly on every YouTube action.
Find it with `list_zapier_connections` and, for each candidate, `youtube_make_api_get_request` on
`https://www.googleapis.com/youtube/v3/channels` with querystring `part=snippet, mine=true`: the right one returns
`snippet.customUrl` = `@prompt-production`. Run this check before every upload. If no connection returns
@prompt-production, do not upload: tell Reza to connect the channel in Zapier. Never use the default connection.

Push first. Zapier fetches files from `https://raw.githubusercontent.com/Obligence/prompt-to-production/main/...`
(check the video URL returns 200).

1. `youtube_upload_video` with `connection_id`: `title` (under 100 characters, format
   `<Lesson title> | AI Application Engineer Course #<lesson number>`), `description` (below), `video` = raw URL,
   `privacy_status` "public", `tags` (8 to 12), `default_language` "en", `default_audio_language` "en",
   `category_id` "27" (Education), `made_for_kids` false.
2. Wait about three minutes, then `youtube_update_video_thumbnail` with `video_id` and the raw URL of
   `covers/<slug>.jpg`. Retry once after a minute if it fails; tell Reza if it still fails.
3. Add the video to the course playlist with `youtube_add_video_to_playlist`. The playlist ID is recorded below
   once it exists. If it does not exist yet, create it once (after Reza's approval of the upload) with
   `youtube_make_api_mutating_request`: POST `https://www.googleapis.com/youtube/v3/playlists?part=snippet,status`,
   body `{"snippet": {"title": "How to Become an AI Application Engineer (Full Free Course)", "description": "..."},
   "status": {"privacyStatus": "public"}}`, then write its ID here and commit.
4. Manual to-dos for Reza (Zapier cannot do these): upload `captions/<slug>.srt` as English subtitles, and in
   YouTube Studio tick "altered or synthetic content" only if YouTube asks (an AI voice on slides is usually not
   required to be labeled; the channel description says the narration is AI-generated).

Course playlist ID: (not created yet)

Description template:
```
<two sentences: what you'll build/learn in this lesson, with the main search terms>

📂 Code: https://github.com/Obligence/prompt-to-production/tree/main/code/<slug>
📚 Full course playlist: <playlist link, once it exists>
⏭️ Next: Lesson <n+1>: <title>

Chapters
<contents of meta/<slug>_chapters.txt>

Sources and docs:
<official docs used>

Narration is AI-generated. Code reviewed and tested.
#AIEngineering #LLM #Python
```

Zapier allows about 5 YouTube uploads per day across all of Reza's channels; "This action has been throttled"
means the limit was hit: stop and upload another day. Always `inspect_zapier_actions` before executing. Upload one
video per run, only after approval, and never change or delete other videos.

## 7. Records

- `curriculum.md`: set the lesson's status to `published` and add the YouTube link.
- `log.md`: add a row (date, lesson number, title, slug, length, YouTube link).
- Commit message: `Lesson <n>: <title>`.
