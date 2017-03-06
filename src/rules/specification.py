def injury_adult(row):
    """Injury Rule

    Module: Adult
    Prediction: Injury
    Conditions:
    """
    no_injury = row.get('a5_01_8')
    return no_injury == 0


def injury_child(row):
    """Injury Rule

    Module: Child
    Prediction: Injury
    Conditions:
    """
    no_injury = row.get('c4_47_11')
    return no_injury == 0


def bite_adult(row):
    """Bite Rule

    Module: Adult
    Prediction: Bite of Venomous Animal
    Conditions:
        a bite from a venomous animal led to the death
        which occurred less than 30 days before the death
        and the injury was unintentional
    """
    bite = row.get('a5_01_5')
    duration = row.get('a5_04', 0)   # True if key is missing

    bite = bite == 1
    recent = duration < 30   # days

    return bite and recent


def bite_child(row):
    """Bite Rule

    Module: Child
    Prediction: Bite of Venomous Animal
    Conditions:
        a bite from a venomous animal led to the death
        which occurred less than 30 days before the death
        and the injury was unintentional
    """
    bite = row.get('c4_47_5')
    duration = row.get('c4_49', 0)   # True if key is missing

    bite = bite == 1
    recent = duration < 30   # days

    return bite and recent


def drowning_adult(row):
    """Drowning Rule

    Module: Adult
    Prediction: Drowning
    Conditions:
        the decedent drowned
        and the injury was unintentional
    """
    drowning = row.get('a5_01_3')
    duration = row.get('a5_04', 0)   # True if key is missing

    drowning = drowning == 1
    recent = duration < 30   # days

    return drowning and recent


def drowning_child(row):
    """Drowning Rule

    Module: Child
    Prediction: Drowning
    Conditions:
        the decedent drowned
        and the injury was unintentional
    """
    drowning = row.get('c4_47_3')
    duration = row.get('c4_49', 0)   # True if key is missing

    drowning = drowning == 1
    recent = duration < 30   # days

    return drowning and recent


def falls_adult(row):
    """Falls Rule

    Module: Adult
    Prediction: Falls
    Conditions:
        a fall led to the death
        which occurred less than 30 days before the death
        and the injury was unintentional
    """
    falls = row.get('a5_01_2')
    duration = row.get('a5_04', 0)   # True if key is missing

    falls = falls == 1
    recent = duration < 30   # days

    return falls and recent


def falls_child(row):
    """Falls Rule

    Module: Child
    Prediction: Falls
    Conditions:
        a fall led to the death
        which occurred less than 30 days before the death
        and the injury was unintentional
    """
    falls = row.get('c4_47_2')
    duration = row.get('c4_49', 0)   # True if key is missing

    falls = falls == 1
    recent = duration < 30   # days

    return falls and recent


def fires_adult(row):
    """Fires Rule

    Module: Adult
    Prediction: Fires
    Conditions:
        a burn led to the death
        which occurred less than 30 days before the death
        and the injury was unintentional
    """
    fires = row.get('a5_01_6')
    duration = row.get('a5_04', 0)   # True if key is missing

    fires = fires == 1
    recent = duration < 30   # days

    return fires and recent


def fires_child(row):
    """Fires Rule

    Module: Child
    Prediction: Fires
    Conditions:
        a burn led to the death
        which occurred less than 30 days before the death
        and the injury was unintentional
    """
    fires = row.get('c4_47_6')
    duration = row.get('c4_49', 0)   # True if key is missing

    fires = fires == 1
    recent = duration < 30   # days

    return fires and recent


def other_injury_adult(row):
    """Other Injuries Rule

    Module: Adult
    Prediction: Other Injuries
    Conditions:
        an other specified injury led to the death
        which occurred less than 30 days before the death
        and the injury was unintentional
    """
    other_injury = row.get('a5_01_9a')
    duration = row.get('a5_04', 0)   # True if key is missing

    other_injury = other_injury == 1
    recent = duration < 30   # days

    return other_injury and recent


def other_injury_child(row):
    """Other Injuries Rule

    Module: Child
    Prediction: Other Defined Causes of Child Deaths
    Conditions:
        an other specified injury led to the death
        which occurred less than 30 days before the death
        and the injury was unintentional
    """
    other_injury = row.get('c4_47_8a')
    duration = row.get('c4_49', 0)   # True if key is missing

    other_injury = other_injury == 1
    recent = duration < 30   # days

    return other_injury and recent


def poisoning_adult(row):
    """Poisonings Rule

    Module: Adult
    Prediction: Poisonings
    Conditions:
        a poisoning led to the death
        which occurred less than 30 days before the death
        and the injury was unintentional
    """
    poisoning = row.get('a5_01_4')
    duration = row.get('a5_04', 0)   # True if key is missing

    poisoning = poisoning == 1
    recent = duration < 30   # days

    return poisoning and recent


