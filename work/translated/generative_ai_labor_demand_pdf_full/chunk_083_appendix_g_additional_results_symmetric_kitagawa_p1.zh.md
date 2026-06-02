---
chunk_id: "chunk_083"
title: "Appendix G Additional Results: Symmetric Kitagawa Decompo-"
model: "deepseek-v4-flash"
source_file: "work/chunks/generative_ai_labor_demand_pdf_full/chunk_083_appendix_g_additional_results_symmetric_kitagawa_p1.md"
---
【中文译文】

# 附录 G 附加结果：对称Kitagawa分解与平衡单元样本

本附录报告两组额外的分解结果。首先，我们呈现基于对称双重Kitagawa分解（Kitagawa, 1955）的结果。其次，我们将样本限制为每个季度均被观测到的平衡工作单元，并在该平衡单元样本上重新估计分解。两种替代分解的结果均与我们的主要发现一致。

### G.1 对称双重Kitagawa分解

我们的主要规格使用了方程（8）中的三重反事实Kitagawa分解，它将总暴露度的整体变化分解为构成效应、单元内暴露效应和交互效应。作为替代方案，我们还考虑了对称双重Kitagawa分解（Kitagawa, 1955），该分解将交互效应等量地吸收到构成成分和单元内成分中。

设第t个季度的总暴露度为 \(\bar{E}_t = \sum_c w_{ct} E_{ct}\)，其中 \(w_{ct}\) 表示第t个季度单元c的职位发布份额，\(E_{ct}\) 表示该单元内的平均暴露度。使用2021年作为固定基准，对称双重分解可写为：

\[
\bar{E}_t - \bar{E}_0 = \sum_c (w_{ct} - w_{c,0}) \frac{E_{ct} + E_{c,0}}{2} + \sum_c (E_{ct} - E_{c,0}) \frac{w_{ct} + w_{c,0}}{2}
\]

| 构成效应 | 单元内暴露效应 |

与三重分解相比，这一公式通过将交互项等额分配给构成效应和单元内暴露效应，为总暴露度的变化提供了更简洁的两部分分解。然而，与三重规格不同，它无法单独捕捉交互效应——即当跨工作单元的重新配置与单元内暴露度变化同时发生时所产生的成分。

【本段术语】
- Kitagawa decomposition: 基塔加瓦分解
- within-cell: 单元内
- posting-level: 职位发布层面
- occupation-level: 职业层面
- balanced-cell: 平衡单元
- three-fold: 三重
- two-fold: 双重
- composition effect: 构成效应
- within-cell exposure effect: 单元内暴露效应
- interaction effect: 交互效应
- aggregate exposure: 总暴露度
- posting share: 职位发布份额
- counterfactual: 反事实
- symmetric: 对称的

【本段要点】
- 本附录报告两组额外分解结果：对称双重Kitagawa分解和基于平衡单元样本的分解。
- 主要规格使用三重分解，将总暴露度变化分为三个成分；对称双重分解将交互项等分给构成效应和单元内效应，形成更简洁的两部分分解。
- 对称双重分解无法单独识别交互效应，而三重分解可以。
- 两种替代分解的结果与主要发现一致。

【可能需人工复核】
- 术语“Kitagawa decomposition”在中文文献中常译为“基塔加瓦分解”或保留英文，此处采用中文音译，需确认是否符合学界惯例。
- “within-cell”译为“单元内”对应原文概念，但需注意该术语在论文中是否已有统一译法。
- “posting-level measure”等术语在术语表中待定，此处根据上下文译为“职位发布层面”，建议作者核实。
