---
chunk_id: "chunk_039"
title: "5.3 Common Support and Robustness of the Decomposition"
model: "deepseek-v4-flash"
source_file: "work/chunks/generative_ai_labor_demand_pdf_full/chunk_039_5_3_common_support_and_robustness_of_the_decompo_p1.md"
---
【中文译文】

# 5.3 共同支撑与分解的稳健性

观测到的单元格集合会随时间变化。某些职业-资历-行业单元格可能在基期出现，但在后续时期消失，反之亦然。为确保分解比较的是可比的单元格，我们将基年与时期 t 之间的时期特定共同支撑定义为 S = {c: w_{c,0} > 0 且 w_{c,t} > 0}。单元格 c 在 2021 年和时期 t 中均被观测到。在应用分解之前，我们在该共同支撑样本中重新标准化职位发布份额。这种方法将分析聚焦于持续性职位单元格的变化，而非机械地将变化归因于单元格的进入或退出。由于重新标准化后的共同支撑总量与原始总量并不相同，

【本段术语】
- common-support: [待定]
- occupation-by-seniority-by-industry cells: [待定]
- baseline: [待定]
- posting shares: [待定]
- decomposition: [待定]
- re-normalize: [待定]
- aggregate: [待定]

【本段要点】
- 单元格集合可能随时间变化，导致某些单元格仅在特定时期存在。
- 定义共同支撑集 S，仅包含基年和目标时期 t 均出现的单元格。
- 在共同支撑样本中对职位发布份额重新标准化，再执行分解。
- 此方法聚焦于持续性岗位的变化，避免将变化机械归因于单元格的进出。
- 重新标准化后的总量与原总量不同，需注意该差异。

【可能需人工复核】
- 术语“occupation-by-seniority-by-industry cells”中的“cells”在上下文中指“单元格”，但中文表达可考虑“单元”或“格子”，此处按学术惯例译为“单元格”。
- 公式符号 w_{c,0} 和 w_{c,t} 的下标在原文中可能带逗号，翻译时保留其数学意义。
- 最后一句未完成，但译文按原文结构处理，保留“并不相同”的省略感。
