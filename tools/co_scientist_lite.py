#!/usr/bin/env python3
"""Generate a Codex prompt for the Co-Scientist Lite workflow.

This script does not search literature itself. It creates a stable task prompt
that asks Codex to use the live search tools available in the current session.
"""

from __future__ import annotations

import argparse
import datetime as dt
import json
import os
import re
import shlex
import sys
import unicodedata
from pathlib import Path


DEFAULT_TIME_WINDOW = "优先近 5 年；必要时追溯奠基文献；必须写明检索日期"
DEFAULT_MEDICAL_BOUNDARY = "科研/转化医学假设，不输出个人化诊断或治疗建议"
DEFAULT_JOURNAL_FOCUS = "top-journals"
DEFAULT_MODE = "multi-agent"
DEFAULT_GENERATORS = "mechanism,translation,methods"
DEFAULT_REVIEWERS = "evidence,methods,translation"
DEFAULT_RANKING = "tournament"
DEFAULT_EXPANSION_LEVEL = "focused"
DEFAULT_TRANSFER_DOMAINS = "liver,thyroid,lymph-node,kidney,prostate"
DEFAULT_REFERENCE_STYLE = "vancouver"
DEFAULT_JOURNAL_METRICS = "impact-factor"
DEFAULT_IMPACT_FACTOR_YEAR = "2025"
DEFAULT_LOCAL_METRICS_DIR = Path("local") / "journal_metrics"

MULTI_AGENT_ONLY_FLAGS = {
    "--rounds": "evolution rounds",
    "--generators": "generation perspectives",
    "--reviewers": "review perspectives",
    "--ranking": "multi-agent ranking method",
    "--expansion-level": "search expansion breadth",
    "--transfer-domains": "cross-disease transfer contexts",
}

HYPOTHESIS_POOL_JSON_CONTRACT = """```json
{
  "run_id": "<search-date-or-short-run-id>",
  "topic": "<research topic>",
  "hypotheses": [
    {
      "id": "H1",
      "title": "<short title>",
      "claim": "<testable if-then claim>",
      "mechanism": "<proposed mechanism>",
      "novelty_level": "完全新颖 | 机制已有但应用场景新 | 靶点/技术已有但组合新 | 已有人做过，不算新颖 | 未核验",
      "evidence_distance": "core | adjacent | cross-disease transfer | mechanism only | methods only | high-impact anchor",
      "supporting_evidence_ids": ["E1", "E2"],
      "key_assumptions": ["<necessary assumption>"],
      "invalidating_assumptions": ["<assumption whose failure would invalidate the hypothesis>"],
      "review_status": "<accepted | refine | reject | unresolved>",
      "tournament_summary": "<pairwise wins/losses and decisive reasons>",
      "validation_plan": "<minimum viable validation path>",
      "risk_flags": ["<bias, feasibility, safety, or transfer-risk flag>"],
      "next_step": "<concrete next action>"
    }
  ]
}
```"""

JOURNAL_FOCUS_INSTRUCTIONS = {
    "top-journals": (
        "顶刊/高影响证据优先：先用 Nature/Science/Cell、NEJM/Lancet/JAMA/BMJ、"
        "Nature Medicine/Nature Biomedical Engineering/Nature Cancer/Cancer Cell、"
        "PNAS、Radiology/European Radiology/Medical Image Analysis 等综合、医学、"
        "肿瘤、影像和方法学高影响来源锚定研究方向；随后补充最直接相关的专科期刊证据。"
        "不得只因期刊级别低而排除直接临床证据，也不得把期刊级别当作研究质量的唯一代理指标。"
    ),
    "balanced": (
        "平衡证据优先：同时重视高影响期刊方向、专科直接证据、指南、临床试验和方法学论文；"
        "按研究设计和与问题的直接相关性排序。"
    ),
    "direct": (
        "直接证据优先：优先纳入与研究问题、人群/模型、技术和终点最直接匹配的论文；"
        "顶刊文献用于补充机制背景和前沿方向。"
    ),
}

REFERENCE_STYLE_INSTRUCTIONS = {
    "vancouver": (
        "参考文献采用 Vancouver/NLM 风格：Authors. Title. Journal. Year;"
        "Volume(Issue):Pages. doi: DOI. PMID: PMID. "
        "作者超过 6 位时可列前 6 位后加 et al。"
    ),
    "nature": (
        "参考文献采用 Nature 风格：Authors. Title. Journal volume, pages (year). "
        "doi: DOI. PMID: PMID."
    ),
    "apa": (
        "参考文献采用 APA 风格：Authors. (Year). Title. Journal, volume(issue), pages. "
        "https://doi.org/DOI. PMID: PMID."
    ),
}


