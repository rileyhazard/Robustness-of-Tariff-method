# Road Traffic Injury

### Rule:
|  If the respondent says   
|    a road traffic injury led to the death   
|    which occurred less than 30 days before the death   
|  SmartVA predicts 'Road Traffic Injury'   




### Applicable questions:
|            |                                          |                  |
|:-----------|:-----------------------------------------|-----------------:|
| a5_01_1 | Decedent suffered road traffic injury that led to his/her death | (N-Y-Ref-DK)* |
| a5_04 | How long did [name] survive after the injury? [days] | (# of days) |
| c4_47_1 | Decedent suffered road traffic injury that led to his/her death | (N-Y-Ref-DK)* |
| c4_49 | How long did [name] survive after the injury or accident? [days] | (# of days) |

|  \* 0="No", 1="Yes", 8="Refused to answer", 9="Don't Know"   


### Logic Rule:

###### Adults:
~~~~~python
    road_traffic = a5_01_1 == 1
    recent = a5_04 < 30

    return road_traffic & recent
~~~~~

###### Children:
~~~~~python
    road_traffic = c4_47_1 == 1
    recent = c4_49 < 30

    return road_traffic & recent
~~~~~
    

### Performance:
|             | PHMRC-Adult |  NHMRC-Adult |  PHMRC-Child |  NHMRC-Child |    
|:-----------:|:------------:|:------------:|:------------:|:------------:|   
| Endorsements| 267 |  513 |  92 |  39 |    
|  True CSMF  | 0.026 |  0.092 |  0.045 |  0.025 |    
| Sensitivity | 82.7 |  89.6 |  94.6 |  90.0 |    
| Specificity | 98.7 |  99.4 |  99.7 |  99.8 |    
|  Precision  | 62.5 |  93.6 |  94.6 |  92.3 |    
|   Accuracy  | 98.3 |  98.5 |  99.5 |  99.6 |    
|Cause-Specific CCC| 83.7 |  91.5 |  94.3 |  89.5 |    
|Cause-Specific CCC Change| 64.8 |  57.7 |  3.4 |  0.0 |    
|  Median CCC | 20.2 |  31.2 |  33.0 |  37.4 |    
|Median CCC Change| 0.7 |  0.0 |  0.0 |  0.0 |    
|CMSF Accuracy| 77.5 |  72.7 |  81.2 |  58.9 |    
|CMSF Accuracy Change| 0.1 |  1.8 |  -0.1 |  0.0 |    
|CCCMSF Accuracy| 38.7 |  25.7 |  48.8 |  -11.8 |    
|CCCMSF Accuracy Change| 0.2 |  4.9 |  -0.4 |  0.0 |    

|  \* not yet calculated   

\pagebreak
