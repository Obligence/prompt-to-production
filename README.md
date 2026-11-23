# Prompt to Production

Code and production pipeline for the YouTube channel **Prompt to Production**
([@prompt-production](https://www.youtube.com/@prompt-production)): free courses on building real AI applications
with LLMs, from your first prompt to production.

**Course: How to Become an AI Application Engineer.** Lesson code lives in [`code/`](code/), one folder per lesson.
The lesson plan is in [`curriculum.md`](curriculum.md).

## Repository layout

- `code/<slug>/`: runnable code for each lesson (start here if you're a viewer)
- `lessons/<slug>.py`: the lesson's scenes and narration
- `template/build.py`: renders a lesson into a narrated 1080p video, thumbnail, captions and chapters
- `videos/`, `covers/`, `captions/`, `meta/`: build outputs
- `PRODUCTION.md`: the production procedure

Videos are produced by an AI pipeline (AI narration, generated slides) and reviewed before publishing.
