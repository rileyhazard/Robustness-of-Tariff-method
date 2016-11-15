** Author: Spencer (revised by Pete)
** Date: Some time in 2010?
** Purpose: Prep Adult s variables from pre-symptom variables

clear all
set mem 500m
capture restore, not

if ("`c(os)'"=="Windows") local prefix	"J:"
else local prefix "/home/j"

** directories
local in_dir "`prefix'/Project/VA/Publication_2015/Revised Data/Presymptom Data"
local out_dir "`prefix'/Project/VA/Publication_2015/Revised Data/Symptom Data/"
local mrr "`prefix'/Project/VA/Publication_2015/Revised Data/Dump Folder/MRRTEXT/"
local dump "`prefix'/Project/VA/Publication_2015/Revised Data/Dump Folder"
local code "`prefix'/Project/VA/Publication_2015/Revised Data/Code"
local tariff_prep "`prefix'/Project/VA/Publication_2015/Revised Data/Codebook"

global out_dir `out_dir'
global tariff_prep `tariff_prep'
global who="Adult"


local gen_splits = 0

local cause_var = "va46"

use "`in_dir'/VA Final - Adult.dta", clear


capture rename a1_01_1 s1
capture rename a1_01_2 s2
capture rename a1_01_3 s3
capture rename a1_01_4 s4
capture rename a1_01_5 s5
capture rename a1_01_6 s6
capture rename a1_01_7 s7
capture rename a1_01_8 s8
capture rename a1_01_9 s9
capture rename a1_01_10 s10
capture rename a1_01_11 s11
capture rename a1_01_12 s12
capture rename a1_01_13 s13
capture rename a1_01_14 s14
capture rename a2_01 s15
capture rename a2_02 s16
capture rename a2_03 s17
capture rename a2_04 s18
capture rename a2_05 s19
capture rename a2_06 s20
capture rename a2_07 s21
capture rename a2_08 s22
capture rename a2_09_1a s23
capture rename a2_09_1b s24
capture rename a2_09_2a s25
capture rename a2_09_2b s26
capture rename a2_10 s27
capture rename a2_11 s28
capture rename a2_12 s29
capture rename a2_13 s30
capture rename a2_14 s31
capture rename a2_15 s32
capture rename a2_16 s33
capture rename a2_17 s34
capture rename a2_18 s35
capture rename a2_19 s36
capture rename a2_20 s37
capture rename a2_21 s38
capture rename a2_22 s39
capture rename a2_23 s40
capture rename a2_24 s41
capture rename a2_25 s42
capture rename a2_26 s43
capture rename a2_27 s44
capture rename a2_28 s45
capture rename a2_29 s46
capture rename a2_30 s47
capture rename a2_31 s48
capture rename a2_32 s49
capture rename a2_33 s50
capture rename a2_34 s51
capture rename a2_35 s52
capture rename a2_36 s53
capture rename a2_37 s54
capture rename a2_38 s55
capture rename a2_39_1 s56
capture rename a2_39_2 s57
capture rename a2_40 s58
capture rename a2_41 s59
capture rename a2_42 s60
capture rename a2_43 s61
capture rename a2_44 s62
capture rename a2_45 s63
capture rename a2_46a s64
capture rename a2_46b s65
capture rename a2_47 s66
capture rename a2_48 s67
capture rename a2_49 s68
capture rename a2_50 s69
capture rename a2_51 s70
capture rename a2_52 s71
capture rename a2_53 s72
capture rename a2_54 s73
capture rename a2_55 s74
capture rename a2_56 s75
capture rename a2_57 s76
capture rename a2_58 s77
capture rename a2_59 s78
capture rename a2_60 s79
capture rename a2_61 s80
capture rename a2_62 s81
capture rename a2_63_1 s82
capture rename a2_63_2 s83
capture rename a2_64 s84
capture rename a2_65 s85
capture rename a2_66 s86
capture rename a2_67 s87
capture rename a2_68 s88
capture rename a2_69 s89
capture rename a2_70 s90
capture rename a2_71 s91
capture rename a2_72 s92
capture rename a2_73 s93
capture rename a2_74 s94
capture rename a2_75 s95
capture rename a2_76 s96
capture rename a2_77 s97
capture rename a2_78 s98
capture rename a2_79 s99
capture rename a2_80 s100
capture rename a2_81 s101
capture rename a2_82 s102
capture rename a2_83 s103
capture rename a2_84 s104
capture rename a2_85 s105
capture rename a2_86 s106
capture rename a2_87_1 s107
capture rename a2_87_2 s108
capture rename a2_87_3 s109
capture rename a2_87_4 s110
capture rename a2_87_5 s111
capture rename a2_87_6 s112
capture rename a2_87_7 s113
capture rename a2_87_8 s114
capture rename a2_87_9 s115
capture rename a2_87_10a s116
capture rename a2_87_10b s117
capture rename a3_01 s118
capture rename a3_02 s119
capture rename a3_03 s120
capture rename a3_04 s121
capture rename a3_05 s122
capture rename a3_06 s123
capture rename a3_07 s124
capture rename a3_08 s125
capture rename a3_09 s126
capture rename a3_10 s127
capture rename a3_11 s128
capture rename a3_12 s129
capture rename a3_13 s130
capture rename a3_14 s131
capture rename a3_15 s132
capture rename a3_16 s133
capture rename a3_17 s134
capture rename a3_18 s135
capture rename a3_19 s136
capture rename a3_20 s137
capture rename a4_01 s138
capture rename a4_02_1 s139
capture rename a4_02_2 s140
capture rename a4_02_3 s141
capture rename a4_02_4 s142
capture rename a4_02_5a s143
capture rename a4_02_5b s144
capture rename a4_02_6 s145
capture rename a4_02_7 s146
capture rename a4_03 s147
capture rename a4_04 s148
capture rename a4_05 s149
capture rename a4_06 s150
capture rename a5_01_1 s151
capture rename a5_01_2 s152
capture rename a5_01_3 s153
capture rename a5_01_4 s154
capture rename a5_01_5 s155
capture rename a5_01_6 s156
capture rename a5_01_7 s157
capture rename a5_01_8 s158
capture rename a5_01_9a s159
capture rename a5_01_9b s160
capture rename a5_02 s161
capture rename a5_03 s162
capture rename a5_04 s163
capture rename a6_01 s164
capture rename a6_02_1 s165
capture rename a6_02_2 s166
capture rename a6_02_3 s167
capture rename a6_02_4 s168
capture rename a6_02_5 s169
capture rename a6_02_6 s170
capture rename a6_02_7 s171
capture rename a6_02_8 s172
capture rename a6_02_9 s173
capture rename a6_02_10 s174
capture rename a6_02_11 s175
capture rename a6_02_12a s176
capture rename a6_02_12b s177
capture rename a6_02_13 s178
capture rename a6_02_14 s179
capture rename a6_02_15 s180
capture rename a6_03 s181
capture rename a6_04 s182
capture rename a6_05 s183
capture rename a6_06_1d s184
capture rename a6_06_1m s185
capture rename a6_06_1y s186
capture rename a6_06_2d  s187
capture rename a6_06_2m s188
capture rename a6_06_2y s189
capture rename a6_07d s190
capture rename a6_07m s191
capture rename a6_07y s192
capture rename a6_08 s193
capture rename a6_09 s194
capture rename a6_10 s195
capture rename a6_11 s196
capture rename a6_12 s197
capture rename a6_13 s198
capture rename a6_14 s199
capture rename a6_15 s200
capture rename a7_01 s201
capture rename a7_02 s202
capture rename a7_03 s203
capture rename a7_04 s204
capture rename a7_05 s205
capture rename a7_06 s206
capture rename a7_07 s207
capture rename a7_08 s208
capture rename a7_09 s209
capture rename a7_10 s210
capture rename a7_11 s211
capture rename a7_12 s212
capture rename a7_13 s213
capture rename a7_14 s214

