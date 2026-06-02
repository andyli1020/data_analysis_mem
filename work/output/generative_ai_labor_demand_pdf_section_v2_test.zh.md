# Front Matter

生成式人工智能与劳动力需求的重组
方岩王∗，魏再彦，杨王
普渡大学丹尼尔斯商学院；西拉斐特，印第安纳州47907
wang6123@purdue.edu；zaiyan@purdue.edu；yangwang@purdue.edu
2026年5月

# Abstract

生成式人工智能（AI）有望改变工作方式，但随着该技术的普及，企业如何重新组织劳动力需求仍鲜为人知。现有研究主要关注哪些职业暴露于AI，或者暴露的工作岗位是否会减少。我们通过考察企业是否通过改变招聘地点、工作内容或两者兼施来调整，从而拓展了这一讨论。利用覆盖美国全国经济各部门的职位发布数据集，我们通过一个两阶段的大语言模型流水线，构建了一个动态的、基于职位发布的生成式AI暴露度测量指标。该流水线识别每则职位发布中描述的任务，并分类生成式AI能够执行或辅助这些任务的程度。然后，我们将总暴露度的变化分解为两个维度：跨岗位的需求重新分配与岗位内任务的重新设计。我们记录了三个主要发现。第一，生成式AI暴露度是动态而非固定的，会随时间大幅变化。第二，劳动力需求通过这两个维度进行调整。招聘重新分配解释了总暴露度下降的最大份额，平均占52%；而岗位内重新设计的重要性日益增强，占39.5%。补充的Oaxaca–Blinder分解表明，职业构成的转变解释了可归因于可观测岗位特征的暴露度变化中约90%的部分。第三，不同职位阶梯的调整存在差异。高级职位调整更早且主要通过重新分配，而初级职位则通过重新分配、重新设计及其交互作用的更广泛组合来调整。这些发现表明，劳动力市场对生成式AI的调整是一个组织重构的过程，在此过程中，企业既重塑招聘需求，也重塑工作的任务架构。

## Keywords: Generative AI; Labor demand; Job ladder; Dynamic AI exposure; Job postings;

招聘再配置；岗位再设计；组织重构 ∗Zaiyan Wei 对 David and Margaret Crow Rising Star 教授职位的资助表示感谢，王阳衷心感谢普渡大学 Mitch Daniels 商学院的财务支持。我们感谢 Lina Rivas 出色的研究协助。我们也感谢特拉华大学研讨会参与者的宝贵意见与建议。所有分析及报告的结果均已接受审查，确保未披露任何机密信息。任何错误均由我们承担。

