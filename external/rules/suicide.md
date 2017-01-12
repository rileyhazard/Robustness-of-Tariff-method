# Suicide

### Rule:
|  If the respondent says   
|    any injury led to the death   
|    and the injury was self-inflicted   
|  SmartVA predicts 'Suicide'   




### Applicable questions:
|            |                                          |                  |
|:-----------|:-----------------------------------------|-----------------:|
| a5_02 | Was the injury or accident self-inflicted? | (N-Y-Ref-DK)* |
| a_7_11 | Open response: 'Suicide' | (1="mentioned", 0="not mentioned") |

|  \* 0="No", 1="Yes", 8="Refused to answer", 9="Don't Know"   


### Logic Rule:

~~~~~python
    return (a5_02 == 1) | (a_7_11 == 1)
~~~~~
    

### Performance:
|             | PHMRC-Adult |  NHMRC-Adult |    
|:-----------:|:------------:|:------------:|   
| Endorsements| 531 |  517 |    
|  True CSMF  | 0.016 |  0.009 |    
| Sensitivity | 3.2 |  0.0 |    
| Specificity | 93.2 |  91.1 |    
|  Precision  | 0.8 |  0.0 |    
|   Accuracy  | 91.7 |  90.3 |    
|Cause-Specific CCC| 51.8 |  43.4 |    
|Cause-Specific CCC Change| 1.7 |  0.0 |    
|  Median CCC | 18.7 |  27.8 |    
|Median CCC Change| -0.8 |  -3.4 |    
|CMSF Accuracy| 73.7 |  64.7 |    
|CMSF Accuracy Change| -3.7 |  -6.1 |    
|CCCMSF Accuracy| 28.5 |  4.1 |    
|CCCMSF Accuracy Change| -10.0 |  -16.7 |    

|  \* not yet calculated   

\pagebreak