** non-automated ones:
capture rename g5_02 sex
capture rename g5_04a age
drop g1* g2* g3* g4* g5* s24 s26 s65 s117 s144 s160 s177 s181 s184 s185 s186 s187 s188 s189 s190 s191 s192 s193 s196 s197 s198 s199 s200 s201 s202 s203 s204 s205 s206 s207 s208 s209 s210 s211 s212 s213 s214
label drop _all
order site module sid gs* va* age sex s*

** age and sex:
xtile ageq = age, nq(4)
levelsof ageq, local(quin)
foreach q of local quin {
    gen s8888`q' = 0
    replace s8888`q' = 1 if ageq==`q'
}
label var s88881 "age quartile 1"
label var s88882 "age quartile 2"
label var s88883 "age quartile 3"
label var s88884 "age quartile 4"
drop ageq

recode sex (1 = 0)
recode sex (2 = 1)
drop if sex==9
label define sex 1 "female" 0  "male"
label values sex sex


** save temp copy just to use in a second:
tempfile adultdata
save `adultdata', replace


*******************************
** ADD ON FREE TEXT
**********************************

    ** Bring in the free text from tm
    if 1==1 {
        use "J:\Project\VA\Publication\FreeText\Words\Adult_text.dta", clear
        merge 1:1 sid using `adultdata', nogen
    }