def normalize_list(value: str) -> str:
    items = [item.strip() for item in value.split(",") if item.strip()]
    return ", ".join(items) if items else "none"


def project_root() -> Path:
    return Path(__file__).resolve().parents[1]


def local_profile_defaults() -> dict[str, str]:
    profile_path = project_root() / "local" / "profile.env"
    if not profile_path.exists():
        return {}

    defaults = {}
    for line in profile_path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        if line.startswith("export "):
            line = line[7:].strip()
        key, value = line.split("=", 1)
        key = key.strip()
        if not key:
            continue
        try:
            parsed = shlex.split(value, comments=False, posix=True)
            defaults[key] = parsed[0] if parsed else ""
        except ValueError:
            defaults[key] = value.strip().strip("'\"")
    return defaults


def local_setting(name: str) -> str | None:
    return os.environ.get(name) or local_profile_defaults().get(name)


def default_request_dir() -> Path:
    configured = local_setting("CO_SCIENTIST_REQUEST_DIR")
    if configured:
        return Path(configured).expanduser()
    return project_root() / "outputs" / "co_scientist_requests"


def slugify(text: str, max_length: int = 48) -> str:
    text = re.sub(r"\s+", "-", text.strip())
    text = re.sub(r"[^\w\-\u4e00-\u9fff]+", "", text)
    return text[:max_length].strip("-") or "co-scientist-lite"


def normalize_journal_key(value: str | None) -> str:
    if not value:
        return ""
    text = unicodedata.normalize("NFKD", str(value)).lower()
    text = text.replace("&", " and ")
    text = re.sub(r"[^a-z0-9]+", " ", text)
    return re.sub(r"\s+", " ", text).strip()


def default_local_impact_factor_source(year: str) -> Path | None:
    metrics_dir = project_root() / DEFAULT_LOCAL_METRICS_DIR
    candidates = [
        metrics_dir / f"jcr_{year}.jsonl",
        metrics_dir / "jcr_2025.jsonl",
    ]
    for candidate in candidates:
        if candidate.exists():
            return candidate.resolve()
    return None


def resolve_impact_factor_source(
    args: argparse.Namespace, force_local: bool = False
) -> Path | None:
    if args.impact_factor_source:
        source_path = Path(args.impact_factor_source).expanduser()
        if source_path.exists():
            source_path = source_path.resolve()
            args.impact_factor_source = str(source_path)
            args.impact_factor_source_kind = "local-file"
            return source_path
        args.impact_factor_source_kind = "description"
        return None

    if args.journal_metrics == "none" and not force_local:
        args.impact_factor_source_kind = "none"
        return None

    local_source = default_local_impact_factor_source(args.impact_factor_year)
    if local_source:
        args.impact_factor_source = str(local_source)
        args.impact_factor_source_kind = "auto-local-file"
        return local_source

    args.impact_factor_source_kind = "none"
    return None


def load_journal_metrics(path: Path) -> list[dict[str, object]]:
    records: list[dict[str, object]] = []
    with path.open("r", encoding="utf-8") as handle:
        for line in handle:
            line = line.strip()
            if line:
                records.append(json.loads(line))
    return records


def is_partial_journal_candidate(query_key: str, candidate_key: str) -> bool:
    if len(query_key) < 6 or len(candidate_key) < 6:
        return False
    return query_key in candidate_key or candidate_key in query_key


def match_journal_metric(
    journal: str, records: list[dict[str, object]]
) -> tuple[dict[str, object] | None, str, list[dict[str, object]]]:
    key = normalize_journal_key(journal)
    for field, label in (
        ("match_full_title", "full_title"),
        ("match_abbreviation", "abbreviation"),
    ):
        for record in records:
            if key and key == record.get(field):
                return record, label, []

    candidates = []
    for record in records:
        title_key = str(record.get("match_full_title") or "")
        abbr_key = str(record.get("match_abbreviation") or "")
        if key and (
            is_partial_journal_candidate(key, title_key)
            or is_partial_journal_candidate(key, abbr_key)
        ):
            candidates.append(record)
            if len(candidates) >= 5:
                break
    return None, "unmatched", candidates


