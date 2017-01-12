def injury(no_injury):
    """Injury Rule

    Module: Adult and Child
    Prediction: Injury
    Conditions:

    Adult questions:
        no_injury: a5_01_8

    Child questions:
        no_injury: c4_47_11

    """
    return no_injury == 0


def bite(bite, other_inflicted, self_inflicted=0, duration=0):
    """Bite Rule

    Module: Adult and Child
    Prediction: Bite of Venomous Animal
    Conditions:
        a bite from a venomous animal led to the death
        which occurred less than 30 days before the death
        and the injury was unintentional

    Adult questions:
        bite: a5_01_5
        other_inflicted: a5_03
        self_inflicted: a5_02
        duration: a5_04

    Child questions:
        bite: c4_47_5
        other_inflicted: c4_48
        duration: c4_49

    """
    bite = bite == 1
    recent = duration < 30   # days
    unintentional = self_inflicted != 1 and other_inflicted != 1
    return recent and unintentional and bite


def drowning(drowning, other_inflicted, self_inflicted=0, duration=0):
    """Drowning Rule

    Module: Adult and Child
    Prediction: Drowning
    Conditions:
        the decedent drowned
        and the injury was unintentional

    Adult questions:
        drowning: a5_01_3
        other_inflicted: a5_03
        self_inflicted: a5_02
        duration: a5_04

    Child questions:
        drowning: c4_47_3
        other_inflicted: c4_48
        duration: c4_49
    """
    recent = duration < 30   # days
    unintentional = self_inflicted != 1 and other_inflicted != 1
    drowning = drowning == 1
    return recent and unintentional and drowning


def falls(falls, other_inflicted, self_inflicted=0, duration=0):
    """Falls Rule

    Module: Adult and Child
    Prediction: Falls
    Conditions:
        a fall led to the death
        which occurred less than 30 days before the death
        and the injury was unintentional

    Adult questions:
        falls: a5_01_2
        other_inflicted: a5_03
        self_inflicted: a5_02
        duration: a5_04

    Child questions:
        falls: c4_47_2
        other_inflicted: c4_48
        duration: c4_49
    """
    recent = duration < 30   # days
    unintentional = self_inflicted != 1 and other_inflicted != 1
    falls = falls == 1
    return recent and unintentional and falls


def fires(fires, other_inflicted, self_inflicted=0, duration=0):
    """Fires Rule

    Module: Adult and Child
    Prediction: Fires
    Conditions:
        a burn led to the death
        which occurred less than 30 days before the death
        and the injury was unintentional

    Adult questions:
        fires: a5_01_6
        other_inflicted: a5_03
        self_inflicted: a5_02
        duration: a5_04

    Child questions:
        fires: c4_47_6
        other_inflicted: c4_48
        duration: c4_49
    """
    recent = duration < 30   # days
    unintentional = self_inflicted != 1 and other_inflicted != 1
    fires = fires == 1
    return recent and unintentional and fires


def other_injury(other_injury, other_inflicted, self_inflicted=0, duration=0):
    """Other Injuries Rule

    Module: Adult and Child
    Prediction: Other Injuries (Other Defined Causes of Child Deaths)
    Conditions:
        an other specified injury led to the death
        which occurred less than 30 days before the death
        and the injury was unintentional

    Adult questions:
        other_injury: a5_01_9a
        other_inflicted: a5_03
        self_inflicted: a5_02
        duration: a5_04

    Child questions:
        other_injury: c4_47_8a
        other_inflicted: c4_48
        duration: c4_49
    """
    recent = duration < 30   # days
    unintentional = self_inflicted != 1 and other_inflicted != 1
    other_injury = other_injury == 1
    return recent and unintentional and other_injury


def poisoning(poisioning, other_inflicted, self_inflicted=0, duration=0):
    """Poisonings Rule

    Module: Adult and Child
    Prediction: Poisonings
    Conditions:
        a poisoning led to the death
        which occurred less than 30 days before the death
        and the injury was unintentional

    Adult questions:
        poisioning: a5_01_4
        other_inflicted: a5_03
        self_inflicted: a5_02
        duration: a5_04

    Child questions:
        poisioning: c4_47_4
        other_inflicted: c4_48
        duration: c4_49
    """
    recent = duration < 30   # days
    unintentional = self_inflicted != 1 and other_inflicted != 1
    poisioning = poisioning == 1
    return recent and unintentional and poisioning


