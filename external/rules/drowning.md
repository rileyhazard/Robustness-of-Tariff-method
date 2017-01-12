# Drowning

### Rule:
|  If the respondent says   
|    the decedent drowned   
|    and the injury was unintentional   
|  SmartVA predicts 'Drowning'   




### Applicable questions:
|            |                                          |                  |
|:-----------|:-----------------------------------------|-----------------:|
| a5_01_3 | Decedent suffered drowning that led to his/her death | (N-Y-Ref-DK)* |
| c4_47_3 | Decedent suffered drowning that led to his/her death | (N-Y-Ref-DK)* |
| a5_02 | Was the injury or accident self-inflicted? | (N-Y-Ref-DK)* |
| a5_03 | Was the injury or accident intentionally inflicted by someone else? | (N-Y-Ref-DK)* |
| c4_48 | Was the injury or accident intentionally inflicted by someone else? | (N-Y-Ref-DK)* |

|  \* 0="No", 1="Yes", 8="Refused to answer", 9="Don't Know"   


### Logic Rule:

###### Adults:
~~~~~python
    drowning = a5_01_3 == 1
    recent = a5_04 < 30
    unintentional = (a5_02 != 1) & (a5_03 != 1)

    return drowning & recent & unintentional
~~~~~

###### Children:
~~~~~python
    drowning = c4_47_3 == 1
    recent = c4_49 < 30
    unintentional = c4_48 != 1

    return drowning & recent & unintentional
~~~~~
    

### Performance:
|             | PHMRC-Adult |  NHMRC-Adult |  PHMRC-Child |  NHMRC-Child |    
|:-----------:|:------------:|:------------:|:------------:|:------------:|   
| Endorsements| 44 |  4 |  73 |  8 |    
|  True CSMF  | 0.014 |  0.001 |  0.04 |  0.005 |    
| Sensitivity | 37.7 |  50.0 |  84.3 |  100.0 |    
| Specificity | 99.9 |  100.0 |  99.8 |  100.0 |    
|  Precision  | 90.9 |  100.0 |  95.9 |  100.0 |    
|   Accuracy  | 99.1 |  99.9 |  99.2 |  100.0 |    
|Cause-Specific CCC| 72.8 |  48.4 |  92.4 |  100.0 |    
|Cause-Specific CCC Change| 30.1 |  0.0 |  0.0 |  0.0 |    
|  Median CCC | 19.5 |  31.2 |  33.0 |  37.4 |    
|Median CCC Change| 0.0 |  0.0 |  0.0 |  0.0 |    
|CMSF Accuracy| 77.6 |  70.9 |  81.3 |  58.9 |    
|CMSF Accuracy Change| 0.2 |  0.0 |  0.0 |  0.0 |    
|CCCMSF Accuracy| 39.1 |  20.8 |  49.2 |  -11.8 |    
|CCCMSF Accuracy Change| 0.5 |  0.0 |  0.0 |  0.0 |    

|  \* not yet calculated   

\pagebreak