def poisoning_child(row):
    """Poisonings Rule

    Module: Adult and Child
    Prediction: Poisonings
    Conditions:
        a poisoning led to the death
        which occurred less than 30 days before the death
        and the injury was unintentional
    """
    poisoning = row.get('c4_47_4')
    duration = row.get('c4_49', 0)   # True if key is missing

    poisoning = poisoning == 1
    recent = duration < 30   # days

    return poisoning and recent


def road_traffic_adult(row):
    """Road Traffic Rule

    Module: Adult
    Prediction: Road Traffic
    Conditions:
        a road traffic injury led to the death
        which occurred less than 30 days before the death
    """
    road_traffic = row.get('a5_01_5')
    duration = row.get('a5_04', 0)   # True if key is missing

    road_traffic = road_traffic == 1
    recent = duration < 30   # days

    return recent and road_traffic


def road_traffic_child(row):
    """Road Traffic Rule

    Module: Child
    Prediction: Road Traffic
    Conditions:
        a road traffic injury led to the death
        which occurred less than 30 days before the death
    """
    road_traffic = row.get('c4_47_5')
    duration = row.get('c4_49', 0)   # True if key is missing

    road_traffic = road_traffic == 1
    recent = duration < 30   # days

    return recent and road_traffic


def homicide_adult(row):
    """Homicide Rule

    Module: Adult
    Prediction: Homicide
    Conditions:
        any injury led to the death
        and the injury was intentionally inflicted by someone else
    """
    no_injury = row.get('a5_01_8')
    other_inflicted = row.get('a5_03')

    injury = no_injury != 1
    other_inflicted = other_inflicted == 1

    return injury and other_inflicted


def homicide_child(row):
    """Homicide Rule

    Module: Child
    Prediction: Violent Death
    Conditions:
        any injury led to the death
        and the injury was intentionally inflicted by someone else
    """
    no_injury = row.get('c4_47_11')
    other_inflicted = row.get('c4_48')

    injury = no_injury != 1
    other_inflicted = other_inflicted == 1

    return injury and other_inflicted


def suicide(row):
    """Suicide Rule

    Module: Adult
    Prediction: Suicide
    Conditions:
        any injury led to the death
        and the injury was self-inflicted
    """
    self_inflicted = row.get('a5_02')
    word_suicide = row.get('a_7_11')

    return self_inflicted == 1 or word_suicide == 1


def maternal(age, sex, pregnant):
    """Maternal Rule

    Module: Adult
    Prediction: Maternal
    Conditions:

    Questions:
        age: g5_04a
        sex: g5_02
        pregnant: a3_10
    """
    return False


def anemia(row):
    """Anemia Rule

    Module: Adult
    Prediction: Anemia
    Conditions:
        the decedent was female
        and was within the maternal age range
        and was pregnant or had given birth within the last six weeks
        and looked pale*
        and had fast or difficult breathing
        and did not die during labor or delivery
        and did not have excessive bleeding during pregnancy

    * Palor is the most important symptom for diagnosis anemia, but it is
        extremely difficult to detect during a VAI

    Unused Questions: a2_37, a2_40, a2_43, a2_45, a2_46a, a2_69

    Note: Anemia is a risk factor for hemorrhage. For deaths which occur
        during labor or delivery, the underlying cause is hemorrhage and
        anemia is a secondary condition. Multiple symptoms for this rule are
        not included on the short-form instrument.
    """
    age = row.get('g5_04a')
    sex = row.get('g5_02')
    pregnant = row.get('a3_10')
    period_overdue = row.get('a3_07')
    period_overdue_days = row.get('a3_08')
    postpartum = row.get('a3_18')
    pale = row.get('a2_20')
    breathing_difficulty = row.get('a2_36')

    maternal_age = 12 < age < 49
    female = sex == 2
    pregnant = pregnant == 1
    period_overdue = period_overdue == 1 and period_overdue_days > 90
    postpartum = postpartum == 1
    pale = pale == 1
    breathing_difficulty = breathing_difficulty == 1

    return (female and maternal_age and (pregnant or period_overdue or
            postpartum) and pale and breathing_difficulty)


