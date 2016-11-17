** Author: Spencer (edited by Pete)
** Date: Some time in 2010?
** Purpose: Prep Neonate s variables from pre-symptom variables

clear all

set mem 500m

if ("`c(os)'"=="Windows") local prefix	"J:"
else local prefix "/home/j"

** directories
local repo "`1'"
if "`repo'" == "" local repo "C:/Users/josephj7/Desktop/repos/va/tariff_2"
global wdir "`repo'/data/working"
global code_dir "`repo'/src"
local in_dir "$wdir"
local out_dir "$wdir"
local mrr "$wdir"
local dump "$wdir/dump"
local code "$code_dir"
local tariff_prep "$wdir"

global who="Neonate"

local gen_splits = 0

use "`in_dir'/VA Final - Neonate.dta", clear

local cause_var va34

** drop variables which don't serve any purpose right now:
quietly {
	capture drop g1_01d
	capture drop g1_01m
	capture drop g1_01y
    capture drop g1_05
	capture drop g1_06d
	capture drop g1_06m
	capture drop g1_06y
	capture drop g1_07a
    capture drop g1_07b
    capture drop g1_07c
    capture drop g1_08
	capture drop g1_09
	capture drop g1_10
	capture drop g2_01
	capture drop g2_02
	capture drop g2_03ad
	capture drop g2_03am
	capture drop g2_03ay
	capture drop g2_03bd
	capture drop g2_03bm
	capture drop g2_03by
	capture drop g2_03cd
	capture drop g2_03cm
	capture drop g2_03cy
	capture drop g2_03dd
	capture drop g2_03dm
	capture drop g2_03dy
	capture drop g2_03ed
	capture drop g2_03em
	capture drop g2_03ey
	capture drop g2_03fd
	capture drop g2_03fm
	capture drop g2_03fy
	capture drop g3_01
	capture drop g4_02
	capture drop g4_03a
	capture drop g4_03b
	capture drop g4_04
	capture drop g4_05
	capture drop g4_06
	capture drop g4_07
	capture drop g4_08
	capture drop g5_01d
	capture drop g5_01m
	capture drop g5_01y
	capture drop g5_03d
	capture drop g5_03m
	capture drop g5_03y
	capture drop g5_05
	capture drop g5_06a
	capture drop g5_06b
	capture drop g5_07
	capture drop g5_08

}


