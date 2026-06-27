# Co-Scientist Lite

Co-Scientist Lite is a reusable Codex workflow for live-literature hypothesis generation. It is not a local deployment of Google Co-Scientist and it does not maintain a local literature database.

Chinese documentation: [README.zh-CN.md](README.zh-CN.md)

## Structure

- `prompts/co-scientist-lite.md`: stable task prompt and output contract.
- `workflows/co-scientist-lite-codex.md`: usage notes and quality checks.
- `tools/co_scientist_lite.py`: local helper that generates a Codex task prompt.

## Quick Use

Clone or enter the project directory, then run:

```bash
python3 tools/co_scientist_lite.py \
  --topic "<one-sentence research question: disease/technology/mechanism/population/setting>" \
  --objective "<choose or customize an objective>" \
  --scope "<combine or customize scope constraints>" \
  --depth standard \
  --journal-focus top-journals
```

`--journal-focus` defaults to `top-journals`, which uses high-impact journals to anchor research directions while still requiring direct specialty evidence for concrete claims. Use `--journal-focus direct` for narrow clinical questions where exact-match evidence matters more than journal tier.

Objective options:

- `Generate testable hypotheses and select the top 3`
- `Identify high-impact research directions and convert them into testable projects`
- `Evaluate novelty, feasibility, and translational value`
- `Find hypotheses suitable for retrospective data validation`
- `Design minimum-cost validation plans for the top 3 hypotheses`
- `Generate a review-topic framework and key evidence map`

Scope options:

- `Translational medicine focus; prioritize the last 5 years; AI may be included`
- `Prioritize high-impact literature while adding direct specialty evidence`
- `Favor clinically deployable ideas and available retrospective data`
- `Mechanism-first; allow foundational literature; label evidence levels`
- `Imaging, pathology, multi-omics, and clinical outcomes may be included`
- `For research ideation only; do not provide personalized diagnosis or treatment advice`

To save the generated task prompt:

```bash
python3 tools/co_scientist_lite.py \
  --topic "<one-sentence research question>" \
  --save
```

With `--save`, generated prompts are written to this project's `outputs/co_scientist_requests/`. Use `--output /path/to/request.md` when you want to write the prompt somewhere else.

## Important Boundary

This project generates a stable prompt for a Codex-like assistant. It does not perform literature search by itself, does not include a local paper database, and does not provide clinical diagnosis or treatment advice.
