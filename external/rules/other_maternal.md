# Obstructed Labor

### Rule:
|  If the respondent says   
|    the decedent was female   
|    and was within the maternal age range   
|    and spent at least 24 hours in labor or delivery   
|    and she died during labor or delivery   
|  SmartVA predicts 'Obstructed Labor'   
|    Which is currently grouped into 'Maternal' for reporting   


This rule currently only predicts obstructed labor

### Applicable questions:
|            |                                          |                  |
|:-----------|:-----------------------------------------|-----------------:|
| g5_02 | What was the sex of the deceased? | (1="male", 2="female") |
| g5_04a | What was the last known age of the deceased? [years] | (# of years) |
| a3_12 | Did [name] die during an abortion? | (N-Y-Ref-DK)* |
| a3_15 | Did she die during labor or delivery? | (N-Y-Ref-DK)* |
| a3_16 | For how long was she in labor? [days] | (# of days) |

|  \* 0="No", 1="Yes", 8="Refused to answer", 9="Don't Know"   


### Logic Rule:

~~~~~python
    female = g5_02 == 2
    age = (g5_04a > 12) & (g5_04a <= 49)
    delivering = (a3_12 == 1) | (a3_15 == 1)
    prolonged = a3_16 >= 1   # coded in days (not hours)
    
    return female & age & delivering & prolonged
~~~~~
    

### Performance:
|             | PHMRC-Other^1^ |  NHMRC-Other^1^ |  PHMRC-Maternal^2^ |  NHMRC-Maternal^2^ |    
|:-----------:|:------------:|:------------:|:------------:|:------------:|   
| Endorsements| 6 |  2 |  6 |  2 |    
|  True CSMF  | 0.014 |  0.0 |  0.06 |  0.017 |    
| Sensitivity | 1.9 |  ~ |  1.3 |  2.0 |    
| Specificity | 99.9 |  100.0 |  100.0 |  100.0 |    
|  Precision  | 33.3 |  0.0 |  100.0 |  100.0 |    
|   Accuracy  | 98.6 |  100.0 |  94.1 |  98.4 |    
|Cause-Specific CCC| 16.1 |  ~ |  78.6 |  85.3 |    
|Cause-Specific CCC Change| 1.9 |  ~ |  0.0 |  0.0 |    
|  Median CCC | 18.3 |  20.5 |  19.5 |  31.2 |    
|Median CCC Change| -0.0 |  0.0 |  0.0 |  0.0 |    
|CMSF Accuracy| 72.7 |  71.7 |  77.4 |  70.9 |    
|CMSF Accuracy Change| 0.0 |  0.0 |  0.0 |  0.0 |    
|CCCMSF Accuracy| 25.7 |  23.2 |  38.6 |  20.8 |    
|CCCMSF Accuracy Change| 0.0 |  0.0 |  0.0 |  0.0 |    

|  ^1^ Performance at detecting 'Other Pregnancy Related Deaths' vs any other cause   
|  ^2^ Performance at detecting any maternal cause vs non-maternal causes   
|  \* not yet calculated   
|  ^~^ This statistic is undefined for this sample   

\pagebreak
