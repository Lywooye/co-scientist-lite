# Co-Scientist Lite

Co-Scientist Lite is a reusable prompt/workflow generator for guiding a Codex-like assistant through live-literature hypothesis generation. The generated prompt asks the assistant to use whatever live search tools are available in the current session; this project does not search the literature by itself.

Chinese documentation: [README.zh-CN.md](README.zh-CN.md)

## Structure

- `prompts/co-scientist-lite.md`: stable task prompt and output contract.
- `workflows/co-scientist-lite-codex.md`: usage notes and quality checks.
- `tools/co_scientist_lite.py`: local helper that generates a Codex task prompt.

## Quick Use

Clone or enter the project directory, then run this full template. You can omit optional lines you do not need, but this template shows the complete research-run surface in one place.

```bash
python3 tools/co_scientist_lite.py \
  --topic "<one-sentence research question: disease/technology/mechanism/population/setting>" \
  --objective "<choose or customize an objective>" \
  --scope "<combine or customize scope constraints>" \
  --time-window "Prioritize the last 5 years; include foundational literature when needed; state the search date" \
  --depth standard \
  --mode multi-agent \
  --rounds 2 \
  --generators mechanism,translation,methods \
  --reviewers evidence,methods,translation \
  --ranking tournament \
  --expansion-level focused \
  --transfer-domains liver,thyroid,lymph-node,kidney,prostate \
  --journal-focus top-journals \
  --reference-style vancouver \
  --journal-metrics impact-factor \
  --impact-factor-year 2025 \
  --impact-factor-source "/path/to/journal-impact-factors.xlsx" \
  --medical-boundary "Research ideation only; do not provide personalized diagnosis or treatment advice"
```

## Common Options

Most options are optional. The tool now defaults to `--mode multi-agent`.

| Option | Values | Default | Meaning |
|---|---|---:|---|
| `--topic` | free text | required for research runs | Research question or topic. Not needed when using `--lookup-if`. |
| `--objective` | free text | built-in hypothesis-ranking objective | Goal of the run. |
| `--scope` | free text | built-in medical research scope | Scope, constraints, and exclusions. |
| `--time-window` | free text | built-in recent-literature window | Literature time window and search-date requirement. |
| `--mode` | `multi-agent`, `standard` | `multi-agent` | Workflow structure. `multi-agent` simulates Co-Scientist-style roles; `standard` uses a linear Scope -> Search -> Evidence -> Hypothesis -> Review -> Ranking flow. |
| `--depth` | `quick`, `standard`, `deep` | `standard` | Output detail level. |
| `--journal-focus` | `top-journals`, `balanced`, `direct` | `top-journals` | Evidence priority. `top-journals` anchors directions in high-impact sources while preserving direct specialty evidence. |
| `--reference-style` | `vancouver`, `nature`, `apa` | `vancouver` | Citation style for final references. |
| `--journal-metrics` | `impact-factor`, `none` | `impact-factor` | Whether to request IF/Q quartile matching. |
| `--impact-factor-year` | free text year label | `2025` | IF year label used in the generated prompt. |
| `--impact-factor-source` | file path or source description | none | Optional journal metrics source. If omitted, the tool auto-detects `local/journal_metrics/jcr_2025.jsonl` when present. |
| `--rounds` | integer >= 1 | `2` | Evolution/refinement rounds in `multi-agent` mode. |
| `--generators` | comma-separated list | `mechanism,translation,methods` | Generation perspectives in `multi-agent` mode. |
| `--reviewers` | comma-separated list | `evidence,methods,translation` | Review perspectives in `multi-agent` mode. |
| `--ranking` | `tournament`, `score` | `tournament` | Ranking method in `multi-agent` mode. |
| `--expansion-level` | `none`, `focused`, `broad` | `focused` | Search expansion breadth. `focused` adds adjacent terms and limited cross-disease transfer. |
| `--transfer-domains` | comma-separated list | `liver,thyroid,lymph-node,kidney,prostate` | Method-transfer disease or organ contexts. |
| `--medical-boundary` | free text | research ideation only | Medical safety boundary for the generated prompt. |
| `--save` | flag | off | Save the generated task prompt. Uses `CO_SCIENTIST_REQUEST_DIR` or `local/profile.env` when configured; otherwise falls back to `outputs/co_scientist_requests/`. |
| `--output` | file path | none | Save the generated prompt to an explicit path. |
| `--lookup-if` | journal name | none | Look up local IF/Q metrics and exit. Can be repeated. |