def print_if_lookup(args: argparse.Namespace) -> int:
    source_path = resolve_impact_factor_source(args, force_local=True)
    if not source_path:
        raise SystemExit(
            "No local IF source found. Put a JSONL file at "
            "local/journal_metrics/jcr_2025.jsonl or pass --impact-factor-source."
        )

    records = load_journal_metrics(source_path)
    for query in args.lookup_if:
        match, match_type, candidates = match_journal_metric(query, records)
        print(f"Query: {query}")
        print(f"Source: {source_path}")
        if match:
            print(f"Match: {match_type}")
            print(f"Journal: {match.get('full_title')}")
            print(f"Abbreviation: {match.get('abbreviation')}")
            print(f"IF: {match.get('impact_factor')}")
            print(f"Quartile: {match.get('quartile')}")
            print(f"Index: {match.get('index_type')}")
            print(f"Subject: {match.get('primary_subject')}")
            print(f"Source row: {match.get('source_row')}")
        else:
            print("IF: 未匹配/未核验")
            if candidates:
                print("Possible candidates:")
                for candidate in candidates:
                    print(
                        "- "
                        f"{candidate.get('full_title')} | "
                        f"{candidate.get('abbreviation')} | "
                        f"IF {candidate.get('impact_factor')} | "
                        f"{candidate.get('quartile')}"
                    )
        print()
    return 0


def build_reference_instructions(args: argparse.Namespace) -> str:
    citation_rule = REFERENCE_STYLE_INSTRUCTIONS[args.reference_style]
    if args.journal_metrics == "none":
        metrics_rule = "本轮不要求补充期刊指标；仍需核验 DOI/PMID 和期刊名。"
    else:
        if args.impact_factor_source:
            source_kind = getattr(args, "impact_factor_source_kind", "description")
            if source_kind in {"auto-local-file", "local-file"}:
                metrics_source = (
                    f"优先使用本地结构化 IF 表：{args.impact_factor_source}。"
                    "字段包括 full_title、abbreviation、impact_factor、quartile、"
                    "match_full_title、match_abbreviation。"
                    "最终报告只能写“本地 2025 IF 表”或“用户提供的 IF 表”，不要暴露本地绝对路径。"
                )
            else:
                metrics_source = (
                    f"优先使用用户提供的 IF/JCR 表：{args.impact_factor_source}。"
                    "最终报告只能写来源文件名或“用户提供的 IF 表”，不要暴露本地绝对路径。"
                )
        else:
            metrics_source = (
                "优先使用用户在当前会话提供的 IF/JCR 表；若未提供，则用实时搜索可核验来源。"
            )
        metrics_rule = (
            f"期刊指标要求：为每条论文补充最新可核验影响因子 IF 和分区，默认年份为 {args.impact_factor_year}。"
            f"在参考文献条目末尾追加：IF: x.x (JCR {args.impact_factor_year}; Qx)。"
            f"{metrics_source}"
            "若使用表格来源，优先匹配期刊全称，其次匹配标准缩写；可识别字段包括全称、简称、影响因子、Q分区。"
            "匹配不到或无法核验时必须写“IF: 未匹配/未核验”，不得猜测或补造。"
            "IF 只作为期刊背景信息，不得替代研究设计质量、样本量、偏倚风险和证据距离判断。"
        )
    return f"{citation_rule}\n{metrics_rule}"


