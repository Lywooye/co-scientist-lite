# Co-Scientist Lite

Co-Scientist Lite is a reusable prompt/workflow generator for guiding a Codex-like assistant through live-literature hypothesis generation. The generated prompt asks the assistant to use whatever live search tools are available in the current session; this project does not search the literature by itself.

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
  --mode standard \
  --journal-focus top-journals \
  --reference-style vancouver \
  --journal-metrics impact-factor
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

## Reference Formatting and Journal Metrics

Reports are prompted to format references in a standard citation style and, by default, add journal impact factors when they can be verified.

```bash
python3 tools/co_scientist_lite.py \
  --topic "<one-sentence research question>" \
  --reference-style vancouver \
  --journal-metrics impact-factor \
  --impact-factor-year 2025 \
  --impact-factor-source "/path/to/journal-impact-factors.xlsx"
```

`--impact-factor-source` is optional. When provided, it should point to a journal metrics spreadsheet with columns such as full journal title, abbreviation, impact factor, and quartile. If a journal cannot be matched, the generated prompt asks the assistant to write `IF: unmatched/unverified` rather than guessing.

## Multi-agent Simulation

Use `--mode multi-agent` to generate a no-database, Co-Scientist-inspired multi-agent simulation prompt:

```bash
python3 tools/co_scientist_lite.py \
  --topic "<one-sentence research question>" \
  --objective "Generate testable hypotheses and select the top 3" \
  --scope "Translational medicine focus; prioritize recent high-impact and direct evidence" \
  --mode multi-agent \
  --rounds 2 \
  --generators mechanism,translation,methods \
  --reviewers evidence,methods,translation \
  --ranking tournament \
  --expansion-level focused \
  --transfer-domains liver,thyroid,lymph-node,kidney,prostate \
  --reference-style vancouver \
  --journal-metrics impact-factor
```

This mode simulates the structure of a supervisor, evidence agent, search expansion agent, cross-disease transfer agent, evidence-distance classifier, generation agents, proximity/clustering agent, reflection reviewers, tournament ranker, evolution agent, and meta-review agent. It does not connect to ChEMBL, UniProt, AlphaFold, or any local paper database.

Search expansion is intended to reduce topic over-narrowing when no local literature database is available. `--expansion-level focused` derives adjacent search terms from the topic and adds limited cross-disease method transfer. Cross-disease evidence is treated as method inspiration only; it cannot directly support clinical claims for the target disease.

To save the generated task prompt:

```bash
python3 tools/co_scientist_lite.py \
  --topic "<one-sentence research question>" \
  --save
```

With `--save`, generated prompts are written to this project's `outputs/co_scientist_requests/`. Use `--output /path/to/request.md` when you want to write the prompt somewhere else.

## Important Boundary

This project generates a stable prompt for a Codex-like assistant. The assistant may perform live literature search when it executes that prompt, but this script and repository do not perform literature search by themselves, do not include a local paper database, and do not provide clinical diagnosis or treatment advice.
