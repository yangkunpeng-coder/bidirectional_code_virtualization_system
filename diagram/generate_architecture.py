"""Generate the v0.2 architecture figure with Python's standard library.

Run from any working directory: python diagram/generate_architecture.py
Uses an existing Chrome/Edge installation for PNG rendering and SVG geometry QA.
No packages are installed, and the source plan is read without modification.
"""

from __future__ import annotations

import hashlib
import html
import json
from pathlib import Path
import re
import struct
import subprocess
import tempfile
import xml.etree.ElementTree as ET


HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
SOURCE = ROOT / "doc" / "Bidirectional_Code_Virtualization_System_总体方案_v0.2.md"
STEM = "Bidirectional_Code_Virtualization_Architecture"
WIDTH, HEIGHT = 1920, 1080
FONT = "'Microsoft YaHei', 'Noto Sans CJK SC', 'Source Han Sans SC', sans-serif"
C = {
    "canvas": "#F4F7FB", "ink": "#1D3047", "muted": "#5D7086",
    "border": "#D8E2EC", "flow": "#64788D", "human": "#49705D",
    "human_fill": "#F0F6F1", "python": "#3C66AF", "python_fill": "#F0F5FC",
    "local": "#147D80", "local_fill": "#ECF7F6", "reverse": "#166C7A",
    "codex": "#A86B18", "codex_fill": "#FFF7E9", "train": "#147D80",
    "optional": "#7B60A5", "optional_fill": "#F8F4FC", "feedback": "#B16B4A",
}
parts: list[str] = []
text_specs: list[dict] = []


def rect(x, y, w, h, fill="white", stroke=None, rx=12, sw=1.2, dash=None):
    attrs = f'x="{x}" y="{y}" width="{w}" height="{h}" rx="{rx}" fill="{fill}"'
    if stroke:
        attrs += f' stroke="{stroke}" stroke-width="{sw}"'
    if dash:
        attrs += f' stroke-dasharray="{dash}"'
    parts.append(f"<rect {attrs}/>")


def text(x, y, value, size=16, color=None, weight=400, anchor="start", bounds=None):
    tid = f"t{len(text_specs):03d}"
    text_specs.append({"id": tid, "text": value, "bounds": bounds})
    parts.append(
        f'<text id="{tid}" x="{x}" y="{y}" font-size="{size}" '
        f'font-weight="{weight}" fill="{color or C["ink"]}" text-anchor="{anchor}">'
        f'{html.escape(value)}</text>'
    )


def line(points, color=None, width=2, dash=None, arrow=True, marker=None):
    color = color or C["flow"]
    d = "M " + " L ".join(f"{x},{y}" for x, y in points)
    attrs = f'd="{d}" fill="none" stroke="{color}" stroke-width="{width}" stroke-linecap="round" stroke-linejoin="round"'
    if dash:
        attrs += f' stroke-dasharray="{dash}"'
    if arrow:
        marker = marker or next((k for k, v in C.items() if v == color), "flow")
        attrs += f' marker-end="url(#{marker}-arrow)"'
    parts.append(f"<path {attrs}/>")


def section(x, y, w, h, key, title, subtitle=None):
    rect(x, y, w, h, "white", C["border"], 16)
    rect(x + 22, y + 18, 29, 29, C["ink"], rx=7)
    text(x + 36.5, y + 39, key, 17, "white", 700, "middle")
    text(x + 64, y + 40, title, 22, weight=700)
    if subtitle:
        text(*subtitle)


def stage(x, w, key, role, title, lines, output, tone, fill, title_size=23):
    y, h = 270, 240
    rect(x, y, w, h, "white", C[tone], 12, 1.5)
    rect(x + 1, y + 1, w - 2, 6, C[tone], rx=3)
    safe = [x + 16, y + 9, x + w - 16, y + h - 9]
    text(x + 18, y + 30, f"{key}  {role}", 14, C[tone], 600, bounds=safe)
    text(x + 18, y + 65, title, title_size, C["ink"], 700, bounds=safe)
    for i, label in enumerate(lines):
        parts.append(f'<circle cx="{x + 21}" cy="{y + 97 + 25 * i}" r="2.2" fill="{C[tone]}"/>')
        text(x + 32, y + 102 + 25 * i, label, 15.5, bounds=safe)
    rect(x + 10, y + 203, w - 20, 27, fill, rx=6)
    text(x + 20, y + 222, output, 14.5, C[tone], 600, bounds=safe)


