# Co-Scientist Lite

Co-Scientist Lite 是一个可复用的 prompt/workflow 生成器，用来引导 Codex 类助手执行“实时文献搜索 -> 假设生成 -> 反方审查 -> 排序 -> 验证方案”的科研流程。生成后的 prompt 会要求助手使用当前会话可用的实时搜索工具；本项目本身不执行文献搜索。

英文文档：[README.md](README.md)

## 项目结构

- `prompts/co-scientist-lite.md`：稳定任务提示词和输出契约。
- `workflows/co-scientist-lite-codex.md`：使用说明和质量检查规则。
- `tools/co_scientist_lite.py`：生成 Codex 任务提示的本地辅助脚本。

## 快速使用

克隆仓库或进入项目目录后运行这个完整模板。实际使用时可以删掉不需要的可选行，但主运行命令统一以这个模板为准。

```bash
python3 tools/co_scientist_lite.py \
  --topic "<一句话研究问题：疾病/技术/机制/人群/场景>" \
  --objective "<选择或自定义 objective>" \
  --scope "<组合或自定义 scope>" \
  --time-window "优先近 5 年；必要时追溯奠基文献；必须写明检索日期" \
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
  --medical-boundary "仅用于科研构思；不输出个人化诊断或治疗建议"
```

## 常用可选项

大多数参数都是可选的。工具现在默认使用 `--mode multi-agent`。

| 参数 | 可选值 | 默认值 | 含义 |
|---|---|---:|---|
| `--topic` | 自由文本 | 研究运行时必填 | 研究问题或主题。使用 `--lookup-if` 时不需要。 |
| `--objective` | 自由文本 | 生成可验证科研假设，并按医疗转化价值和实验可行性排序 | 本轮运行目标。 |
| `--scope` | 自由文本 | 偏医学科研和转化应用；不输出个人临床诊疗建议 | 范围、限制和排除项。 |
| `--time-window` | 自由文本 | 优先近 5 年；必要时追溯奠基文献；必须写明检索日期 | 文献时间范围和检索日期要求。 |
| `--mode` | `multi-agent`, `standard` | `multi-agent` | 工作流结构。`multi-agent` 仿真 Co-Scientist 风格的多角色流程；`standard` 使用 Scope -> Search -> Evidence -> Hypothesis -> Review -> Ranking 的线性流程。 |
| `--depth` | `quick`, `standard`, `deep` | `standard` | 输出详略程度。 |
| `--journal-focus` | `top-journals`, `balanced`, `direct` | `top-journals` | 文献优先级。`top-journals` 用顶刊/高影响文献锚定方向，同时保留专科直接证据。 |
| `--reference-style` | `vancouver`, `nature`, `apa` | `vancouver` | 最终参考文献格式。 |
| `--journal-metrics` | `impact-factor`, `none` | `impact-factor` | 是否要求匹配 IF 和 Q 分区。 |
| `--impact-factor-year` | 任意年份标签 | `2025` | 生成 prompt 时使用的 IF 年份标签。 |
| `--impact-factor-source` | 文件路径或来源描述 | 无 | 可选的期刊指标来源。省略时，如果本机存在 `local/journal_metrics/jcr_2025.jsonl`，工具会自动引用。 |
| `--rounds` | >= 1 的整数 | `2` | `multi-agent` 模式下的假设演化/修订轮数。 |
| `--generators` | 逗号分隔列表 | `mechanism,translation,methods` | `multi-agent` 模式下的假设生成视角。 |
| `--reviewers` | 逗号分隔列表 | `evidence,methods,translation` | `multi-agent` 模式下的审查视角。 |
| `--ranking` | `tournament`, `score` | `tournament` | `multi-agent` 模式下的排序方式。 |
| `--expansion-level` | `none`, `focused`, `broad` | `focused` | 检索扩展范围。`focused` 会加入相邻检索词和有限跨病种方法迁移。 |
| `--transfer-domains` | 逗号分隔列表 | `liver,thyroid,lymph-node,kidney,prostate` | 可参考的方法迁移病种或器官场景。 |
| `--medical-boundary` | 自由文本 | 科研/转化医学假设，不输出个人化诊断或治疗建议 | 生成 prompt 时的医学安全边界。 |
| `--save` | flag | 关闭 | 保存生成的任务提示。若配置了 `CO_SCIENTIST_REQUEST_DIR` 或 `local/profile.env`，优先使用该目录；否则回退到 `outputs/co_scientist_requests/`。 |
| `--output` | 文件路径 | 无 | 将生成的任务提示保存到指定路径。 |
| `--lookup-if` | 期刊名 | 无 | 查询本地 IF/Q 指标后退出，可重复使用。 |

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

## 参考文献格式和影响因子

生成的报告默认会要求使用规范参考文献格式，并在能够核验时补充期刊影响因子和 Q 分区。

`--impact-factor-source` 是可选项，可以指向 JCR/IF 表格。表格最好包含期刊全称、简称、影响因子、Q分区等列。若某个期刊匹配不到，生成的 prompt 会要求报告写“IF: 未匹配/未核验”，不能猜测或补造。

公开仓库不内置 Journal Citation Reports 或影响因子数据。如果本机存在私有文件 `local/journal_metrics/jcr_2025.jsonl`，工具会在生成 prompt 时自动引用它；如果没有这个文件，工具不会报错，会降级为使用实时可核验来源，或明确写“未匹配/未核验”。

本地快速查 IF：

```bash
python3 tools/co_scientist_lite.py --lookup-if "Radiology"
```

## 多 agent 仿真模式

`--mode multi-agent` 是默认模式，会生成一个不接数据库的 Co-Scientist-inspired 多 agent 仿真 prompt。

这个模式会仿真 supervisor、evidence agent、search expansion agent、cross-disease transfer agent、evidence-distance classifier、generation agents、proximity/clustering agent、reflection reviewers、tournament ranker、evolution agent 和 meta-review agent 的结构。它不连接 ChEMBL、UniProt、AlphaFold，也不使用本地论文库。

`--expansion-level focused` 用来避免没有本地文献库时检索范围过窄：先从 topic 拆出疾病、技术、相邻技术、任务/终点、方法学和机制，再有限扩展检索式。`--transfer-domains` 用于指定可参考的跨病种/跨器官方法学场景；这些证据只能作为方法迁移和假设生成启发，不能直接支撑目标病种的临床有效性结论。

如果要保存生成的任务提示，在上面的完整模板后追加一个输出选项：

```bash
--save
```

或者：

```bash
--output "/path/to/request.md"
```

使用 `--save` 时，如果环境变量或 `local/profile.env` 配置了 `CO_SCIENTIST_REQUEST_DIR`，生成的任务提示会优先写入该目录；否则回退到本项目的 `outputs/co_scientist_requests/`。如果想写到其他位置，请显式使用 `--output /path/to/request.md`。保存的是任务提示，不是文献库。

## 重要边界

本项目只生成面向 Codex 类助手的稳定提示词。执行该提示词的助手可以在会话中使用实时文献搜索能力，但这个脚本和仓库本身不执行文献搜索、不包含本地论文数据库，也不提供临床诊断或治疗建议。
