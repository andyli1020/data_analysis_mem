After the two-stage annotation is complete, we aggregate task-level exposure labels into postinglevel exposure measures. The objective is to summarize, for each vacancy, the extent to which the tasks described in the posting are exposed to generative AI. This posting-level aggregation is important because our analysis treats the job posting, rather than the occupation, as the basic unit at which employers describe labor demand. Each extracted task is matched in Stage 1 to either a specialized-skill group or a common-skill group based on the posting’s Lightcast skills. We use this distinction to assign task-importance

[Footnote 6] Thespecialized/commondistinctionisassignedthroughthetask–skill-groupmatchratherthanthroughadirect



task classification. The Stage 1 prompt groups Lightcast-provided specialized and common skills separately and assigns each extracted task to the closest skill group, as shown in Appendix A. Tasks matched to specialized-skill groupsaretreatedasspecialized-skilltasks; tasksmatchedtocommon-skillgroupsaretreatedascommon-skilltasks. In ties, the prompt gives priority to specialized-skill groups.
