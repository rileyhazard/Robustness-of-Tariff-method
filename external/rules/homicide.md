# Homicide

### Rule:
|  If the respondent says   
|    any injury led to the death   
|    and the injury was intentionally inflicted by someone else   
|  SmartVA predicts 'Homicide' for adults and 'Violent Death' for children    




### Applicable questions:
|            |                                          |                  |
|:-----------|:-----------------------------------------|-----------------:|
| a5_01_8 | Decedent did not suffer any injuries that led to his/her death | (N-Y-Ref-DK)* |
| a5_03 | Was the injury or accident intentionally inflicted by someone else? | (N-Y-Ref-DK)* |
| c4_47_11 | Decedent did not suffer accident that led to his/her death | (N-Y-Ref-DK)* |
| c4_48 | Was the injury or accident intentionally inflicted by someone else? | (N-Y-Ref-DK)* |

|  \* 0="No", 1="Yes", 8="Refused to answer", 9="Don't Know"   


### Logic Rule:

###### Adults:
~~~~~python
    return (a5_01_8 != 1) & (a5_03 == 1)
~~~~~

###### Children:
~~~~~python
    return (c4_47_11 != 1) & (c4_48 == 1)
~~~~~
    

### Performance:
|             | PHMRC-Adult |  NHMRC-Adult |  PHMRC-Child |  NHMRC-Child |    
|:-----------:|:------------:|:------------:|:------------:|:------------:|   
| Endorsements| 242 |  162 |  54 |  0 |    
|  True CSMF  | 0.021 |  0.006 |  0.025 |  0.0 |    
| Sensitivity | 70.1 |  79.4 |  84.6 |  ~ |    
| Specificity | 98.4 |  97.7 |  99.5 |  100.0 |    
|  Precision  | 48.3 |  16.7 |  81.5 |  ~ |    
|   Accuracy  | 97.8 |  97.6 |  99.1 |  100.0 |    
|Cause-Specific CCC| 70.4 |  78.8 |  83.8 |  ~ |    
|Cause-Specific CCC Change| 8.6 |  21.2 |  2.0 |  ~ |    
|  Median CCC | 19.5 |  27.8 |  33.0 |  37.4 |    
|Median CCC Change| 0.0 |  -3.4 |  0.0 |  0.0 |    
|CMSF Accuracy| 77.0 |  70.0 |  81.2 |  58.9 |    
|CMSF Accuracy Change| -0.4 |  -0.8 |  -0.1 |  0.0 |    
|CCCMSF Accuracy| 37.4 |  18.6 |  48.9 |  -11.8 |    
|CCCMSF Accuracy Change| -1.1 |  -2.2 |  -0.3 |  0.0 |    

|  \* not yet calculated   
|  ^~^ This statistic is undefined for this sample   

\pagebreak