yaM

]NG. noce[

[脚注 1] v95132. 5062: viXra

# 1 Introduction

# 2 Related Literature

## 2.1 AI and Generative AI Exposure Metrics

## 2.2 Effects of Generative AI in the Labor Market

## 3.1 Lightcast Job Postings Data

## 3.2 Sampling Strategy

# 4 Measurement of Posting-Level Exposure to Generative AI

### Figure 1: Quarterly Number of Job Postings in the U. S. Population and Our Sample

## 4.1 Two-Stage LLM Pipeline

### Figure 2: Two-Stage LLM Pipeline for Computing Posting-Level AI Exposure Indices

## 4.2 From Task-Level Labels to Posting-Level Exposure

### Table 1: Summary of Exposure Rubric

### Table 2: Illustrative Examples of Task-Level Exposure Classification

## Appendix D shows that the time-series patterns of α , β , and γ are similar. This suggests

## 4.3 Descriptive Patterns

### Table 3 reports summary statistics for the posting-level exposure measures overall and by job

### Table 3: Summary Statistics of Posting-Level Generative AI Exposure

### Figure 3: Quarterly Trend in Mean Generative AI Exposure (β)

### Figure 4: Changes in Generative AI Exposure by Occupation Group

## Appendix D further splits these occupation groups by seniority. The broad tercile pattern

### Figure 5: Sector-Level Mean Generative AI Exposure (β) by Two-Digit NAICS Industry Code

# 5 Decomposition of Generative AI Exposure: Methods

## 5.1 Cell-Level Representation of Aggregate Exposure

## 5.2 Three-Fold Kitagawa Decomposition

## 5.3 Common Support and Robustness of the Decomposition

## Appendix F reports overlap diagnostics, reconstruction checks, and the gap between the raw and

## 5.4 Oaxaca–Blinder Decomposition

# 6 Results

### Figure 6 presents the three-fold Kitagawa decomposition of changes in mean exposure relative to

### Figure 6: Three-Fold Decomposition of Changes in Aggregate Generative AI Exposure

### Table 4 summarizes the relative importance of the three components from Q3 of 2023 onward.

### Table 4: Relative Contributions in the Three-Fold Kitagawa Decomposition Since Q3 of 2023

## 6.2 Heterogeneity Across the Job Ladder

### Figure 9: Three-Fold Decomposition of Changes in Generative AI Exposure: Senior Jobs

## 6.3 Robustness to Cross-Sector Reallocation

## 6.4 Oaxaca–Blinder Decomposition: Observable Sources of the Exposure Gap

### Table 5 reports the weighted Oaxaca–Blinder decomposition for the full sample and separately

### Table 5: Weighted Oaxaca–Blinder Decomposition of Aggregate Exposure: Pre- vs. Post-GPT

### Figure 10 decomposes the explained component into contributions from observed job-characteristic

### Figure 10: Explained Component by Observed Job-Characteristic Block: Pre-GPT vs. Post-GPT

## 6.6 Observable Sources of the Exposure Gap by Seniority

### Figure 13: Explained Component by Observed Job-Characteristic Block for Senior Jobs

# 7 Conclusions

## Appendix A Full Annotation Prompts

## Appendix B Comparison with Eloundou et al. (2024)

### Figure B2 summarizes these two additional dimensions directly. Panel (a) plots, for each occu-

### Figure B1: Comparison with the Occupation-Level Exposure Measure in Eloundou et al. (2024)

### Figure B2: Additional Heterogeneity Captured by the Posting-Based Measure

### Table C1: Sector-Level Average Generative AI Exposure (β) by Two-Digit NAICS Code

### Figure D5 report the quarterly trends in the alternative exposure indices α and γ. Figure D6

### Figure D3: Quarterly Trends in E0, E1, and E2 Shares

### Figure D4: Quarterly Trend in Exposure Measure α

### Figure D5: Quarterly Trend in Exposure Measure γ

### Figure D6: Changes in Generative AI Exposure by Occupation Group and Job Seniority

## Appendix E Occupations with the Highest and Lowest Exposure

### Table E2 presents the ten occupations with the highest and lowest average exposure across the full

### Table E2: Top and Bottom Occupations by Generative AI Exposure

## Appendix F Common Support and Renormalization

### Table F3 reports diagnostic results for the renormalized common-support decomposition used in

### Table F3: Diagnostic Decomposition Results under Renormalized Common Support

## Appendix G Additional Results: Symmetric Kitagawa Decompo-

### Figure G7 reports the results from the symmetric two-fold decomposition. The pattern is

### Figure G7: Symmetric Two-Fold Kitagawa Decomposition of Changes in Aggregate Exposure

### Figure G8 presents the results based on the balanced-cell sample. The results remain consistent

## Appendix H Additional decomposition evidence

### Figure H9 plots observed aggregate generative AI exposure together with two counterfactual paths.

### Figure H9: Aggregate Generative AI Exposure over Time and Counterfactual Paths

### figure complements the main decomposition by showing the relative importance of each margin

### Figure H10: Relative Contribution of Decomposition Components

### Figure H11 summarizes the average quarterly contribution of these four cases. The figure

### Figure H12 decomposes the interaction term for junior postings by the sign of changes in hiring

### Figure H12: Average Quarterly Contribution to The Interaction Term by Sign Pattern: Junior

## Appendix I Within-Sector Decomposition

## Appendix Figure I13 reports the results. The overall pattern is highly similar to the baseline

### Figure I13: Within-Sector Decomposition of Changes in Generative AI Exposure