*******************************
** DURATION SYMPTOMS
**********************************
***********************************
** Use mad estimator to make cutoff (OLD WAY)
*************************************


if 1==0 {
  ** identify the duration symptoms:
 local dur_symps = "age s15 s17 s22 s32 s39 s41 s43 s45 s50 s54 s59 s67 s73 s77 s81 s85 s88 s90 s93 s96 s99 s103 s106 s125 s128 s133 s147 s148 s163"

foreach s of varlist `dur_symps' {
    replace `s' = 1000 if `s' > 1000 & `s' != .
}


tempfile adultdata
save `adultdata', replace
save "`dump'/adult_pre_cutoff.dta", replace



** get mean of duration variables by cause:
collapse (mean) `dur_symps', by(`cause_var')

mkmat s*, matrix(means)
count
local rows = r(N)

** get the median of the means:
preserve
    collapse (median) s* age
    mkmat s* age, matrix(medians)
restore

** get the absolute value of (mean - median of means)
foreach s of varlist `dur_symps' {
    matrix dur  = medians[1, "`s'"]
    local dur = dur[1,1]
    replace `s' = abs(`s' - `dur')
}

** get the median of these values - -this will be used as the MAD estimator to dichotomize:
preserve
    collapse (median) s* age
    mkmat s* age, matrix(medians2)
restore

** use the data again:
use `adultdata', clear

collapse (mean) `dur_symps', by(`cause_var')
collapse (median) s* age

foreach s of local dur_symps {
    matrix mad = medians2[1, "`s'"]
    local mad = mad[1,1]
    replace `s' = `s' + 2*`mad'
}

mkmat s* age, matrix(cutoffs)

save "`dump'/adult_cutoffs.dta", replace

use `adultdata', clear

foreach s of local dur_symps {
    matrix cutoff = cutoffs[1, "`s'"]
    local cutoff = cutoff[1,1]
    replace `s' = 1 if `s'>=`cutoff' & `s' != .
    replace `s' = 0 if `s'!= 1
}
save `adultdata', replace
}

*************************************
** create cutoff at median (NEW WAY)
***************************************
** create a cutoff matrix for community data
** this is the age quartile cutoffs
_pctile age, percentiles(25 50 75)
preserve
clear
set obs 1
gen age_p25=`r(r1)'
gen age_p50=`r(r2)'
gen age_p75=`r(r3)'

save "`dump'/adult_cutoffs.dta", replace
restore


 ** DROPPED OUT s163 (Injury Duration) for new method
if 1==1 {
 ** exclude s163 (injury dur) because we are combining this with other info.
    ** identify the duration symptoms:
 local dur_symps = "age s15 s17 s22 s32 s39 s41 s43 s45 s50 s54 s59 s67 s73 s77 s81 s85 s88 s90 s93 s96 s99 s103 s106 s125 s128 s133 s147 s148"

foreach s of varlist `dur_symps' {
    replace `s' = 1000 if `s' > 1000 & `s' != .
}


tempfile adultdata
save `adultdata', replace
save "`dump'/adult_pre_cutoff.dta", replace
** get median of duration variables by cause:
foreach var of local dur_symps {
    use `adultdata', clear
    keep `var'
    drop if `var'==0
    drop if `var'==.
    
    collapse (median) `var'
    local median_`var'=`var'

    ** save these cutoffs as well
    use "`dump'/adult_cutoffs.dta", clear
    gen `var'=`median_`var''
    save "`dump'/adult_cutoffs.dta", replace
}

use `adultdata', clear

foreach s of local dur_symps {
    replace `s' = 1 if `s'>=`median_`s'' & `s' != .
    replace `s' = 0 if `s'!= 1
}
save `adultdata', replace
}

**********************
** New way to count s163- injury duration with injury questions
if 1==1 {
use `adultdata', clear