def road_traffic(road_traffic, duration=0):
    """Road Traffic Rule

    Module: Adult and Child
    Prediction: Road Traffic
    Conditions:
        a road traffic injury led to the death
        which occurred less than 30 days before the death

    Adult questions:
        road_traffic: a5_01_5
        duration: a5_04

    Child questions:
        road_traffic: c4_47_5
        duration: c4_49
    """
    recent = duration < 30   # days
    road_traffic = road_traffic == 1
    return recent and road_traffic


def homicide(no_injury, other_inflicted):
    """Homicide Rule

    Module: Adult and Child
    Prediction: Homicide (Violent Death)
    Conditions:
        any injury led to the death
        and the injury was intentionally inflicted by someone else

    Adult questions:
        no_injury: a5_01_8
        other_inflicted: a5_03

    Child questions:
        no_injury: c4_47_11
        other_inflicted: c4_48
    """
    injury = no_injury != 1
    other_inflicted = other_inflicted == 1
    return injury and other_inflicted


def suicide(self_inflicted, word_suicide=0):
    """Suicide Rule

    Module: Adult
    Prediction: Suicide
    Conditions:
        any injury led to the death
        and the injury was self-inflicted

    Questions:
        self_inflicted: a5_02
        word_suicide: a_7_11
    """
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


def anemia(age, sex, pregnant, period_overdue, period_overdue_days,
           postpartum, pale, breathing_difficulty):
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

    Questions:
        age: g5_04a
        sex: g5_02
        pregnant: a3_10
        period_overdue: a3_07
        period_overdue_days: a3_08
        postpartum: a3_18
        pale: a2_20
        breathing_difficulty: a2_36

    Unused Questions: a2_37, a2_40, a2_43, a2_45, a2_46a, a2_69

    Note: Anemia is a risk factor for hemorrhage. For deaths which occur
        during labor or delivery, the underlying cause is hemorrhage and
        anemia is a secondary condition. Multiple symptoms for this rule are
        not included on the short-form instrument.
    """
    maternal_age = 12 < age < 49
    female = sex == 2
    pregnant = pregnant == 1
    period_overdue = period_overdue == 1 and period_overdue_days > 90
    postpartum = postpartum == 1
    pale = pale == 1
    breathing_difficulty = breathing_difficulty == 1
    return (female and maternal_age and (pregnant or period_overdue or
            postpartum) and pale and breathing_difficulty)


def hemorrhage(age, sex, pregnant, period_overdue, period_overdue_days,
               delivering, postpartum, bleeding, convulsions, epilepsy,
               labor_duration):
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

    Questions:
        age: g5_04a
        sex: g5_02
        pregnant: a3_10
        period_overdue: a3_07
        period_overdue_days: a3_08
        delivering: a3_15
        postpartum: a3_18
        bleeding: a3_06
        convulsions: a2_82
        epilepsy: a1_01_8
        labor_duration: a3_16

    Unused questions: a3_13, a3_14, a3_19

    Note: For deaths which involve excessive bleeding during prolonged labor,
        the underlying cause is obstructed labor and hemorrhage is a secondary
        condition.
    """
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


def hypertensive(age, sex, pregnant, period_overdue, period_overdue_days,
                 convulsions, epilepsy):
    """Hypertensive Disorder Rule

    Module: Adult
    Prediction: Hypertensive Disorder
    Conditions:
        the decedent was female
        and was within the maternal age range
        and was pregnant or her period was late
        and had convulsions or mentioned epilepsy

    Questions:
        age: g5_04a
        sex: g5_02
        pregnant: a3_10
        period_overdue: a3_07
        period_overdue_days: a3_08
        convulsions: a2_82
        epilepsy: a1_01_8

    Note: In many settings, interviewees confuse epilepsy and convulsions.
        Any mention of epilepsy likely indicates the decedent had convulsions.
        Convulsion during pregnancy is a cardinal symptom which clearly
        distinguish hypertensive disorders from any other subtype of maternal
        death.
    """
    maternal_age = 12 < age < 49
    female = sex == 2
    pregnant = pregnant == 1
    period_overdue = period_overdue == 1 and period_overdue_days > 90
    convulsions = convulsions == 1
    epilepsy = epilepsy == 1
    return (female and maternal_age and (pregnant or period_overdue) and
            (convulsions or epilepsy))


