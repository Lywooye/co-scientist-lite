# Co-Scientist Lite

Co-Scientist Lite 是一个可复用的 Codex 工作流，用于基于实时文献搜索生成科研假设、反方审查、排序和验证方案。它不是 Google Co-Scientist 的本地部署，也不维护本地文献库。

英文文档：[README.md](README.md)

## 项目结构

- `prompts/co-scientist-lite.md`：稳定任务提示词和输出契约。
- `workflows/co-scientist-lite-codex.md`：使用说明和质量检查规则。
- `tools/co_scientist_lite.py`：生成 Codex 任务提示的本地辅助脚本。

## 快速使用

克隆仓库或进入项目目录后运行：

```bash
python3 tools/co_scientist_lite.py \
  --topic "<一句话研究问题：疾病/技术/机制/人群/场景>" \
  --objective "<选择或自定义 objective>" \
  --scope "<组合或自定义 scope>" \
  --depth standard \
  --journal-focus top-journals
```

`--journal-focus` 默认值为 `top-journals`，表示先用顶刊/高影响文献锚定研究方向，再补充最直接相关的专科证据。对于非常窄的临床问题，可以使用 `--journal-focus direct`，让 exact-match 直接证据优先于期刊层级。

Objective 可选：

- `生成可验证假设并筛选 Top 3 假设`
- `识别顶刊研究方向，并转化为可验证课题`
- `评估研究方向的创新性、可行性和转化价值`
- `找可做回顾性数据验证的科研假设`
- `为 Top 3 假设设计最低成本验证路线`
- `生成综述选题框架和关键证据地图`

Scope 可选：

- `偏转化医学；优先近 5 年；可结合 AI`
- `顶刊/高影响文献优先；同步补充专科直接证据`
- `临床可落地优先；优先使用可获得的回顾性数据`
- `机制研究优先；允许追溯奠基文献；标明证据等级`
- `影像、病理、多组学、临床结局均可纳入`
- `仅用于科研构思；不输出个人化诊断或治疗建议`

保存生成的任务提示：

```bash
python3 tools/co_scientist_lite.py \
  --topic "<一句话研究问题>" \
  --save
```

如果命令在包含 `08_Outputs/` 的 Obsidian 风格工作区运行，保存的任务提示会写入 `08_Outputs/co_scientist_requests/`；否则会写入本项目的 `outputs/co_scientist_requests/`。保存的是任务提示，不是文献库。

## 重要边界

本项目只生成面向 Codex 类助手的稳定提示词。它本身不执行文献搜索、不包含本地论文数据库，也不提供临床诊断或治疗建议。