capture rename g5_04a s2
capture rename g5_04b s3
capture rename g5_04c s4
capture rename c1_01 s5
capture rename c1_02 s6
capture rename c1_03 s7
capture rename c1_04 s8
capture rename c1_05b s10
capture rename c1_06a s11
capture rename c1_07 s13
capture rename c1_08b s14
capture rename c1_09 s15
capture rename c1_11 s16
capture rename c1_12 s17
capture rename c1_13 s18
capture rename c1_14 s19
capture rename c1_15 s20
capture rename c1_16 s21
capture rename c1_17 s22
capture rename c1_18 s23
capture rename c1_19_1 s24
capture rename c1_19_2 s25
capture rename c1_19_3 s26
capture rename c1_19_4a s27
capture rename c1_20b s28
capture rename c1_21b s29
capture rename c1_22a s30
capture rename c1_25 s31
capture rename c1_26 s32
capture rename c2_01_1 s33
capture rename c2_01_2 s34
capture rename c2_01_3 s35
capture rename c2_01_4 s36
capture rename c2_01_5 s37
capture rename c2_01_6 s38
capture rename c2_01_7 s39
capture rename c2_01_8 s40
capture rename c2_01_9 s41
capture rename c2_01_10 s42
capture rename c2_01_12 s43
** no longer wanat Complications: placenta came out first as a symptom because only found in Mexican data
drop c2_01_14
** capture rename c2_01_14 s44
capture rename c2_02b s45
capture rename c2_03 s46
capture rename c2_04 s47
capture rename c2_05b s48
capture rename c2_06 s49
capture rename c2_07 s50
capture rename c2_08a s51
capture rename c2_09 s52
capture rename c2_10b s53
capture rename c2_11 s54
capture rename c2_12 s55
capture rename c2_13a s56
capture rename c2_15a s57
capture rename c2_17 s58
capture rename c2_18 s59
capture rename c3_01 s60
capture rename c3_02 s61
capture rename c3_03_1 s62
capture rename c3_03_2 s63
capture rename c3_03_3 s64
capture rename c3_04 s65
capture rename c3_05 s66
capture rename c3_06 s67
capture rename c3_07 s68
capture rename c3_08 s69
capture rename c3_09 s70
capture rename c3_10 s71
capture rename c3_11 s72
capture rename c3_12 s73
capture rename c3_13 s74
capture rename c3_14b s75
capture rename c3_15 s76
capture rename c3_16 s77
capture rename c3_17 s78
capture rename c3_18b s79
capture rename c3_19b s80
capture rename c3_20 s81
capture rename c3_21b s82
capture rename c3_22b s83
capture rename c3_23 s84
capture rename c3_24 s85
capture rename c3_25 s86
capture rename c3_26 s87
capture rename c3_27b s88
capture rename c3_28b s89
capture rename c3_29 s90
capture rename c3_30b s91
capture rename c3_31b s92
capture rename c3_32 s93
capture rename c3_33 s94
capture rename c3_34 s95
capture rename c3_35 s96
capture rename c3_36 s97
capture rename c3_37 s98
capture rename c3_38 s99
capture rename c3_39 s100
capture rename c3_40 s101
capture rename c3_41 s102
capture rename c3_42 s103
capture rename c3_44 s104
capture rename c3_45b s105
capture rename c3_46 s106
capture rename c3_47 s107
capture rename c3_48 s108
capture rename c3_49 s109
capture rename c4_01 s110
capture rename c4_02b s111
capture rename c4_03 s112
capture rename c4_04 s113
capture rename c4_05 s114
capture rename c4_06 s115
capture rename c4_07b s116
capture rename c4_08b s117
capture rename c4_09 s118
capture rename c4_10b s119
capture rename c4_11 s120
capture rename c4_12 s121
capture rename c4_13b s122
capture rename c4_14 s123
capture rename c4_15 s124
capture rename c4_16 s125
capture rename c4_17b s126
capture rename c4_18 s127
capture rename c4_19b s128
capture rename c4_20 s129
capture rename c4_22 s130
capture rename c4_23 s131
capture rename c4_24 s132
capture rename c4_25 s133
capture rename c4_26 s134
capture rename c4_27 s135
capture rename c4_28 s136
capture rename c4_29 s137
capture rename c4_30 s138
capture rename c4_31_1 s139
capture rename c4_31_2 s140
capture rename c4_32 s141
capture rename c4_33b s142
capture rename c4_34 s143
capture rename c4_35 s144
capture rename c4_36 s145
capture rename c4_37b s146
capture rename c4_38 s147
capture rename c4_39 s148
capture rename c4_40 s149
capture rename c4_41 s150
capture rename c4_42 s151
capture rename c4_43 s152
capture rename c4_44 s153
capture rename c4_46 s154
capture rename c4_47_1 s155
capture rename c4_47_2 s156
capture rename c4_47_3 s157
capture rename c4_47_4 s158
capture rename c4_47_5 s159
capture rename c4_47_6 s160
capture rename c4_47_7 s161
capture rename c4_47_8a s162
capture rename c4_47_9 s163
capture rename c4_47_11 s164
capture rename c4_48 s165
capture rename c4_49b s166
capture rename c5_01 s167
capture rename c5_02_1 s168
capture rename c5_02_2 s169
capture rename c5_02_3 s170
capture rename c5_02_4 s171
capture rename c5_02_5 s172
capture rename c5_02_6 s173
capture rename c5_02_7 s174
capture rename c5_02_8 s175
capture rename c5_02_9 s176
capture rename c5_02_10 s177
capture rename c5_02_11a s178
capture rename c5_02_12 s179
capture rename c5_07_1 s180
capture rename c5_07_2 s181
capture rename c5_09 s182
capture rename c5_12 s183
capture rename c5_13 s184
capture rename c5_14 s185
capture rename c5_15 s186
capture rename c5_16 s187
capture rename c5_17 s188
capture rename c5_18 s189
capture rename c5_19 s190