def generate_svg(source_hash):
    parts.clear()
    text_specs.clear()
    parts.extend([
        '<?xml version="1.0" encoding="UTF-8"?>',
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{WIDTH}" height="{HEIGHT}" viewBox="0 0 {WIDTH} {HEIGHT}" role="img" aria-labelledby="title description">',
        '<title id="title">Bidirectional Code Virtualization System — 总体架构与工作流程图</title>',
        '<desc id="description">依据总体方案 v0.2：Python 编排本地模型正向虚拟化、Codex CLI 修改虚拟切片、本地模型反向还原；人工负责完整项目的应用与验证。映射仅在本地传递。下方为规划训练体系及职责边界，DPO、GRPO 为后续可选优化。</desc>',
        f'<!-- Sole factual source: {SOURCE.name}; SHA-256: {source_hash} -->',
        '<defs>',
    ])
    for key in ["flow", "human", "python", "local", "reverse", "codex", "train", "optional", "feedback"]:
        parts.append(f'<marker id="{key}-arrow" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse"><path d="M 1,1 L 9,5 L 1,9 Z" fill="{C[key]}"/></marker>')
    parts.extend(['</defs>', f'<g font-family="{html.escape(FONT, quote=True)}">'])
    rect(0, 0, WIDTH, HEIGHT, C["canvas"], rx=0)
    text(32, 55, "Bidirectional Code Virtualization System — 总体架构与工作流程图", 31, weight=700,
         bounds=[32, 18, 1888, 65])
    text(33, 89, "真实代码 ⇄ 虚拟代码  ·  Python 流程编排  ·  人在环（Human-in-the-Loop）", 18, C["muted"])
    rect(1557, 72, 331, 27, "#E8EEF6", rx=6)
    text(1722.5, 91, "方案 v0.2  /  实验性原型 · 规划视图", 14.5, C["muted"], 600, "middle")

    # A: the Python boundary is an orchestrator, not another code transformer.
    section(32, 118, 1856, 520, "A", "系统运行时工作流程")
    line([(1730, 270), (1730, 181), (173, 181), (173, 265)], C["human"], 1.8, "9 5")
    rect(633, 164, 930, 32, "white", rx=5)
    text(1098, 185, "仍有 BUG / 需要修改：人工发起下一轮，重新选择目标切片与修改目的", 16, C["human"], 500, "middle")

    rect(324, 204, 1238, 355, C["python_fill"], "#B8CBE8", 14, 1.4)
    text(344, 234, "S2  Python 原型系统", 21, C["python"], 700)
    text(614, 233, "接收切片与目的 · 创建虚拟工作区 · 保存映射 · 调用本地模型 / Codex CLI · 展示恢复结果", 15, C["python"],
         bounds=[605, 208, 1543, 248])
    text(345, 257, "流程编排与数据传递", 13.5, C["muted"])
    text(1540, 257, "本地系统保存映射，Codex CLI 仅接触虚拟工作内容", 13.5, C["muted"], anchor="end")

    # Planned trained-model association: enter outside the mapping bypass.
    line([(1325, 599), (370, 599), (370, 515)], C["train"], 1.8, "6 4")
    line([(1325, 599), (1505, 599), (1505, 515)], C["train"], 1.8, "6 4")
    rect(561, 580, 729, 31, "white", rx=5)
    text(925.5, 601, "规划训练所得的同一本地模型，用于正向虚拟化与反向还原两个阶段", 16, C["train"], 600, "middle")

    stage(54, 238, "S1", "人工 · 真实代码域", "完整真实项目", [
        "人工开发与发现问题", "提出本次修改需求", "选择目标函数 / 代码切片", "描述本次修改目的",
    ], "输入由人工指定", "human", C["human_fill"], 22)
    stage(346, 366, "S3", "本地小模型 · 真实 → 虚拟", "正向代码虚拟化", [
        "识别函数、类、参数与变量", "生成虚拟名称，建立稳定映射", "尽量保持原有代码逻辑与结构", "按目标代码和修改目的生成虚假上下文",
    ], "输出：虚拟目标切片 + 虚假上下文", "local", C["local_fill"])
    stage(748, 350, "S4", "Codex CLI · 虚拟工作区", "虚拟代码修改", [
        "接收虚拟化后的目标代码切片", "结合虚假上下文和用户修改目的", "仅在虚拟代码空间进行修改",
    ], "输出：修改后的虚拟代码", "codex", C["codex_fill"])
    rect(768, 447, 158, 21, C["codex_fill"], rx=5)
    text(847, 462, "仅处理虚拟目标切片", 13.5, C["codex"], 600, "middle")
    stage(1134, 406, "S5", "本地小模型 · 虚拟 → 真实", "反向代码还原", [
        "对照修改前后代码，识别变量身份", "处理变量重命名、新增与删除", "生成符合项目风格的真实变量名", "结合原映射还原，保留有效代码修改",
    ], "输出：恢复后的真实代码", "reverse", C["local_fill"])
    stage(1594, 272, "S6", "人工 · 真实代码域", "应用与实验验证", [
        "检查恢复代码，决定是否采用", "人工应用到完整真实项目", "自行编译、运行和测试", "按实际效果判断是否达标",
    ], "记录成功 / 失败案例", "human", C["human_fill"], 22)
    # Runtime data arrows are all solid. No arrow exposes original mapping to Codex.
    line([(298, 393), (340, 393)], C["flow"])
    text(319, 378, "目标切片", 12.5, C["muted"], anchor="middle")
    text(319, 418, "修改目的", 12.5, C["muted"], anchor="middle")
    line([(718, 393), (742, 393)], C["local"])
    line([(1104, 393), (1128, 393)], C["codex"])
    line([(1546, 393), (1588, 393)], C["reverse"])
    text(1567, 378, "真实代码", 12.5, C["muted"], anchor="middle")

    # Bypass stays below the Codex card and inside the Python boundary.
    line([(684, 510), (684, 535), (1160, 535), (1160, 515)], C["python"], 1.6)
    text(925.5, 530, "本地保留的原映射 + 修改前虚拟代码 → 反向还原", 14, C["python"], 600, "middle")
    text(925.5, 553, "映射信息不提供给 Codex CLI", 13.5, C["python"], anchor="middle")

    # B and C sit below the primary runtime view.
    section(32, 664, 1412, 327, "B", "本地模型训练体系")
    text(379, 703, "规划路线；训练前验证加载、适配、训练与重载推理", 14.5, C["muted"])
    section(1468, 664, 420, 327, "C", "系统职责边界")
    # Draw after section backgrounds so the trained-model link stays continuous.
    line([(1325, 724), (1325, 599)], C["train"], 1.8, "6 4", arrow=False)

    rect(54, 724, 470, 66, "#F5F8FD", "#C6D4E9", 10)
    text(72, 751, "Qwen3-Coder-Next", 23, C["python"], 700)
    rect(332, 738, 173, 24, "#E6EDF8", rx=5)
    text(418.5, 755, "首选基础模型候选", 14, C["python"], 600, "middle")
    text(72, 777, "正式训练前验证模型加载、训练框架适配与推理能力", 15, C["muted"],
         bounds=[69, 730, 509, 786])

    rect(54, 804, 470, 124, "white", "#C6D4E9", 10)
    text(72, 831, "专用训练数据集构建", 19, C["ink"], 700)
    for y, label in [
        (857, "01 正向代码虚拟化    02 虚假上下文生成"),
        (880, "03 变量身份识别      04 真实命名生成"),
        (903, "05 反向代码还原 · 配对样本、质量检查与数据划分"),
    ]:
        text(72, y, label, 15, C["muted"], bounds=[68, 811, 511, 920])

    rect(580, 724, 320, 184, "#F2F8F8", "#B6D6D5", 10)
    text(598, 752, "LoRA + SFT", 24, C["local"], 700)
    text(598, 775, "第一阶段 · 参数高效微调 / 多任务监督训练", 13.5, C["local"],
         bounds=[595, 731, 886, 902])
    for y, label in [
        (799, "ms-swift · 主训练框架"),
        (821, "Megatron-SWIFT · 分布式训练"),
        (843, "ModelScope MCore-Bridge · 模型桥接"),
        (865, "Megatron-Core · 底层训练引擎"),
    ]:
        text(598, y, label, 14, C["ink"], bounds=[595, 731, 886, 902])
    text(598, 892, "备选 / 对照：LLaMA-Factory", 13.5, C["muted"])

    rect(944, 724, 478, 184, C["local_fill"], "#A9CECB", 10, 1.4)
    text(964, 748, "训练目标产物 · 规划能力，非已完成部署", 13.5, C["local"], 600)
    text(964, 779, "具备双向虚拟化能力的本地模型", 22, C["local"], 700,
         bounds=[959, 730, 1406, 902])
    text(964, 810, "正向虚拟化 / 虚假上下文生成", 16, C["ink"])
    text(964, 835, "变量身份识别 / 真实命名生成", 16, C["ink"])
    text(964, 860, "变量变化处理 / 反向代码还原", 16, C["ink"])
    text(964, 892, "经核心能力测试与端到端实验评估", 14.5, C["muted"])

    line([(530, 757), (574, 757)], C["train"], 1.8, "6 4")
    line([(530, 866), (551, 866), (551, 839), (574, 839)], C["train"], 1.8, "6 4")
    line([(906, 818), (938, 818)], C["train"], 1.8, "6 4")

    rect(580, 923, 842, 53, C["optional_fill"], C["optional"], 9, 1.4, "3 4")
    line([(1240, 909), (1240, 920)], C["optional"], 1.6, "2 4")
    text(598, 944, "后续可选优化：DPO / GRPO", 17, C["optional"], 700)
    text(894, 944, "SFT 基本可用且评价可靠后，按实验收益决定", 14.5, C["optional"])
    text(598, 966, "vLLM：仅根据后续强化学习方案决定是否采用；DPO / GRPO 不作为第一阶段必经步骤。", 14, C["optional"])

    rows = [
        ("人工", "human", 734, "完整项目管理、选片与需求", "最终应用、编译、运行和测试"),
        ("Python", "python", 793, "实验流程编排；本地模型与", "Codex CLI 调度；本地保存映射"),
        ("本地小模型", "local", 852, "正向虚拟化、虚假上下文生成", "身份识别、变量变化、命名与还原"),
        ("Codex CLI", "codex", 911, "仅修改虚拟化后的目标切片", "完整真实项目与原映射不提供"),
    ]
    for i, (name, tone, y, a, b) in enumerate(rows):
        rect(1490, y - 15, 4, 37, C[tone], rx=2)
        text(1504, y, name, 16, C[tone], 700)
        text(1593, y, a, 14, C["ink"], bounds=[1590, y - 19, 1871, y + 24])
        text(1593, y + 20, b, 14, C["muted"], bounds=[1590, y - 19, 1871, y + 24])
        if i < 3:
            line([(1490, y + 34), (1866, y + 34)], C["border"], 1, arrow=False)
    text(1593, 953, "正向转换与反向还原由本地模型负责", 14, C["codex"],
         bounds=[1590, 935, 1871, 966])
    text(1490, 976, "接受修改与否，由人通过实际项目验证决定。", 14, C["muted"])

    # Experiment feedback goes around the right and bottom perimeter, with no
    # crossings through the model association or the responsibility panel.
    line([(1866, 485), (1901, 485), (1901, 1009), (300, 1009), (300, 933)],
         C["feedback"], 1.8, "10 4 2 4")
    rect(542, 994, 1020, 29, C["canvas"], rx=5)
    text(1052, 1015, "实验反馈：记录成功 / 失败案例 → 补充薄弱任务数据 → 新一轮 SFT 与评估", 16,
         C["feedback"], 600, "middle")

    # Compact, explicit arrow and border legend.
    legend_y = 1048
    text(33, legend_y + 5, "图例", 14, C["muted"], 700)
    line([(81, legend_y), (117, legend_y)], C["flow"], 1.8)
    text(126, legend_y + 5, "运行时数据 / 本地映射", 13, C["muted"])
    line([(304, legend_y), (340, legend_y)], C["train"], 1.8, "6 4")
    text(349, legend_y + 5, "训练 / 模型关联", 13, C["muted"])
    line([(486, legend_y), (522, legend_y)], C["optional"], 1.8, "2 4")
    text(531, legend_y + 5, "后续可选优化", 13, C["muted"])
    line([(656, legend_y), (692, legend_y)], C["human"], 1.8, "9 5")
    text(701, legend_y + 5, "人工下一轮", 13, C["muted"])
    line([(811, legend_y), (847, legend_y)], C["feedback"], 1.8, "10 4 2 4")
    text(856, legend_y + 5, "实验 / 数据反馈", 13, C["muted"])
    rect(1000, legend_y - 9, 23, 16, "white", C["flow"], 3, 1)
    text(1032, legend_y + 5, "实框：核心流程", 13, C["muted"])
    rect(1164, legend_y - 9, 23, 16, "white", C["optional"], 3, 1, "3 4")
    text(1196, legend_y + 5, "虚框：可选分支", 13, C["muted"])
    text(1888, legend_y + 5, "唯一事实依据：总体方案 v0.2 · §§ 2–10、13", 12.5, C["muted"], anchor="end")
    parts.extend(["</g>", "</svg>"])
    svg = "\n".join(parts) + "\n"
    ET.fromstring(svg)
    assert "\ufffd" not in svg
    (HERE / f"{STEM}.svg").write_text(svg, encoding="utf-8")


