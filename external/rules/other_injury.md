# Other Injury

### Rule:
|  If the respondent says   
|    an other specified injury led to the death   
|    which occurred less than 30 days before the death   
|    and the injury was unintentional   
|  SmartVA predicts 'Other Injury' for adults and 'Other Defined Causes of Child Deaths' for children    




### Applicable questions:
|            |                                          |                  |
|:-----------|:-----------------------------------------|-----------------:|
| a5_01_9a | Decedent suffered other injury that led to his/her death | (N-Y-Ref-DK)* |
| a5_04 | How long did [name] survive after the injury? [days] | (# of days) |
| c4_47_8a | Decedent suffered other injury that led to his/her death | (N-Y-Ref-DK)* |
| c4_49 | How long did [name] survive after the injury or accident? [days] | (# of days) |
| a5_02 | Was the injury or accident self-inflicted? | (N-Y-Ref-DK)* |
| a5_03 | Was the injury or accident intentionally inflicted by someone else? | (N-Y-Ref-DK)* |
| c4_48 | Was the injury or accident intentionally inflicted by someone else? | (N-Y-Ref-DK)* |

|  \* 0="No", 1="Yes", 8="Refused to answer", 9="Don't Know"   


### Logic Rule:

###### Adults:
~~~~~python
    other_injury = a5_01_9a == 1
    recent = a5_04 < 30
    unintentional = (a5_02 != 1) & (a5_03 != 1)

    return other_injury & recent & unintentional
~~~~~

###### Children:
~~~~~python
    other_injury = c4_47_8a == 1
    recent = c4_49 < 30
    unintentional = c4_48 != 1

    return other_injury & recent & unintentional
~~~~~
    

### Performance:
|             | PHMRC-Adult |  NHMRC-Adult |  PHMRC-Child |  NHMRC-Child |    
|:-----------:|:------------:|:------------:|:------------:|:------------:|   
| Endorsements| 109 |  43 |  67 |  4 |    
|  True CSMF  | 0.013 |  0.008 |  0.0 |  0.001 |    
| Sensitivity | 28.2 |  12.2 |  ~ |  0.0 |    
| Specificity | 99.0 |  99.4 |  96.8 |  99.7 |    
|  Precision  | 26.6 |  14.0 |  0.0 |  0.0 |    
|   Accuracy  | 98.0 |  98.6 |  96.8 |  99.6 |    
|Cause-Specific CCC| 40.0 |  9.5 |  ~ |  -5.0 |    
|Cause-Specific CCC Change| 28.0 |  12.6 |  ~ |  0.0 |    
|  Median CCC | 19.5 |  31.2 |  33.0 |  37.4 |    
|Median CCC Change| 0.0 |  0.0 |  0.0 |  0.0 |    
|CMSF Accuracy| 76.8 |  70.4 |  79.7 |  58.9 |    
|CMSF Accuracy Change| -0.6 |  -0.4 |  -1.6 |  0.1 |    
|CCCMSF Accuracy| 36.9 |  19.7 |  44.9 |  -11.6 |    
|CCCMSF Accuracy Change| -1.6 |  -1.1 |  -4.3 |  0.2 |    

|  \* not yet calculated   
|  ^~^ This statistic is undefined for this sample   

\pagebreak
