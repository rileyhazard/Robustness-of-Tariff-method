# Protein-Energy Malnutrition

### Rule:
|  If the respondent says   
|    the decendent had three of the following symptoms:   
|    limbs became thin during the illness   
|    skin began to flake   
|    hair changed to a yellow or red color   
|    protruding belly   
|    palor   
|  SmartVA predicts 'Protein-Energy Malnutrition'   

|    * This cause is currently not on the cause list   

One key symptom for this rule is not included on the short-form instrument.

### Applicable questions:
|            |                                          |                  |
|:-----------|:-----------------------------------------|-----------------:|
| c4_35^1^ | During the illness that led to death, did [name]'s limbs (legs, arms) become very thin? | (N-Y-Ref-DK)* |
| c4_38 | During the illness that led to death, did [name]'s skin flake off in patches? | (N-Y-Ref-DK)* |
| c4_39 | Did [name]'s hair change in color to a reddish or yellowish color? | (N-Y-Ref-DK)* |
| c4_40 | Did [name] have a protruding belly? | (N-Y-Ref-DK)* |
| c4_41 | During the illness that led to death, did [name] suffer from 'lack of blood' or 'pallor'? | (N-Y-Ref-DK)* |

|  \* 0="No", 1="Yes", 8="Refused to answer", 9="Don't Know"   
|  ^1^ This question is not on the shortened questionnaire   


### Logic Rule:

~~~~~python
    thin_limbs = c4_35 == 1
    skin_flaking = c4_38 == 1
    hair_color = c4_39 == 1
    pallor = c4_41 == 1
    
    symptoms == thin_limbs + skin_flaking + hair_color  + pallor
    
    return symptoms >= 3
~~~~~
    

### Performance:
|             | PHMRC |  NHMRC |    
|:-----------:|:------------:|:------------:|   
| Endorsements| 19 |  11 |    
|  True CSMF  | 0.0 |  0.0 |    
| Sensitivity | ~ |  ~ |    
| Specificity | 99.1 |  99.3 |    
|  Precision  | 0.0 |  0.0 |    
|   Accuracy  | 99.1 |  99.3 |    
|Cause-Specific CCC| ~ |  ~ |    
|Cause-Specific CCC Change| ~ |  ~ |    
|  Median CCC | 33.0 |  37.4 |    
|Median CCC Change| 0.0 |  0.0 |    
|CMSF Accuracy| 81.2 |  59.2 |    
|CMSF Accuracy Change| -0.1 |  0.3 |    
|CCCMSF Accuracy| 48.9 |  -10.8 |    
|CCCMSF Accuracy Change| -0.3 |  0.9 |    

|  \* not yet calculated   
|  ^~^ This statistic is undefined for this sample   

\pagebreak
