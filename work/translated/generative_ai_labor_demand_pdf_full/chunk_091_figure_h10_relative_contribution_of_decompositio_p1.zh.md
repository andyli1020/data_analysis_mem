---
chunk_id: "chunk_091"
title: "Figure H10: Relative Contribution of Decomposition Components"
model: "deepseek-v4-flash"
source_file: "work/chunks/generative_ai_labor_demand_pdf_full/chunk_091_figure_h10_relative_contribution_of_decompositio_p1.md"
---
【中文译文】
# 图H10：分解成分的相对贡献

注释：对于每个季度，该图报告了每个分解成分在绝对值上的百分比贡献。一个成分的贡献定义为其绝对值除以该季度中构成效应、单元格内暴露效应及交互效应的绝对值之和。季度从2022年第一季度开始，因为分解是基于2021年全年基线定义的。

## H.3 解构交互项

三重分解分离出一个交互项，该交互项捕捉了招聘份额与单元格内暴露的联合变动。对于单元格c，交互贡献由下式给出：交互项 = Δw_c × Δβ_c，其中Δw_c表示单元格c相对于基线的职位发布份额变化，Δβ_c表示该单元格内暴露的变化。这一交互项可能源于四种符号组合。第一，当Δw_c < 0且Δβ_c > 0时，招聘在暴露上升的单元格中下降；这产生负的交互贡献。第二，当Δw_c > 0且Δβ_c < 0时，招聘在暴露下降的单元格中上升；这也产生负的交互贡献。第三，当Δw_c > 0且Δβ_c > 0时，招聘在暴露同时上升的单元格中上升；这产生正的交互贡献。第四，当Δw_c < 0且Δβ_c < 0时，招聘在暴露同时下降的单元格中下降；这也产生正的交互贡献。

【本段术语】
- decomposition：分解
- component：成分
- absolute value：绝对值
- composition effect：构成效应
- within-cell exposure effect：单元格内暴露效应
- interaction effect：交互效应
- three-fold decomposition：三重分解
- interaction term：交互项
- hiring share：招聘份额
- within-cell exposure：单元格内暴露
- cell：单元格
- posting share：职位发布份额
- exposure：暴露

【本段要点】
- 图H10展示每个季度各分解成分（构成效应、单元格内暴露效应、交互效应）的绝对贡献百分比，基线为2021年全年。
- 三重分解中的交互项捕捉招聘份额与单元格内暴露的联合变动，由Δw_c × Δβ_c计算。
- 四种符号组合产生正负交互贡献：招聘与暴露反向变动时交互项为负，同向变动时交互项为正。

【可能需人工复核】
- “posting share”译为“职位发布份额”，需确认是否与上下文一致（如“职位发布”是否涵盖所有招聘帖子）。
- “within-cell exposure effect”译为“单元格内暴露效应”，其中“单元格”可能需根据具体实证分析语境调整为“分组”或“类别”。
- 术语表中“within-cell”、“posting-level”、“occupation-level”等术语未给定中文，此处按学术惯例翻译，建议作者根据研究背景统一。
