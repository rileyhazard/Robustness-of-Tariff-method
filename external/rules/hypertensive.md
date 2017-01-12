# Hypertensive Disorder

### Rule:
|  If the respondent says   
|    the decedent was female   
|    and was within the maternal age range   
|    and was pregnant or her period was late   
|    and had convulsions or mentioned epilepsy   
|  SmartVA predicts 'Hypertensive Disorder'   
|    Which is currently grouped into 'Maternal' for reporting   


In many settings, interviewees confuse epilepsy and convulsions. Any mention of epilepsy likely indicates the decedent had convulsions. Convulsion during pregnancy is a cardinal symptom which clearly distinguish hypertensive disorders from any other subtype of maternal death.

### Applicable questions:
|            |                                          |                  |
|:-----------|:-----------------------------------------|-----------------:|
| g5_02 | What was the sex of the deceased? | (1="male", 2="female") |
| g5_04a | What was the last known age of the deceased? [years] | (# of years) |
| a3_10 | Was [name] pregnant at the time of death? | (N-Y-Ref-DK)* |
| a3_07 | At the time of death was her period overdue? | (N-Y-Ref-DK)* |
| a3_08 | For how many weeks was her period overdue? [days] | (# of days) |
| a2_82 | Did [name] have convulsions? | (N-Y-Ref-DK)* |
| a1_01_8^1^ | Did Decedent Have Epilepsy? | (N-Y-Ref-DK)* |

|  \* 0="No", 1="Yes", 8="Refused to answer", 9="Don't Know"   
|  ^1^ This question is part of the Health Care Experience module   


### Logic Rule:

~~~~~python
    female = g5_02 == 2
    age = (g5_04a > 12) & (g5_04a <= 49)
    pregnant = a3_10 == 1
    overdue = (a3_07 == 1) & (a3_08 > 90)
    convulsions = a2_82 == 1
    epilepsy = a1_01_8 == 1
    
    return female & age & (pregnant | overdue) & (convulsions | epilepsy) 
~~~~~
    

### Performance:
|             | PHMRC-Hypertensive^1^ |  NHMRC-Hypertensive^1^ |  PHMRC-Maternal^2^ |  NHMRC-Maternal^2^ |    
|:-----------:|:------------:|:------------:|:------------:|:------------:|   
| Endorsements| 17 |  0 |  17 |  0 |    
|  True CSMF  | 0.014 |  0.0 |  0.06 |  0.017 |    
| Sensitivity | 10.1 |  ~ |  3.6 |  0.0 |    
| Specificity | 99.9 |  100.0 |  100.0 |  100.0 |    
|  Precision  | 64.7 |  ~ |  100.0 |  ~ |    
|   Accuracy  | 98.7 |  100.0 |  94.2 |  98.3 |    
|Cause-Specific CCC| 19.3 |  ~ |  79.1 |  85.3 |    
|Cause-Specific CCC Change| 7.5 |  ~ |  0.4 |  0.0 |    
|  Median CCC | 19.3 |  20.5 |  19.5 |  31.2 |    
|Median CCC Change| 1.0 |  0.0 |  0.0 |  0.0 |    
|CMSF Accuracy| 72.8 |  71.7 |  77.4 |  70.9 |    
|CMSF Accuracy Change| 0.1 |  0.0 |  0.0 |  0.0 |    
|CCCMSF Accuracy| 26.0 |  23.2 |  38.6 |  20.8 |    
|CCCMSF Accuracy Change| 0.3 |  0.0 |  0.1 |  0.0 |    

|  ^1^ Performance at detecting 'Hypertensive Disorder' vs any other cause   
|  ^2^ Performance at detecting any maternal cause vs non-maternal causes   
|  \* not yet calculated   
|  ^~^ This statistic is undefined for this sample   

\pagebreak
