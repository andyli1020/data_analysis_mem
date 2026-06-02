---
chunk_id: "chunk_011"
title: "2.1 AI and Generative AI Exposure Metrics"
model: "deepseek-v4-flash"
source_file: "work/chunks/generative_ai_labor_demand_pdf_full/chunk_011_2_1_ai_and_generative_ai_exposure_metrics_p1.md"
---
【中文译文】
## 2.1 人工智能与生成式AI暴露度指标

已有大量文献探讨哪些类型的工作可能受到人工智能的影响。该领域文献的概念基础是任务导向型的：技术并非直接作用于职业来影响劳动力需求，而是通过改变职业内部所执行的任务来实现（Acemoglu 和 Autor, 2011; Autor, 2015; Acemoglu 和 Restrepo, 2019）。由于职业是任务的组合，技术变革可能会对职业的某些部分（而非其他部分）实现自动化、增强或以其他方式重塑。与此观点一致，许多AI暴露度指标将O*NET中的职业任务信息与外部对AI能力的评估相结合，构建职业层面的暴露指数（Frey 和 Osborne, 2017; Felten 等, 2018, 2021; Webb, 2019; Pizzinelli 等, 2023; Hampole 等, 2025）。近期研究将这一方法扩展至生成式AI和大语言模型（LLM）。其中许多研究仍依赖O*NET的任务或能力信息，但将暴露度概念适配至语言模型的能力。例如，Eloundou等（2024）开发了一套基于任务的评估标准，评估LLM及基于LLM的软件能否大幅缩短执行特定任务所需的时间，然后将这些评估结果汇总至职业层面。Felten等（2023）将基于能力的职业暴露框架适配至语言建模领域的进展。Gmyrek等（2023）利用任务层面的评估，根据任务在职业内的暴露分布来区分自动化和增强。Benítez-Rueda和Parrado（2024）使用合成AI调查，基于职业的特征任务构建了更全面的职业层面指标。其他研究则使用现实世界的交互数据。Anthropic经济指数（Handa等, 2025）分析了数百万条Claude.ai对话，并将其映射至O*NET任务和职业，以确定AI使用的集中领域。Tomlinson等（2025）同样使用匿名的微软Bing Copilot对话，将用户目标和AI行为分类为O*NET工作活动，并将这些分类汇总为职业层面的AI适用性评分。

这些指标对于识别哪些职业可能暴露于生成式AI方面具有重要价值。然而，大多数指标是在职业层面构建的，因此在同一职业内部是固定的，且在很大程度上不随时间变化。³ 这一特征限制了它们捕捉任务导向观本身一个重要含义的能力：如果企业在技术扩散过程中修订了工作岗位所需的任务，那么即使在同一职业内部，暴露度也未必保持不变。职业层面的指标可以事前识别暴露度，但无法观察雇主随后是否重写了工作要求、调整了技能需求或改变了其他方面相似工作岗位的任务内容。

我们通过构建动态的、招聘信息层面的生成式AI暴露度度量，从而摆脱了上述方法。以招聘信息作为分析单元，允许暴露度在不同招聘信息之间变化。

[脚注3] O*NET以五年滚动周期对职业进行重新调查；在调查波次之间，给定职业的任务画像保持不变。参见 https://www.onetcenter.org/dataUpdates.html#summary。

【本段术语】
- AI: 人工智能
- Generative AI: 生成式人工智能（生成式AI）
- GPT: 生成式预训练变换器（GPT）
- within-cell: 单元内
- posting-level: 招聘信息层面
- occupation-level: 职业层面
- LLM: 大语言模型
- O*NET: 美国职业信息网络（O*NET）
- NAICS: 北美行业分类系统
- Blinder decomposition: Blinder分解
- pre-GPT: GPT前时期
- post-GPT: GPT后时期
- three-fold: 三重分解
- common-support: 共同支持域
- remote-work: 远程工作
- full-time: 全职
- hiring reallocation: 招聘重新配置
- labor-demand: 劳动力需求
- level exposure: 暴露水平
- two-fold: 双重分解
- JSON: JSON（JavaScript对象表示法）
- Three-Fold: 三重分解
- two-digit: 两位数
- cross-sector: 跨部门
- entry-level: 入门级
- high-exposure: 高暴露
- labor demand: 劳动力需求
- labor-market: 劳动力市场
- posting-level measure: 招聘信息层面度量
- SSRN: 社会科学研究网络（SSRN）
- balanced-cell: 平衡单元
- Changes in Generative AI Exposure: 生成式AI暴露度变化
- job redesign: 工作重新设计
- Oaxaca-Blinder decomposition: Oaxaca-Blinder分解
- occupation-level exposure: 职业层面暴露度
- ONE: 待确认（原文未出现，可能为笔误）
- task-level: 任务层面
- two-stage: 两阶段
- within the same occupation: 同一职业内
- AI-exposed: 人工智能暴露
- ChatGPT: ChatGPT
- generative AI: 生成式人工智能

【本段要点】
- 传统AI暴露度研究基于任务框架，利用O*NET数据构建职业层面的暴露指标；生成式AI研究在此基础上进行了扩展。
- 近期研究通过评估LLM能力、使用合成调查或真实交互数据（如Claude.ai、Copilot会话）来构建暴露指标。
- 现有职业层面指标在职业内部固定且不随时间变化，无法捕捉技术扩散后企业修改任务内容导致的暴露度变动。
- 作者提出构建动态的、以招聘信息（posting）为分析单位的暴露度量，允许同一职业内不同招聘信息之间的暴露度存在差异。

【可能需人工复核】
- 术语表中“ONE”在原文中未出现，可能为误写（如“O*NET”之讹），需核对原文后确认。
- 部分术语（如“within-cell”、“balanced-cell”）虽在术语表中列出，但本段未直接出现，翻译时仅纳入但未使用，待后续章节验证。
- 脚注中O*NET调查周期原文为“five-year cycle”，译为“五年滚动周期”符合学术惯例，但需保持与原文一致。