** non-automated ones:

rename g5_02 sex
rename c1_05 s9
rename c1_20 s28
rename c1_21 s29
rename c2_02 s45
rename c2_05 s48
rename c2_10 s53
rename c3_14 s75
rename c3_18 s79
rename c3_19 s80
rename c3_21 s82
rename c3_22 s83
rename c3_27 s88
rename c3_28 s89
rename c3_30 s91
rename c3_31 s92

drop c1_06b
drop c1_08a
drop c1_10*
drop c1_19*
drop c2_01_11
drop c2_01_13
drop  c3_03_4a 
drop c3_03_4b 
drop c3_03_5 
drop c3_03_6
drop c3_43
drop  c3_45a
drop  c5_02_11b c5_02_13 c5_02_14 c5_03 c5_04 c5_05 c5_06_1d c5_06_1m c5_06_1y c5_06_2d c5_06_2m c5_06_2y c5_08d c5_08m c5_08y c5_10 c5_11 s183 s184 s185 s186 s187 c6_01 c6_02 c6_03 c6_04 c6_05 c6_06 c6_07 c6_08 c6_09 c6_10 c6_11 c6_12 c6_13 c6_14
drop  c1_22b c1_23 c1_24 c1_24d c1_24m c1_24y module
drop  c2_08b c2_13b c2_14 c2_15b
drop s182

order site sid va* gs* sex s*



** age and sex:

gen marker = 0
replace marker = 1 if s2==999 & s3==99 & s4==99

replace s2 = . if marker==1
replace s3 = . if marker==1
replace s4 = . if marker==1

replace s2 = 0 if s2==999
replace s3 = 0 if s3==99
replace s4 = 0 if s4==99

drop marker



replace s3 = s3*30

replace s4 = s3 if s4 == 0 & s3 > 1 & s3 != .

drop s2 s3

xtile s4q = s4, nq(4)

levelsof s4q, local(quin)

foreach q of local quin {
	gen s499`q' = 0
	replace s499`q' = 1 if s4q==`q'
}

label var s4991 "age quartile 1"
label var s4993 "age quartile 3"
label var s4994 "age quartile 4"
drop s4q

recode sex (1 = 0)
recode sex (2 = 1)

label define sex 1 "female" 0  "male"
label values sex sex
		


** save temp copy just to use in a second:
save "`dump'/neonataldata", replace

*******************************
** ADD ON FREE TEXT
**********************************

** README WORDS NO LONGER MATCH UP TO OUR MODULES...THIS MAKES THIS PARTICULAR MERGE IMPOSSIBLE
** therefore, just merge on previously create mrr from published material
if 1==0 {
    use  "$wdir/NeonateData.dta", clear
    keep sid s99991-s999939

    merge 1:1 sid using "`dump'/neonataldata"
    keep if _m==3
    drop _m
}

** Bring in the free text from tm
if 1==1 {
    use "$wdir/freetext/Neonate_text.dta", clear
    merge 1:1 sid using "`dump'/neonataldata", nogen
}

drop if va34==.

**************************
** Duration Variables
*********************************
***********************************
** Use mad estimator to make cutoff (OLD WAY)
*************************************
if 0==1 {


save "`dump'/neonataldata", replace
save "`dump'/neonate_pre_cutoff.dta", replace




** identify the duration symptoms:
local dur_symps = "s4 s9 s14 s28 s29 s31 s45 s48 s53 s75  s79 s80 s82 s83 s88 s89 s91 s92"



** get mean of duration variables by cause:
collapse (mean) `dur_symps', by(`cause_var')

mkmat s*, matrix(means)
count
local rows = r(N)

** get the median of the means:
preserve
	collapse (median) s*
	mkmat s*, matrix(medians)
restore

** get the absolute value of (mean - median of means)
foreach s of varlist `dur_symps' {
	matrix dur  = medians[1, "`s'"]
	local dur = dur[1,1]
	replace `s' = abs(`s' - `dur')
}