** get the 95th percentile of s163 for true injury deaths
preserve
keep if va46==5 | va46==15 | va46== 18 | va46== 19 | va46== 21 | va46==34| va46== 38 | va46==41 | va46==45
_pctile s163, percentiles(95)
local injury_cut=r(r1)

use "`dump'/adult_cutoffs.dta", clear
gen injury_cut=`injury_cut'
save "`dump'/adult_cutoffs.dta", replace
restore

** these are the injury indicators, only yes if under the cutoff (about 30 days)
foreach x of varlist s151-s157 s159-s162 {
    replace `x'=0 if `x'==1 & s163>`injury_cut'
}

drop s163
}

********************************************
** renaming is done, start the recategorization:
*****************************************
gen s36991 = 0
replace s36991 = 1 if s36 == 1
gen s36992 = 0
replace s36992 = 1 if s36 == 2 | s36 == 3
label var s36991 "Loss of weight was slight"
label var s36992 "Loss of weight was moderate to large"
order s36991 s36992, before(s36)
drop s36

gen s18991 = 0
replace s18991 = 1 if s18 == 1
gen s18992 = 0
replace s18992 = 1 if s18 == 2 | s18 == 3
label var s18991 "Severity of fever was mild"
label var s18992 "Severity of fever was moderate to large"
order s18991 s18992, before(s18)
drop s18

gen s19991 = 0
replace s19991 = 1 if s19 == 1
gen s19992 = 0
replace s19992 = 1 if s19 == 2
label var s19991 "Pattern of fever was continuous"
label var s19992 "Pattern of fever was on-and-off"
order s19991 s19992, before(s19)
drop s19

gen s23991 = 0
replace s23991 = 1 if s23 == 1 | s25 == 1
gen s23992 = 0
replace s23992 = 1 if s23 == 2 | s25 == 2
gen s23993 = 0
replace s23993 = 1 if s23 == 3 | s25 == 3
gen s23994 = 0
replace s23994 = 1 if s23 == 4 | s25 == 4
label var s23991 "Rash was located on face"
label var s23992 "Rash was located on trunk"
label var s23993 "Rash was located on extremities"
label var s23994 "Rash was located everywhere"
order s23991 s23992 s23993 s23994, before(s23)
drop s23 s25

gen s56991 = 0
replace s56991 = 1 if s56 == 1 | s57 == 1
gen s56992 = 0
replace s56992 = 1 if s56 == 2 | s57 == 2
gen s56993 = 0
replace s56993 = 1 if s56 == 3 | s57 == 3
gen s56994 = 0
replace s56994 = 1 if s56 == 4 | s57 == 4
label var s56991 "Breathing difficulty worse in lying position"
label var s56992 "Breathing difficulty worse in sitting position"
label var s56993 "Breathing difficulty worse in walking position"
label var s56994 "Breathing difficulty not worse in any position"
order s56991 s56992 s56993 s56994, before(s56)
drop s56 s57

gen s55991 = 0
replace s55991 = 1 if s55 == 1
gen s55992 = 0
replace s55992 = 1 if s55 == 2
label var s55991 "Breathing difficulty was continuous"
label var s55992 "Breathing difficulty was on-and-off"
order s55991 s55992, before(s55)
drop s55

recode s62 (1=0) (2=0) (3=1) (8=0) (9=0)
label var s62 "Pain greater than 24 hours"

gen s64991 = 0
replace s64991 = 1 if s64 == 1 | s64 == 2
gen s64992 = 0
replace s64992 = 1 if s64 == 3
label var s64991 "Pain located in chest"
label var s64992 "Pain located in left arm"
order s64991 s64992, before(s64)
drop s64

recode s78 (1=0) (2=0) (3=1) (8=0) (9=0)
label var s78 "Difficulty swallowing both solids and liquids"

gen s82991 = 0
replace s82991 = 1 if s82 == 2 | s83 == 2
label var s82991 "Pain located in lower belly"
order s82991, before(s82)
drop s82 s83

recode s86 (1=0) (2=1) (8=0) (9=0)
label var s86 "Slowly protruding belly"

recode s91 (2=0) (8=0) (9=0)
label var s91 "Rapid headache onset"

