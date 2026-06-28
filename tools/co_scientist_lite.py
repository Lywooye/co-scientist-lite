#!/usr/bin/env python3
"""Generate a Codex prompt for the Co-Scientist Lite workflow.

This script does not search literature itself. It creates a stable task prompt
that asks Codex to use the live search tools available in the current session.
"""

from __future__ import annotations

import argparse
import datetime as dt
import re
from pathlib import Path


DEFAULT_TIME_WINDOW = "优先近 5 年；必要时追溯奠基文献；必须写明检索日期"
DEFAULT_MEDICAL_BOUNDARY = "科研/转化医学假设，不输出个人化诊断或治疗建议"
DEFAULT_JOURNAL_FOCUS = "top-journals"
DEFAULT_MODE = "standard"
DEFAULT_GENERATORS = "mechanism,translation,methods"
DEFAULT_REVIEWERS = "evidence,methods,translation"
DEFAULT_RANKING = "tournament"

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


def normalize_list(value: str) -> str:
    items = [item.strip() for item in value.split(",") if item.strip()]
    return ", ".join(items) if items else "none"


def project_root() -> Path:
    return Path(__file__).resolve().parents[1]


def slugify(text: str, max_length: int = 48) -> str:
    text = re.sub(r"\s+", "-", text.strip())
    text = re.sub(r"[^\w\-\u4e00-\u9fff]+", "", text)
    return text[:max_length].strip("-") or "co-scientist-lite"


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

{mode_instructions}

## 输出要求

1. 先给出窄化后的可执行研究问题和成功标准。
2. 输出检索日志、证据表、假设表、反方审查、排序表、Top 3 验证方案。
3. 所有论文、指南、数据库页面都要给链接；能核验 DOI/PMID 时写出 DOI/PMID。
4. 预印本、综述、动物/体外研究、回顾性研究、RCT、指南要分层标注。
5. 单独标注“顶刊/高影响文献提供的研究方向”和“专科直接证据提供的可验证事实”，不要混为同一种证据。
6. 证据不足时明确写“不足”，不要补造结论。
7. 结尾列出医疗转化前景、关键风险和待补证据。
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

3. Generation agents
   - 生成视角：{normalize_list(args.generators)}
   - 每个生成 agent 至少提出 2-3 条候选假设，并写明证据链和最小验证方式。

4. Proximity agent
   - 对候选假设去重、聚类、合并相似项。
   - 输出 hypothesis clusters，并说明每个 cluster 的共同机制、差异点和覆盖空白。

5. Reflection agents
   - 审查视角：{normalize_list(args.reviewers)}
   - 对每条候选假设进行证据、方法学、临床转化和偏倚风险审查。

6. Ranking agent
   - 排序方式：{args.ranking}
   - 若使用 tournament，则进行成对比较，给出胜负理由、关键否决项和最终积分/排序。

7. Evolution agent
   - 进化轮数：{args.rounds}
   - 对高分假设进行 refine、combine、split 或 reject。
   - 每一轮都要说明假设发生了什么变化，以及为什么变化。

8. Meta-review agent
   - 综合 evidence、reviews、ranking 和 evolution，输出最终 Top 3。
   - 明确哪些结论来自强证据，哪些只是可验证设想。

额外输出要求：

- 输出 hypothesis pool、clusters、review matrix、tournament/ranking log、evolution log。
- 不要把多 agent 仿真写成真实独立模型并行执行；应明确这是单次 Codex 会话中的结构化角色仿真。
- 不接入 ChEMBL、UniProt、AlphaFold 或其他专用数据库，除非用户在当前会话中另行明确要求。"""


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Generate a reusable Codex prompt for Co-Scientist Lite."
    )
    parser.add_argument("--topic", required=True, help="Research question or topic.")
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
        "--journal-focus",
        choices=tuple(JOURNAL_FOCUS_INSTRUCTIONS),
        default=DEFAULT_JOURNAL_FOCUS,
        help=(
            "Evidence priority: top-journals anchors directions, balanced mixes "
            "high-impact and direct evidence, direct prioritizes exact-match studies."
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
        help="Save the generated prompt under outputs/co_scientist_requests/.",
    )
    parser.add_argument(
        "--output",
        help="Optional explicit output path. Overrides --save destination.",
    )
    return parser.parse_args()


def write_output(content: str, args: argparse.Namespace) -> Path | None:
    if args.output:
        path = Path(args.output).expanduser()
        if not path.is_absolute():
            path = Path.cwd().resolve() / path
    elif args.save:
        stamp = dt.datetime.now().strftime("%Y%m%d-%H%M%S")
        base_dir = project_root() / "outputs" / "co_scientist_requests"
        path = base_dir / f"{stamp}-{slugify(args.topic)}.md"
    else:
        return None

    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")
    return path


def main() -> int:
    args = parse_args()
    if args.rounds < 1:
        raise SystemExit("--rounds must be >= 1")
    content = build_prompt(args)
    saved_path = write_output(content, args)
    print(content)
    if saved_path:
        print(f"\nSaved: {saved_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