def hemorrhage(row):
    """Hemorrhage Rule

    Module: Adult
    Prediction: Hemorrhage
    Conditions:
        the decedent was female
        and was within the maternal age range
        and was pregnant or her period was late or giving birth or died within
            6 weeks of delivery
        and had excessive bleeding during pregnancy or delivery
        and did not die during a prolonged delivery
        and did not have convulsions

    Unused questions: a3_13, a3_14, a3_19

    Note: For deaths which involve excessive bleeding during prolonged labor,
        the underlying cause is obstructed labor and hemorrhage is a secondary
        condition.
    """
    age = row.get('g5_04a')
    sex = row.get('g5_02')
    pregnant = row.get('a3_10')
    period_overdue = row.get('a3_07')
    period_overdue_days = row.get('a3_08')
    delivering = row.get('a3_15')
    postpartum = row.get('a3_18')
    bleeding = row.get('a3_06')
    convulsions = row.get('a2_82')
    epilepsy = row.get('a1_01_8')
    labor_duration = row.get('a3_16')

    maternal_age = 12 < age < 49
    female = sex == 2
    pregnant = pregnant == 1
    period_overdue = period_overdue == 1 and period_overdue_days > 90
    delivering = delivering == 1
    postpartum = postpartum == 1
    bleeding = bleeding == 1
    no_convulsions = convulsions != 1 and epilepsy != 1
    not_prolonged = labor_duration < 1.0   # in days

    return (female and maternal_age and (pregnant or period_overdue or
            delivering or postpartum) and bleeding and no_convulsions and
            not_prolonged)


def hypertensive(row):
    """Hypertensive Disorder Rule

    Module: Adult
    Prediction: Hypertensive Disorder
    Conditions:
        the decedent was female
        and was within the maternal age range
        and was pregnant or her period was late
        and had convulsions or mentioned epilepsy

    Questions:

    Note: In many settings, interviewees confuse epilepsy and convulsions.
        Any mention of epilepsy likely indicates the decedent had convulsions.
        Convulsion during pregnancy is a cardinal symptom which clearly
        distinguish hypertensive disorders from any other subtype of maternal
        death.
    """
    age = row.get('g5_04a')
    sex = row.get('g5_02')
    pregnant = row.get('a3_10')
    period_overdue = row.get('a3_07')
    period_overdue_days = row.get('a3_08')
    convulsions = row.get('a2_82')
    epilepsy = row.get('a1_01_8')

    maternal_age = 12 < age < 49
    female = sex == 2
    pregnant = pregnant == 1
    period_overdue = period_overdue == 1 and period_overdue_days > 90
    convulsions = convulsions == 1
    epilepsy = epilepsy == 1

    return (female and maternal_age and (pregnant or period_overdue) and
            (convulsions or epilepsy))


def other_maternal(row):
    """Other Pregnancy-Related Deaths Rule

    Module: Adult
    Prediction: Other Pregnancy-Related Deaths
    Conditions:
        the decedent was female
        and was within the maternal age range
        and spent at least 24 hours in labor or delivery
        and she died during labor or delivery

    Note: This rule currently only predicts obstructed labor
    """
    age = row.get('g5_04a')
    sex = row.get('g5_02')
    delivering = row.get('a3_15')
    labor_duration = row.get('a3_16')

    maternal_age = 12 < age < 49
    female = sex == 2
    delivering = delivering == 1
    long_delivery = labor_duration >= 1.0   # in days

    return maternal_age and female and delivering and long_delivery


def sepsis(row):
    """Sepsis Rule

    Module: Adult
    Prediction: Sepsis
    Conditions:
        the decedent was female
        and was within the maternal age range
        and died within six weeks of an abortion
        or had given birth within the last six weeks
        and had a lower belly pain
        and had a fever
        and had offensive vaginal discharge
    """
    age = row.get('g5_04a')
    sex = row.get('g5_02')
    pregnant = row.get('a3_10')
    period_overdue = row.get('a3_07')
    period_overdue_days = row.get('a3_08')
    abortion = row.get('a3_17')
    postpartum = row.get('a3_18')
    fever = row.get('a2_02')
    discharge = row.get('a3_20')
    belly_pain = row.get('a2_61')
    belly_pain_location1 = row.get('a2_63_1')
    belly_pain_location2 = row.get('a2_63_2')

    maternal_age = 12 < age < 49
    female = sex == 2
    pregnant = pregnant == 1
    period_overdue = period_overdue == 1 and period_overdue_days > 90
    abortion = abortion == 1
    postpartum = postpartum == 1
    fever = fever == 1
    discharge = discharge == 1
    lower_belly_pain = belly_pain == 1 and (belly_pain_location1 == 2 or
                                            belly_pain_location2 == 2)

    return (female and maternal_age and (abortion or (postpartum and
            fever and discharge and lower_belly_pain)))