recode s95 (2=0) (8=0) (9=0)
label var s95 "Sudden loss of consciousness"

recode s100 (2=0) (8=0) (9=0)
label var s100 "Sudden confusion"

gen s150991 = 0
replace s150991 = 1 if s150 == 1
gen s150992 = 0
replace s150992 = 1 if s150 == 2 | s150 == 3
label var s150991 "Amount of alcohol drank daily was low"
label var s150992 "Amount of alcohol drank daily was moderate to large"
order s150991 s150992, before(s150)
drop s150

** based on clinical evidence combine right side paralyzed s107 and left side paralyzed s108 together
replace s107=s108 + s107
label var s107 "Paralyzed on one side (arm and leg)"
drop s108

** ensure all binary variables actually ARE 0 or 1:
capture replace s1 = 0 if s1 != 1
capture replace s2 = 0 if s2 != 1
capture replace s3 = 0 if s3 != 1
capture replace s4 = 0 if s4 != 1
capture replace s5 = 0 if s5 != 1
capture replace s6 = 0 if s6 != 1
capture replace s7 = 0 if s7 != 1
capture replace s8 = 0 if s8 != 1
capture replace s9 = 0 if s9 != 1
capture replace s10 = 0 if s10 != 1
capture replace s11 = 0 if s11 != 1
capture replace s12 = 0 if s12 != 1
capture replace s13 = 0 if s13 != 1
capture replace s14 = 0 if s14 != 1
capture replace s16 = 0 if s16 != 1
capture replace s20 = 0 if s20 != 1
capture replace s21 = 0 if s21 != 1
capture replace s27 = 0 if s27 != 1
capture replace s28 = 0 if s28 != 1
capture replace s29 = 0 if s29 != 1
capture replace s30 = 0 if s30 != 1
capture replace s31 = 0 if s31 != 1
capture replace s33 = 0 if s33 != 1
capture replace s34 = 0 if s34 != 1
capture replace s35 = 0 if s35 != 1
capture replace s37 = 0 if s37 != 1
capture replace s38 = 0 if s38 != 1
capture replace s40 = 0 if s40 != 1
capture replace s42 = 0 if s42 != 1
capture replace s44 = 0 if s44 != 1
capture replace s46 = 0 if s46 != 1
capture replace s47 = 0 if s47 != 1
capture replace s48 = 0 if s48 != 1
capture replace s49 = 0 if s49 != 1
capture replace s51 = 0 if s51 != 1
capture replace s52 = 0 if s52 != 1
capture replace s53 = 0 if s53 != 1
capture replace s58 = 0 if s58 != 1
capture replace s60 = 0 if s60 != 1
capture replace s61 = 0 if s61 != 1
capture replace s63 = 0 if s63 != 1
capture replace s66 = 0 if s66 != 1
capture replace s68 = 0 if s68 != 1
capture replace s69 = 0 if s69 != 1
capture replace s70 = 0 if s70 != 1
capture replace s71 = 0 if s71 != 1
capture replace s72 = 0 if s72 != 1
capture replace s74 = 0 if s74 != 1
capture replace s75 = 0 if s75 != 1
capture replace s76 = 0 if s76 != 1
capture replace s79 = 0 if s79 != 1
capture replace s80 = 0 if s80 != 1
capture replace s84 = 0 if s84 != 1
capture replace s87 = 0 if s87 != 1
capture replace s89 = 0 if s89 != 1
capture replace s92 = 0 if s92 != 1
capture replace s94 = 0 if s94 != 1
capture replace s97 = 0 if s97 != 1
capture replace s98 = 0 if s98 != 1
capture replace s101 = 0 if s101 != 1
capture replace s102 = 0 if s102 != 1
capture replace s104 = 0 if s104 != 1
capture replace s105 = 0 if s105 != 1
capture replace s107 = 0 if s107 != 1
capture replace s108 = 0 if s108 != 1
capture replace s109 = 0 if s109 != 1
capture replace s110 = 0 if s110 != 1
capture replace s111 = 0 if s111 != 1
capture replace s112 = 0 if s112 != 1
capture replace s113 = 0 if s113 != 1
capture replace s114 = 0 if s114 != 1
capture replace s115 = 0 if s115 != 1
capture replace s116 = 0 if s116 != 1
capture replace s118 = 0 if s118 != 1
capture replace s119 = 0 if s119 != 1
capture replace s120 = 0 if s120 != 1
capture replace s121 = 0 if s121 != 1
capture replace s122 = 0 if s122 != 1
capture replace s123 = 0 if s123 != 1
capture replace s124 = 0 if s124 != 1
capture replace s126 = 0 if s126 != 1
capture replace s127 = 0 if s127 != 1
capture replace s129 = 0 if s129 != 1
capture replace s130 = 0 if s130 != 1
capture replace s131 = 0 if s131 != 1
capture replace s132 = 0 if s132 != 1
capture replace s134 = 0 if s134 != 1
capture replace s135 = 0 if s135 != 1
capture replace s136 = 0 if s136 != 1
capture replace s137 = 0 if s137 != 1
capture replace s138 = 0 if s138 != 1
capture replace s139 = 0 if s139 != 1
capture replace s140 = 0 if s140 != 1
capture replace s141 = 0 if s141 != 1
capture replace s142 = 0 if s142 != 1
capture replace s143 = 0 if s143 != 1
capture replace s145 = 0 if s145 != 1
capture replace s146 = 0 if s146 != 1
capture replace s149 = 0 if s149 != 1
capture replace s151 = 0 if s151 != 1
capture replace s152 = 0 if s152 != 1
capture replace s153 = 0 if s153 != 1
capture replace s154 = 0 if s154 != 1
capture replace s155 = 0 if s155 != 1
capture replace s156 = 0 if s156 != 1
capture replace s157 = 0 if s157 != 1
capture replace s158 = 0 if s158 != 1
capture replace s159 = 0 if s159 != 1
capture replace s161 = 0 if s161 != 1
capture replace s162 = 0 if s162 != 1
capture replace s164 = 0 if s164 != 1
capture replace s165 = 0 if s165 != 1
capture replace s166 = 0 if s166 != 1
capture replace s167 = 0 if s167 != 1
capture replace s168 = 0 if s168 != 1
capture replace s169 = 0 if s169 != 1
capture replace s170 = 0 if s170 != 1
capture replace s171 = 0 if s171 != 1
capture replace s172 = 0 if s172 != 1
capture replace s173 = 0 if s173 != 1
capture replace s174 = 0 if s174 != 1
capture replace s175 = 0 if s175 != 1
capture replace s176 = 0 if s176 != 1
capture replace s178 = 0 if s178 != 1
capture replace s179 = 0 if s179 != 1
capture replace s180 = 0 if s180 != 1
capture replace s182 = 0 if s182 != 1
capture replace s183 = 0 if s183 != 1
capture replace s194 = 0 if s194 != 1
capture replace s195 = 0 if s195 != 1

