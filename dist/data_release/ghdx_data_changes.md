GHDx Changelog
==============

### Free Text
* The word "pox" was mistranslated in the original survey. All occurrences of
  the pox have been recoded to the word "rash"

### Injuries
* The question about injuries elicited responses about many injuries not related
  to the terminal illness. The published analyses only considered observations
  in which the injury occurred less than 30 days before the death. The survey
  instrument has been corrected to ask only about injuries related to the death.
  Endorsement of injuries which occurred more than 30 days before the death have
  been removed from the dataset to prevent further confusion.

### Age Recoding
* newid 3138 and 7459 in the adult module list age in the days column instead of
  the years columns. These are data entry errors from data collection and have
  been recoded. Calculating the age from the accompanying birth date and death
  date corroborates the age.

* newid 954, 1301, and 1329 in the child module list age values in the year
  columns which are between 12 and 20. The age calculated from the reported
  birth date and death date gives ages between 1 and 2 years. These are likely
  data entry errors and the value has been moved to the months column. None of
  the age in months exactly match the reported value, however, many records show
  discrepancies between the age calculated from dates and the age reported.

* newid 545, 1192, 1377, 2152 in the neonate module list age values of less than
  28 in either the year or the months columns instead of the days column. These
  are data entry errors from data collection and have been recoded. Calculating
  age from the accompanying birth date and death dates corroborates the age.

* newid 1372 in the child module lists the age as 28 days. The age calculated
  from the dates is 29 days. The value has been corrected so that the
  observation is correctly classified as a child and the symptoms and gold
  standard diagnosis match child data.

* newid 2062 in the child module lists the age as 28 days in all fields. This
  observation has been dropped because the symptoms and gold standard diagnosis
  do not match neonate data.
