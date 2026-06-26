# Co-Scientist Lite

Co-Scientist Lite is a reusable Codex workflow for live-literature hypothesis generation. It is not a local deployment of Google Co-Scientist and it does not maintain a local literature database.

## Structure

- `prompts/co-scientist-lite.md`: stable task prompt and output contract.
- `workflows/co-scientist-lite-codex.md`: usage notes and quality checks.
- `tools/co_scientist_lite.py`: local helper that generates a Codex task prompt.

## Quick Use

Clone or enter the project directory, then run:

```bash
python3 tools/co_scientist_lite.py \
  --topic "肠癌肝转移超声造影研究" \
  --objective "生成可验证假设并筛选 Top 3 假设" \
  --scope "偏转化医学；优先近 5 年；可结合AI" \
  --depth standard
```

To save the generated task prompt:

```bash
python3 tools/co_scientist_lite.py \
  --topic "肠癌肝转移超声造影研究" \
  --save
```

If the command is run from an Obsidian-style workspace containing `08_Outputs/`, saved prompts go to `08_Outputs/co_scientist_requests/`. Otherwise they go to this project's `outputs/co_scientist_requests/`.

## Important Boundary

This project generates a stable prompt for a Codex-like assistant. It does not perform literature search by itself, does not include a local paper database, and does not provide clinical diagnosis or treatment advice.
