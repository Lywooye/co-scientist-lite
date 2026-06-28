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
  --mode standard \
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

### 方式 C：No-database multi-agent simulation

```bash
python3 tools/co_scientist_lite.py \
  --topic "<一句话研究问题>" \
  --objective "生成可验证假设并筛选 Top 3 假设" \
  --scope "偏转化医学；优先近期顶刊方向和直接证据" \
  --mode multi-agent \
  --rounds 2 \
  --generators mechanism,translation,methods \
  --reviewers evidence,methods,translation \
  --ranking tournament
```

这个模式仿真以下结构：

- `Supervisor agent`：拆题、规划、定义成功标准和停止条件。
- `Evidence agent`：使用当前会话可用的实时搜索能力形成证据表。
- `Generation agents`：从不同视角生成候选假设。
- `Proximity agent`：去重、聚类、合并相似假设。
- `Reflection agents`：从证据、方法学和转化可行性做虚拟同行评审。
- `Ranking agent`：用 score 或 tournament 排序。
- `Evolution agent`：对高分假设做 refine/combine/split/reject。
- `Meta-review agent`：综合输出最终 Top 3 和验证路线。

边界：不接 ChEMBL、UniProt、AlphaFold，不建本地文献库；这是结构化角色仿真，不是 Google Co-Scientist 的复刻。

保存一份任务请求：

```bash
python3 tools/co_scientist_lite.py \
  --topic "<一句话研究问题>" \
  --objective "<选择或自定义 objective>" \
  --scope "<组合或自定义 scope>" \
  --depth deep \
  --save
```

使用 `--save` 时，默认保存到本项目的 `outputs/co_scientist_requests/`。如果需要写到其他位置，请显式使用 `--output /path/to/request.md`。保存的是任务提示，不是文献库。

## 推荐输出验收标准

一次合格输出至少应该包含：

- 检索日期和检索日志。
- 8-15 条关键证据，且标明研究类型和链接。
- 5-8 条可验证假设。
- 每条假设的反方审查。
- 按机制可信度、证据强度、新颖性、实验可行性、医疗转化价值、风险可控性打分。
- Top 3 的最小验证方案。
- 明确的不确定性和不能过度解读的地方。

## 本地归档建议

- 生成的 Markdown 报告建议归档到你自己的知识库或项目管理系统，但不要把私人路径写进公开仓库。
- 本项目内的 `outputs/` 只作为临时输出或备份位置，默认不提交到 Git。
- 如果要沉淀到个人知识库，不要直接把长报告塞进概念页；先作为来源页或项目页保存，再提炼概念页。
- 涉及论文、指南、数据库页面时，保留 URL、DOI、PMID、检索日期和“是否核验全文”的状态。
