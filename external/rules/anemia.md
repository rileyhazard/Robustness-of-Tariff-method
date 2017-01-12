# Anemia

### Rule:
|  If the respondent says   
|    the decedent was female   
|    and was within the maternal age range   
|    and was pregnant or had given birth within the last six weeks   
|    and looked pale   
|    and had fast or difficult breathing   
|    and did not die during labor or delivery   
|    and did not have excessive bleeding during pregnancy   
|  SmartVA predicts 'Anemia'   
|    Which is currently grouped into 'Maternal' for reporting   


Anemia is a risk factor for hemorrhage. For deaths which occur during labor or delivery, the underlying cause is hemorrhage and anemia is a secondary condition. Multiple symptoms for this rule are not included on the short-form instrument.

### Applicable questions:
|            |                                          |                  |
|:-----------|:-----------------------------------------|-----------------:|
| g5_02 | What was the sex of the deceased? | (1="male", 2="female") |
| g5_04a | What was the last known age of the deceased? [years] | (# of years) |
| a3_10 | Was [name] pregnant at the time of death? | (N-Y-Ref-DK)* |
| a3_07 | At the time of death was her period overdue? | (N-Y-Ref-DK)* |
| a3_08 | For how many weeks was her period overdue? [days] | (# of days) |
| a3_15 | Did she die during labor or delivery? | (N-Y-Ref-DK)* |
| a3_17 | Did she die within 6 weeks after having an abortion? | (N-Y-Ref-DK)* |
| a3_18 | Did she die within 6 weeks of childbirth? | (N-Y-Ref-DK)* |
| a2_20^1,3^ | Did [name] look pale? | (N-Y-Ref-DK)* |
| a2_36 | Did [name] have difficulty breathing? | (N-Y-Ref-DK)* |
| a2_40^1^ | Did [name] have fast breathing? | (N-Y-Ref-DK)* |
| a2_42^1^ | Did [name] wheeze? | (N-Y-Ref-DK)* |
| a2_43 | Did [name] experience pain in the chest in the month preceding death? | (N-Y-Ref-DK)* |
| a2_69^1^ | Did [name] have headaches? | (N-Y-Ref-DK)* |
| a2_45^1,2^ | Was the pain during physical activity? | (N-Y-Ref-DK)* |
| a2_46a^1,2^ | Where was the pain located? | (N-Y-Ref-DK)* |
| a3_06 | Was there excessive vaginal bleeding in the week prior to death? | (N-Y-Ref-DK)* |
| a3_14 | Did she have excessive bleeding during labor or delivery? | (N-Y-Ref-DK)* |

|  \* 0="No", 1="Yes", 8="Refused to answer", 9="Don't Know"   
|  ^1^ This question is not on the shortened questionnaire   
|  ^2^ This question is not currently being used in the rule   
|  ^3^ This is the most important symptom for diagnosis anemia, but it is extremely difficult to detect during a VAI   


### Logic Rule:

~~~~~python
    female = g5_02 == 2
    age = (g5_04a > 12) & (g5_04a <= 49)
    pregnant = a3_10 == 1
    overdue = (a3_07 == 1) & (a3_08 > 90)
    postpartum = (a3_17 == 1) | (a3_18 == 1)
    palor = a2_20 == 1
    breathing = (a2_36 == 1) | (a2_40 == 1)
    not_hemorrhage = (a3_06 != 1) & (a3_14 != 1)
    not_delivering = a3_15 != 1
    not_prolonged_labor = a3_16 < 1 # coded in days
    exclusions = not_hemorrhage & not_delivering & not_prolonged_labor
    
    return female & age & (pregnant | overdue | postpartum) &
        palor & breathing & exclusions
~~~~~
    

### Performance:
|             | PHMRC-Anemia^1^ |  NHMRC-Anemia^1^ |  PHMRC-Maternal^2^ |  NHMRC-Maternal^2^ |    
|:-----------:|:------------:|:------------:|:------------:|:------------:|   
| Endorsements| 3 |  1 |  3 |  1 |    
|  True CSMF  | 0.009 |  0.0 |  0.06 |  0.017 |    
| Sensitivity | 0.0 |  ~ |  0.2 |  1.0 |    
| Specificity | 100.0 |  100.0 |  100.0 |  100.0 |    
|  Precision  | 0.0 |  0.0 |  33.3 |  100.0 |    
|   Accuracy  | 99.1 |  100.0 |  94.0 |  98.3 |    
|Cause-Specific CCC| 17.3 |  ~ |  78.6 |  85.3 |    
|Cause-Specific CCC Change| 0.0 |  ~ |  0.0 |  0.0 |    
|  Median CCC | 18.3 |  20.5 |  19.5 |  31.2 |    
|Median CCC Change| 0.0 |  0.0 |  0.0 |  0.0 |    
|CMSF Accuracy| 72.7 |  71.7 |  77.4 |  70.9 |    
|CMSF Accuracy Change| 0.0 |  0.0 |  0.0 |  0.0 |    
|CCCMSF Accuracy| 25.8 |  23.2 |  38.6 |  20.8 |    
|CCCMSF Accuracy Change| 0.0 |  0.0 |  0.0 |  0.0 |    

|  ^1^ Performance at detecting 'Anemia' vs any other cause   
|  ^2^ Performance at detecting any maternal cause vs non-maternal causes   
|  \* not yet calculated   
|  ^~^ This statistic is undefined for this sample   

\pagebreak