def generate_mermaid(source_hash):
    # Same modules and information paths as the SVG. Mermaid is an editable
    # semantic source; the publication layout is authored explicitly in SVG.
    mmd = '''---
title: Bidirectional Code Virtualization System — 总体架构与工作流程图
config:
  theme: base
  themeVariables:
    fontFamily: 'Microsoft YaHei, Noto Sans CJK SC, Source Han Sans SC, sans-serif'
    fontSize: 17px
    primaryTextColor: '#1D3047'
    lineColor: '#64788D'
  flowchart:
    htmlLabels: true
    curve: linear
    nodeSpacing: 30
    rankSpacing: 42
---
%% 唯一事实依据：doc/Bidirectional_Code_Virtualization_System_总体方案_v0.2.md
%% 这是实验规划图，候选模型与训练目标不代表已经完成部署。
%% SVG 采用固定 1920×1080 出版布局；本文件保留同一模块与信息流供修改。
flowchart TB
  subgraph A["A · 系统运行时工作流程｜人在环 Human-in-the-Loop"]
    direction LR
    S1["<b>S1 · 完整真实项目 / 人工</b><br/>人工开发、发现 BUG 或提出需求<br/>选择目标函数 / 代码切片，描述修改目的"]
    subgraph PY["S2 · Python 原型系统｜流程编排与数据传递<br/>接收切片和目的 · 创建虚拟工作区 · 保存映射 · 调用本地模型 / Codex CLI · 展示恢复结果"]
      direction LR
      S3["<b>S3 · 本地小模型：正向代码虚拟化</b><br/>真实代码 → 虚拟代码<br/>识别函数、类、参数与变量<br/>生成虚拟名称，建立稳定映射<br/>尽量保持原有逻辑与结构<br/>按目标代码和修改目的生成虚假上下文"]
      S4["<b>S4 · Codex CLI / 虚拟工作区</b><br/>仅修改虚拟化后的目标代码切片<br/>结合虚假上下文和用户修改目的<br/>输出修改后的虚拟代码<br/><b>不承担正向转换或反向还原</b>"]
      S5["<b>S5 · 本地小模型：反向代码还原</b><br/>虚拟代码 → 真实代码<br/>对照修改前后代码，识别变量身份<br/>处理变量重命名、新增与删除<br/>生成符合项目风格的真实变量名<br/>结合原映射恢复，保留有效代码修改"]
      MAP["<b>Python 本地保留的信息</b><br/>原映射 + 修改前虚拟代码<br/>映射信息不提供给 Codex CLI"]
    end
    S6["<b>S6 · 人工应用与实验验证</b><br/>检查恢复代码，决定是否采用<br/>将代码应用到完整真实项目<br/>自行编译、运行和测试，判断实际效果<br/>记录成功 / 失败案例"]
  end

  subgraph B["B · 本地模型训练体系｜规划路线，训练前验证加载、适配、训练与重载推理"]
    direction LR
    BASE["<b>Qwen3-Coder-Next</b><br/>首选基础模型候选"]
    DATA["<b>专用训练数据集构建</b><br/>Dataset 01 正向代码虚拟化<br/>Dataset 02 虚假上下文生成<br/>Dataset 03 变量身份识别<br/>Dataset 04 真实命名生成<br/>Dataset 05 反向代码还原<br/>配对样本、质量检查与数据划分"]
    SFT["<b>第一阶段：LoRA + SFT</b><br/>参数高效微调 / 多任务监督训练<br/>ms-swift · 主训练框架<br/>Megatron-SWIFT · 分布式训练<br/>ModelScope MCore-Bridge · 模型桥接<br/>Megatron-Core · 底层训练引擎<br/>LLaMA-Factory · 备选 / 对照"]
    MODEL["<b>训练目标：具备双向虚拟化能力的本地模型</b><br/>正向虚拟化 / 虚假上下文生成<br/>变量身份识别 / 真实命名生成<br/>变量变化处理 / 反向代码还原<br/>核心能力测试与端到端实验评估<br/><b>规划能力，非已完成部署</b>"]
    OPT["<b>后续可选优化：DPO / GRPO</b><br/>SFT 基本可用且评价可靠后，按实验收益决定<br/>vLLM 仅根据后续强化学习方案决定是否采用<br/>DPO / GRPO 不作为第一阶段必经步骤"]
  end

  subgraph C["C · 系统职责边界"]
    direction LR
    HUMAN["<b>人工</b><br/>完整项目管理、选片与需求<br/>最终应用、编译、运行和测试<br/>根据实际效果决定是否接受修改"]
    PYROLE["<b>Python</b><br/>实验流程编排<br/>本地模型与 Codex CLI 调度<br/>虚拟工作区与本地映射管理"]
    LOCAL["<b>本地小模型</b><br/>正向虚拟化 / 虚假上下文生成<br/>变量身份识别 / 变量变化处理<br/>真实命名生成 / 反向代码还原"]
    CODEX["<b>Codex CLI</b><br/>仅修改虚拟化后的目标代码切片<br/>完整真实项目与原映射不提供<br/>代码转换与还原由本地模型负责"]
  end
'''
    edges = [
        ('S1 -->|"目标切片 + 修改目的"| S3', "flow"),
        ('S3 -->|"虚拟目标切片 + 虚假上下文"| S4', "local"),
        ('S4 -->|"修改后的虚拟代码"| S5', "codex"),
        ('S5 -->|"恢复后的真实代码（经 Python 展示）"| S6', "reverse"),
        ('S3 -->|"Python 在本地保存"| MAP', "python"),
        ('MAP -->|"原映射 + 修改前虚拟代码"| S5', "python"),
        ('S6 -.->|"仍有 BUG / 新需求：人工发起下一轮"| S1', "human"),
        ('BASE -.-> SFT', "train"),
        ('DATA -.-> SFT', "train"),
        ('SFT -.-> MODEL', "train"),
        ('MODEL -.->|"同一本地模型 · 正向阶段"| S3', "train"),
        ('MODEL -.->|"同一本地模型 · 反向阶段"| S5', "train"),
        ('MODEL -.->|"按 SFT 效果与实验收益决定"| OPT', "optional"),
        ('S6 -.->|"成功 / 失败案例 → 补充薄弱数据 → 再训练与评估"| DATA', "feedback"),
    ]
    for edge, _ in edges:
        mmd += "  " + edge + "\n"
    mmd += '''
  classDef human fill:#F0F6F1,stroke:#49705D,color:#1D3047,stroke-width:1.5px;
  classDef local fill:#ECF7F6,stroke:#147D80,color:#1D3047,stroke-width:1.5px;
  classDef python fill:#F0F5FC,stroke:#3C66AF,color:#1D3047;
  classDef codex fill:#FFF7E9,stroke:#A86B18,color:#1D3047,stroke-width:1.5px;
  classDef optional fill:#F8F4FC,stroke:#7B60A5,color:#1D3047,stroke-dasharray:3 4;
  class S1,S6,HUMAN human;
  class S3,S5,MODEL,SFT,LOCAL local;
  class MAP,BASE,DATA,PYROLE python;
  class S4,CODEX codex;
  class OPT optional;
  style A fill:#FFFFFF,stroke:#D8E2EC
  style PY fill:#F0F5FC,stroke:#B8CBE8
  style B fill:#FFFFFF,stroke:#D8E2EC
  style C fill:#FFFFFF,stroke:#D8E2EC
'''
    dash = {"train": "6 4", "optional": "2 4", "human": "9 5", "feedback": "10 4 2 4"}
    for i, (_, kind) in enumerate(edges):
        mmd += f"  linkStyle {i} stroke:{C[kind]},stroke-width:1.8px"
        if kind in dash:
            mmd += f",stroke-dasharray:{dash[kind]}"
        mmd += ";\n"
    mmd += "\n%% 图例：实线=运行时数据/映射；6 4虚线=训练/模型关联；2 4点线及虚框=可选优化；9 5长虚线=人工下一轮；点划线=实验数据反馈。\n"
    mmd += f"%% 原始方案 SHA-256: {source_hash}\n"
    (HERE / f"{STEM}.mmd").write_text(mmd, encoding="utf-8")


