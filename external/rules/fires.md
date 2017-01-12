# Fires

### Rule:
|  If the respondent says   
|    a burn led to the death   
|    which occurred less than 30 days before the death   
|    and the injury was unintentional   
|  SmartVA predicts 'Fires'   




### Applicable questions:
|            |                                          |                  |
|:-----------|:-----------------------------------------|-----------------:|
| a5_01_6 | Decedent suffered burn that led to his/her death | (N-Y-Ref-DK)* |
| a5_04 | How long did [name] survive after the injury? [days] | (# of days) |
| c4_47_6 | Decedent suffered burn/fire that led to his/her death | (N-Y-Ref-DK)* |
| c4_49 | How long did [name] survive after the injury or accident? [days] | (# of days) |
| a5_02 | Was the injury or accident self-inflicted? | (N-Y-Ref-DK)* |
| a5_03 | Was the injury or accident intentionally inflicted by someone else? | (N-Y-Ref-DK)* |
| c4_48 | Was the injury or accident intentionally inflicted by someone else? | (N-Y-Ref-DK)* |

|  \* 0="No", 1="Yes", 8="Refused to answer", 9="Don't Know"   


### Logic Rule:

###### Adults:
~~~~~python
    burn = a5_01_6 == 1
    recent = a5_04 < 30
    unintentional = (a5_02 != 1) & (a5_03 != 1)

    return burn & recent & unintentional
~~~~~

###### Children:
~~~~~python
    burn = c4_47_6 == 1
    recent = c4_49 < 30
    unintentional = c4_48 != 1

    return burn & recent & unintentional
~~~~~
    

### Performance:
|             | PHMRC-Adult |  NHMRC-Adult |  PHMRC-Child |  NHMRC-Child |    
|:-----------:|:------------:|:------------:|:------------:|:------------:|   
| Endorsements| 76 |  35 |  50 |  16 |    
|  True CSMF  | 0.016 |  0.006 |  0.033 |  0.008 |    
| Sensitivity | 37.7 |  77.8 |  64.7 |  100.0 |    
| Specificity | 99.6 |  99.9 |  99.7 |  99.7 |    
|  Precision  | 60.5 |  80.0 |  88.0 |  75.0 |    
|   Accuracy  | 98.6 |  99.7 |  98.5 |  99.7 |    
|Cause-Specific CCC| 37.5 |  77.1 |  70.7 |  100.0 |    
|Cause-Specific CCC Change| 35.5 |  80.2 |  7.7 |  0.0 |    
|  Median CCC | 20.2 |  32.7 |  33.0 |  37.4 |    
|Median CCC Change| 0.7 |  1.4 |  0.0 |  0.0 |    
|CMSF Accuracy| 77.8 |  70.7 |  81.3 |  58.9 |    
|CMSF Accuracy Change| 0.4 |  -0.2 |  0.0 |  0.0 |    
|CCCMSF Accuracy| 39.7 |  20.4 |  49.3 |  -11.8 |    
|CCCMSF Accuracy Change| 1.1 |  -0.4 |  0.1 |  0.0 |    

|  \* not yet calculated   

\pagebreak
