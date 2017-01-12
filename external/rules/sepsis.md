# Sepsis

### Rule:
|  If the respondent says   
|    the decedent was female   
|    and was within the maternal age range   
|    and died within six weeks of an abortionor had given birth within the last six weeks   
|    and had a lower belly pain   
|    and had a fever   
|    and had offensive vaginal discharge   
|  SmartVA predicts 'Sepsis'   
|    Which is currently grouped into 'Maternal' for reporting   


One key symptom for this rule is not included on the short-form instrument.

### Applicable questions:
|            |                                          |                  |
|:-----------|:-----------------------------------------|-----------------:|
| g5_02 | What was the sex of the deceased? | (1="male", 2="female") |
| g5_04a | What was the last known age of the deceased? [years] | (# of years) |
| a3_17 | Did she die within 6 weeks after having an abortion? | (N-Y-Ref-DK)* |
| a3_18 | Did she die within 6 weeks of childbirth? | (N-Y-Ref-DK)* |
| a3_09 | Did [name] have a sharp pain in the belly shortly before death? | (N-Y-Ref-DK)* |
| a2_61 | Did [name] have belly pain? | (N-Y-Ref-DK)* |
| a2_63_1 | Was the pain in the upper or lower belly? | (1="Upper belly", 2="Lower belly", 8="Refused to answer", 9="Don't Know") |
| a2_63_2 | Was the pain in the upper or lower belly? | (1="Upper belly", 2="Lower belly", 8="Refused to answer", 9="Don't Know") |
| a2_02 | Did [name] have a fever? | (N-Y-Ref-DK)* |
| a3_20^1^ | Did [name] have bad smelling vaginal discharge within 6 weeks after delivery or labor? | (N-Y-Ref-DK)* |

|  \* 0="No", 1="Yes", 8="Refused to answer", 9="Don't Know"   
|  ^1^ This question is not on the shortened questionnaire   


### Logic Rule:

~~~~~python
    female = g5_02 == 2
    age = (g5_04a > 12) & (g5_04a <= 49)
    abortion = a3_17 == 1
    postpartum = a3_18 == 1
    lower_belly_pain = a2_61 == 1 & (a2_63_1 == 2) | (a2_63_2 == 2)
    fever = a2_02 == 1
    discharge = a3_20 == 1
    sepsis_symptoms = fever & lower_belly_pain & discharge
    
    return female & age & (abortion | (postpartum & sepsis_symptoms))
~~~~~
    

### Performance:
|             | PHMRC-Sepsis^1^ |  NHMRC-Sepsis^1^ |  PHMRC-Maternal^2^ |  NHMRC-Maternal^2^ |    
|:-----------:|:------------:|:------------:|:------------:|:------------:|   
| Endorsements| 48 |  48 |  48 |  48 |    
|  True CSMF  | 0.009 |  0.0 |  0.06 |  0.017 |    
| Sensitivity | 16.9 |  ~ |  8.1 |  38.8 |    
| Specificity | 99.5 |  99.2 |  99.9 |  99.8 |    
|  Precision  | 25.0 |  0.0 |  79.2 |  79.2 |    
|   Accuracy  | 98.8 |  99.2 |  94.4 |  98.8 |    
|Cause-Specific CCC| 66.9 |  ~ |  79.1 |  87.4 |    
|Cause-Specific CCC Change| 4.3 |  ~ |  0.4 |  2.1 |    
|  Median CCC | 18.3 |  20.5 |  19.5 |  31.2 |    
|Median CCC Change| 0.0 |  0.0 |  0.0 |  0.0 |    
|CMSF Accuracy| 72.6 |  71.7 |  77.4 |  70.8 |    
|CMSF Accuracy Change| -0.1 |  -0.0 |  0.0 |  -0.0 |    
|CCCMSF Accuracy| 25.6 |  23.2 |  38.6 |  20.7 |    
|CCCMSF Accuracy Change| -0.1 |  -0.0 |  0.0 |  -0.1 |    

|  ^1^ Performance at detecting 'Sepsis' vs any other cause   
|  ^2^ Performance at detecting any maternal cause vs non-maternal causes   
|  \* not yet calculated   
|  ^~^ This statistic is undefined for this sample   

\pagebreak