gen lastvar = 1

foreach var of varlist age-lastvar {
     count if `var' > 1
     count if `var' < 0
    }


** get rid of nonvarying symptoms:
foreach var of varlist age-lastvar {
    quietly summarize `var'
    local mean = r(mean)
     if `mean'==0 drop `var'
     if `mean'==0 di "`var'"
     if `mean'==1 drop `var'
}

drop module

********************************************************
** DROP SCREENERS
************************************************************
** questions dropped:
** Was care sought outside the home while [name] had this illness?
** Care sought - traditional healer
** Care sought - homeopath
** Care sought - religious leader
** Care sought - government hospital
** Care sought - government health center or clinic
** Care sought - private hospital
** Care sought - community based practitioner
** Care sought - trained birth attendant
** Care sought - private physician
** Care sought - pharmacy
** Care sought - other provider
** Care sought - relative, friend
** Do you have any health records that belonged to the deceased?
** Can I see the health records?
** Was a death certificate issued?
** Can I see the death certificate? 

local screen_symps= "s164 s165 s166 s167 s168 s169 s170 s172 s173 s174 s175 s176 s178 s182 s183 s194 s195"

foreach var of local screen_symps {
    drop `var'
}


order  sid site gs* va* age sex s* s9999*
order s9999*, last
save "`dump'/AdultDataLabeled.dta", replace
label drop _all
order  sid site gs* va* age sex s* s9999*
order s9999*, last


** save final versions of the datasetes:
save "`out_dir'/AdultData.dta", replace
** save "J:\Project\VA\external_va\Data\Symptom Data\Validation\AdultData.dta", replace
outsheet using "`out_dir'/AdultData.csv", comma replace
