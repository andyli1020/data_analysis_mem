---
chunk_id: "chunk_018"
title: "3.2 Sampling Strategy"
model: "deepseek-v4-flash"
source_file: "work/chunks/generative_ai_labor_demand_pdf_full/chunk_018_3_2_sampling_strategy_p1.md"
---
【中文译文】
# 3.2 抽样策略

我们的抽样策略基于原始数据的规模以及测量方法对计算资源的需求。在研究期间（2021年1月至2025年6月），原始Lightcast数据包含超过1.88亿条美国职位发帖。由于我们的暴露度测量需要将两阶段大型语言模型流程应用于职位发帖文本，处理整个语料库在计算上不可行。因此，我们采用一种重复随机抽样程序，旨在保留与研究设计核心相关的关键异质性来源：职业、行业、资历和时间。我们在由三个维度定义的单元内进行抽样。第一个维度是职业，使用O*NET职业代码进行测量。职业是自然的起点，因为现有生成式AI暴露度文献大多在职业或职业-任务层面测量暴露度（Eloundou等，2024；Brynjolfsson等，2025a）。这也可能捕捉到工作任务内容以及生成式AI潜在适用性的广泛差异。第二个维度是行业，使用两位NAICS代码进行测量。即使在同一个职业内，不同行业的工作可能涉及不同任务。例如，数据分析师、营销专家或软件开发人员可能因雇主所属行业（金融、医疗、制造、零售或专业服务）而从事不同活动。将行业纳入抽样设计有助于保留这种跨部门异质性，并使我们能够区分整体经济的劳动力需求调整与特定部门集中的变化。第三个维度是资历，使用Lightcast的职位资历分类进行测量。资历对我们的分析至关重要，因为近期研究和公众讨论提出了生成式AI可能对初级和高级职位产生不同影响的可能性（Hampole等，2025；Brynjolfsson等，2025a）。现有研究通常将相同的职业层面暴露度分数分配给所有。

【本段术语】
- exposure measurerequiresapplyingatwo-stagelargelanguagemodelpipelinetojobpostingtext: [待定]
- repeated random sampling: [待定]
- within cells defined by three dimensions: [待定]
- O*NET: [待定]
- NAICS: [待定]
- seniority: [待定]
- task-level: [待定]
- occupation-level: [待定]
- generative AI: [待定]
- occupation-task level: [待定]

【本段要点】
- 抽样策略的动机：原始数据规模巨大且测量方法计算成本高。
- 采用重复随机抽样，保留职业、行业、资历和时间四个异质性来源。
- 抽样单元由三个维度定义：职业（O*NET代码）、行业（两位NAICS代码）、资历（Lightcast分类）。
- 职业维度是基础，反映生成式AI暴露度的文献传统；行业维度捕捉同职业内不同行业的任务差异；资历维度回应近期对AI影响不同级别职位的关注。
- 现有研究常对所有职位分配相同职业层面暴露度分数，本抽样旨在改进。

【可能需人工复核】
- “exposure measurerequiresapplyingatwo-stagelargelanguagemodelpipelinetojobpostingtext” 中单词连写，原文可能为 "exposure measure requires applying a two-stage large language model pipeline to job posting text"，翻译时已按意调整。
- “from changes concentrated in particular sectors” 中“concentrated”译为“集中”可保留原意，但需确认上下文。
- “O*NET occupation code” 和 “O*NET” 术语表中为 [待定]，保留英文。
- “two-digit NAICS code” 中“two-digit”术语表未单独列，但“NAICS”为[待定]。
- “Lightcast’s job seniority classification” 中“Lightcast”无对应术语，保留。
- 最后一句“assign the same occupation-level exposure score to all” 后文未完整，翻译时按原文截断处理。
