# Falls

### Rule:
|  If the respondent says   
|    a fall led to the death   
|    which occurred less than 30 days before the death   
|    and the injury was unintentional   
|  SmartVA predicts 'Falls'   




### Applicable questions:
|            |                                          |                  |
|:-----------|:-----------------------------------------|-----------------:|
| a5_01_2 | Decedent suffered fall that led to his/her death | (N-Y-Ref-DK)* |
| a5_04 | How long did [name] survive after the injury? [days] | (# of days) |
| c4_47_2 | Decedent suffered fall that led to his/her death | (N-Y-Ref-DK)* |
| c4_49 | How long did [name] survive after the injury or accident? [days] | (# of days) |
| a5_02 | Was the injury or accident self-inflicted? | (N-Y-Ref-DK)* |
| a5_03 | Was the injury or accident intentionally inflicted by someone else? | (N-Y-Ref-DK)* |
| c4_48 | Was the injury or accident intentionally inflicted by someone else? | (N-Y-Ref-DK)* |

|  \* 0="No", 1="Yes", 8="Refused to answer", 9="Don't Know"   


### Logic Rule:

###### Adults:
~~~~~python
    fall = a5_01_2 == 1
    recent = a5_04 < 30
    unintentional = (a5_02 != 1) & (a5_03 != 1)

    return fall & recent & unintentional
~~~~~

###### Children:
~~~~~python
    fall = c4_47_2 == 1
    recent = c4_49 < 30
    unintentional = c4_48 != 1

    return fall & recent & unintentional
~~~~~
    

### Performance:
|             | PHMRC-Adult |  NHMRC-Adult |  PHMRC-Child |  NHMRC-Child |    
|:-----------:|:------------:|:------------:|:------------:|:------------:|   
| Endorsements| 251 |  157 |  68 |  44 |    
|  True CSMF  | 0.022 |  0.028 |  0.024 |  0.025 |    
| Sensitivity | 40.5 |  58.5 |  63.3 |  90.0 |    
| Specificity | 97.6 |  98.9 |  98.2 |  99.5 |    
|  Precision  | 27.9 |  61.1 |  45.6 |  81.8 |    
|   Accuracy  | 96.4 |  97.8 |  97.3 |  99.2 |    
|Cause-Specific CCC| 40.4 |  57.2 |  65.7 |  100.0 |    
|Cause-Specific CCC Change| 36.9 |  52.8 |  19.3 |  10.5 |    
|  Median CCC | 19.6 |  32.7 |  33.0 |  37.4 |    
|Median CCC Change| 0.2 |  1.4 |  0.0 |  0.0 |    
|CMSF Accuracy| 77.6 |  71.1 |  80.0 |  58.9 |    
|CMSF Accuracy Change| 0.2 |  0.3 |  -1.3 |  0.0 |    
|CCCMSF Accuracy| 39.0 |  21.5 |  45.7 |  -11.8 |    
|CCCMSF Accuracy Change| 0.5 |  0.7 |  -3.5 |  0.0 |    

|  \* not yet calculated   

\pagebreak
