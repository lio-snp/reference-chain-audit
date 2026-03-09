# Reference Chain Audit

[English](README.md) | 简体中文

这是一个面向论文、毕业论文与研究写作场景的 Codex skill 与脚本工具集，用来在最终参考文献格式整理之前，先做“引用证据链审计”。

它检查每条被引用文献的 3 个核心问题：

1. 被引用条目是否真实存在
2. 本地引用语句是否真的能被该文献的摘要、官方简介或数据集说明支持
3. DOI 或 URL 是否真正落到了该条目的正确页面

这个仓库适合那些“不能只因为参考文献里有链接，就默认它没问题”的写作场景。

## 仓库定位

这个仓库最准确的定位是：

- 在规则层面，它是风格无关的引用证据审计工具
- 在自动化工具层面，它当前以 LaTeX/BibTeX 工作流为主
- 现在已经通过 `CSL JSON importer` 和 `citation_contexts` 骨架生成，把非 TeX 工作流往前推进了一步

它不是一个通用的参考文献排版器。APA、GB/T 7714、Chicago 等格式规范属于后续整理层，而不是证据链是否成立的判断依据。

## 它审计什么

一条参考文献只有在以下 3 个条件都满足时，才算真正通过：

- `existence`：条目存在
- `local claim relevance`：本地引用语句与文献内容相关
- `landing correctness`：DOI 或 URL 落到正确页面

典型失败案例包括：

- DOI 能解析，但实际跳到了另一篇文章
- URL 是带 token 的 CNKI 会话链接
- 文献本身存在，但正文里的表述明显超出了该文献实际支持的范围
- APA 或 GB/T 7714 格式看起来正确，但链接指向了错误条目

## 三类工作流

### 1. LaTeX + BibTeX

这是目前支持最完整的路径。

- 解析 TeX 中的引用命令
- 抽取实际被引用的 BibTeX 子集
- 可选地提取编译后 PDF 中的外链
- 生成统一的 reference audit matrix
- 必要时再做浏览器落地页探测

### 2. 已有 contexts 的非 TeX 工作流

Word、Zotero、EndNote、CSL JSON、RIS 或混合写作流程，也可以复用这套审计逻辑。

最低要求是：

- 一份 `citation_contexts.json`，用于记录 citekey 与其本地引用上下文
- 一份 BibTeX 文件，或者可以被转换成 BibTeX 的元数据来源
- 如果想核对 PDF 中实际嵌入的链接，可以额外提供编译后的 PDF

主包装脚本已经支持通过 `--contexts-json` 接入非 TeX 工作流。

### 3. 从 CSL JSON 起步的非 TeX 工作流

如果你的参考文献来自 Zotero 或其他支持 `CSL JSON` 导出的工具，现在可以直接先生成审计输入文件：

```bash
python3 scripts/import_csl_json.py \
  --csl-json examples/non_tex/csl_items.sample.json \
  --out-bib writing/paper/references.imported.bib \
  --out-mapping writing/paper/build/csl_mapping.json \
  --out-contexts-skeleton writing/paper/build/citation_contexts.json
```

这一步会生成：

- 一份可供后续脚本使用的 BibTeX 文件
- 一份原始 CSL item id 到生成 citekey 的映射表
- 一份 `citation_contexts.json` 骨架，你只需要再把 Word、Markdown、笔记中的本地引用上下文补进去

然后继续跑主审计流程：

```bash
python3 scripts/run_reference_chain_audit.py \
  --contexts-json writing/paper/build/citation_contexts.json \
  --bib writing/paper/references.imported.bib \
  --outdir writing/paper/build/reference_audit
```

## 关于 APA 与 GB/T 7714

这个仓库会考虑 APA 与 GB/T 7714，但方式是“分层处理”。

### APA

下面这些通常属于格式层问题：

- 标题大小写
- 斜体与标点
- retrieval date 的写法

这些问题不会覆盖证据链错误。

### GB/T 7714

下面这些通常属于格式层问题：

- `[J]`、`[M]`、`[EB/OL]` 这类类型标识
- 全角与半角标点
- 作者姓名与顺序的院系要求

这些问题同样不会覆盖证据链错误。

更多说明见：

- `references/style-scope.md`
- `references/decision-rules.md`

## 仓库结构

