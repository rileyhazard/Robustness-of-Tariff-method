# Hemorrhage

### Rule:
|  If the respondent says   
|    the decedent was female   
|    and was within the maternal age range   
|    and was pregnant or her period was late or giving birth or died within 6 weeks of delivery   
|    and had excessive bleeding during pregnancy or delivery   
|    and did not die during a prolonged delivery   
|    and did not have convulsions   
|  SmartVA predicts 'Hemorrhage'   
|    Which is currently grouped into 'Maternal' for reporting   


For deaths which involve excessive bleeding during prolonged labor, the underlying cause is obstructed labor and hemorrhage is a secondary condition.

### Applicable questions:
|            |                                          |                  |
|:-----------|:-----------------------------------------|-----------------:|
| g5_02 | What was the sex of the deceased? | (1="male", 2="female") |
| g5_04a | What was the last known age of the deceased? [years] | (# of years) |
| a3_10 | Was [name] pregnant at the time of death? | (N-Y-Ref-DK)* |
| a3_07 | At the time of death was her period overdue? | (N-Y-Ref-DK)* |
| a3_08 | For how many weeks was her period overdue? [days] | (# of days) |
| a3_12 | Did [name] die during an abortion? | (N-Y-Ref-DK)* |
| a3_15 | Did she die during labor or delivery? | (N-Y-Ref-DK)* |
| a3_17 | Did she die within 6 weeks after having an abortion? | (N-Y-Ref-DK)* |
| a3_18 | Did she die within 6 weeks of childbirth? | (N-Y-Ref-DK)* |
| a3_06 | Was there excessive vaginal bleeding in the week prior to death? | (N-Y-Ref-DK)* |
| a3_14 | Did she have excessive bleeding during labor or delivery? | (N-Y-Ref-DK)* |
| a3_19 | Did she have excessive bleeding after delivery or abortion? | (N-Y-Ref-DK)* |
| a3_13^1^ | Did bleeding occur while she was pregnant? | (N-Y-Ref-DK)* |
| a3_15^1^ | Did she die during labor or delivery? | (N-Y-Ref-DK)* |
| a3_16 | For how long was she in labor? [days] | (# of days) |
| a2_82 | Did [name] have convulsions? | (N-Y-Ref-DK)* |
| a1_01_8^1^ | Did Decedent Have Epilepsy? | (N-Y-Ref-DK)* |

|  \* 0="No", 1="Yes", 8="Refused to answer", 9="Don't Know"   
|  ^1^ This question is not currently being used in the rule   


### Logic Rule:

~~~~~python
    female = g5_02 == 2
    age = (g5_04a > 12) & (g5_04a <= 49)
    pregnant = a3_10 == 1
    overdue = (a3_07 == 1) & (a3_08 > 90)
    delivering = (a3_12 == 1) | (a3_15 == 1)
    excessive_bleeding = (a3_06 == 1) | (a3_14 == 1)
    not_prolonged = a3_16 < 1   #coded in days
    no_convulsions = (a2_82 != 1) & (a1_01_8 != 1)
    
    return female & age & (pregnant | overdue | delivering) &
        excessive_bleeding & not_prolonged & no_convulsion
~~~~~
    

### Performance:
|             | PHMRC-Hemorrhage^1^ |  NHMRC-Hemorrhage^1^ |  PHMRC-Maternal^2^ |  NHMRC-Maternal^2^ |    
|:-----------:|:------------:|:------------:|:------------:|:------------:|   
| Endorsements| 248 |  69 |  248 |  69 |    
|  True CSMF  | 0.015 |  0.0 |  0.06 |  0.017 |    
| Sensitivity | 34.2 |  ~ |  37.4 |  54.1 |    
| Specificity | 97.3 |  98.8 |  99.0 |  99.7 |    
|  Precision  | 15.7 |  0.0 |  70.6 |  76.8 |    
|   Accuracy  | 96.4 |  98.8 |  95.3 |  99.0 |    
|Cause-Specific CCC| 49.8 |  ~ |  81.7 |  87.4 |    
|Cause-Specific CCC Change| 21.5 |  ~ |  3.1 |  2.1 |    
|  Median CCC | 17.2 |  20.5 |  19.2 |  31.2 |    
|Median CCC Change| -1.0 |  0.0 |  -0.3 |  0.0 |    
|CMSF Accuracy| 71.2 |  71.8 |  77.1 |  70.8 |    
|CMSF Accuracy Change| -1.5 |  0.0 |  -0.3 |  -0.0 |    
|CCCMSF Accuracy| 21.6 |  23.3 |  37.8 |  20.7 |    
|CCCMSF Accuracy Change| -4.1 |  0.1 |  -0.8 |  -0.1 |    

|  ^1^ Performance at detecting 'Hemorrhage' vs any other cause   
|  ^2^ Performance at detecting any maternal cause vs non-maternal causes   
|  \* not yet calculated   
|  ^~^ This statistic is undefined for this sample   

\pagebreak