def measles(row):
    """Measles Rule

    Module: Child
    Prediction: Measles
    Conditions:
        the illness that led to death started less than 30 days before death
        and the decedent had a rash on the face
        and the decedent had a fever
        and the decedent had a cough or trouble breathing or conjunctivitis
            (pink eye)*
        and had diarrhea or pneumonia

    Unused Questions: c4_32, c4_04, c4_12, c4_18, c4_20, c_6_10

    Note: This formulation of the rule matches the Level 2a gold standard
        criteria from the PHMRC study.
    """
    illness_start = row.get('c1_21', 9999)  # Defaults to false
    any_rash = row.get('c4_30')
    rash_location = row.get('c4_31_1')
    rash_location2 = row.get('c4_31_2')
    measles_rash = row.get('c4_43')
    fever = row.get('c4_01')
    breathing_difficulty = row.get('c4_16')
    loose_stool = row.get('c4_06')
    word_diarrhea = row.get('c_6_5')
    word_fever = row.get('c_6_6')
    word_pneumonia = row.get('c_6_9')

    acute = illness_start < 30
    rash = any_rash == 1
    face_rash = rash and (rash_location == 1) or (rash_location2 == 1)
    measles_rash = measles_rash == 1
    word_fever = word_fever == 1
    word_diarrhea = word_diarrhea == 1
    word_pneumonia = word_pneumonia == 1
    fever = fever == 1 or word_fever
    breathing_difficulty = breathing_difficulty == 1
    loose_stool = loose_stool or word_diarrhea

    return ((breathing_difficulty or loose_stool or word_pneumonia) and
            (face_rash or measles_rash) and acute)


def cancer(row):
    """Caner Rule

    Module: Child
    Prediction: Other Cancers
    Conditions:
        the word cancer
    """
    checklist_word = row.get('c_6_2')
    long_form_word = row.get('s99999')

    word_cancer = (checklist_word == 1) or (long_form_word == 1)

    return word_cancer


def malnutrition(row):
    """Protein-energy malnutrition Rule

    Module: Child
    Prediction: Protein-energy malnutrition
    Conditions:
        the decendent had three of the following symptoms:
            limbs became thin during the illness
            skin began to flake
            hair changed to a yellow or red color
            protruding belly
            palor

    Unused Questions: c4_39, c4_40
    """
    thin_limbs = row.get('c4_35')
    skin_flaking = row.get('c4_38')
    palor = row.get('c4_41')

    thin_limbs = thin_limbs == 1
    skin_flaking = skin_flaking == 1
    palor = palor == 1

    return (thin_limbs + skin_flaking + palor) >= 2


def stillbirth(row):
    """Stillbirth Rule

    Module: Neonate
    Prediction: Stillbirth
    Conditions:
        the decedent never cried, moved or breathed
    """
    never_cried_moved_breathed = row.get('c1_15')

    never_cried_moved_breathed = never_cried_moved_breathed == 1

    return never_cried_moved_breathed


def tetanus(row):
    """Neonatal Tetanus Rule

    Module: Neonate
    Prediction: Neonatal tetanus
    Conditions:
        the decedent is a neonate
        and the illness started more than two days after birth
        and the baby stopped suckling
        and was rigid
        and had either spasms, convulsions or back arching (opisthotonus*)

    Questions:

    Unused Questions: c3_15, c3_16, c3_33

    Note: *This is a key symptom, but we do not have a question for this
    """
    convulsions = row.get('c3_25')
    ever_suckle = row.get('c3_12')
    stop_suckling = row.get('c3_13')
    when_stopped_suckling = row.get('c3_14')

    convulsions = convulsions == 1
    stop_suckling = (ever_suckle == 1) & (stop_suckling == 1)
    stopped_day2 = when_stopped_suckling >= 2  # days
    return convulsions & stop_suckling & stopped_day2


ADULT_RULES = [
    road_traffic_adult,
    bite_adult,
    drowning_adult,
    fires_adult,
    falls_adult,
    poisoning_adult,
    other_injury_adult,
    homicide_adult,
    suicide,
    hypertensive,
    other_maternal,
    sepsis,
    hemorrhage,
    anemia,
]

CHILD_RULES = [
    road_traffic_child,
    bite_child,
    drowning_child,
    fires_child,
    falls_child,
    poisoning_child,
    other_injury_child,
    homicide_child,
    measles,
    cancer,
    malnutrition,
]

NEONATE_RULES = [
    stillbirth,
    tetanus,
]

RULES_BY_MODULE = {
    'adult': ADULT_RULES,
    'child': CHILD_RULES,
    'neonate': NEONATE_RULES,
}

RULES_FOR_DOC = [
    (road_traffic_adult, road_traffic_child),
    (bite_adult, bite_child),
    (drowning_adult, drowning_child),
    (fires_adult, fires_child),
    (falls_adult, falls_child),
    (poisoning_adult, poisoning_child),
    (other_injury_adult, other_injury_child),
    (homicide_adult, homicide_child),
    (suicide,),
    (hypertensive,),
    (other_maternal,),
    (sepsis,),
    (hemorrhage,),
    (anemia,),
    (measles,),
    (cancer,),
    (malnutrition,),
    (stillbirth,),
    (tetanus,),
]