def build_output_requirements(args: argparse.Namespace) -> str:
    if args.journal_metrics == "none":
        evidence_columns = (
            "规范参考文献、期刊、研究类型、对象/模型、核心发现、主要限制、链接/DOI/PMID"
        )
        reference_detail = (
            "参考文献列表必须使用指定引用格式；每条论文都要给 DOI/PMID（能核验时）和链接。"
        )
        uncertainty_detail = (
            "证据不足或引用信息无法核验时明确写“不足/未核验”，不要补造结论。"
        )
    else:
        evidence_columns = (
            "规范参考文献、期刊、IF、Q分区、研究类型、对象/模型、核心发现、主要限制、链接/DOI/PMID"
        )
        reference_detail = (
            "参考文献列表必须使用指定引用格式；每条论文都要给 DOI/PMID（能核验时）、IF/Q分区（能匹配时）和链接。"
        )
        uncertainty_detail = (
            "证据不足、IF 匹配失败或引用信息无法核验时明确写“不足/未核验/未匹配”，不要补造结论。"
        )

    return f"""1. 先给出窄化后的可执行研究问题和成功标准。
2. 输出检索日志、证据表、假设表、反方审查、排序表、Top 3 验证方案。
3. 证据表至少包含：{evidence_columns}。
4. {reference_detail}
5. 预印本、综述、动物/体外研究、回顾性研究、RCT、指南要分层标注。
6. 单独标注“顶刊/高影响文献提供的研究方向”和“专科直接证据提供的可验证事实”，不要混为同一种证据。
7. {uncertainty_detail}
8. 对进入最终排序的假设输出 Deep Verification Review：拆成核心假设、必要假定、可检验子假定、支持证据、反证/缺失证据，并标注哪些假定一旦失败会推翻该假设。
9. 输出 Novelty Search Review：每条 Top 假设在标注新颖性前必须做针对性实时检索；无法完成核查时不得声称新颖，只能写“未核验”。新颖性分级限定为：完全新颖、机制已有但应用场景新、靶点/技术已有但组合新、已有人做过，不算新颖、未核验。
10. 输出 Tournament Pairwise Log：multi-agent/tournament 模式必须给出成对比较记录；高分候选需要更细的正反论证，低分候选可用简化比较。比较时必须检查顺序/位置偏倚，必要时反向顺序复核。
11. 输出 Meta-review Feedback for next run：列出反复出现的薄弱点、缺失检索方向、下轮 reviewer/agent 调整、应避免的假设模式、值得扩展的方向，以及建议的下一轮 scope/transfer-domains/reviewers。
12. 结尾列出医疗转化前景、关键风险、待补证据和规范参考文献。
13. 最后追加一个 fenced JSON 块，标题写 `hypothesis_pool.json`，使用下面字段，便于后续机器解析：

{HYPOTHESIS_POOL_JSON_CONTRACT}"""


def build_prompt(args: argparse.Namespace) -> str:
    generated_at = dt.datetime.now().astimezone().isoformat(timespec="seconds")
    prompt_path = "prompts/co-scientist-lite.md"
    mode_instructions = build_mode_instructions(args)

    return f"""# Co-Scientist Lite Task

生成时间：{generated_at}
提示词模板：{prompt_path}

请按本项目 `{prompt_path}` 中的 Co-Scientist Lite 流程执行。本任务使用当前默认模型，不要求切换模型；不使用本地文献库；必须使用本轮可用的实时文献搜索能力并保留检索日志。

## 任务输入

研究问题：{args.topic}

目标：{args.objective}

范围和限制：{args.scope}

时间范围：{args.time_window}

输出深度：{args.depth}

执行模式：{args.mode}

文献优先级：{JOURNAL_FOCUS_INSTRUCTIONS[args.journal_focus]}

医疗安全边界：{args.medical_boundary}

参考文献格式和期刊指标：
{build_reference_instructions(args)}

{mode_instructions}

## 输出要求

{build_output_requirements(args)}
"""


