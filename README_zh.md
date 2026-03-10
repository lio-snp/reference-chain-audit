# Reference Chain Audit

[English](README.md) | 简体中文

这是一个面向 Codex、Claude Code 等 agent 的引用审计 skill，用来在最终参考文献格式整理之前，先做“引用证据链审计”。

这个仓库提供一个可复用的引用审计 skill，并附带若干用于抽取、归一化和证据整理的可选辅助脚本。

## 这个仓库是做什么的

它给 agent 一个很明确的任务：

1. 确认被引用条目真实存在
2. 确认本地引用语句确实能被该文献支持
3. 确认 DOI 或 URL 真正落到了正确页面
4. 把这些问题和 APA、GB/T 7714 这类格式问题分开处理

`scripts/` 目录里的脚本只是可选辅助工具，用来在合适的时候加速抽取、归一化和证据整理。它们不应该变成用户必须手动照着跑的固定流程。

## 默认使用方式

推荐的使用方式是：

- 把论文草稿、参考文献或导出的元数据交给 agent
- 让 agent 使用这个 skill 去做引用审计
- 由 agent 自己判断是否值得调用某个脚本

最典型的使用提示可以是：

```text
使用 reference-chain-audit skill 审计这篇论文的参考文献。
重点检查 existence、local claim relevance 和 landing correctness。
APA 或 GB/T 7714 只作为后续格式整理，不要与证据链判断混在一起。
只有在确实能节省时间时才调用 helper scripts。
```

## 核心审计逻辑

一条参考文献只有在以下 3 项都成立时才算通过：

- `existence`
- `local claim relevance`
- `landing correctness`

典型失败情况包括：

- DOI 能解析，但实际跳到了另一篇文章
- URL 是带 token 的 CNKI 会话链接
- 正文中的引用语句明显超出了文献本身支持的范围
- APA 或 GB/T 7714 看起来格式正确，但指向了错误条目

## Skill-First 工作流

### 1. 收集本地引用证据

agent 找到每条参考文献在正文中是怎么被引用的，以及附近语句到底在声称什么。

### 2. 必要时归一化元数据

如果参考文献来源比较乱，agent 可以把它们整理成 BibTeX 或其他结构化形式。

### 3. 审计证据链

逐条检查：

- existence
- relevance to the local claim
- landing correctness

### 4. 单独处理格式层

APA、GB/T 7714、Chicago 等属于后续格式层，不应覆盖证据链判断。

### 5. 输出审计报告

agent 最终应给出清晰动作建议，例如：

- keep as is
- revise prose
- replace DOI or URL
- remove DOI or URL
- replace citation

## 可选 Helper Scripts

只有在它们真的能减少工作量时才使用。

- `scripts/run_reference_chain_audit.py`
  - 封装好的抽取与 matrix 流程
- `scripts/extract_citation_contexts.py`
  - TeX 引用上下文抽取
- `scripts/subset_cited_bib.py`
  - cited-only BibTeX 子集生成
- `scripts/import_csl_json.py`
  - 从 CSL JSON 生成 BibTeX、citekey mapping 与 contexts skeleton
- `scripts/extract_pdf_links.py`
  - 从编译后的 PDF 中抽取超链接
- `scripts/link_browser_probe.py`
  - 可选的浏览器落地页探测
- `scripts/build_reference_audit_matrix.py`
  - 生成 review matrix

## 非 TeX 工作流

这个 skill 也支持非 TeX 工作流，但方式仍然是 agent-first。

agent 可以基于以下任一输入工作：

- `citation_contexts.json`
- BibTeX 或其他结构化元数据
- Zotero 等工具导出的 CSL JSON
- 带有外链的编译后 PDF

如果有 CSL JSON，agent 可以在需要时调用 `scripts/import_csl_json.py`，自动生成：

- BibTeX
- citekey mapping
- `citation_contexts.json` skeleton

## 仓库结构

```text
reference-chain-audit/
├── SKILL.md
├── LICENSE
├── README.md
├── README_zh.md
├── agents/
├── references/
├── scripts/
└── examples/
```

## 建议先看什么

- `SKILL.md`
  - skill 的主行为定义
- `references/decision-rules.md`
  - DOI/URL 的保留、替换与删除规则
- `references/style-scope.md`
  - APA、GB/T 7714 作为格式层处理
- `references/report-template.md`
  - 结构化报告模板

## 边界

它不是通用参考文献排版器。

它是一个 `reference evidence audit skill`。

当前脚本层支持最好的部分是：

- LaTeX 引用抽取
- BibTeX 元数据处理
- CSL JSON 导入
- PDF 外链抽取

但 skill 本身的审计逻辑并不被这些格式完全限制。

## Acknowledgments

本项目部分思路受到 [Bib-Check](https://github.com/LeoJ-xy/Bib-Check) 的启发。Bib-Check 主要面向 BibTeX 校验与联网元数据矫正；Reference Chain Audit 则进一步扩展为一个 agent-first 的引用证据链审计 skill，重点关注 existence、local claim relevance 与 landing correctness。

## GitHub 推广时的表述

更准确的短描述应该是：

- reference evidence audit skill
- agent-first workflow
- LaTeX/BibTeX-first helper tooling
- practical CSL JSON bridge for non-TeX workflows