** get the median of these values - -this will be used as the MAD estimator to dichotomize:

preserve
	collapse (median) s*
	mkmat s*, matrix(medians2)
restore

** use the data again:
use "`dump'/neonataldata", clear

collapse (mean) `dur_symps', by(`cause_var')
collapse (median) s*

** drop out s14 from the symps here cause i want to make it a low cutoff instead of high since it si birth weight.
local dur_symps = "s4 s9 s28 s29 s31 s45 s48 s53 s75 s80 s79 s82 s83 s88 s89 s91 s92"
foreach s of local dur_symps {
	matrix mad = medians2[1, "`s'"]
	local mad = mad[1,1]
	replace `s' = `s' + 2*`mad'
	}

** Did each one of the low cutoffs separately, but I am going to leave it as mean-2*mad	
matrix mad = medians2[1, "s14"]
local mad = mad[1,1]
replace s14 = s14 - 2*`mad'

mkmat s*, matrix(cutoffs)

	
use "`dump'/neonataldata", clear
local dur_symps = "s4 s9 s28 s29 s31 s45 s48 s53 s75 s80 s79 s82 s83 s88 s89 s91 s92"

foreach s of local dur_symps {
	matrix cutoff = cutoffs[1, "`s'"]
	local cutoff = cutoff[1,1]
	replace `s' = 1 if `s'>=`cutoff' & `s' != .
	replace `s' = 0 if `s'!= 1
}

local dur_symps = "s14"

foreach s of local dur_symps {
	matrix cutoff = cutoffs[1, "`s'"]
	local cutoff = cutoff[1,1]
	replace `s' = 1 if `s'<=`cutoff' & `s' != .
	replace `s' = 0 if `s'!= 1
}
}

*************************************
** create cutoff at median (NEW WAY)
***************************************
 ** this is the age quintile cutoffs, save in cutoff file
_pctile s4, percentiles(25 50 75)
preserve
clear
set obs 1
gen age_p25=`r(r1)'
gen age_p50=`r(r2)'
gen age_p75=`r(r3)'

save "`dump'/neonate_cutoffs.dta", replace
restore

