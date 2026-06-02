---
chunk_id: "chunk_024"
title: "4.2 From Task-Level Labels to Posting-Level Exposure"
model: "deepseek-v4-flash"
source_file: "work/chunks/generative_ai_labor_demand_pdf_full/chunk_024_4_2_from_task_level_labels_to_posting_level_expo_p1.md"
---
【中文译文】
# 4.2 从任务级标签到职位发布级暴露

在两阶段标注完成后，我们将任务级暴露标签聚合为职位发布级的暴露度量。其目标是针对每个职位空缺，总结该职位描述中所列任务受生成式AI影响的程度。这一职位发布级的聚合之所以重要，是因为我们的分析将职位发布（而非职业）视为雇主描述劳动力需求的基本单位。每个被提取的任务在第一阶段根据发布内容中的Lightcast技能被匹配到专门技能组或通用技能组。我们利用这一区分来分配任务重要性[脚注6：专门/通用的区分是通过任务-技能组匹配而非直接的任务分类实现的。第一阶段提示将Lightcast提供的专门技能和通用技能分别分组，并将每个提取的任务分配到最接近的技能组，如附录A所示。匹配到专门技能组的任务被视为专门技能任务；匹配到通用技能组的任务被视为通用技能任务。在平局情况下，提示优先选择专门技能组。]。

【本段术语】
- posting-level: [待定]
- occupation: [待定]
- labor demand: [待定]
- O*NET: [待定]
- NAICS: [待定]
- Blinder decomposition: [待定]
- pre-GPT: [待定]
- post-GPT: [待定]
- three-fold: [待定]
- common-support: [待定]
- remote-work: [待定]
- full-time: [待定]
- hiring reallocation: [待定]
- labor-demand: [待定]
- level exposure: [待定]
- two-fold: [待定]
- JSON: [待定]
- Two-Fold: [待定]
- two-digit: [待定]
- cross-sector: [待定]
- entry-level: [待定]
- high-exposure: [待定]
- labor market: [待定]
- posting-level measure: [待定]
- SSRN: [待定]
- balanced-cell: [待定]
- Changes in Generative AI Exposure: [待定]
- job redesign: [待定]
- Oaxaca-Blinder decomposition: [待定]
- occupation-level exposure: [待定]
- ONE: [待定]
- task-level: [待定]
- two-stage: [待定]
- within the same occupation: [待定]
- AI-exposed: [待定]
- ChatGPT: [待定]
- generative AI: [待定]
- posting-level: [待定]
- occupation: [待定]
- labor demand: [待定]
- task-level: [待定]

【本段要点】
- 两阶段标注完成后，需进行任务级暴露标签到职位发布级暴露度量的聚合。
- 聚合目标是总结每个职位空缺中任务受生成式AI影响的整体程度。
- 职位发布（而非职业）是分析雇主劳动力需求的基本单位。
- 每个提取的任务根据Lightcast技能匹配到专门技能组或通用技能组，据此分配任务重要性。
- 脚注说明：专门/通用区分基于任务-技能组匹配，而非直接分类；匹配规则优先专门技能组。

【可能需人工复核】
- 术语表中所有术语均标注为[待定]，需根据上下文和领域惯例确定最终译法。
- “posting-level”在术语表中存在两次，可统一处理。
- 脚注6中的内容需确保与正文逻辑衔接自然，原文脚注标记为[Footnote 6]，译文保留脚注格式。
