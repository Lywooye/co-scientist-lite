# Co-Scientist Lite Codex Workflow

这个 workflow 用来让 Codex 稳定执行“实时文献搜索 -> 假设生成 -> 反方审查 -> 排序 -> 验证方案”的科研流程。它不是 Google Co-Scientist 的本地部署，也不创建本地文献库。

## 适用场景

- 想快速判断一个医学/生命科学研究方向是否值得做。
- 想从文献中生成可验证假设，而不是只要综述摘要。
- 想把假设按临床转化价值、证据强度和实验可行性排序。
- 想获得 Top 3 的最低成本验证路线。

## 不适用场景

- 个人化诊断、治疗、用药建议。
- 需要注册方案的正式系统综述或 meta-analysis。
- 需要访问院内隐私数据、未公开数据库或付费全文的任务。

## 调用方式

### 方式 A：直接复制 prompt

1. 打开 `prompts/co-scientist-lite.md`。
2. 复制“复制给 Codex 的任务模板”。
3. 替换 `<topic>`、`<objective>`、`<scope_and_constraints>`、`<time_window>`。
4. 发给 Codex 执行。

### 方式 B：用本地生成器生成任务提示

```bash
python3 tools/co_scientist_lite.py \
  --topic "<一句话研究问题：疾病/技术/机制/人群/场景>" \
  --objective "<选择或自定义 objective>" \
  --scope "<组合或自定义 scope>" \
  --depth standard \
  --journal-focus top-journals
```

`--objective` 可选：

- `生成可验证假设并筛选 Top 3 假设`
- `识别顶刊研究方向，并转化为可验证课题`
- `评估研究方向的创新性、可行性和转化价值`
- `找可做回顾性数据验证的科研假设`
- `为 Top 3 假设设计最低成本验证路线`
- `生成综述选题框架和关键证据地图`

`--scope` 可选：

- `偏转化医学；优先近 5 年；可结合 AI`
- `顶刊/高影响文献优先；同步补充专科直接证据`
- `临床可落地优先；优先使用可获得的回顾性数据`
- `机制研究优先；允许追溯奠基文献；标明证据等级`
- `影像、病理、多组学、临床结局均可纳入`
- `仅用于科研构思；不输出个人化诊断或治疗建议`

`--journal-focus` 可选：

- `top-journals`：默认值。先用顶刊/高影响文献锚定研究方向，再补专科直接证据。
- `balanced`：高影响方向、专科直接证据、指南和临床试验平衡纳入。
- `direct`：优先 exact-match 直接证据，顶刊主要用于机制背景和前沿方向。

保存一份任务请求：

```bash
python3 tools/co_scientist_lite.py \
  --topic "<一句话研究问题>" \
  --objective "<选择或自定义 objective>" \
  --scope "<组合或自定义 scope>" \
  --depth deep \
  --save
```

如果在含 `08_Outputs/` 的 Obsidian 风格工作区运行，默认保存到 `08_Outputs/co_scientist_requests/`；否则保存到本项目的 `outputs/co_scientist_requests/`。保存的是任务提示，不是文献库。

## 推荐输出验收标准

一次合格输出至少应该包含：

- 检索日期和检索日志。
- 8-15 条关键证据，且标明研究类型和链接。
- 5-8 条可验证假设。
- 每条假设的反方审查。
- 按机制可信度、证据强度、新颖性、实验可行性、医疗转化价值、风险可控性打分。
- Top 3 的最小验证方案。
- 明确的不确定性和不能过度解读的地方。

## 写回 Obsidian 的建议

- 生成的 Markdown 报告统一归档到 vault 的 `08_Outputs/co_scientist_reports/`，作为项目材料。
- 本项目内的 `outputs/` 只作为临时输出或备份位置；面向 Obsidian 查阅时，以 vault 内 `08_Outputs/co_scientist_reports/` 为准。
- 如果要沉淀到个人知识库，不要直接把长报告塞进概念页；先作为来源页或项目页保存，再提炼概念页。
- 涉及论文、指南、数据库页面时，保留 URL、DOI、PMID、检索日期和“是否核验全文”的状态。
