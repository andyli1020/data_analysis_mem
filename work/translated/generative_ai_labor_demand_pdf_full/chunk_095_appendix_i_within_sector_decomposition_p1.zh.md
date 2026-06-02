---
chunk_id: "chunk_095"
title: "Appendix I Within-Sector Decomposition"
model: "deepseek-v4-flash"
source_file: "work/chunks/generative_ai_labor_demand_pdf_full/chunk_095_appendix_i_within_sector_decomposition_p1.md"
---
【中文译文】
# 附录 I 部门内分解

一个担忧是，总体暴露度的变化可能部分反映的是部门层面的劳动力需求周期，而非对生成式人工智能的调整。这一担忧在2022年之后的时期尤为相关，当时货币紧缩可能通过融资成本、资本支出和需求条件的变化影响了跨部门的招聘活动。遵循 Iscenko 和 Millet (2026) 的逻辑，此类宏观经济冲击最可能通过部门层面的招聘转移来影响总体招聘发布的构成。例如，如果更高的利率减少了信息、金融或专业服务等对利率更敏感部门的招聘，而这些部门的生成式人工智能基线暴露度也较高，那么总体构成效应可能部分捕捉的是跨部门重新配置，而非与人工智能相关的调整。为解决这一担忧，我们实施了分解的部门内版本。具体而言，我们分别在每个两位数 NAICS 部门内运行分解，仅利用同一部门内不同职位单元格之间的变异。然后，我们使用固定的基准部门权重来汇总特定部门的分解成分。这一过程移除了跨部门重新配置作为变异来源：部门相对规模随时间的变化不再机械地贡献于总体分解。相反，这些估计捕捉的是：部门内职位-资历单元格之间的招聘转移是否发生，以及这些单元格内部的暴露度是否有变化。其识别逻辑是，在给定部门条件下，部门层面的宏观经济冲击被吸收为该部门招聘发布的共同背景冲击。例如，如果更高的利率使金融行业的总招聘减少20%，这一部门层面的收缩会影响金融领域招聘发布的数量，但本身并不会导致金融招聘发布在职位-资历单元格之间的相对构成发生变化。因此，部门内分解要问的是：在移除了利率冲击最可能影响总体暴露度的跨部门渠道之后，同样的调整模式是否仍然存在。

【本段术语】
- within-sector: 部门内
- two-digit NAICS: 两位数 NAICS
- job cells: 职位单元格
- occupation-seniority cells: 职位-资历单元格
- cross-sector: 跨部门
- aggregate exposure: 总体暴露度
- generative AI: 生成式人工智能
- hiring reallocation: 招聘重新配置
- labor-demand: 劳动力需求
- posting-level: 岗位发布层面
- occupation-level: 职业层面
- task-level: 任务层面
- GPT: [待定]
- LLM: [待定]
- O*NET: [待定]
- Oaxaca-Blinder decomposition: [待定]
- Blinder decomposition: [待定]
- pre-GPT: [待定]
- post-GPT: [待定]
- common-support: [待定]
- remote-work: [待定]
- full-time: [待定]
- level exposure: [待定]
- two-fold: [待定]
- three-fold: [待定]
- JSON: [待定]
- Three-Fold: [待定]
- entry-level: [待定]
- high-exposure: [待定]
- labor-market: [待定]
- posting-level measure: [待定]
- SSRN: [待定]
- balanced-cell: [待定]
- Changes in Generative AI Exposure: [待定]
- job redesign: [待定]
- ONE: [待定]
- two-stage: [待定]
- within the same occupation: [待定]
- AI-exposed: [待定]
- ChatGPT: [待定]

【本段要点】
- 指出总体暴露度变化可能受部门层面劳动力需求周期（如货币紧缩）影响，而非单纯由生成式AI调整所致。
- 引用 Iscenko 和 Millet (2026) 的逻辑，说明宏观经济冲击通过部门招聘转移影响总体招聘发布构成。
- 为排除跨部门重新配置的干扰，实施了“部门内分解”：在每个两位数 NAICS 部门内分别运行分解，仅利用部门内职位单元格间的变异，并使用固定部门权重汇总。
- 该分解移除了部门相对规模变化的机械影响，专注于捕捉部门内职位-资历单元格间的招聘转移和暴露度变化。
- 识别逻辑：在部门条件下，部门层面的宏观经济冲击被视为共同背景冲击，不影响部门内招聘发布的相对构成。

【可能需人工复核】
- 术语翻译：术语表中多数术语标记为[待定]（如 GPT、LLM、O*NET、Oaxaca-Blinder decomposition 等），此处直接保留英文，需根据后续上下文或领域惯例确定中文译名。
- “postings”在本文中译为“招聘发布”，但需确认是否始终一致；亦可考虑“岗位发布”或“招聘信息”。
- “occupation-seniority cells”译为“职位-资历单元格”，需确保与原文“occupation-seniority cells”对应，且与正文中“job cells”一致。
- “aggregate exposure”统一译为“总体暴露度”，可能需根据全文风格微调。