def build_mode_instructions(args: argparse.Namespace) -> str:
    if args.mode == "standard":
        return """## 执行模式说明

使用标准顺序流程：Scope -> Search -> Evidence Extraction -> Hypothesis Generation -> Red Team -> Ranking -> Validation Plan -> Final Output。"""

    return f"""## 执行模式说明：No-database multi-agent simulation

这是一个受 Co-Scientist 启发的多 agent 工作流仿真，不是 Google Co-Scientist 的复刻，也不接入本地文献库或专用数据库。

Agent 结构：

1. Supervisor agent
   - 拆解研究问题，定义成功标准、排除项、搜索策略和停止条件。
   - 维护 hypothesis pool，并安排后续 agent 的输入输出。

2. Evidence agent
   - 使用当前会话可用的实时搜索能力，形成证据表。
   - 只使用公开网页、论文页面、摘要、指南和用户提供材料；不调用本地文献库或专用数据库。

3. Search Expansion agent
   - 扩展级别：{args.expansion_level}
   - 先把 topic 拆成概念组：疾病/对象、技术、相邻技术、任务/终点、方法学、机制。
   - 按扩展级别生成并记录检索式：none 只保留 core 和 high-impact anchor；focused 加入 adjacent、methods 和有限 cross-disease transfer；broad 可更积极加入机制、相邻技术和跨病种方法学检索。
   - 可用检索式类型包括：core、adjacent、cross-disease transfer、mechanism、methods、high-impact anchor。
   - 每类检索式都要说明目的、可能漂移风险和纳入/排除标准。

4. Cross-Disease Transfer agent
   - 候选迁移病种/场景：{normalize_list(args.transfer_domains)}
   - 若扩展级别为 none，则只说明未启用跨病种迁移检索，不展开该 agent。
   - 只搜索“同技术或相邻技术在其他病种中的方法学启发”，例如参数设计、动态图像分析、运动校正、AI/radiomics、验证终点。
   - 跨病种证据不得直接支撑目标病种临床有效性结论，只能进入“可迁移启发”或“待验证假设”。

5. Evidence Distance Classifier
   - 为每条证据标注 evidence distance：core、adjacent、cross-disease transfer、mechanism only、methods only、high-impact anchor。
   - core/adjacent 可支撑主要结论；cross-disease、mechanism、methods 只能支撑假设生成或方法设计。
   - 若跨病种证据与目标病种生理、血供、检查窗口或临床终点不一致，必须写明迁移风险。

6. Generation agents
   - 生成视角：{normalize_list(args.generators)}
   - 每个生成 agent 至少提出 2-3 条候选假设，并写明证据链和最小验证方式。

7. Proximity agent
   - 对候选假设去重、聚类、合并相似项。
   - 输出 hypothesis clusters，并说明每个 cluster 的共同机制、差异点和覆盖空白。

8. Reflection agents
   - 审查视角：{normalize_list(args.reviewers)}
   - 对每条候选假设进行证据、方法学、临床转化和偏倚风险审查。
   - 对进入最终排序的假设执行 deep verification：拆解关键假定、子假定和可推翻条件，逐条标注支持证据、反证和缺失证据。
   - 新颖性判断前必须做针对性实时检索；未完成检索核查时只能标注“未核验”。

9. Ranking agent
   - 排序方式：{args.ranking}
   - 若使用 tournament，则进行成对比较，给出胜负理由、关键否决项和最终积分/排序。
   - 对高分候选进行更细的成对辩论，对低分候选使用简化比较；显式检查顺序/位置偏倚。

10. Evolution agent
   - 进化轮数：{args.rounds}
   - 对高分假设进行 refine、combine、split 或 reject。
   - 每一轮都要说明假设发生了什么变化，以及为什么变化。

11. Meta-review agent
   - 综合 evidence、reviews、ranking 和 evolution，输出最终 Top 3。
   - 明确哪些结论来自强证据，哪些只是可验证设想。
   - 提炼本轮反复出现的批评点，生成“下一轮运行反馈”，用于后续 scope、搜索词、reviewer 和 transfer-domains 调整。

额外输出要求：

- 输出 query expansion map、evidence distance table、cross-disease transfer table、hypothesis pool、clusters、review matrix、deep verification review、novelty search review、tournament pairwise log、evolution log、meta-review feedback for next run、hypothesis_pool.json。
- 不要把多 agent 仿真写成真实独立模型并行执行；应明确这是单次 Codex 会话中的结构化角色仿真。
- 不接入 ChEMBL、UniProt、AlphaFold 或其他专用数据库，除非用户在当前会话中另行明确要求。"""


def explicit_option_flags(argv: list[str]) -> set[str]:
    flags: set[str] = set()
    for token in argv:
        if token.startswith("--"):
            flags.add(token.split("=", 1)[0])
    return flags