if 1==1 {

** identify the duration symptoms:
local dur_symps = "s4 s9 s14 s28 s29 s31 s45 s48 s53 s75  s79 s80 s82 s83 s88 s89 s91 s92"
    
    
tempfile neonataldata
save `neonataldata', replace
save "`dump'/neonate_pre_cutoff.dta", replace
** get median of duration variables by cause:

foreach var of local dur_symps {
	use `neonataldata', clear
	keep `var'
	drop if `var'==0
	drop if `var'==.
	
	collapse (median) `var'
	local median_`var'=`var'
    
    ** save these cutoffs as well
    use "`dump'/neonate_cutoffs.dta", clear
    gen `var'=`median_`var''
    save "`dump'/neonate_cutoffs.dta", replace
}

use `neonataldata', clear

foreach s of local dur_symps {
	replace `s' = 1 if `s'>=`median_`s'' & `s' != .
	replace `s' = 0 if `s'!= 1
}
save `neonataldata', replace
} 
    

********************************************
** renaming is done, start the recategorization:
*****************************************  
    
gen s5_1 = 0
replace s5_1 = 1 if s5 ==2
drop s5
rename s5_1 s5
label var s5 "deceased was a multiple birth"


gen s6_1 = 0
replace s6_1 = 1 if s6==2 | s6==3
drop s6
rename s6_1 s6
label var s6 "baby was 2nd or later in the birth order"

 gen s8_1 = 0
 replace s8_1 = 1 if s8 == 1
 label var s8_1 "mother died during delivery"
 
 ** gen variable did mom die after?
 gen s8_2 = 0
 replace s8_2 = 1 if s8 == 2
 label var s8_2 "mother died after delivery"
 drop s8
 
gen s11_1 = 0
replace s11_1 = 1 if s11==4 | s11==5
drop s11
label var s11 "baby was not born in a health facility"

gen s13_1 = 0
replace s13_1 = 1 if s13==1 | s13==2
drop s13
rename s13_1 s13
label var s13 "baby was small or very small"

gen s16_1 = 0
replace s16_1 = 1 if s16==2
drop s16
rename s16_1 s16
label var s16 "Baby was born dead"

capture gen s30_1 = 0
capture replace s30_1 = 1 if s30==3 | s30==4
drop s30
label var s30_1 "deceased didn't die in a hospital"

capture gen s46_1 = 0
capture replace s46_1 = 1 if s46==1
label var s46_1 "pregnancy ended early"
 
capture gen s46_2 = 0
capture replace s46_2 = 1 if s46==3
drop s46
label var s46_2 "pregnancy ended late"

capture gen s49_1 = 0
capture replace s49_1 = 1 if s49== 2
drop s49
label var s49_1 "water broke after labor"

gen s50_1 = 0
replace s50_1 = 1 if s50 == 2
drop s50
label var s50_1 "water broke a day or more before labor"

capture gen s51_1 = 0
capture replace s51_1 = 1 if s51 == 1 | s51==3
drop s51
label var s51_1 "water wasn't normal color"

capture gen s55_1 = 0
capture replace s55_1 = 1 if s55 == 1 | s55==2
drop s55
label var s55_1 "insufficient vaccines"

capture gen s56_1 = 0
capture replace s56_1 = 1 if s56 == 4 | s56== 5
drop s56
label var s56_1 "pregnancy not in health facility"

capture gen s57_1 = 0
capture replace s57_1 = 1 if s57 != 1 & s57 != 2
drop s57
label var s57_1 "wasn't delivered by a medical professional"


capture gen s58_1 = 0
capture replace s58_1 = 1 if s58 == 1

capture gen s58_2 = 0
capture replace s58_2 = 1 if s58 == 2

capture gen s58_3 = 0
capture replace s58_3 = 1 if s58 == 3

capture gen s58_4 = 0
capture replace s58_4 = 1 if s58 == 4

drop s58

capture gen s69_1 = 0
capture replace s69_1 = 1 if s69 == 3 | s69 == 4
drop s69
label var s69_1 "baby didn't cry right after birth"

capture gen s71_1 = 0
capture replace s71_1 = 1 if s71 == 2
drop s71
label var s71_1 "baby died for more than a day"

capture gen s76_1 = 0
capture replace s76_1 = 1 if s76 == 2
label var s76_1 "baby stopped sucking more than a day before death"
drop s76

gen s105_1 = 0
replace s105_1  = 1 if s105 > 1 & s105 != .
drop s105
rename s105_1 s105
label var s105 "more than 1 loose stools"

capture gen s113_1 = 0
capture replace s113_1 = 1 if s113==3
drop s113

capture gen s114_1 = 0
capture replace s114_1 = 1 if s114==2 | s114==3
drop s114

capture gen s135_1 = 0
capture replace s135_1 = 1 if s135==3
drop s135

capture gen s139_1 = 0
capture replace s139_1 = 1 if s139==1
drop s139
 
capture gen s140_1 = 0
capture replace s140_1 = 1 if s140==1
drop s140

capture gen s141_1 = 0
capture replace s141_1 = 1 if s141==1
drop s141

** ensure all binary variables actually ARE 0 or 1:
capture replace s7 = 0 if s7 != 1   
capture replace s17 = 0 if s17 != 1
capture replace s18 = 0 if s18 != 1
capture replace s19 = 0 if s19 != 1
capture replace s20 = 0 if s20 != 1
capture replace s21 = 0 if s21 != 1
capture replace s22 = 0 if s22 != 1
capture replace s23 = 0 if s23 != 1
capture replace s24 = 0 if s24 != 1
capture replace s25 = 0 if s25 != 1
capture replace s26 = 0 if s26 != 1
capture replace s27 = 0 if s27 != 1
capture replace s32 = 0 if s32 != 1
capture replace s33 = 0 if s33 != 1
capture replace s34 = 0 if s34 != 1
capture replace s35 = 0 if s35 != 1
capture replace s36 = 0 if s36 != 1
capture replace s37 = 0 if s37 != 1
capture replace s38 = 0 if s38 != 1
capture replace s39 = 0 if s39 != 1
capture replace s40 = 0 if s40 != 1
capture replace s41 = 0 if s41 != 1
capture replace s42 = 0 if s42 != 1
capture replace s43 = 0 if s43 != 1
capture replace s44 = 0 if s44 != 1
capture replace s47 = 0 if s47 != 1
capture replace s52 = 0 if s52 != 1
capture replace s54 = 0 if s54 != 1
capture replace s59 = 0 if s59 != 1
capture replace s60 = 0 if s60 != 1
capture replace s61 = 0 if s61 != 1
capture replace s62 = 0 if s62 != 1
capture replace s63 = 0 if s63 != 1
capture replace s64 = 0 if s64 != 1
capture replace s65 = 0 if s65 != 1
capture replace s66 = 0 if s66 != 1
capture replace s67 = 0 if s67 != 1
capture replace s68 = 0 if s68 != 1
capture replace s70 = 0 if s70 != 1
capture replace s72 = 0 if s72 != 1
capture replace s73 = 0 if s73 != 1
capture replace s74 = 0 if s74 != 1
capture replace s77 = 0 if s77 != 1
capture replace s78 = 0 if s78 != 1
capture replace s81 = 0 if s81 != 1
capture replace s84 = 0 if s84 != 1
capture replace s85 = 0 if s85 != 1
capture replace s86 = 0 if s86 != 1
capture replace s87 = 0 if s87 != 1
capture replace s90 = 0 if s90 != 1
 capture replace s93 = 0 if s93 != 1
capture replace s94 = 0 if s94 != 1
capture replace s95 = 0 if s95 != 1
capture replace s96 = 0 if s96 != 1
capture replace s97 = 0 if s97 != 1
capture replace s98 = 0 if s98 != 1
capture replace s99 = 0 if s99 != 1
capture replace s100 = 0 if s100 != 1
capture replace s101 = 0 if s101 != 1
capture replace s102 = 0 if s102 != 1
capture replace s103 = 0 if s103 != 1
capture replace s104 = 0 if s104 != 1
capture replace s106 = 0 if s106 != 1
capture replace s107 = 0 if s107 != 1
capture replace s108 = 0 if s108 != 1
capture replace s109 = 0 if s109 != 1
capture replace s110 = 0 if s110 != 1
capture replace s112 = 0 if s112 != 1
capture replace s115 = 0 if s115 != 1
capture replace s118 = 0 if s118 != 1
capture replace s120 = 0 if s120 != 1
capture replace s121 = 0 if s121 != 1
capture replace s123 = 0 if s123 != 1
capture replace s124 = 0 if s124 != 1
capture replace s125 = 0 if s125 != 1
capture replace s127 = 0 if s127 != 1
capture replace s129 = 0 if s129 != 1
capture replace s130 = 0 if s130 != 1
capture replace s131 = 0 if s131 != 1
capture replace s132 = 0 if s132 != 1
capture replace s133 = 0 if s133 != 1
capture replace s134 = 0 if s134 != 1
capture replace s136 = 0 if s136 != 1
capture replace s137 = 0 if s137 != 1
capture replace s138 = 0 if s138 != 1
capture replace s143 = 0 if s143 != 1
capture replace s144 = 0 if s144 != 1
capture replace s145 = 0 if s145 != 1
capture replace s147 = 0 if s147 != 1
capture replace s148 = 0 if s148 != 1
capture replace s149 = 0 if s149 != 1
capture replace s150 = 0 if s150 != 1
capture replace s151 = 0 if s151 != 1
capture replace s152 = 0 if s152 != 1
capture replace s153 = 0 if s153 != 1
capture replace s154 = 0 if s154 != 1
capture replace s155 = 0 if s155 != 1
capture replace s156 = 0 if s156 != 1
capture replace s157 = 0 if s157 != 1
capture replace s158 = 0 if s158 != 1
capture replace s159 = 0 if s159 != 1
capture replace s160 = 0 if s160 != 1
capture replace s161 = 0 if s161 != 1
capture replace s162 = 0 if s162 != 1
capture replace s163 = 0 if s163 != 1
capture replace s164 = 0 if s164 != 1
capture replace s165 = 0 if s165 != 1
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
capture replace s177 = 0 if s177 != 1
capture replace s178 = 0 if s178 != 1
capture replace s179 = 0 if s179 != 1
capture replace s188 = 0 if s188 != 1
capture replace s189 = 0 if s189 != 1
capture replace s190 = 0 if s190 != 1


label var s5 "multiple birth"
label var s6 "2nd or later in birth order"
label var s8_1 "mother died before delivery"
label var s8_2 "mother died after delivery"

capture label var s11_1 "not born in a hospital"
capture label var s13_1 "decedent was small or very small"
capture label var s30_1 "didn't die in a hospital"
capture label var s16_1 "decedent was born dead"
capture label var s46_1 "early pregnancy"
capture label var s46_2 "late pregnancy"
capture label var s58_1 "pregancy: vaginal with forceps"
capture label var s58_2 "pregnancy: vaginal without forceps"
capture label var s58_3 "pregancy: vaginal don't know"
capture label var s58_4 "c-section"
capture label var s113_1 "severe fever"
capture label var s114_1 "fever not continuous"
capture label var s135_1 "unconsciousness started >24hrs before death"
capture label var s139_1 "decedent had face rash"
capture label var s140_1 "2nd rash var: face rash"
capture label var s141_1 "rash started on face"

** GOT RID OF 2nd Sex VAR
** ** recode second sex variable:
** recode s1 (1 = 0) (2 = 1)
** drop if s1==9
** drop s1

recode s15 (1 = 0) (2 = 1)

gen lastvar = 1

foreach var of varlist sex-lastvar {
	 count if `var' > 1
	 count if `var' < 0
	}


** rename these since the underscore causes problems down the road:
rename s8_1		s8991
rename s8_2		s8992
rename s11_1	s11991
rename s30_1	s30991
rename s46_1	s46991
rename s46_2	s46992
rename s49_1	s49991
rename s50_1	s50991
rename s51_1	s51991
rename s55_1	s55991
rename s56_1	s56991
rename s57_1	s57991
rename s58_1	s58991
rename s58_2	s58992
rename s58_3	s58993
rename s58_4	s58994
rename s69_1	s69991
rename s71_1	s71991
rename s76_1	s76991

rename s4 age

********************************************************
** DROP SCREENERS
************************************************************
** questions dropped
** Was care sought outside the home while the deceased had this illness?
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
** Care sought - traditional healer

local screen_symps= "s167 s168 s169 s170 s171 s172 s173 s174 s175 s176 s177 s178 s179"

foreach var of local screen_symps {
	drop `var'
}

