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
3. 替换 `<topic>`、`<objective>`、`<scope_and_constraints>`、`<time_window>`、搜索扩展级别和迁移参考场景。
4. 发给 Codex 执行。

### 方式 B：用本地生成器生成任务提示

```bash
python3 tools/co_scientist_lite.py \
  --topic "<一句话研究问题：疾病/技术/机制/人群/场景>" \
  --objective "<选择或自定义 objective>" \
  --scope "<组合或自定义 scope>" \
  --depth standard \
  --mode multi-agent \
  --research-domain biomedical \
  --venue-focus high-impact \
  --reference-style vancouver \
  --journal-metrics impact-factor
```

默认执行模式现在是 `multi-agent`。如果只想走线性流程，可以显式加 `--mode standard`。
当 `--mode standard` 和 multi-agent 专属参数同时显式传入时，CLI 会提示这些参数会被忽略或降级为线性流程提示。

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

`--research-domain` 可选：

- `biomedical`：默认值。PubMed/PMC、ClinicalTrials.gov、指南、医学/生命科学期刊和生物医学预印本优先。
- `engineering`：IEEE Xplore、ACM Digital Library、SpringerLink、ScienceDirect、Wiley、arXiv、标准、专利和开源实现。
- `ai-cs`：arXiv、OpenReview、NeurIPS/ICML/ICLR、CVPR/ICCV/ECCV、ACL/EMNLP、Papers with Code、GitHub、ACM/IEEE。
- `materials`：Nature Materials、Advanced Materials、ACS、RSC、ChemRxiv/arXiv、专利、标准和实验数据。
- `general`：跨学科来源，按 topic 自动混合学术搜索、出版商页面、预印本、标准、专利、数据集和开源项目。

`--venue-focus` 可选：

- `high-impact`：默认值。先用领域顶刊、顶会、旗舰 Transactions、权威指南/标准或高影响预印本锚定方向，再补直接证据。
- `balanced`：高影响来源、直接证据、综述/指南/标准、预印本、实现和数据集平衡纳入。
- `direct`：优先 exact-match 直接证据，高影响 venue 主要用于机制背景和前沿方向。

`--journal-focus` 仍可用于旧命令兼容：`top-journals` 会映射为 `--venue-focus high-impact`，`balanced` 和 `direct` 保持同义。新命令优先使用 `--venue-focus`。

`--mode` 可选：

- `multi-agent`：默认值。仿真 supervisor、evidence、search expansion、cross-disease transfer、review、ranking、evolution、meta-review 等角色结构。
- `standard`：线性顺序流程，按 Scope -> Search -> Evidence Extraction -> Hypothesis Generation -> Red Team -> Ranking -> Validation Plan -> Final Output 执行。

`--depth` 可选：

- `quick`：快速概览。
- `standard`：默认值。完整但不过度展开。
- `deep`：更长、更细的证据表、假设审查和验证方案。

`--reference-style` 可选：

- `vancouver`：默认值。适合医学报告，格式为 Authors. Title. Journal. Year;Volume(Issue):Pages. doi: DOI. PMID: PMID.
- `nature`：适合偏 Nature 风格的参考文献列表。
- `apa`：适合更通用的作者-年份风格。

`--journal-metrics` 可选：

- `impact-factor`：默认值。适合期刊论文；会议、预印本、标准、专利、数据集和代码应标注 venue/source status，不强行匹配 IF。
- `none`：不要求期刊指标，但仍需核验 DOI/PMID/arXiv ID/官方链接。

`multi-agent` 模式相关可选项：

- `--rounds`：默认 `2`，控制假设演化/修订轮数。
- `--generators`：默认 `mechanism,translation,methods`，控制假设生成视角。
- `--reviewers`：默认 `evidence,methods,translation`，控制审查视角。
- `--ranking`：默认 `tournament`，可选 `score`。
- `--expansion-level`：默认 `focused`，可选 `none`、`focused`、`broad`。
- `--transfer-domains`：默认 `liver,thyroid,lymph-node,kidney,prostate`，用于跨病种、跨器官、跨应用、跨材料、跨平台或 benchmark 方法迁移参考。

如果有 JCR/IF 表格，可以加：

```bash
--impact-factor-year 2025 \
--impact-factor-source "/path/to/journal-impact-factors.xlsx"
```

IF 表建议包含期刊全称、简称、影响因子、Q分区。匹配不到的期刊必须写“IF: 未匹配/未核验”，不能猜测。

本地私有 IF 表可放在：

```text
local/journal_metrics/jcr_2025.jsonl
```

该路径被 Git 忽略，适合放授权边界不明确或不应公开分发的表格转换结果。若文件存在，工具会自动引用；若文件不存在，公开版不会报错，只会要求使用实时可核验来源或标记未匹配/未核验。

