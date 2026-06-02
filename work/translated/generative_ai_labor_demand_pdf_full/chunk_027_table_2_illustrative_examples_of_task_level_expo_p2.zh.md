---
chunk_id: "chunk_027"
title: "Table 2: Illustrative Examples of Task-Level Exposure Classification"
model: "deepseek-v4-flash"
source_file: "work/chunks/generative_ai_labor_demand_pdf_full/chunk_027_table_2_illustrative_examples_of_task_level_expo_p2.md"
---
【中文译文】

# 表2：任务级暴露分类的说明性示例

其中 k ∈ {0, 1, 2}。我们将招聘岗位 p 在暴露层级 E 中的任务内容的加权份额定义为：
$$
\text{share}^E_{k,p} = \sum_{j=1}^{J_p} w_{p,j} \cdot \mathbb{I}(\text{任务 } j \text{ 属于层级 } k)
$$
因此，\(\text{share}^E_{0,p}\)、\(\text{share}^E_{1,p}\) 和 \(\text{share}^E_{2,p}\) 分别表示无暴露、直接暴露和间接暴露任务内容的加权份额。由于每个任务恰好被分配到一个暴露层级，且任务权重之和为1，这些份额满足：
$$
\text{share}^E_{0,p} + \text{share}^E_{1,p} + \text{share}^E_{2,p} = 1.
$$

利用这些份额，我们构建了三个 posting-level 暴露指标：
\[
\alpha_p = \text{share}^E_{1,p}, \tag{2}
\]
\[
\beta_p = \text{share}^E_{1,p} + 0.5 \cdot \text{share}^E_{2,p}, \tag{3}
\]
\[
\gamma_p = \text{share}^E_{1,p} + \text{share}^E_{2,p}. \tag{4}
\]

第一个指标 \(\alpha_p\) 仅计算直接暴露的任务，可被解释为一种保守的下界暴露度量。第二个指标 \(\beta_p\) 完全计入直接暴露的任务，并对间接暴露的任务赋予0.5的权重。这是我们的主要度量。第三个指标 \(\gamma_p\) 完全计入直接和间接暴露的任务，可被解释为上界暴露度量。我们使用 \(\beta_p\) 作为主要暴露指数，因为它捕捉了即时暴露与更依赖实施的暴露之间的区别。被分类为 E1 的任务可以借助现成的生成式 AI 工具完成，几乎不需要额外的组织变革。被分类为 E2 的任务也是暴露的，但其暴露不那么直接，因为有意义的生产力提升很可能需要配套软件、工作流集成或组织采用。因此，对 E2 赋予部分权重反映了这样一种观点：间接暴露在经济上有意义，但不如 E1 直接。这种方法与区分直接和间接生成式 AI 暴露的先前研究一致（Eloundou et al., 2024; Brynjolfsson et al., 2025a; Chen et al., 2025）。

生成的指数 \(\beta_p\) 取值范围为0到1。值为0表示招聘岗位中所有加权任务都被分类为无暴露。值为1表示所有加权任务均为直接暴露。中间值则捕捉了岗位中无暴露、直接暴露和间接暴露任务的加权混合。由于 \(\beta_p\) 是根据特定招聘岗位的任务构建的，因此它可以在同一职业内的不同岗位之间以及随时间变化。这一特征对于我们的分解分析至关重要：总体暴露的变化可能反映了岗位在职业间分布的变动，也可能反映了同类岗位任务构成的变化。

【本段术语】
- posting-level: [待定]
- task-level: [待定]
- exposure tier: 暴露层级
- weighted share: 加权份额
- conservative lower-bound measure: 保守下界度量
- upper-bound measure: 上界度量
- direct exposure: 直接暴露
- indirect exposure: 间接暴露
- immediate exposure: 即时暴露
- implementation-dependent exposure: 依赖实施的暴露
- off-the-shelf generative AI tools: 现成的生成式AI工具
- organizational change: 组织变革
- workflow integration: 工作流集成
- organizational adoption: 组织采用
- partial weight: 部分权重
- within the same occupation: [待定]
- decomposition analysis: 分解分析
- aggregate exposure: 总体暴露
- distribution of postings: 岗位分布
- task composition: 任务构成
- comparable postings: 同类岗位

【本段要点】
- 定义了三个暴露层级（0、1、2），并给出任务内容加权份额的公式。
- 利用加权份额构建三个 posting-level 暴露指数：α（仅直接暴露）、β（直接暴露加0.5倍间接暴露，为主要指数）、γ（直接加间接暴露，上界）。
- 解释β作为主要指数的理由：区分即时暴露（E1，可直接用现成AI）与依赖实施的暴露（E2，需要配套改变），对E2赋半权重体现经济意义但非直接。
- β取值范围0~1，可跨相同职业内不同岗位及时间变化，这对分解分析很重要：总体暴露变化可源于岗位分布变化或同类岗位任务构成变化。

【可能需人工复核】
- 公式中的下标和符号可能需要确认是否与原文一致（原文可能有排版问题）。
- 术语表中部分术语为[待定]，翻译中保留了英文，但需确认是否统一使用术语表名称。
- 原文中“shareE_k, p”的表示在翻译中已调整，注意核对。
