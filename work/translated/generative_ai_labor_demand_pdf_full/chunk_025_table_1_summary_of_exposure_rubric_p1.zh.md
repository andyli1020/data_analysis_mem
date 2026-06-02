---
chunk_id: "chunk_025"
title: "Table 1: Summary of Exposure Rubric"
model: "deepseek-v4-flash"
source_file: "work/chunks/generative_ai_labor_demand_pdf_full/chunk_025_table_1_summary_of_exposure_rubric_p1.md"
---
【中文译文】
# 表1：暴露分级标准摘要

无暴露（E0）如果：
• 单个现成的生成式AI或LLM工具无法在保持同等质量的情况下，将完成任务所需时间减少至少50%；或者使用此类工具会显著降低输出质量。

直接暴露（E1）如果：
• 单个现成的生成式AI或LLM工具（无需特殊集成或微调）能够在保持同等质量的情况下，将完成任务所需时间减少至少50%。

间接暴露（E2）如果：
• 单个现成的生成式AI或LLM工具本身无法将完成任务所需时间减少至少50%；但
• 在此类工具基础上构建的、基于人工智能的轻量级软件层，有可能在保持同等质量的情况下实现至少50%的时间缩减。

权重。遵循Eloundou等人（2024）的逻辑，他们在职业层面赋予核心任务比补充任务更高的权重，我们赋予与专业技能相关联的任务更高的权重。具体而言，与专业技能相匹配的任务的原始权重为2，而与通用技能相匹配的任务的原始权重为1。这种加权方案反映了以下理念：专业技能任务对于招聘信息中角色特定内容更为核心，而通用技能任务则涵盖更广泛的一般性工作活动。表2通过两个招聘信息示例说明了这一映射关系，并展示了如何将任务层面的暴露标签汇总到招聘信息层面。形式上，假设招聘信息p包含任务j = 1, ..., J。令raw_p,j表示任务j的原始权重：
   若任务j匹配到专业技能组，则raw_p,j = 2；
   若任务j匹配到通用技能组，则raw_p,j = 1。
我们在每个招聘信息内部对这些原始权重进行归一化：
   w_p,j = raw_p,j / Σ_{k=1}^{J_p} raw_p,k，使得 Σ_{j=1}^{J_p} w_p,j = 1。
令 I_{p,j}^{(k)} 为指示变量，如果招聘信息p中的任务j被分类为暴露等级E_k，则取值为1，否则为0。

【本段术语】
- generative AI: [待定]
- LLM: [待定]
- direct exposure: [待定]
- indirect exposure: [待定]
- core tasks: [待定]
- supplemental tasks: [待定]
- specialized skills: [待定]
- common skills: [待定]
- raw weight: [待定]
- posting-level: [待定]
- task-level: [待定]
- occupation-level: [待定]
- within the same occupation: [待定]
- exposure rubric: [待定]
- off-the-shelf: [待定]
- fine-tuning: [待定]
- thin AI-powered software layer: [待定]
- time reduction: [待定]
- equivalent quality: [待定]
- indicator: [待定]
- exposure tier: [待定]

【本段要点】
- 表1定义了三种暴露等级：无暴露（E0）、直接暴露（E1）、间接暴露（E2），分别基于生成式AI或LLM工具能否减少至少50%完成任务时间并维持质量。
- 权重分配：与专业技能匹配的任务原始权重为2，与通用技能匹配的任务原始权重为1，反映任务对招聘信息角色的核心程度。
- 权重归一化：在每个招聘信息内部将原始权重归一化，使权重之和为1。
- 任务级暴露标签通过加权汇总到招聘信息级别。

【可能需人工复核】
- 术语表中未提供“generative AI”“LLM”等术语的指定中文译法，需由领域专家确认。
- “thin AI-powered software layer”的翻译“基于人工智能的轻量级软件层”是否准确表达“thin”的含义（指轻量、薄层）需确认。
- 公式部分的中文表述需确保与原始数学符号一致，避免歧义。
