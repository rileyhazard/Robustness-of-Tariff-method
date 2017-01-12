# Poisoning

### Rule:
|  If the respondent says   
|    a poisoning led to the death   
|    which occurred less than 30 days before the death   
|    and the injury was unintentional   
|  SmartVA predicts 'Poisoning'   




### Applicable questions:
|            |                                          |                  |
|:-----------|:-----------------------------------------|-----------------:|
| a5_01_4 | Decedent suffered poisoning that led to his/her death | (N-Y-Ref-DK)* |
| a5_04 | How long did [name] survive after the injury? [days] | (# of days) |
| c4_47_4 | Decedent suffered poisoning that led to his/her death | (N-Y-Ref-DK)* |
| c4_49 | How long did [name] survive after the injury or accident? [days] | (# of days) |
| a5_02 | Was the injury or accident self-inflicted? | (N-Y-Ref-DK)* |
| a5_03 | Was the injury or accident intentionally inflicted by someone else? | (N-Y-Ref-DK)* |
| c4_48 | Was the injury or accident intentionally inflicted by someone else? | (N-Y-Ref-DK)* |

|  \* 0="No", 1="Yes", 8="Refused to answer", 9="Don't Know"   


### Logic Rule:

###### Adults:
~~~~~python
    poisoning = a5_01_4 == 1
    recent = a5_04 < 30
    unintentional = (a5_02 != 1) & (a5_03 != 1)

    return poisoning & recent & unintentional
~~~~~

###### Children:
~~~~~python
    poisoning = c4_47_4 == 1
    recent = c4_49 < 30
    unintentional = c4_48 != 1

    return poisoning & recent & unintentional
~~~~~
    

### Performance:
|             | PHMRC-Adult |  NHMRC-Adult |  PHMRC-Child |  NHMRC-Child |    
|:-----------:|:------------:|:------------:|:------------:|:------------:|   
| Endorsements| 11 |  28 |  16 |  16 |    
|  True CSMF  | 0.011 |  0.037 |  0.009 |  0.015 |    
| Sensitivity | 7.0 |  11.1 |  66.7 |  50.0 |    
| Specificity | 99.9 |  99.9 |  99.8 |  99.7 |    
|  Precision  | 54.5 |  85.7 |  75.0 |  75.0 |    
|   Accuracy  | 98.9 |  96.6 |  99.5 |  99.0 |    
|Cause-Specific CCC| 19.7 |  27.4 |  70.8 |  65.0 |    
|Cause-Specific CCC Change| 7.2 |  11.5 |  5.8 |  0.0 |    
|  Median CCC | 19.6 |  31.2 |  33.0 |  37.4 |    
|Median CCC Change| 0.2 |  0.0 |  0.0 |  0.0 |    
|CMSF Accuracy| 77.4 |  71.1 |  81.3 |  58.9 |    
|CMSF Accuracy Change| 0.0 |  0.3 |  0.0 |  0.0 |    
|CCCMSF Accuracy| 38.6 |  21.5 |  49.2 |  -11.8 |    
|CCCMSF Accuracy Change| 0.0 |  0.7 |  0.0 |  0.0 |    

|  \* not yet calculated   

\pagebreak
