# Neonatal Tetanus

### Rule:
|  If the respondent says   
|    the decedent is a neonate   
|    and the illness started more than two days after birth   
|    and the baby stopped suckling   
|    and was rigid   
|    and had either spasms, convulsions or back arching (opisthotonus*)   
|  SmartVA predicts 'Neonatal Tetanus'   

|    * We do not have a question about this directly   
|    ** This cause is currently not on the cause list   

Multiple key symptoms for this rule are not included on the short-form instrument.

### Applicable questions:
|            |                                          |                  |
|:-----------|:-----------------------------------------|-----------------:|
| c3_12 | Did the baby ever suckle in a normal way? | (N-Y-Ref-DK)* |
| c3_13^1^ | Did the baby stop being able to suckle in a normal way? | (N-Y-Ref-DK)* |
| c3_14^1,2^ | How long after birth did the baby stop suckling? [days] | (# of days) |
| c3_15^1,2^ | How long before he/she died did the baby stop suckling? | (# of days) |
| c3_16^1^ | Was the baby able to open his/her mouth at the time he/she stopped sucking? | (N-Y-Ref-DK)* |
| c3_25^1^ | During the illness that led to death did the baby have spasms or convulsions? | (N-Y-Ref-DK)* |
| c3_33 | During the illness that led to death, did the baby become unresponsive or unconscious?  | (N-Y-Ref-DK)* |

|  \* 0="No", 1="Yes", 8="Refused to answer", 9="Don't Know"   
|  ^1^ This question is not on the shortened questionnaire   
|  ^2^ This question is not currently being used in the rule   


### Logic Rule:

~~~~~python
    convulsions = c3_25 == 1
    stop_suckling = (a3_12 == 1) & (c3_13 == 1)
    stopped_day2 = c3_14 >= 2

    return convulsions & not_open_mouth & stop_suckling & stopped_day2
~~~~~
    

### Performance:
|             | PHMRC |  NHMRC |    
|:-----------:|:------------:|:------------:|   
| Endorsements| 6 |  17 |    
|  True CSMF  | 0.0 |  0.0 |    
| Sensitivity | ~ |  ~ |    
| Specificity | 99.8 |  99.1 |    
|  Precision  | 0.0 |  0.0 |    
|   Accuracy  | 99.8 |  99.1 |    
|Cause-Specific CCC| ~ |  ~ |    
|Cause-Specific CCC Change| ~ |  ~ |    
|  Median CCC | 29.7 |  19.3 |    
|Median CCC Change| -0.4 |  -1.7 |    
|CMSF Accuracy| 72.8 |  75.8 |    
|CMSF Accuracy Change| 0.1 |  0.1 |    
|CCCMSF Accuracy| 26.1 |  34.3 |    
|CCCMSF Accuracy Change| 0.2 |  0.2 |    

|  \* not yet calculated   
|  ^~^ This statistic is undefined for this sample   

\pagebreak
