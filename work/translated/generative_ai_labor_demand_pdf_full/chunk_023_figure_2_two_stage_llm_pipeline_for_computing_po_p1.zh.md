---
chunk_id: "chunk_023"
title: "Figure 2: Two-Stage LLM Pipeline for Computing Posting-Level AI Exposure Indices"
model: "deepseek-v4-flash"
source_file: "work/chunks/generative_ai_labor_demand_pdf_full/chunk_023_figure_2_two_stage_llm_pipeline_for_computing_po_p1.md"
---
【中文译文】

# 图2：用于计算岗位级AI暴露指数的两阶段LLM流程

第一阶段将非结构化的岗位文本转化为结构化的岗位特定任务集。LLM接收由Lightcast提取的职位名称、职位描述以及专业技能和通用技能。模型被要求识别岗位描述中具体的工作活动，而非根据职业名称推断通用任务。这一区分至关重要，因为同一职业的两个岗位可能强调不同的职责、工具、交付物或工作情境。针对每个岗位，模型提取3到10项任务。同时，模型利用岗位的Lightcast技能形成语义相关的技能组，并保留专业技能与通用技能之间的区分。每项提取的任务精准匹配到一个技能组，这一匹配决定了该任务是与专业技能还是通用技能相关联。我们利用这一区分来分配任务重要性权重：与专业技能匹配的任务获得原始权重2，而与通用技能匹配的任务获得原始权重1。6 这种加权目的在于使与职业或角色特定技能要求相关的任务具有更大影响力，同时保留与通用职场技能相关的任务。

第二阶段：暴露分类。第二阶段对每项提取的任务进行生成式AI暴露分类。模型接收职位名称和第一阶段的任务列表，为每项任务分配一个来自集合{E0, E1, E2}的暴露标签。这些标签旨在反映当前可用的生成式AI工具能否在保持同等质量的前提下显著减少完成任务所需时间。遵循Eloundou等人（2024）的研究，我们将任务定义为暴露的，若生成式AI能以同等质量将完成时间减少至少50%。同等质量意味着接收或评估输出的第三方不会注意到或在意是否使用了生成式AI辅助。三个标签区分了不同程度的暴露。E0表示当前现成的生成式AI工具不太可能带来显著生产力提升、或使用此类工具会实质性降低输出质量的任务。E1表示可以直接由单个现成的生成式AI或LLM工具辅助的任务，无需特殊集成、微调或工作流重新设计。E2表示单独的工具可能不足，但通过薄层的AI驱动软件或工作流集成有望带来显著生产力提升的任务。表1总结了评分细则。

【本段术语】
- GPT: [待定]（原文未提供，此处保留英文）
- within-cell: [待定]
- posting-level: 岗位级
- occupation-level: [待定]
- LLM: [待定]（大型语言模型，暂保留英文）
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
- Three-Fold: [待定]
- two-digit: [待定]
- cross-sector: [待定]
- entry-level: [待定]
- high-exposure: [待定]
- labor demand: [待定]
- labor-market: [待定]
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
- generative AI: 生成式AI

【本段要点】
- 介绍了一个两阶段LLM流程，用于计算岗位级AI暴露指数。
- 第一阶段：从非结构化工单文本中提取结构化任务，区分专业与通用技能，并赋予权重（专业2，通用1）。
- 第二阶段：将每项任务分类为E0、E1或E2，基于当前生成式AI工具能否以同等质量减少至少50%完成时间。
- 强调了同一职业内不同岗位的差异，以及根据任务与技能的匹配来调整重要性权重。

【可能需人工复核】
- 术语表中所有[待定]项需根据论文语境及领域共识确定最终译名。
- 权重赋值部分（raw weight）是否应译为“原始权重”需确认，此处译为“原始权重”以避免歧义。
- “off-the-shelf”译为“现成的”是否准确？需结合AI工具市场语境确认。
- “thin AI-powered software layer”中“thin”译为“薄层的”是否恰当？可能需译为“轻量的”。