When `--mode standard` is explicitly used, multi-agent-only options such as `--rounds`, `--generators`, `--reviewers`, `--ranking`, `--expansion-level`, and `--transfer-domains` are ignored or reduced to the linear workflow. The CLI emits a warning if those options are explicitly passed with `--mode standard`.

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

`--impact-factor-source` is optional. When provided, it should point to a journal metrics spreadsheet with columns such as full journal title, abbreviation, impact factor, and quartile. If a journal cannot be matched, the generated prompt asks the assistant to write `IF: unmatched/unverified` rather than guessing.

The public repository does not bundle Journal Citation Reports or impact factor datasets. If a private local file exists at `local/journal_metrics/jcr_2025.jsonl`, the tool will automatically reference it in generated prompts. If the file is missing, the tool does not fail; it falls back to verifiable live sources or explicit `unmatched/unverified` labels.

For a quick local lookup:

```bash
python3 tools/co_scientist_lite.py --lookup-if "Radiology"
```

## Multi-agent Simulation

`--mode multi-agent` is the default and generates a no-database, Co-Scientist-inspired multi-agent simulation prompt.

This mode simulates the structure of a supervisor, evidence agent, search expansion agent, cross-disease transfer agent, evidence-distance classifier, generation agents, proximity/clustering agent, reflection reviewers, tournament ranker, evolution agent, and meta-review agent. It does not connect to ChEMBL, UniProt, AlphaFold, or any local paper database.

Search expansion is intended to reduce topic over-narrowing when no local literature database is available. `--expansion-level focused` derives adjacent search terms from the topic and adds limited cross-disease method transfer. Cross-disease evidence is treated as method inspiration only; it cannot directly support clinical claims for the target disease.

## Output Contract

Generated prompts now require a stricter phase-one output contract:

- `Deep Verification Review`: decompose each ranked hypothesis into the core claim, necessary assumptions, testable sub-assumptions, supporting evidence, counter-evidence or missing evidence, and assumptions that would invalidate the hypothesis.
- `Novelty Search Review`: perform targeted live searches before assigning novelty. If live verification is unavailable, the novelty level must be marked as unverified rather than stated as novel.
- `Tournament Pairwise Log`: record pairwise comparisons for tournament ranking, with deeper debate for high-scoring candidates and an explicit order-bias check.
- `Meta-review Feedback for next run`: capture recurring weaknesses, missing search directions, reviewer or agent adjustments, hypothesis patterns to avoid, and recommended next-run scope or transfer-domain changes.
- `hypothesis_pool.json`: append a fenced JSON block with stable fields for downstream parsing, including hypothesis IDs, novelty level, evidence distance, supporting evidence IDs, key assumptions, invalidating assumptions, validation plan, risk flags, and next step.

To save the generated task prompt, add one output option to the full template above:

```bash
--save
```

or:

```bash
--output "/path/to/request.md"
```

With `--save`, generated prompts are written to `CO_SCIENTIST_REQUEST_DIR` if that environment variable or `local/profile.env` configures it. Otherwise the fallback is this project's `outputs/co_scientist_requests/`. Use `--output /path/to/request.md` when you want to write the prompt somewhere else.

## Important Boundary

This project generates a stable prompt for a Codex-like assistant. The assistant may perform live literature search when it executes that prompt, but this script and repository do not perform literature search by themselves, do not include a local paper database, and do not provide clinical diagnosis or treatment advice.
