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
  --topic "<一句话研究问题：疾病/技术/机制/人群/场景>" \
  --objective "<选择或自定义 objective>" \
  --scope "<组合或自定义 scope>" \
  --depth standard \
  --journal-focus top-journals
```

`--journal-focus` defaults to `top-journals`, which uses high-impact journals to anchor research directions while still requiring direct specialty evidence for concrete claims. Use `--journal-focus direct` for narrow clinical questions where exact-match evidence matters more than journal tier.

Objective options:

- `生成可验证假设并筛选 Top 3 假设`
- `识别顶刊研究方向，并转化为可验证课题`
- `评估研究方向的创新性、可行性和转化价值`
- `找可做回顾性数据验证的科研假设`
- `为 Top 3 假设设计最低成本验证路线`
- `生成综述选题框架和关键证据地图`

Scope options:

- `偏转化医学；优先近 5 年；可结合 AI`
- `顶刊/高影响文献优先；同步补充专科直接证据`
- `临床可落地优先；优先使用可获得的回顾性数据`
- `机制研究优先；允许追溯奠基文献；标明证据等级`
- `影像、病理、多组学、临床结局均可纳入`
- `仅用于科研构思；不输出个人化诊断或治疗建议`

To save the generated task prompt:

```bash
python3 tools/co_scientist_lite.py \
  --topic "<一句话研究问题>" \
  --save
```

If the command is run from an Obsidian-style workspace containing `08_Outputs/`, saved prompts go to `08_Outputs/co_scientist_requests/`. Otherwise they go to this project's `outputs/co_scientist_requests/`.

## Important Boundary

This project generates a stable prompt for a Codex-like assistant. It does not perform literature search by itself, does not include a local paper database, and does not provide clinical diagnosis or treatment advice.