*************************************
** Bring in weight for age variables....
**************************************

drop s180 s181
preserve
do "`code'/weight_for_age_who_standards.do"
restore

merge 1:1 sid using "`dump'/${who}_weightforage.dta", nogen

drop if va34==.

drop lastvar

order  sid site gs* va* age sex s* s9999*
order s9999*, last
compress
label drop _all

order  sid site gs* va* age sex s* s9999*
order s9999*, last
save "`dump'/NeonateDataLabeled.dta", replace
compress
label drop _all
order  sid site gs* va* age sex s*
order s9999*, last

** save final versions of the datasetes:
save "`out_dir'/NeonateData.dta", replace
** save "J:\Project\VA\external_va\Data\Symptom Data\Validation\NeonateData.dta", replace
outsheet using "`out_dir'/NeonateData.csv", comma replace

*************************************
** Generate Splits....
**************************************


 ** run the 75/25 split generation algorithm:
 global who = "Neonate"
 global cl = "`cause_var'"
 
** if `gen_splits'==1 do "J:/Project/VA/Publication/Data/Code/03_generate_splits.do"


*************************************
** Generate Tariff tables....
**************************************
        
        ** do "J:\Project\VA\Publication\Revised Data\Code\Tariff prep.do"
        
		** do "J:\Project\VA\Publication\Code\mrr symptoms map generation.do"
		** do "J:\Project\VA\Publication\Code\create va models based on symptoms sd.do"
