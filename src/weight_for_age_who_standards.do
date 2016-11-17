** Practice for making symptom vars for malnourished / severely malnourished children & neonates 
** Andrea Stewart
** February 22, 2013


clear all
set more off
capture log close
capture restore

** local who Child

local who "$who"
local in_dir "$wdir"

local who_standards "J:\Usable\Tools\Child Growth Standards\WHO Child Growth Standards 2006"


use "$wdir/VA Final - `who'.dta", clear

** fix missingness coding for weight from medical record
forvalues i= 1/2 {
	replace c5_07_`i' = . if c5_07_`i'==0
	replace c5_07_`i' = . if c5_07_`i'==9999
	replace c5_07_`i' = . if c5_07_`i'==99
	replace c5_07_`i' = . if c5_07_`i'==999


	}

*** age prep
*** use most recent record data

** Date of birth - clean up so you can get at least an estimated age
replace c1_10d = 0 if c1_10d == 99 
replace c1_10m = 0 if c1_10m == 99
replace c1_10y = 0 if c1_10y == 9999
                 
** generate how many months after Jan 1 1960 they were born
gen mofd = mofd(mdy(c1_10m, c1_10d, c1_10y))

** clean up medical record dates
replace c5_06_1d = . if c5_06_1d == 99
replace c5_06_1m = . if c5_06_1m == 99
replace c5_06_1y = . if c5_06_1y == 9999

replace c5_06_2d = . if c5_06_2d == 99
replace c5_06_2m = . if c5_06_2m == 99
replace c5_06_2y = . if c5_06_2y == 9999
                         
gen mofm1 = mofd(mdy(c5_06_1m, c5_06_1d, c5_06_1y))
gen mofm2 = mofd(mdy(c5_06_2m, c5_06_2d, c5_06_2y))					 

** Assume the health records match up (sometimes they have two weights but one date)
replace mofm2 = . if c5_07_2 ==.

** identify most recent medical record
gen max_age = max(mofm1, mofm2)

** Calculate age in months at last medical visit
gen month = max_age-mofd

** Drop out if they had a negative age
replace month = . if month<0

** all neonates are 0
if "`who'" == "Neonate" {
	replace month = 0 if c5_07_2 != . | c5_07_1 != .
}

** Generate a weight (in kg) variable that corresponds to the weight at most recent medical record
gen weight_kg = .

if "`who'" == "Child" {
	replace weight_kg = c5_07_1/1000 if max_age == mofm1
	replace weight_kg = c5_07_2/1000 if max_age == mofm2
}

** Neonates are all 0 months
if "`who'" == "Neonate" {
	replace weight_kg = max(c5_07_1, c5_07_2)/1000
}


rename g5_02 sex

merge m:1 month sex using "`who_standards'/weightforage_0-5yrs_zscores_bothsexes.dta"

** drop the z scores without observations
drop if _merge == 2 & sid == ""

count if _merge == 2

if `r(N)' ! = 0 {
	di in red "BREAK - WEIGHT FOR AGE CODE LINE 87 (merge on WHO standards)"
	BREAK
}

gen weightforage_3sdneg = (weight_kg < std_weightforage_3sdneg) if _merge == 3 & weight_kg != .
gen weightforage_2sdneg = (weight_kg < std_weightforage_2sdneg) if _merge == 3 & weight_kg != .

rename weightforage_3sdneg s180
rename weightforage_2sdneg s181

** replace missingness with 0's
replace s180 = 0 if s180 == .
replace s181 = 0 if s181 == .

keep sid s180 s181

label var s180 "severely underweight"
label var s181 "underweight"


save "$wdir/dump/`who'_weightforage.dta", replace
