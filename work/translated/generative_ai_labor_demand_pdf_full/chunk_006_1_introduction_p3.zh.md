---
chunk_id: "chunk_006"
title: "1 Introduction"
model: "deepseek-v4-flash"
source_file: "work/chunks/generative_ai_labor_demand_pdf_full/chunk_006_1_introduction_p3.md"
---
【中文译文】
# 1 引言

行业单元格，最终得到9,373,092条招聘信息。这种全国覆盖至关重要，因为生成式AI的相关性取决于工作的任务内容，而任务内容在不同职业、行业和资历层级之间各不相同。因此，基于选定行业或职业的研究可能仅捕捉到劳动力市场调整的一部分。通过覆盖美国整体经济，我们的数据能够考察劳动力市场不同部分的变化如何共同形成劳动力需求重组的总体模式。我们利用一个两阶段大型语言模型流水线构建了一个动态的、职位发布层面的生成式AI暴露度量。在第一阶段，我们从每个职位描述中提取任务，并将这些任务与技能组（专业或通用）相匹配。在第二阶段，我们根据当前的生成式AI工具能否在同等质量下大幅减少完成该任务所需的时间，对每项任务进行分类。然后，我们将任务层面的标签聚合为职位发布层面的暴露指数。这种设计将先前暴露度量的基于任务的逻辑适应到了企业实际描述职位空缺的层面，使得暴露度在同一职业内部、不同行业和资历层级之间，以及随着企业修订职位内容的时间推移而有所不同。随后，我们使用两种互补的分解方法来分离调整的边际。第一种是Kitagawa分解的三重扩展（Kitagawa, 1955）。我们将总的生成式AI暴露视为职业-by-行业-by-资历单元格中暴露的加权平均值。总暴露可能因企业改变其发布的岗位组合、类似岗位的任务内容随时间变化、或这两种调整同时发生而改变。我们将这些成分解释为招聘再配置、岗位再设计及其交互作用。第二种方法是加权Oaxaca–Blinder分解，比较GPT前和GPT后时期（Oaxaca, 1973; Oaxaca and Sierminska, 2025）。这种基于回归的分解使我们能够考察哪些可观测的职位特征（尤其是职业、行业、资历、地点、远程工作状态、实习状态和雇佣类型）解释了暴露度的构成性变化。分析得出三个主要发现。首先，已发布岗位中的生成式AI暴露是动态的。平均暴露度在2022年初上升，2023年间下降，此后部分恢复。这种模式难以与“暴露是职业的固定属性”这一观点相协调；相反，它表明企业陈述的任务要求随时间演变。暴露度下降尤其集中于高暴露职业，而低暴露和中暴露职业则……（原文至此中断）

【本段术语】
- industry cells: 行业单元格
- posting-level measure: 职位发布层面的度量
- generative AI exposure: 生成式AI暴露度
- two-stage large language model (LLM) pipeline: 两阶段大型语言模型流水线
- task-level labels: 任务层面的标签
- Kitagawa decomposition: Kitagawa分解（北川分解）
- hiring reallocation: 招聘再配置
- job redesign: 岗位再设计
- Oaxaca–Blinder decomposition: Oaxaca–Blinder分解
- pre-GPT / post-GPT: GPT前/后时期
- high-exposure occupations: 高暴露职业
- composition change: 构成性变化

【本段要点】
- 研究的数据来源：覆盖美国经济全行业的9,373,092条招聘信息，确保结论的普适性。
- 构建动态职位发布层面生成式AI暴露度的方法：两阶段LLM流水线（任务提取与匹配 → 任务级分类 → 聚合为职位级指数），允许暴露度在同一职业内部（跨行业、资历、时间）变化。
- 两种互补的分解方法：三重Kitagawa分解（区分招聘再配置、岗位再设计及交互效应）和加权Oaxaca–Blinder分解（分析可观测特征对暴露度构成变化的影响）。
- 三个主要发现的核心：生成式AI暴露度随时间动态变化（2022初上升→2023下降→部分恢复），且暴露度下降主要集中于高暴露职业，质疑了“暴露度是职业固定属性”的观点。

【可能需人工复核】
- “within the same occupation”译为“同一职业内部”，术语表中虽列出但未定，此处根据上下文处理。
- “three-fold extension of the Kitagawa decomposition”中的“three-fold”译为“三重”，需确认是否与“Two-fold”等术语保持一致性（术语表中列出“Three-Fold”和“two-fold”均为[待定]）。
- “occupation-by-industry-by-seniority cells”译为“职业-by-行业-by-资历单元格”，原文为“occupationby-industry-by-seniority”可能为笔误，按“occupation-by-industry-by-seniority”理解。
- 末尾原文截断，翻译时保留原样并注明。