def find_browser():
    for candidate in [
        Path(r"C:\Program Files\Google\Chrome\Application\chrome.exe"),
        Path(r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe"),
        Path(r"C:\Program Files\Microsoft\Edge\Application\msedge.exe"),
    ]:
        if candidate.is_file():
            return candidate
    raise RuntimeError("No existing Chrome/Edge installation found; SVG and Mermaid were generated.")


def render_and_audit():
    browser = find_browser()
    # The disposable profile only lives under the system temporary directory.
    # Its resolved absolute target is checked before automatic cleanup.
    temp_root = Path(tempfile.gettempdir()).resolve()
    tmp = tempfile.TemporaryDirectory(prefix="bcvs_diagram_", dir=temp_root)
    task_tmp = Path(tmp.name).resolve()
    assert task_tmp.is_relative_to(temp_root) and task_tmp.name.startswith("bcvs_diagram_")
    try:
        common = [str(browser), "--headless=new", f"--user-data-dir={task_tmp / 'profile'}",
                  "--no-first-run", "--no-default-browser-check", "--disable-sync",
                  "--disable-background-networking", "--disable-component-update",
                  "--disable-default-apps", "--disable-crashpad-for-testing", "--disable-breakpad",
                  "--allow-file-access-from-files", "--hide-scrollbars"]
        png = HERE / f"{STEM}.png"
        result = subprocess.run(common + ["--force-device-scale-factor=2", "--window-size=1920,1080",
                                f"--screenshot={png}", (HERE / f"{STEM}.svg").as_uri()],
                                capture_output=True, timeout=60)
        if result.returncode or not png.is_file():
            raise RuntimeError(result.stderr.decode("utf-8", "replace")[-3000:])
        raw = png.read_bytes()
        assert raw[:8] == b"\x89PNG\r\n\x1a\n"
        pixel_width, pixel_height = struct.unpack(">II", raw[16:24])
        assert (pixel_width, pixel_height) == (3840, 2160), (pixel_width, pixel_height)

        # Browser SVG font metrics catch clipping, text overlaps and canvas overflow.
        audit_path = task_tmp / "audit.html"
        svg = (HERE / f"{STEM}.svg").read_text(encoding="utf-8")
        spec_json = json.dumps(text_specs, ensure_ascii=False)
        audit_js = r'''
const specs = SPECS;
const getBox = el => {const b=el.getBBox();return {x:b.x,y:b.y,w:b.width,h:b.height};};
const intersects = (a,b) => Math.min(a.x+a.w,b.x+b.w)-Math.max(a.x,b.x)>1 && Math.min(a.y+a.h,b.y+b.h)-Math.max(a.y,b.y)>1;
function audit(){
  const entries=specs.map(s=>({...s,box:getBox(document.getElementById(s.id))}));
  const overflow=entries.filter(({box:b})=>b.x<0||b.y<0||b.x+b.w>1920||b.y+b.h>1080);
  const clipping=entries.filter(({bounds:r,box:b})=>r&&(b.x<r[0]-0.5||b.y<r[1]-0.5||b.x+b.w>r[2]+0.5||b.y+b.h>r[3]+0.5));
  const collisions=[];
  for(let i=0;i<entries.length;i++)for(let j=i+1;j<entries.length;j++)if(intersects(entries[i].box,entries[j].box))collisions.push([entries[i],entries[j]]);
  const result={texts:entries.length,fontLoaded:document.fonts.check('16px "Microsoft YaHei"'),overflow,clipping,collisions};
  document.getElementById('qa').textContent=JSON.stringify(result);
}
document.fonts.ready.then(audit);
'''.replace("SPECS", spec_json)
        audit_path.write_text("<!doctype html><meta charset='utf-8'><style>body{margin:0}</style>" + svg
                              + "<pre id='qa'></pre><script>" + audit_js + "</script>", encoding="utf-8")
        audit = subprocess.run(common + ["--dump-dom", "--virtual-time-budget=2500", audit_path.as_uri()],
                               capture_output=True, timeout=60)
        dom = audit.stdout.decode("utf-8", "replace")
        match = re.search(r'<pre id="qa">(.*?)</pre>', dom, re.S)
        if not match:
            raise RuntimeError("No browser geometry audit result: " + audit.stderr.decode("utf-8", "replace")[-1200:])
        qa = json.loads(html.unescape(match.group(1)))
        print(json.dumps({"png": [pixel_width, pixel_height], "qa": qa}, ensure_ascii=False, indent=2))
        if qa["overflow"] or qa["clipping"] or qa["collisions"] or not qa["fontLoaded"]:
            raise RuntimeError("SVG geometry QA requires layout corrections (see report above).")
    finally:
        # Chrome may briefly retain profile files on Windows. Do not force-delete
        # arbitrary paths or touch any user's browser profile.
        try:
            tmp.cleanup()
        except PermissionError:
            pass


def main():
    if not SOURCE.is_file():
        raise FileNotFoundError(f"Required sole source not found: {SOURCE}")
    source_bytes = SOURCE.read_bytes()
    source = source_bytes.decode("utf-8")
    for term in ["Qwen3-Coder-Next", "LoRA + SFT", "Codex CLI", "Python", "DPO", "GRPO",
                 "ms-swift", "Megatron-SWIFT", "ModelScope MCore-Bridge", "Megatron-Core"]:
        assert term in source, f"Source term not found: {term}"
    source_hash = hashlib.sha256(source_bytes).hexdigest()
    generate_svg(source_hash)
    generate_mermaid(source_hash)
    render_and_audit()
    assert hashlib.sha256(SOURCE.read_bytes()).hexdigest() == source_hash, "Source plan changed"
    print(f"Generated {STEM}.svg, .png and .mmd in {HERE}")


if __name__ == "__main__":
    main()
