Metrics
=======

Individual-Level Metrics
------------------------
These metrics are used to determine the accuracy of the individual predictions.
Chance-corrected concordance (CCC) is the metric recommended by Murray et al for
assessing performance at the individual level. McCormick et al also report
sensitivity and specificity by cause in the supplemental material.

.. autofunction:: tariff2.metrics.calc_ccc

.. autofunction:: tariff2.metrics.calc_sensitivity

.. autofunction:: tariff2.metrics.calc_specificity

.. autofunction:: tariff2.metrics.calc_positive_predictive_value

.. autofunction:: tariff2.metrics.calc_negative_predictive_value

.. autofunction:: tariff2.metrics.calc_specific_accuracy

.. autofunction:: tariff2.metrics.calc_overall_correctness

Aggregating Cause-Specific metrics
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
Most individual-level metrics are cause-specific. Many applications will be
concerned with a single overall measure of performance at the individual-level.
Murray et explore three methods for aggregating cause-specific metrics to a
single summary measure:

1. weight by the true cause distribution - this would be biased by any
   correlation between the individual-level predictions and the population-level
   predictions.
2. weight by a standardized distribution, such as the global distribution of
   causes of death - this would requires studies to include collectively
   exhaustive list of causes, possible by including an "all other" category,
   or to rescale weights to cause list.
3. use equal weights.

.. autofunction:: tariff2.metrics.agg_cause_specific_metrics

.. autofunction:: tariff2.metrics.calc_mean_ccc

.. autofunction:: tariff2.metrics.calc_median_ccc

Population-Level Metrics
------------------------
These metrics are used to determine the accuracy of the predicted cause
distribution. Some verbal autopsy classification methods only estimate a
cause distribution without generating individual-level predictions. other
methods, like InSilicoVA, predict the cause distribution in a manner slightly
decoupled from the individual-level predictions. Population-level accuracy
is most important for applications such as generating national or subnational
estimates of cause-of-death for vital statistics and health information
systems.

.. autofunction:: tariff2.metrics.calc_csmf_accuracy_from_csmf

.. autofunction:: tariff2.metrics.correct_csmf_accuracy

.. autofunction:: tariff2.metrics.calc_csmf_accuracy

.. autofunction:: tariff2.metrics.calc_cccsmf_accuracy

.. autofunction:: tariff2.metrics.calc_cccsmf_accuracy_from_csmf