```text
reference-chain-audit/
├── SKILL.md
├── LICENSE
├── README.md
├── README_zh.md
├── requirements.txt
├── requirements-optional.txt
├── agents/
│   └── openai.yaml
├── examples/
│   └── non_tex/
│       ├── README.md
│       ├── citation_contexts.sample.json
│       └── csl_items.sample.json
├── references/
│   ├── decision-rules.md
│   ├── report-template.md
│   └── style-scope.md
└── scripts/
    ├── build_reference_audit_matrix.py
    ├── extract_citation_contexts.py
    ├── extract_pdf_links.py
    ├── import_csl_json.py
    ├── link_browser_probe.py
    ├── run_reference_chain_audit.py
    └── subset_cited_bib.py
```

## 安装

### 基础依赖

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

### 可选浏览器探测依赖

```bash
pip install -r requirements-optional.txt
python -m playwright install chromium
```

## 快速开始

### LaTeX + BibTeX

```bash
python3 scripts/run_reference_chain_audit.py \
  --main-tex writing/paper/main.tex \
  --bib writing/paper/references.bib \
  --pdf writing/paper/build/main.pdf \
  --outdir writing/paper/build/reference_audit
```

### 已有 contexts 的非 TeX 工作流

```bash
python3 scripts/run_reference_chain_audit.py \
  --contexts-json examples/non_tex/citation_contexts.sample.json \
  --bib writing/paper/references.bib \
  --outdir writing/paper/build/reference_audit
```

### 从 CSL JSON 开始

```bash
python3 scripts/import_csl_json.py \
  --csl-json examples/non_tex/csl_items.sample.json \
  --out-bib writing/paper/references.imported.bib \
  --out-mapping writing/paper/build/csl_mapping.json \
  --out-contexts-skeleton writing/paper/build/citation_contexts.json

python3 scripts/run_reference_chain_audit.py \
  --contexts-json writing/paper/build/citation_contexts.json \
  --bib writing/paper/references.imported.bib \
  --outdir writing/paper/build/reference_audit
```

### 可选的 Bib-Check 阶段

如果你本地有 Bib-Check clone，包装脚本会按以下顺序寻找：

1. `--bibcheck-root`
2. `$BIBCHECK_ROOT`
3. `<repo>/_external/Bib-Check`

例如：

```bash
python3 scripts/run_reference_chain_audit.py \
  --main-tex writing/paper/main.tex \
  --bib writing/paper/references.bib \
  --outdir writing/paper/build/reference_audit \
  --run-bibcheck \
  --bibcheck-root /path/to/Bib-Check
```

## 输出文件

常见输出包括：

- `citation_contexts.json`
- `cited_subset.bib`
- `pdf_reference_links.json`
- `reference_audit_matrix.json`
- `csl_mapping.json`
- 基于 `references/report-template.md` 编写的审计报告

## 默认决策原则

默认策略重点如下：

- 优先使用稳定的官方落地页，而不是搜索页或会话页
- 非中文文献优先使用 DOI canonical link 或 publisher 官方页面
- 中文文献优先使用官方期刊摘要页或稳定 DOI 落地页
- 避免保留带 token 的 CNKI 链接
- 如果无法确认 DOI 或 URL 对应的落地页正确，应替换或删除，而不是保留一个高风险链接

## 当前边界

当前自动化能力最强的部分仍然是：

- LaTeX 引用抽取
- BibTeX 元数据处理
- PDF 外链抽取
- CSL JSON 到 BibTeX 与 citekey mapping 的导入

如果你想进一步支持 Word、Zotero、CSL JSON、RIS 等流程，下一步比较合理的是继续补 importer 和本地上下文提取辅助工具。

## 路线图

下一步比较合理的扩展包括：

- RIS importer
- APA / GB/T 7714 的 style-only checker
- 更强的 PDF link 与参考文献信息匹配逻辑
- 面向 Word 或 Markdown 导出的 citation context 收集辅助脚本

## Codex Skill 结构说明

这个仓库本身就是一个 Codex skill：

- `SKILL.md` 定义 skill 的用途与工作流
- `agents/openai.yaml` 提供 agent 元数据
- `references/` 放的是规则、报告模板与风格边界说明

## GitHub 推广建议

如果你要在 GitHub 上推广它，建议这样描述：

- reference evidence audit
- style-agnostic at the rule layer
- LaTeX/BibTeX-first starter tooling with a practical CSL JSON bridge for non-TeX workflows

这个表述更准确，也能正确管理别人对 APA、GB/T 7714 与非 TeX 工作流的预期。
