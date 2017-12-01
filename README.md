# Tariff 2.0
This repo holds methods development for the Tariff 2.0. This work occurred after
the publication of the Tariff 2.0 method.

## What's Here
1. Validation framework and metrics for analyzing performance
2. Rewrite of Tariff 2.0 into python using primarily Pandas/Numpy. Currently
   this implementation is unrelated to the implementation in SmartVA which uses
   exclusively native python data structures
3. Backport of SmartVA add-on methods to be compatible with this implementation.
   This includes:
   * rule based predictions
   * Expert Tuning: censoring, required symptoms, spurious associations
4. Scripts for creating performance reports
5. Scripts for creating inputs for SmartVA, including:
    * Proportions used for redistributing undetermined causes
    * Tariff matrices

## How to run this code
#### Environment
This code uses Python 3.6. I love my py3.6 language features and nobody else is
around to complain about running my code. I'm making no attempt to maintain
compatibility with even py3.5. #thefutureisnow

There's a conda environment file that list the dependencies for this project. To
create a conda environment run:

```
conda env create -f=conda-environment.yml
```

or just `pip install stemming` into a conda environement with the anaconda
package.


#### Docs
We (ok I) use Google-style docstrings to document code. Docs can be built by
running `make html` from within the `./docs` directory. This require at least
sphinx 1.5, which has napoleon as a built in extension. #thefutureisnow

#### Tests
We (still just I) use pytest. Some of the test are regression tests against
data or files within the SmartVA repo. The default assumes the repo is in a
directory next to this repo. If this is not the case, use the `--smartva-repo`
option with the location of your smartva repo when running regression tests.
Otherwise, these will be skipped.

## Relevant literature
* [Tariff 1 methods paper](https://pophealthmetrics.biomedcentral.com/articles/10.1186/1478-7954-9-31):
  Initial development of the Tariff method.
* [Tariff 2 methods paper](https://bmcmedicine.biomedcentral.com/articles/10.1186/s12916-015-0527-9):
  Extension to the Tariff methods that added significance testing for tariffs,
  biological plausibility criteria, and thresholds for indeterminacy.
* [PHMRC Dataset paper](https://pophealthmetrics.biomedcentral.com/articles/10.1186/1478-7954-9-27):
  Study design for the validation dataset including feature selection and cause of death selection.
* [Shortened Instrument Paper](https://bmcmedicine.biomedcentral.com/articles/10.1186/s12916-015-0528-8):
  Exploration of a smaller set of symptoms, most importantly to the use of a
  short checklist of words instead processing the entire open response text.
* [Robust Metrics paper](https://pophealthmetrics.biomedcentral.com/articles/10.1186/1478-7954-9-28):
  Defense of the validation framework and metrics used to measure performance.
* [CCCSMF paper](https://pophealthmetrics.biomedcentral.com/articles/10.1186/s12963-015-0061-1):
  Chance correction of the CSMF  accuracy measure.

### Relationship to other repos in this project
This code contains pieces of previous work from other repos in the VA project.

Processing of NHMRC data originally occurred in:
* https://stash.ihme.washington.edu/projects/VA/repos/nhmrc_mapping/browse

Processing of PHMRC data from the GHDx originally occurred in:
* https://stash.ihme.washington.edu/projects/VA/repos/smartva_testing/browse

Initially development of tariff as an sklearn classifier object occurred in:
* https://stash.ihme.washington.edu/projects/VA/repos/insilicova/browse

Development of logic rules originally occurred in:
* https://stash.ihme.washington.edu/projects/VA/repos/business_rules/browse

Development of estimating tariffs using hierarchical causes originally occurred in:
* https://stash.ihme.washington.edu/projects/VA/repos/hierarchical_causes/browse

Visualizing misclassification originally occurred in:
* https://stash.ihme.washington.edu/projects/VA/repos/confusion_matrix/browse