def warn_standard_mode_ignored_options(
    args: argparse.Namespace, argv: list[str]
) -> None:
    if args.mode != "standard":
        return
    used_flags = sorted(explicit_option_flags(argv) & set(MULTI_AGENT_ONLY_FLAGS))
    if not used_flags:
        return
    details = ", ".join(f"{flag} ({MULTI_AGENT_ONLY_FLAGS[flag]})" for flag in used_flags)
    print(
        "Warning: --mode standard uses the linear workflow; "
        f"multi-agent-only options will be ignored or reduced: {details}",
        file=sys.stderr,
    )


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Generate a reusable Codex prompt for Co-Scientist Lite."
    )
    parser.add_argument("--topic", help="Research question or topic.")
    parser.add_argument(
        "--objective",
        default="生成可验证科研假设，并按医疗转化价值和实验可行性排序",
        help="Goal of the run.",
    )
    parser.add_argument(
        "--scope",
        default="偏医学科研和转化应用；不输出个人临床诊疗建议",
        help="Scope, constraints, exclusions.",
    )
    parser.add_argument(
        "--time-window",
        default=DEFAULT_TIME_WINDOW,
        help="Literature time window.",
    )
    parser.add_argument(
        "--depth",
        choices=("quick", "standard", "deep"),
        default="standard",
        help="Expected output depth.",
    )
    parser.add_argument(
        "--mode",
        choices=("standard", "multi-agent"),
        default=DEFAULT_MODE,
        help="Workflow mode. Use multi-agent for a no-database Co-Scientist-inspired simulation.",
    )
    parser.add_argument(
        "--rounds",
        type=int,
        default=2,
        help="Evolution rounds for --mode multi-agent.",
    )
    parser.add_argument(
        "--generators",
        default=DEFAULT_GENERATORS,
        help="Comma-separated generation perspectives for --mode multi-agent.",
    )
    parser.add_argument(
        "--reviewers",
        default=DEFAULT_REVIEWERS,
        help="Comma-separated reviewer perspectives for --mode multi-agent.",
    )
    parser.add_argument(
        "--ranking",
        choices=("score", "tournament"),
        default=DEFAULT_RANKING,
        help="Ranking method for --mode multi-agent.",
    )
    parser.add_argument(
        "--expansion-level",
        choices=("none", "focused", "broad"),
        default=DEFAULT_EXPANSION_LEVEL,
        help=(
            "Search expansion level for --mode multi-agent. focused adds adjacent "
            "and limited cross-disease searches; broad expands more aggressively."
        ),
    )
    parser.add_argument(
        "--transfer-domains",
        default=DEFAULT_TRANSFER_DOMAINS,
        help=(
            "Comma-separated disease or organ contexts for cross-disease transfer "
            "in --mode multi-agent."
        ),
    )
    parser.add_argument(
        "--journal-focus",
        choices=tuple(JOURNAL_FOCUS_INSTRUCTIONS),
        default=DEFAULT_JOURNAL_FOCUS,
        help=(
            "Evidence priority: top-journals anchors directions, balanced mixes "
            "high-impact and direct evidence, direct prioritizes exact-match studies."
        ),
    )
    parser.add_argument(
        "--reference-style",
        choices=tuple(REFERENCE_STYLE_INSTRUCTIONS),
        default=DEFAULT_REFERENCE_STYLE,
        help="Reference citation style for the final report.",
    )
    parser.add_argument(
        "--journal-metrics",
        choices=("none", "impact-factor"),
        default=DEFAULT_JOURNAL_METRICS,
        help="Whether the report should include journal metrics such as IF and quartile.",
    )
    parser.add_argument(
        "--impact-factor-year",
        default=DEFAULT_IMPACT_FACTOR_YEAR,
        help="Impact factor year label to use when journal metrics are requested.",
    )
    parser.add_argument(
        "--impact-factor-source",
        help=(
            "Optional path or description for a journal metrics spreadsheet. "
            "Expected columns can include full journal title, abbreviation, IF, and quartile."
        ),
    )
    parser.add_argument(
        "--lookup-if",
        action="append",
        metavar="JOURNAL",
        help=(
            "Look up local IF/Q metrics for a journal and exit. Can be repeated. "
            "Uses --impact-factor-source or local/journal_metrics/jcr_2025.jsonl."
        ),
    )
    parser.add_argument(
        "--medical-boundary",
        default=DEFAULT_MEDICAL_BOUNDARY,
        help="Medical safety boundary.",
    )
    parser.add_argument(
        "--save",
        action="store_true",
        help=(
            "Save the generated prompt. Uses CO_SCIENTIST_REQUEST_DIR or "
            "local/profile.env when configured; otherwise uses outputs/co_scientist_requests/."
        ),
    )
    parser.add_argument(
        "--output",
        help="Optional explicit output path. Overrides --save destination.",
    )
    return parser.parse_args(argv)


def write_output(content: str, args: argparse.Namespace) -> Path | None:
    if args.output:
        path = Path(args.output).expanduser()
        if not path.is_absolute():
            path = Path.cwd().resolve() / path
    elif args.save:
        stamp = dt.datetime.now().strftime("%Y%m%d-%H%M%S")
        base_dir = default_request_dir()
        path = base_dir / f"{stamp}-{slugify(args.topic)}.md"
    else:
        return None

    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")
    return path


def main(argv: list[str] | None = None) -> int:
    raw_argv = sys.argv[1:] if argv is None else argv
    args = parse_args(raw_argv)
    if args.lookup_if:
        return print_if_lookup(args)
    if not args.topic:
        raise SystemExit("--topic is required unless --lookup-if is used")
    if args.rounds < 1:
        raise SystemExit("--rounds must be >= 1")
    warn_standard_mode_ignored_options(args, raw_argv)
    resolve_impact_factor_source(args)
    content = build_prompt(args)
    saved_path = write_output(content, args)
    print(content)
    if saved_path:
        print(f"\nSaved: {saved_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