快速查单个期刊：

```bash
python3 tools/co_scientist_lite.py --lookup-if "Radiology"
```

### 方式 C：No-database multi-agent simulation

```bash
python3 tools/co_scientist_lite.py \
  --topic "<一句话研究问题>" \
  --objective "生成可验证假设并筛选 Top 3 假设" \
  --scope "偏转化医学；优先近期顶刊方向和直接证据" \
  --mode multi-agent \
  --research-domain biomedical \
  --venue-focus high-impact \
  --rounds 2 \
  --generators mechanism,translation,methods \
  --reviewers evidence,methods,translation \
  --ranking tournament \
  --expansion-level focused \
  --transfer-domains liver,thyroid,lymph-node,kidney,prostate \
  --reference-style vancouver \
  --journal-metrics impact-factor
```

这个模式仿真以下结构：

- `Supervisor agent`：拆题、规划、定义成功标准和停止条件。
- `Evidence agent`：使用当前会话可用的实时搜索能力形成证据表。
- `Journal Metrics step`：按规范格式整理参考文献；期刊论文尽量匹配 IF/Q 分区，非期刊来源标注 venue/source status。
- `Search Expansion agent`：从 topic 拆出对象/系统/疾病、技术/材料/算法、任务/终点/指标等概念组，生成 core、adjacent、methods、cross-disease/cross-scenario transfer 等检索式。
- `Cross-Disease Transfer agent`：检索同技术在其他病种、器官、应用、材料、平台或 benchmark 中的方法学启发，但不把它当作目标场景的直接有效性证据。
- `Evidence Distance Classifier`：给每条证据标注 core、adjacent、cross-disease transfer、mechanism only、methods only 或 high-impact anchor。
- `Generation agents`：从不同视角生成候选假设。
- `Proximity agent`：去重、聚类、合并相似假设。
- `Reflection agents`：从证据、方法学和转化可行性做虚拟同行评审。
- `Ranking agent`：用 score 或 tournament 排序。
- `Evolution agent`：对高分假设做 refine/combine/split/reject。
- `Meta-review agent`：综合输出最终 Top 3 和验证路线。

边界：不接 ChEMBL、UniProt、AlphaFold，不建本地文献库；跨病种/跨场景证据只用于方法迁移和假设生成；这是结构化角色仿真，不是 Google Co-Scientist 的复刻。

保存一份任务请求：

```bash
python3 tools/co_scientist_lite.py \
  --topic "<一句话研究问题>" \
  --objective "<选择或自定义 objective>" \
  --scope "<组合或自定义 scope>" \
  --depth deep \
  --save
```

使用 `--save` 时，若环境变量或 `local/profile.env` 配置了 `CO_SCIENTIST_REQUEST_DIR`，默认保存到该目录；否则回退到本项目的 `outputs/co_scientist_requests/`。如果需要写到其他位置，请显式使用 `--output /path/to/request.md`。保存的是任务提示，不是文献库。

## 推荐输出验收标准

一次合格输出至少应该包含：

- 检索日期和检索日志。
- 8-15 条关键证据，且标明研究类型和链接。
- 5-8 条可验证假设。
- 每条假设的反方审查。
- `Deep Verification Review`：拆解 Top 假设的核心假设、必要假定、可检验子假定、支持证据、反证/缺失证据和可推翻条件。
- `Novelty Search Review`：每条 Top 假设必须先经针对性实时检索再分级；未核查时只能写“未核验”。
- 按机制可信度、证据强度、新颖性、实验可行性、医疗转化价值、风险可控性打分。
- `Tournament Pairwise Log`：若使用 tournament 排序，给出成对比较、关键胜负理由和顺序/位置偏倚检查。
- Top 3 的最小验证方案。
- 规范参考文献列表，且每条论文尽量包含 DOI/PMID、IF、Q分区；无法匹配时明确写未匹配/未核验。
- `Meta-review Feedback for next run`：总结本轮反复问题、缺失检索方向和下一轮参数调整建议。
- `hypothesis_pool.json` fenced JSON 块，便于后续机器解析。
- 明确的不确定性和不能过度解读的地方。

## 本地归档建议

- 生成的 Markdown 报告建议归档到你自己的知识库或项目管理系统，但不要把私人路径写进公开仓库。
- 本项目内的 `outputs/` 只作为临时输出或备份位置，默认不提交到 Git。
- 如果要沉淀到个人知识库，不要直接把长报告塞进概念页；先作为来源页或项目页保存，再提炼概念页。
- 涉及论文、指南、数据库页面时，保留 URL、DOI、PMID、检索日期和“是否核验全文”的状态。
