# Other Cancer

### Rule:
|  If the respondent says   
|    the word cancer   
|  SmartVA predicts 'Other Cancer'   


This rule only applies to children and predicts all childhood cancers.

### Applicable questions:
|            |                                          |                  |
|:-----------|:-----------------------------------------|-----------------:|
| c_6_2 | Open response: 'Cancer' | (1="mentioned", 0="not mentioned") |
| s99999 | Open response: 'cancer' | (1="mentioned", 0="not mentioned") |

|  \* 0="No", 1="Yes", 8="Refused to answer", 9="Don't Know"   


### Logic Rule:

###### Children:
~~~~~python
    return c_6_2 == 1 | s99999 == 1
~~~~~
    

### Performance:
|             | PHMRC |  NHMRC |    
|:-----------:|:------------:|:------------:|   
| Endorsements| 14 |  4 |    
|  True CSMF  | 0.014 |  0.009 |    
| Sensitivity | 28.6 |  14.3 |    
| Specificity | 99.7 |  99.9 |    
|  Precision  | 57.1 |  50.0 |    
|   Accuracy  | 98.7 |  99.1 |    
|Cause-Specific CCC| 43.8 |  17.5 |    
|Cause-Specific CCC Change| 3.8 |  7.5 |    
|  Median CCC | 33.0 |  37.4 |    
|Median CCC Change| 0.0 |  0.0 |    
|CMSF Accuracy| 81.3 |  58.9 |    
|CMSF Accuracy Change| 0.0 |  0.0 |    
|CCCMSF Accuracy| 49.2 |  -11.8 |    
|CCCMSF Accuracy Change| 0.0 |  0.0 |    

|  \* not yet calculated   

\pagebreak
