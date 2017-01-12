# Bite of Venomous Animal

### Rule:
|  If the respondent says   
|    a bite from a venomous animal led to the death   
|    which occurred less than 30 days before the death   
|    and the injury was unintentional   
|  SmartVA predicts 'Bite of Venomous Animal'   




### Applicable questions:
|            |                                          |                  |
|:-----------|:-----------------------------------------|-----------------:|
| a5_01_5 | Decedent suffered bite/sting that led to his/her death | (N-Y-Ref-DK)* |
| a5_04 | How long did [name] survive after the injury? [days] | (# of days) |
| c4_47_5 | Decedent suffered bite/sting that led to his/her death | (N-Y-Ref-DK)* |
| c4_49 | How long did [name] survive after the injury or accident? [days] | (# of days) |
| a5_02 | Was the injury or accident self-inflicted? | (N-Y-Ref-DK)* |
| a5_03 | Was the injury or accident intentionally inflicted by someone else? | (N-Y-Ref-DK)* |
| c4_48 | Was the injury or accident intentionally inflicted by someone else? | (N-Y-Ref-DK)* |

|  \* 0="No", 1="Yes", 8="Refused to answer", 9="Don't Know"   


### Logic Rule:

###### Adults:
~~~~~python
    bite = a5_01_5 == 1
    recent = a5_04 < 30
    unintentional = (a5_02 != 1) & (a5_03 != 1)

    return bite & recent & unintentional
~~~~~

###### Children:
~~~~~python
    bite = c4_47_5 == 1
    recent = c4_49 < 30
    unintentional = c4_48 != 1

    return bite & recent & unintentional
~~~~~
    

### Performance:
|             | PHMRC-Adult |  NHMRC-Adult |  PHMRC-Child |  NHMRC-Child |    
|:-----------:|:------------:|:------------:|:------------:|:------------:|   
| Endorsements| 49 |  15 |  58 |  13 |    
|  True CSMF  | 0.008 |  0.002 |  0.026 |  0.005 |    
| Sensitivity | 47.0 |  100.0 |  92.6 |  100.0 |    
| Specificity | 99.8 |  99.9 |  99.6 |  99.7 |    
|  Precision  | 63.3 |  80.0 |  86.2 |  61.5 |    
|   Accuracy  | 99.3 |  99.9 |  99.4 |  99.7 |    
|Cause-Specific CCC| 71.9 |  100.0 |  94.2 |  100.0 |    
|Cause-Specific CCC Change| 31.2 |  34.4 |  3.9 |  0.0 |    
|  Median CCC | 19.5 |  31.2 |  33.0 |  37.4 |    
|Median CCC Change| 0.0 |  0.0 |  0.0 |  0.0 |    
|CMSF Accuracy| 77.6 |  70.9 |  81.2 |  58.7 |    
|CMSF Accuracy Change| 0.2 |  -0.0 |  -0.1 |  -0.2 |    
|CCCMSF Accuracy| 39.1 |  20.8 |  48.9 |  -12.3 |    
|CCCMSF Accuracy Change| 0.5 |  -0.0 |  -0.3 |  -0.5 |    

|  \* not yet calculated   

\pagebreak
