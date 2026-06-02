---
chunk_id: "chunk_038"
title: "5.2 Three-Fold Kitagawa Decomposition"
model: "deepseek-v4-flash"
source_file: "work/chunks/generative_ai_labor_demand_pdf_full/chunk_038_5_2_three_fold_kitagawa_decomposition_p1.md"
---
【中文译文】
# 5.2 三重木场分解法

我们将总暴露度的变化分解为三个反事实成分：

X X X ∆E¯ = (w −w)E + w (E −E) + (w −w)(E −E). (8) t c, t c, 0 c, 0 c, 0 c, t c, 0 c, t c, 0 c, t c, 0 |c {z } |c {z } |c {z } 构成效应 单元内暴露度效应 交互效应

第一项是构成效应。它衡量如果招聘岗位份额从2021年的分布转变为时期t的分布，而每个单元内的暴露度保持在2021年水平不变，总暴露度将如何变化。实质上，这一项捕捉了跨职位单元的招聘再配置。正值表示招聘岗位正转向在基准期对生成式AI暴露度更高的单元。负值表示招聘岗位正远离这些暴露度较高的单元。

第二项是单元内暴露度效应。它衡量如果单元级暴露度从2021年水平转变为时期t水平，而招聘岗位份额保持在2021年分布不变，总暴露度将如何变化。实质上，这一项捕捉了同类职位内的职位重新设计。负值表示在保持基准招聘岗位分布不变的情况下，单元内描述的任务随时间推移对生成式AI的暴露度有所降低。正值表示单元内任务内容向更高暴露度方向移动。

第三项是交互效应。它捕捉因招聘岗位份额和单元内暴露度同时变动而产生的额外变化。这一项表明招聘再配置与职位重新设计是相互强化还是相互抵消。例如，当招聘岗位转向暴露度下降的单元，或远离暴露度上升的单元时，交互项为负。当两种变动共同推动总暴露度朝同一方向时，交互项为正。

这种三重分解公式在我们这里很有用，因为它分别识别了企业招聘地点的变化、同类职位内容的变化以及这两者的联合变动。经典的双重木场分解将交互项分配到构成效应和单元内成分中。我们在附录G中报告相应的双重分解结果。

【本段术语】
- Three-Fold Kitagawa Decomposition: 三重木场分解法
- composition effect: 构成效应
- within-cell exposure effect: 单元内暴露度效应
- interaction effect: 交互效应
- aggregate exposure: 总暴露度
- posting shares: 招聘岗位份额
- hiring reallocation: 招聘再配置
- job redesign: 职位重新设计
- two-fold: 双重
- Kitagawa decomposition: 木场分解
- generative AI: 生成式AI
- baseline period: 基准期
- within-cell: 单元内
- occupation-level: 职位级别（本段未直接出现但相关）
- task-level: 任务级别

【本段要点】
- 将总暴露度变化分解为三个反事实成分：构成效应、单元内暴露度效应和交互效应。
- 构成效应衡量岗位份额变化带来的影响，反映招聘再配置；正值表示转向高暴露度单元，负值反之。
- 单元内暴露度效应衡量单元级暴露度变化的影响，反映职位重新设计；负值表示任务暴露度降低，正值反之。
- 交互效应捕捉份额与暴露度同时变动的额外影响，表明招聘再配置与职位重新设计是相互强化还是抵消。
- 三重分解分别识别招聘地点变化、职位内容变化及其联合变动，优于将交互项分配至前两者的双重分解。

【可能需人工复核】
- 公式中的符号和下标（如 w_c, t 等）需要保持与原文一致，中文译文已保留原公式形式，但需确认数学表达式在Markdown中是否正确呈现。
- “Kitagawa decomposition”译为“木场分解”是否准确？通常为“木场分解”或“北川分解”，此处采用前者，需确认学界常用译法。
- “within-cell exposure”译为“单元内暴露度”，术语表中“within-cell”待定，此处暂译，需对照原文用法统一。
- “period-t”和“2021 level”等时间表述的准确性，注意原文中的下标0和t分别对应2021年和时期t。
- “job redesign”译为“职位重新设计”，与“job redesign within comparable jobs”对应，需确保上下文一致性。
