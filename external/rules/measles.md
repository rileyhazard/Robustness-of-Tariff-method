# Measles

### Rule:
|  If the respondent says   
|    the illness that led to death started less than 30 days before death   
|    and the decedent had a rash on the face   
|    and the decedent had a fever   
|    and the decedent had a cough or trouble breathing or conjunctivitis (pink eye)*and had diarrhea or pneumonia   
|  SmartVA predicts 'Measles'   

|    * We do not have a question about this directly   

This formulation of the rule matches the Level 2a gold standard criteria from the PHMRC study.

### Applicable questions:
|            |                                          |                  |
|:-----------|:-----------------------------------------|-----------------:|
| c1_21 | How long did the illness last? [days] | (# of days) |
| c4_30 | During the month before he/she died, did [name] have a skin rash? | (N-Y-Ref-DK)* |
| c4_31_1^1^ | Where was the rash? | (1="Face" 2="Trunk" 3="Extremities" 4="Everywhere") |
| c4_31_2^1^ | Where was the rash? | (1="Face" 2="Trunk" 3="Extremities" 4="Everywhere") |
| c4_43^1^ | During the illness that led to death, did [name] have a whitish rash inside the mouth or on the tongue? | (N-Y-Ref-DK)* |
| c4_01 | During the illness that led to death, did [name] have a fever? | (N-Y-Ref-DK)* |
| c4_04^2^ | How severe was the fever? | (1="Mild", 2="Moderate", 3="Severe", 8="Refused", 9="Don't Know") |
| c4_06 | During the illness that led to death, did [name] have more frequent loose or liquid stools than usual? | (N-Y-Ref-DK)* |
| c4_12 | During the illness that led to death, did the child have a cough? | (N-Y-Ref-DK)* |
| c4_16 | During the illness that led to death, did [name] have difficult breathing? | (N-Y-Ref-DK)* |
| c4_18^2^ | During the illness that led to death, did [name] have fast breathing? | (N-Y-Ref-DK)* |
| c4_20 | During the illness that led to death, did he/she have indrawing of the chest? | (N-Y-Ref-DK)* |
| c4_32^1^ | Where did the rash start? | (# of days) |
| c_6_5 | Open response: 'Diarrhea' | (1="mentioned", 0="not mentioned") |
| c_6_6 | Open response: 'Fever' | (1="mentioned", 0="not mentioned") |
| c_6_9 | Open response: 'Pneumonia' | (1="mentioned", 0="not mentioned") |
| c_6_10^2^ | Open response: 'Rash' | (1="mentioned", 0="not mentioned") |

|  \* 0="No", 1="Yes", 8="Refused to answer", 9="Don't Know"   
|  ^1^ This question is not on the shortened questionnaire   
|  ^2^ This question is not currently being used in the rule   


### Logic Rule:

~~~~~python
    acute = c1_21 < 30
    face_rash = c4_30 == 1 & (c4_31_1 == 1 | c4_31_2 == 1)
    measles_rash = c4_43 == 1
    diff_breathing = c4_12 == 1 & ((c4_18 == 1) | (c4_20 == 1))
    loose_stool = (c4_06 == 1) | (c_6_5 == 1)
    pneumonia = c_6_9 == 1
    
    return acute & (face_rash | measles_rash) & 
           (diff_breathing | loose_stool | pneumonia) 
~~~~~
    

### Performance:
|             | PHMRC |  NHMRC |    
|:-----------:|:------------:|:------------:|   
| Endorsements| 1044 |  839 |    
|  True CSMF  | 0.011 |  0.0 |    
| Sensitivity | 69.6 |  ~ |    
| Specificity | 49.6 |  46.7 |    
|  Precision  | 1.5 |  0.0 |    
|   Accuracy  | 49.9 |  46.7 |    
|Cause-Specific CCC| 68.0 |  ~ |    
|Cause-Specific CCC Change| 73.0 |  ~ |    
|  Median CCC | 16.7 |  5.5 |    
|Median CCC Change| -16.3 |  -31.9 |    
|CMSF Accuracy| 43.2 |  59.7 |    
|CMSF Accuracy Change| -38.1 |  0.8 |    
|CCCMSF Accuracy| -54.3 |  -9.6 |    
|CCCMSF Accuracy Change| -103.5 |  2.2 |    

|  \* not yet calculated   
|  ^~^ This statistic is undefined for this sample   

\pagebreak