def other_maternal(age, sex, delivering, labor_duration):
    """Other Pregnancy-Related Deaths Rule

    Module: Adult
    Prediction: Other Pregnancy-Related Deaths
    Conditions:
        the decedent was female
        and was within the maternal age range
        and spent at least 24 hours in labor or delivery
        and she died during labor or delivery

    Questions:
        age: g5_04a
        sex: g5_02
        delivering: a3_15
        labor_duration: a3_16

    Note: This rule currently only predicts obstructed labor
    """
    maternal_age = 12 < age < 49
    female = sex == 2
    delivering = delivering == 1
    long_delivery = labor_duration >= 1.0   # in days
    return maternal_age and female and delivering and long_delivery


def sepsis(age, sex, pregnant, period_overdue, period_overdue_days,
           abortion, postpartum, fever, discharge, belly_pain,
           belly_pain_location1, belly_pain_location2):
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

    Questions:
        age: g5_04a
        sex: g5_02
        pregnant: a3_10
        period_overdue: a3_07
        period_overdue_days: a3_08
        abortion: a3_17
        postpartum: a3_18
        fever: a2_02
        discharge: a3_20
        belly_pain: a2_61
        belly_pain_location1: a2_63_1
        belly_pain_location2: a2_63_2
    """
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


def measles(illness_start, any_rash, rash_location, measles_rash,
            fever, breathing_difficulty, loose_stool, rash_location2=0,
            word_diarrhea=0, word_fever=0, word_pneumonia=0):
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

    Questions:
        illness_start: c1_21
        any_rash: c4_30
        rash_location: c4_31_1
        rash_location2: c4_31_2
        measles_rash: c4_43
        fever: c4_01
        breathing_difficulty: c4_16
        loose_stool: c4_06
        word_diarrhea: c_6_5
        word_fever: c_6_6
        word_pneumonia: c_6_9

    Unused Questions: c4_32, c4_04, c4_12, c4_18, c4_20, c_6_10

    Note: This formulation of the rule matches the Level 2a gold standard
        criteria from the PHMRC study.
    """
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


def cancer(checklist_word=0, long_form_word=0):
    """Caner Rule

    Module: Child
    Prediction: Other Cancers
    Conditions:
        the word cancer

    Questions:
        checklist_word: c_6_2
        long_form_word: s99999
    """
    word_cancer = (checklist_word == 1) or (long_form_word == 1)
    return word_cancer


def malnutrition(thin_limbs, skin_flaking, palor):
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

    Questions:
        thin_limbs: c4_35
        skin_flaking: c4_38
        palor: c4_41

    Unused Questions: c4_39, c4_40
    """
    thin_limbs = thin_limbs == 1
    skin_flaking = skin_flaking == 1
    palor = palor == 1
    return (thin_limbs + skin_flaking + palor) >= 2


def stillbirth(never_cried_moved_breathed):
    """Stillbirth Rule

    Module: Neonate
    Prediction: Stillbirth
    Conditions:
        the decedent never cried, moved or breathed

    Questions:
        never_cried_moved_breathed: c1_15
    """
    never_cried_moved_breathed = never_cried_moved_breathed == 1
    return never_cried_moved_breathed


def tetanus(convulsions, ever_suckle, stop_suckling, when_stopped_suckling):
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
        convulsions: c3_25
        ever_suckle: c3_12
        stop_suckling: c3_13
        when_stopped_suckling: c3_14

    Unused Questions: c3_15, c3_16, c3_33

    Note: *This is a key symptom, but we do not have a question for this
    """
    convulsions = convulsions == 1
    stop_suckling = (ever_suckle == 1) & (stop_suckling == 1)
    stopped_day2 = when_stopped_suckling >= 2  # days
    return convulsions & stop_suckling & stopped_day2


ADULT_RULES = [
    road_traffic,
    homicide,
    suicide,
    bite,
    drowning,
    fires,
    falls,
    poisoning,
    other_injury,
    hypertensive,
    other_maternal,
    sepsis,
    hemorrhage,
    anemia,
]

CHILD_RULES = [
    road_traffic,
    homicide,
    bite,
    drowning,
    fires,
    falls,
    poisoning,
    other_injury,
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
    road_traffic,
    homicide,
    suicide,
    bite,
    drowning,
    fires,
    falls,
    poisoning,
    other_injury,
    hypertensive,
    other_maternal,
    sepsis,
    hemorrhage,
    anemia,
    measles,
    cancer,
    malnutrition,
    stillbirth,
    tetanus,
]
