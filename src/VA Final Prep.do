** quietly {
**************************************************************************************************************************************************
**************************************************************************************************************************************************
**
**	Project:	GC13 Verbal Autopsy
**	Purpose:	This code cleans and checks the data sent from the site, generating a cleaned dataset and error log.
**	Author:	Charles Atkinson
**
**************************************************************************************************************************************************
**************************************************************************************************************************************************
clear all
set more off
set mem 800m
capture restore, not
set linesize 84
local sites "AP_28072010 AP_SR_03122010 Bohol_10082010 Bohol_SR_20130206 Dar_24052010 Mexico_25012011 Pemba_08102010 UP_06042010"
** local sites "Bohol_10082010"
if c(os) == "Windows" {
	local prefix "J:"
}
if c(os) == "Unix" {
	local prefix "/home/j"
}

global code_dir "`prefix'/Project/VA/Publication_2015/Revised Data/Code"
local code_dir "`prefix'/Project/VA/Publication_2015/Revised Data/Code"
local tab_dir "`prefix'/Project/VA/Publication_2015/Revised Data/Code/Tabulations"
local in_dir "`prefix'/Project/GC13/Verbal Autopsy/VA Data"
local out_dir "`prefix'/Project/VA/Publication_2015/Revised Data/Presymptom Data"
local out_dir "`prefix'/Project/VA/Publication_2015/Revised Data/Presymptom Data"

** capture log close
** log using "`out_dir'/Log.smcl", replace

**************************************************************************************************************************************************
**************************************************************************************************************************************************
**
**	PREP SITE DATA
**
**************************************************************************************************************************************************
**************************************************************************************************************************************************

foreach site of local sites {
	cd "`in_dir'/GC13_VA_`site'/INT/"

 	 if "`site'" == "AP_28072010" {
		noisily display as error _newline(2) "`site' - General"
			use "`site'_GS.dta", clear
			gen gs_diagnosis = ""
			foreach cause in "A09" "A091" "A092" "A15" "A16" "A33" "A37" "A39" "A83" "A91" "B05" "B20" "B54" "C13" "C15" "C30" "C34" "C50" "C55" "D05" "D91" "E10" "E11" "F03" "F56" "G18" "G40" "G96" "H11" "H61" "I10" "I21" "I52" "I64" "J12" "J33" "J45" "K22" "K71" "M14" "N17" "N77" "O60" "O601" "O6011" "O6012" "O6013" "O602" "O603" "O64" "O67" "P21" "P351" "P352" "P353" "P3531" "P354" "Q00" "Q10" "R20" "S30" "S85" "T36" "T50" "V99" "W00" "W15" "W65" "X09" "X20" "X70" "Y00" "Y05" "Z37" "ZZ11" "ZZ12" "ZZ13" "ZZ14" "ZZ15" "ZZ16" "ZZ21" "ZZ22" "ZZ23" "ZZ24" "ZZ25" "ZZ26" "ZZ27" {
				replace gs_diagnosis = "`cause'" if regexm(cause_of_death,"`cause'")
			}
			gen gs_comorbid1 = "E10" if co_morbid_conditions___diabetes != ""
			gen gs_comorbid2 = "I10" if co_morbid_conditions___hypertens != ""
			rename level_of_diagnosis gs_level
			rename va_regno reg_num
			replace gs_level = "1" if gs_level == "8"
			replace gs_level = "2" if gs_level == "2A"
			replace gs_level = "3" if gs_level == "2B"
			replace gs_level = "1" if regexm(gs_diagnosis,"ZZ") == 1
			destring gs_level, replace
			tostring reg_num, replace
			keep reg_num gs_diagnosis gs_comorbid1 gs_comorbid2 gs_level
			noisily merge 1:1 reg_num using "`site'_GEN1", nogen
			noisily merge 1:1 reg_num using "`site'_GEN2", nogen
			gen SR=0
			tempfile AP_General
			save `AP_General', replace
		noisily display as error _newline(2) "`site' - Adult"
			use "`site'_ADU1.dta", clear
			noisily merge 1:1 reg_num using "`site'_ADU2", nogen keep(1 3)
			noisily merge 1:1 reg_num using "`site'_ADU3", nogen keep(1 3)
			noisily merge 1:1 reg_num using "`site'_ADU4", nogen keep(1 3)
			noisily merge 1:1 reg_num using `AP_General', nogen keep(1 3)
			rename reg_num sid
			replace gs_diagnosis = "P21" if sid == "21360729"
			replace gs_diagnosis = "ZZ15" if sid == "21580051"
			drop if sid == "21361200" | sid == "21580212" | sid == "21580380" | sid == "21580426"
			tempfile AP_Adult
			save `AP_Adult', replace
		noisily display as error _newline(2) "`site' - Child"
			use "`site'_CHI1.dta", clear
			noisily merge 1:1 reg_num using "`site'_CHI2", nogen keep(1 3)
			noisily merge 1:1 reg_num using "`site'_CHI3", nogen keep(1 3)
			noisily merge 1:1 reg_num using `AP_General', nogen keep(1 3)
			rename reg_num sid
			replace gs_diagnosis = "P21" if sid == "21360729"
			replace gs_diagnosis = "ZZ15" if sid == "21580051"
			drop if sid == "21361200" | sid == "21580212" | sid == "21580380" | sid == "21580426"
			tempfile AP_Child
			save `AP_Child', replace
		noisily display as error _newline(2) "`site' - translations"
			clear
			gen sid = ""
			tempfile temp
			save `temp', replace
			local files: dir "`in_dir'/GC13_VA_`site'/INT/" files "*.csv"
			foreach file of local files {
				insheet using "`file'", comma clear names
				capture drop v*
				tostring sid, replace
				drop if sid == ""
				merge 1:1 sid using `temp', nogen
				tempfile temp
				save `temp', replace
			}
			tempfile AP_translations
			save `AP_translations', replace
	}
	
	 if "`site'" == "AP_SR_03122010" {
		use "J:\Project\GC13\Verbal Autopsy\VA Data\GC13_VA_AP_28072010\INT\AP_28072010_GS.dta", clear
		gen gs_diagnosis = ""
			foreach cause in "A09" "A091" "A092" "A15" "A16" "A33" "A37" "A39" "A83" "A91" "B05" "B20" "B54" "C13" "C15" "C30" "C34" "C50" "C55" "D05" "D91" "E10" "E11" "F03" "F56" "G18" "G40" "G96" "H11" "H61" "I10" "I21" "I52" "I64" "J12" "J33" "J45" "K22" "K71" "M14" "N17" "N77" "O60" "O601" "O6011" "O6012" "O6013" "O602" "O603" "O64" "O67" "P21" "P351" "P352" "P353" "P3531" "P354" "Q00" "Q10" "R20" "S30" "S85" "T36" "T50" "V99" "W00" "W15" "W65" "X09" "X20" "X70" "Y00" "Y05" "Z37" "ZZ11" "ZZ12" "ZZ13" "ZZ14" "ZZ15" "ZZ16" "ZZ21" "ZZ22" "ZZ23" "ZZ24" "ZZ25" "ZZ26" "ZZ27" {
				replace gs_diagnosis = "`cause'" if regexm(cause_of_death,"`cause'")
			}
			gen gs_comorbid1 = "E10" if co_morbid_conditions___diabetes != ""
			gen gs_comorbid2 = "I10" if co_morbid_conditions___hypertens != ""
			rename level_of_diagnosis gs_level
			rename va_regno reg_num
			replace gs_level = "1" if gs_level == "8"
			replace gs_level = "2" if gs_level == "2A"
			replace gs_level = "3" if gs_level == "2B"
			replace gs_level = "1" if regexm(gs_diagnosis,"ZZ") == 1
			destring gs_level, replace
			tostring reg_num, replace
			rename reg_num old_va_reg_num
			keep old_va_reg_num gs_diagnosis gs_comorbid1 gs_comorbid2 gs_level
			replace gs_diagnosis = "ZZ15" if old_va_reg_num == "21580051"
			merge 1:1 old_va_reg_num using "`site'_GEN1"		
			drop if _merge != 3
			drop _m

		noisily display as error _newline(2) "`site' - General"
			noisily merge 1:1 reg_num using "`site'_GEN2", nogen
			** gen gs_diagnosis = "SR"
			** gen gs_comorbid1 = ""
			** gen gs_comorbid2 = ""
			** gen gs_level = 1
			tempfile AP_SR_General
			save `AP_SR_General', replace
			
		noisily display as error _newline(2) "`site' - Adult"
			use "`site'_ADU1.dta", clear
			noisily merge 1:1 reg_num using "`site'_ADU2", nogen keep(1 3)
			noisily merge 1:1 reg_num using "`site'_ADU3", nogen keep(1 3)
			noisily merge 1:1 reg_num using "`site'_ADU4", nogen keep(1 3)
			noisily merge 1:1 reg_num using `AP_SR_General', nogen keep(1 3)
			rename reg_num newsid
			rename old_va_reg_num sid
			gen SR=1
			tempfile AP_SR_Adult
			save `AP_SR_Adult', replace
		noisily display as error _newline(2) "`site' - Child"
			use "`site'_CHI1.dta", clear
			noisily merge 1:1 reg_num using "`site'_CHI2", nogen keep(1 3)
			noisily merge 1:1 reg_num using "`site'_CHI3", nogen keep(1 3)
			noisily merge 1:1 reg_num using `AP_SR_General', nogen keep(1 3)
			rename reg_num newsid
			rename old_va_reg_num sid
			gen SR=1
			tempfile AP_SR_Child
			save `AP_SR_Child', replace
	}
	
	if "`site'" == "Bohol_10082010" {
		noisily display as error _newline(2) "`site' - Adult"
			use "`site'_ADU.dta", clear
			rename studyid sid
			destring sid, replace
			tostring sid, replace
			rename primdiaggc_new gs_diagnosis
			rename primdiag gs_text
			rename othdiag1gc13code gs_comorbid1
			rename othdiag2gc13code gs_comorbid2
			replace gs_comorbid1 = "" if gs_comorbid1 != "E10" & gs_comorbid1 != "I10"
			replace gs_comorbid2 = "" if gs_comorbid2 != "E10" & gs_comorbid2 != "I10"
			rename plevdiagfin gs_level
			drop if gs_level == 3 | gs_level == 5 | gs_level == 21 | gs_level == 24 | gs_level == 25 | gs_level == 27
			recode gs_level (4=1) (11=2) (12=3)
			gen SR=0
			tempfile Bohol_Adult
			save `Bohol_Adult', replace
		noisily display as error _newline(2) "`site' - Child"
			use "`site'_CHI.dta", clear
			rename studyid sid
			destring sid, replace
			tostring sid, replace
			rename primdiaggc_new gs_diagnosis
			rename primdiag gs_text
			rename othdiag1gc13code gs_comorbid1
			rename othdiag2gc13code gs_comorbid2
			replace gs_comorbid1 = "" if gs_comorbid1 != "E10" & gs_comorbid1 != "I10"
			replace gs_comorbid2 = "" if gs_comorbid2 != "E10" & gs_comorbid2 != "I10"
			rename plevdiagfin gs_level
			drop if gs_level == 3 | gs_level == 5 | gs_level == 21 | gs_level == 24 | gs_level == 25 | gs_level == 27
			recode gs_level (4=1) (11=2) (12=3)
			gen SR=0
            tempfile Bohol_Child
			save `Bohol_Child', replace
		noisily display as error _newline(2) "`site' - translations"
			clear
			gen sid = ""
			tempfile temp
			save `temp', replace
			local files: dir "`in_dir'/GC13_VA_`site'/INT/" files "*.csv"
			foreach file of local files {
				insheet using "`file'", comma clear names
				capture drop v*
				destring sid, replace
				tostring sid, replace
				drop if sid == ""
				merge 1:1 sid using `temp', nogen
				tempfile temp
				save `temp', replace
			}
			gen SR=0
			tempfile Bohol_translations
			save `Bohol_translations', replace
	}
	
	if "`site'" == "Bohol_SR_20130206" {
		noisily display as error _newline(2) "`site' - Adult"
			use "`site'_ADU.dta", clear
			rename studyid sid
			destring sid, replace
			tostring sid, replace
			gen gs_diagnosis = "SR"
			gen gs_comorbid1 = ""
			gen gs_comorbid2 = ""
			gen gs_level = 1
			gen SR=1
			tempfile Bohol_SR_Adult
			save `Bohol_SR_Adult', replace
		noisily display as error _newline(2) "`site' - Child"
			use "`site'_CHI.dta", clear
			replace studyid=substr(studyid, -5, .)
			merge 1:1 studyid using "J:\Project\GC13\Verbal Autopsy\VA Data\GC13_VA_Bohol_10082010\INT\Bohol_10082010_CHI.dta", keepusing(primdiag othdiag1gc13code othdiag2gc13code primdiaggc_new)
			keep if _merge==3
			drop _m
			rename primdiaggc_new gs_diagnosis
			rename primdiag gs_text
			rename othdiag1gc13code gs_comorbid1
			rename othdiag2gc13code gs_comorbid2
			rename studyid sid
			destring sid, replace
			tostring sid, replace
			
			** gen gs_diagnosis = ""
			** gen gs_comorbid1 = ""
			** gen gs_comorbid2 = ""
			gen gs_level = 1
			gen SR=1
			tempfile Bohol_SR_Child
			save `Bohol_SR_Child', replace
			noisily display as error _newline(2) "`site' - translations"
			clear
			gen sid = ""
			tempfile temp
			save `temp', replace 
			insheet using "verbatim_recall final adult.csv", clear names 
			keep sid a7* 
			tempfile temp	
			save `temp', replace
			insheet using "verbatim_recall final child.csv", clear names 
			keep sid c6*
			merge 1:1 sid using `temp', nogen
			destring sid, replace
			tostring sid, replace			
			gen SR=1
			tempfile Bohol_SR_translations
			save `Bohol_SR_translations', replace			
	}
	
	if "`site'" == "Dar_24052010" {
		noisily display as error _newline(2) "`site' - General"
			use "`site'_GS.dta", clear
			egen gs_diagnosis = concat(gsn gsncmc gscid gsi gsccmc gscrc gsm gsaid gscan gsancd gsi1 gsrcat)
			gen gs_comorbid1 = "E10" if dia == "1"
			gen gs_comorbid2 = "I10" if hyper == "1"
			rename gsldiag gs_level
			replace gs_level = 1 if regexm(gs_diagnosis,"ZZ") == 1
			rename idno sid
			keep sid gs_diagnosis gs_comorbid1 gs_comorbid2 gs_level
			noisily merge 1:1 sid using "`site'_GEN", keep(3) nogen
			foreach var of varlist gi11 gi16 gi23a gi23b gi23c gi23d gi23e gi23f gi51 gi53 {
				replace `var' = regexr(`var',"/","")
				replace `var' = regexr(`var',"/","")
			}
			gen SR=0
			tempfile Dar_General
			save `Dar_General', replace
		noisily display as error _newline(2) "`site' - Adult"
			use "`site'_ADU.dta", clear
			noisily merge 1:1 sid using `Dar_General', keep(3) nogen
			foreach var of varlist am66a am66b am67 {
				replace `var' = regexr(`var',"/","")
				replace `var' = regexr(`var',"/","")
			}
			drop if sid == "5000855001" | sid == "0000464002"
			tempfile Dar_Adult
			save `Dar_Adult', replace
		noisily display as error _newline(2) "`site' - Child"
			use "`site'_CHI1.dta", clear
			noisily merge 1:1 idno using "`site'_CHI2", keep(3) nogen
			rename idno sid
			noisily merge 1:1 sid using `Dar_General', keep(3) nogen
			foreach var of varlist nc110a nc124a nc56a nc56b nc58 {
				replace `var' = regexr(`var',"/","")
				replace `var' = regexr(`var',"/","")
			}
			replace nc57a = regexr(nc57a,"G","")
			replace nc57b = regexr(nc57b,"G","")
			replace nc57a = regexr(nc57a,"K","")
			replace nc57b = regexr(nc57b,"K","")
			drop if sid == "5000855001" | sid == "0000464002"
			tempfile Dar_Child
			save `Dar_Child', replace
		noisily display as error _newline(2) "`site' - translations"
			clear
			gen sid = ""
			tempfile temp
			save `temp', replace
			local files: dir "`in_dir'/GC13_VA_`site'/INT/" files "*.csv"
			foreach file of local files {
				insheet using "`file'", comma clear names
				capture drop v*
				tostring sid, replace
				drop if sid == ""
				merge 1:1 sid using `temp', nogen
				tempfile temp
				save `temp', replace
			}
			gen SR=0
			tempfile Dar_translations
			save `Dar_translations', replace
	}

	if "`site'" == "Mexico_25012011" {
		noisily display as error _newline(2) "`site' - General"
			use "`site'.dta", clear
			gen gs_diagnosis = ""
			replace gs_diagnosis = "O67" if m4_01 == 1
			replace gs_diagnosis = "S85" if m4_01 == 2
			replace gs_diagnosis = "H11" if m4_01 == 3
			replace gs_diagnosis = "O64" if m4_01 == 4
			replace gs_diagnosis = "B20" if m4_01 == 5
			replace gs_diagnosis = "C30" if m4_01 == 6
			replace gs_diagnosis = "A09" if m4_01 == 7 | m4_01 == 8
			replace gs_diagnosis = "N77" if m4_01 == 9
			replace gs_diagnosis = "J12" if m4_01 == 10
			replace gs_diagnosis = "A15" if m4_01 == 11
			replace gs_diagnosis = "C50" if m4_01 == 12
			replace gs_diagnosis = "D05" if m4_01 == 13
			replace gs_diagnosis = "G18" if m4_01 == 14
			replace gs_diagnosis = "C15" if m4_01 == 15
			replace gs_diagnosis = "D91" if m4_01 == 16
			replace gs_diagnosis = "K22" if m4_01 == 17
			replace gs_diagnosis = "C34" if m4_01 == 18
			replace gs_diagnosis = "G96" if m4_01 == 19
			replace gs_diagnosis = "C13" if m4_01 == 20
			replace gs_diagnosis = "F56" if m4_01 == 21
			replace gs_diagnosis = "H61" if m4_01 == 22
			replace gs_diagnosis = "A16" if m4_01 == 23
			replace gs_diagnosis = "C55" if m4_01 == 24
			replace gs_diagnosis = "J45" if m4_01 == 25
			replace gs_diagnosis = "I52" if m4_01 == 26
			replace gs_diagnosis = "K71" if m4_01 == 27
			replace gs_diagnosis = "J33" if m4_01 == 28
			replace gs_diagnosis = "F03" if m4_01 == 29
			replace gs_diagnosis = "E11" if m4_01 == 30
			replace gs_diagnosis = "M14" if m4_01 == 31
			replace gs_diagnosis = "Q10" if m4_01 == 32
			replace gs_diagnosis = "I52" if m4_01 == 33
			replace gs_diagnosis = "G40" if m4_01 == 34
			replace gs_diagnosis = "I21" if m4_01 == 35
			replace gs_diagnosis = "T50" if m4_01 == 36
			replace gs_diagnosis = "I52" if m4_01 == 37
			replace gs_diagnosis = "N17" if m4_01 == 38
			replace gs_diagnosis = "I64" if m4_01 == 39
			replace gs_diagnosis = "X20" if m4_01 == 40
			replace gs_diagnosis = "W65" if m4_01 == 41
			replace gs_diagnosis = "W00" if m4_01 == 42
			replace gs_diagnosis = "X09" if m4_01 == 43
			replace gs_diagnosis = "T36" if m4_01 == 44
			replace gs_diagnosis = "V99" if m4_01 == 45
			replace gs_diagnosis = "Y00" if m4_01 == 46
			replace gs_diagnosis = "X70" if m4_01 == 47
			replace gs_diagnosis = "P21" if m3_01 == 1
			replace gs_diagnosis = "Q00" if m3_01 == 2
			replace gs_diagnosis = "P35" if m3_01 == 3 | m3_01 == 4 | m3_01 == 5
			replace gs_diagnosis = "O60" if m3_01 == 6 | m3_01 == 7
			replace gs_diagnosis = "P351" if m3_01 == 8
			replace gs_diagnosis = "P354" if m3_01 == 9
			replace gs_diagnosis = "Z37" if m3_01 == 10
			replace gs_diagnosis = "O6011" if m3_01 == 11
			replace gs_diagnosis = "O6012" if m3_01 == 12
			replace gs_diagnosis = "O6013" if m3_01 == 13
			replace gs_diagnosis = "B20" if m3_01 == 14
			replace gs_diagnosis = "C30" if m3_01 == 15
			replace gs_diagnosis = "A09" if m3_01 == 16 | m3_01 == 17
			replace gs_diagnosis = "A83" if m3_01 == 18
			replace gs_diagnosis = "A91" if m3_01 == 19
			replace gs_diagnosis = "A39" if m3_01 == 20
			replace gs_diagnosis = "A37" if m3_01 == 21
			replace gs_diagnosis = "J12" if m3_01 == 22
			replace gs_diagnosis = "R20" if m3_01 == 23
			replace gs_diagnosis = "S30" if m3_01 == 24
			replace gs_diagnosis = "A15" if m3_01 == 25
			replace gs_diagnosis = "X20" if m3_01 == 26
			replace gs_diagnosis = "W65" if m3_01 == 27
			replace gs_diagnosis = "W00" if m3_01 == 28
			replace gs_diagnosis = "X09" if m3_01 == 29
			replace gs_diagnosis = "T36" if m3_01 == 30
			replace gs_diagnosis = "V99" if m3_01 == 31
			replace gs_diagnosis = "Y05" if m3_01 == 32
			replace gs_diagnosis = "P3531" if m3_01 == 33
			replace gs_diagnosis = "ZZ11" if m3_02 == 1
			replace gs_diagnosis = "ZZ12" if m3_02 == 2
			replace gs_diagnosis = "ZZ13" if m3_02 == 3
			replace gs_diagnosis = "ZZ14" if m3_02 == 4
			replace gs_diagnosis = "ZZ15" if m3_02 == 5
			replace gs_diagnosis = "ZZ16" if m3_02 == 6
			replace gs_diagnosis = "ZZ21" if m4_03 == 1
			replace gs_diagnosis = "ZZ22" if m4_03 == 2
			replace gs_diagnosis = "ZZ23" if m4_03 == 3
			replace gs_diagnosis = "ZZ24" if m4_03 == 4
			replace gs_diagnosis = "ZZ25" if m4_03 == 5
			replace gs_diagnosis = "ZZ27" if m4_03 == 6
			replace gs_diagnosis = "ZZ26" if m4_03 == 7
			gen gs_comorbid1 = "E10" if m4_02a == 1 | m4_02b == 1 | m4_02c == 1
			gen gs_comorbid2 = "I10" if m4_02a == 2 | m4_02b == 2 | m4_02c == 2
			rename m5_02 gs_level
			drop if gs_level == 3 | gs_level == 4 | gs_level == 5
			replace gs_level = 1 if regexm(gs_diagnosis,"ZZ") == 1
			rename a5_01_8 a5_01_9a
			rename a6_02_7 a6_02_7a
			rename a6_02_8 a6_02_8a
			rename a6_02_9 a6_02_9a
			rename a6_02_10 a6_02_10a
			rename c2_01_14 c2_01_14a
			rename c2_01_13 c2_01_13a
			drop a7_01 a7_02 c6_01 c6_02 a3_14 a3_18
			destring sid, replace
			tostring sid, replace
			** prep adult injuries b/c string too long in codebook, keep most recent injury duration, self-inflicted, inflected by other info
			forvalues x=1/8 {
				g a5_04_`x'=.
				replace a5_04_`x'= a5_04_`x'b/24 if a5_04_`x'a==1
				replace a5_04_`x'= a5_04_`x'b if a5_04_`x'a==2
				replace a5_04_`x'= a5_04_`x'b*30 if a5_04_`x'a==3
				replace a5_04_`x'= a5_04_`x'b*365 if a5_04_`x'a==4
			}
			g a5_04a=4
			egen a5_04b= rowmin(a5_04_1-a5_04_8)
			g a5_03=.
			g a5_02=.
			forvalues x=1/8 {
				replace a5_02=a5_02_`x' if a5_04_`x'==a5_04b
				replace a5_03=a5_03_`x' if a5_04_`x'==a5_04b
			}
		noisily display as error _newline(2) "`site' - Adult"
			preserve
			keep if g1_m03 == 2
			gen SR=0
			tempfile Mexico_Adult
			save `Mexico_Adult', replace
			restore
		noisily display as error _newline(2) "`site' - Child"
			preserve
			keep if g1_m03 == 1
			gen SR=0
			tempfile Mexico_Child
			save `Mexico_Child', replace
			restore
		noisily display as error _newline(2) "`site' - translations"
			clear
			gen sid = ""
			tempfile temp
			save `temp', replace
			local files: dir "`in_dir'/GC13_VA_`site'/INT/" files "*.csv"
			foreach file of local files {
				insheet using "`file'", comma clear names
				capture drop v*
				destring sid, replace
				tostring sid, replace
				drop if sid == ""
				merge 1:1 sid using `temp', nogen
				tempfile temp
				save `temp', replace
			}
			gen SR=0
			tempfile Mexico_translations
			save `Mexico_translations', replace
	}
	
	if "`site'" == "Pemba_08102010" {
		noisily display as error _newline(2) "`site' - General"
			use "`site'_GEN1.dta", clear
			rename comorbid_1 co_morbid1
			rename comorbid_2 co_morbid2
			append using "`site'_GEN2.dta"
			rename gs_cause_code gs_diagnosis
			rename co_morbid1 gs_comorbid1
			rename co_morbid2 gs_comorbid2
			recode gs_level (8=1)
			gen SR=0
			tempfile Pemba_General
			save `Pemba_General', replace
		noisily display as error _newline(2) "`site' - Adult"
			use "`site'_ADU1.dta", clear
			noisily merge 1:1 study_id using "`site'_ADU2", nogen keep(1 3)
			noisily merge 1:1 study_id using "`site'_ADU3", nogen keep(1 3)
			noisily merge 1:1 study_id using "`site'_ADU4", nogen keep(1 3)
			noisily merge 1:1 study_id using `Pemba_General', nogen keep(1 3)
			rename study_id sid
			rename a2_87_8 a2_87_8a
			rename a3_03 a3_03a
			rename a3_05 a3_05a
			rename a3_06 a3_06a
			rename a3_07 a3_07a
			rename a3_09 a3_09a
			rename a3_12 a3_12a
			rename a3_17 a3_17a
			rename a3_19 a3_19a
			rename a4_05 a4_06
			rename a4_04 a4_05
			rename a5_01_8 a5_01_8a
			rename a6_02_6 a6_02_6a
			rename a6_02_7 a6_02_7a
			rename a6_02_8 a6_02_8a
			rename a6_02_9 a6_02_9a
			rename a6_02_10 a6_02_10a
			rename a6_02_11 a6_02_11a
			drop q7_1
			tempfile Pemba_Adult
			save `Pemba_Adult', replace
		noisily display as error _newline(2) "`site' - Child"
			use "`site'_CHI1.dta", clear
			noisily merge 1:1 study_id using "`site'_CHI2", nogen keep(1 3)
			noisily merge 1:1 study_id using "`site'_CHI3", nogen keep(1 3)
			noisily merge 1:1 study_id using "`site'_CHI4", nogen keep(1 3)
			noisily merge 1:1 study_id using "`site'_CHI5", nogen keep(1 3)
			noisily merge 1:1 study_id using `Pemba_General', nogen keep(1 3)
			rename study_id sid
			rename c5_02_6 c5_02_6a
			rename c5_02_7 c5_02_7a
			rename c5_02_8 c5_02_8a
			rename c5_02_9 c5_02_9a
			rename c5_02_10 c5_02_10a
			drop c6_01
			tempfile Pemba_Child
			save `Pemba_Child', replace
		noisily display as error _newline(2) "`site' - translations"
			clear
			gen sid = ""
			tempfile temp
			save `temp', replace
			local files: dir "`in_dir'/GC13_VA_`site'/INT/" files "*.csv"
			foreach file of local files {
				insheet using "`file'", comma clear names
				capture drop v*
				tostring sid, replace
				drop if sid == ""
				merge 1:1 sid using `temp', nogen
				tempfile temp
				save `temp', replace
			}
			tempfile Pemba_translations
			save `Pemba_translations', replace
	}
	
	if "`site'" == "UP_06042010" {
		noisily display as error _newline(2) "`site' - General"
			use "`site'_GEN1.dta", clear
			append using "`site'_GEN2.dta", force
			rename rec_id sid
			noisily merge 1:1 gsdid using "`site'_GS1", nogen keep(1 3)
			noisily merge 1:1 gsdid using "`site'_GS2", force update nogen keep(1 3 4 5)
			rename disease gs_text
			rename co_morbidity gs_comorbid
			rename diagnosislevel gs_level
			foreach var of varlist g1_05 g4_02 g5_02 {
				replace `var' = "0" if `var' == "Male"
				replace `var' = "1" if `var' == "Female"
			}
			foreach var of varlist g1_08 g5_05 {
				replace `var' = "1" if `var' == "Never Married"
				replace `var' = "2" if `var' == "Married"
				replace `var' = "3" if `var' == "Separated"
				replace `var' = "4" if `var' == "Divorced"
				replace `var' = "5" if `var' == "Widowed"
			}
			foreach var of varlist g4_03 {
				replace `var' = "1" if `var' == "Mother"
				replace `var' = "2" if `var' == "Father"
				replace `var' = "3" if `var' == "Grandmother"
				replace `var' = "4" if `var' == "Grandfather"
				replace `var' = "5" if `var' == "Aunt"
				replace `var' = "6" if `var' == "Uncle"
				replace `var' = "7" if `var' == "Husband"
				replace `var' = "8" if `var' == "Wife"
				replace `var' = "9" if `var' == "Brother"
				replace `var' = "10" if `var' == "Sister"
				replace `var' = "11" if `var' == "Birth Attendant"
				replace `var' = "12" if `var' == "Other Male"
				replace `var' = "13" if `var' == "Other Female"
			}
			foreach var of varlist g1_09 g4_05 g5_06 {
				replace `var' = "1" if `var' == "No education"
				replace `var' = "2" if `var' == "< than Primary school"
				replace `var' = "3" if `var' == "Primary school"
				replace `var' = "4" if `var' == "High School"
				replace `var' = "5" if `var' == "Inter"
				replace `var' = "6" if `var' == "Degree"
				replace `var' = "7" if `var' == "Technical Education"
				replace `var' = "8" if `var' == "Others"
			}
			gen gs_diagnosis = ""
			replace gs_diagnosis = "A09" if gs_text == "Diarrhea or dysentery?"
			replace gs_diagnosis = "A091" if gs_text == "Diarrhoea"
			replace gs_diagnosis = "A092" if gs_text == "Dysentery"
			replace gs_diagnosis = "A15" if gs_text == "Tuberculosis" | gs_text == "Pulmonary TB"
			replace gs_diagnosis = "A16" if gs_text == "Stomach Cancer"
			replace gs_diagnosis = "A33" if gs_text == "Neonatal tetanus"
			replace gs_diagnosis = "A37" if gs_text == "Pertussis"
			replace gs_diagnosis = "A39" if gs_text == "Meningitis"
			replace gs_diagnosis = "A83" if gs_text == "Encephalitis"
			replace gs_diagnosis = "A91" if gs_text == "Haemorrhagic fever"
			replace gs_diagnosis = "B05" if gs_text == "Measles"
			replace gs_diagnosis = "B20" if gs_text == "AIDS"
			replace gs_diagnosis = "B54" if gs_text == "Malaria"
			replace gs_diagnosis = "C13" if gs_text == "Mouth/Orapharynx Cancer"
			replace gs_diagnosis = "C15" if gs_text == "Esophageal Cancer"
			replace gs_diagnosis = "C30" if gs_text == "AIDS with TB"
			replace gs_diagnosis = "C34" if gs_text == "Lung Cancer"
			replace gs_diagnosis = "C50" if gs_text == "Breast Cancer"
			replace gs_diagnosis = "C55" if gs_text == "Uterine Cancer"
			replace gs_diagnosis = "D05" if gs_text == "Cervical Cancer"
			replace gs_diagnosis = "D91" if gs_text == "Leukaemia"
			replace gs_diagnosis = "E10" if gs_text == "Diabetes"
			replace gs_diagnosis = "E11" if gs_text == "Diabetes with Coma"
			replace gs_diagnosis = "F03" if gs_text == "Dementia"
			replace gs_diagnosis = "F56" if gs_text == "Ovarian Cancer"
			replace gs_diagnosis = "G18" if gs_text == "Colorectal Cancer"
			replace gs_diagnosis = "G40" if gs_text == "Epilepsy"
			replace gs_diagnosis = "G96" if gs_text == "Lymphomas"
			replace gs_diagnosis = "H11" if gs_text == "Hypertensive Disorder"
			replace gs_diagnosis = "H61" if gs_text == "Prostate Cancer"
			replace gs_diagnosis = "I10" if gs_text == "Hypertension "
			replace gs_diagnosis = "I21" if gs_text == "IHD Acute Myocardial Infarction"
			replace gs_diagnosis = "I52" if gs_text == "Cardiomyopathy (Inflammatory Heart Disease)" | gs_text == "Pericarditis (Inflammatory Heart Disease)"
			replace gs_diagnosis = "I64" if gs_text == "Stroke"
			replace gs_diagnosis = "J12" if gs_text == "Pneumonia"
			replace gs_diagnosis = "J33" if gs_text == "COPD"
			replace gs_diagnosis = "J45" if gs_text == "Asthma"
			replace gs_diagnosis = "K22" if gs_text == "Liver Cancer"
			replace gs_diagnosis = "K71" if gs_text == "Cirrhosis"
			replace gs_diagnosis = "M14" if gs_text == "Diabetes with Renal Failure"
			replace gs_diagnosis = "N17" if gs_text == "Renal Failure"
			replace gs_diagnosis = "N77" if gs_text == "Pelvic Inflammatory Disease"
			replace gs_diagnosis = "O60" if gs_text == "Preterm Delivery with Respiratory Distress Syndrome (RDS)"
			replace gs_diagnosis = "O601" if gs_text == "Preterm Delivery (without Respiratory Distress Syndrome)"
			replace gs_diagnosis = "O6011" if gs_text == "Preterm Delivery (without RDS) and Birth Asphyxia"
			replace gs_diagnosis = "O6012" if gs_text == "Preterm Delivery (with or without RDS) and Sepsis"
			replace gs_diagnosis = "O6013" if gs_text == "Preterm Delivery (without RDS) and Sepsis and Birth Asphyxia"
			replace gs_diagnosis = "O602" if gs_text == "Respiratory distress syndrome (<33 wks GA)"
			replace gs_diagnosis = "O603" if gs_text == "Respiratory distress syndrome (33-36 wks GA)"
			replace gs_diagnosis = "O64" if gs_text == "Obstructed Labor"
			replace gs_diagnosis = "O67" if gs_text == "Haemorrhage"
			replace gs_diagnosis = "P21" if gs_text == "Birth asphyxia"
			replace gs_diagnosis = "P35" if gs_text == "Serious Infection (Meningitis, Pneumonia, Sepsis)"
			replace gs_diagnosis = "P351" if gs_text == "Sepsis (Serious Infection)"
			replace gs_diagnosis = "P352" if gs_text == "Meningitis (Serious Infection)"
			replace gs_diagnosis = "P353" if gs_text == "Pneumonia (Serious Infection)"
			replace gs_diagnosis = "P3531" if gs_text == "Pneumonia and Diarrhoea"
			replace gs_diagnosis = "P354" if gs_text == "Sepsis (with Local Bacterial Infection)" & discategory == "Neonatal"
			replace gs_diagnosis = "Q00" if gs_text == "Congenital malformation"
			replace gs_diagnosis = "Q10" if gs_text == "Diabetes with Skin Infection/Sepsis"
			replace gs_diagnosis = "R20" if gs_text == "Sepsis (with local bacterial infection)"  & discategory == "ChildHood Infectious Disease"
			replace gs_diagnosis = "S30" if gs_text == "Sepsis (without local bacterial infection)"
			replace gs_diagnosis = "S85" if gs_text == "Sepsis"
			replace gs_diagnosis = "T36" if gs_text == "Poisonings"
			replace gs_diagnosis = "T50" if gs_text == "IHD Congestive Heart Failure"
			replace gs_diagnosis = "V99" if gs_text == "Road Traffic"
			replace gs_diagnosis = "W00" if gs_text == "Falls"
			replace gs_diagnosis = "W15" if gs_text == "Anaemia"
			replace gs_diagnosis = "W65" if gs_text == "Drowning"
			replace gs_diagnosis = "X09" if gs_text == "Fires"
			replace gs_diagnosis = "X20" if gs_text == "Bite of Venomous Animal"
			replace gs_diagnosis = "X70" if gs_text == "Suicide"
			replace gs_diagnosis = "Y00" if gs_text == "Homicide"
			replace gs_diagnosis = "Y05" if gs_text == "Violent Death"
			replace gs_diagnosis = "Z37" if gs_text == "Stillbirth"
			replace gs_diagnosis = "ZZ11" if gs_text == "Other Childhood Infectious Diseases"
			replace gs_diagnosis = "ZZ12" if gs_text == "Malignant Neoplasms"
			replace gs_diagnosis = "ZZ13" if gs_text == "Cardiovascular Diseases"
			replace gs_diagnosis = "ZZ14" if gs_text == "Respiratory Diseases"
			replace gs_diagnosis = "ZZ15" if gs_text == "Digestive Diseases"
			replace gs_diagnosis = "ZZ16" if gs_text == "Other Defined Causes of Child Deaths"
			replace gs_diagnosis = "ZZ21" if gs_text == "Other Infectious Diseases"
			replace gs_diagnosis = "ZZ22" if gs_text == "Other Defined Cancers"
			replace gs_diagnosis = "ZZ23" if gs_text == "Other Specified Cardiovascular Diseases"
			replace gs_diagnosis = "ZZ24" if gs_text == "Other Specified Digestive Diseases"
			replace gs_diagnosis = "ZZ25" if gs_text == "Other Non-communicable Diseases"
			replace gs_diagnosis = "ZZ26" if gs_text == "Other Defined Causes of Death as a consequence of pregnancy"
			replace gs_diagnosis = "ZZ27" if gs_text == "Other Injuries"
			gen gs_comorbid1 = "E10" if gs_comorbid == "Diabetes" | gs_comorbid == "Diabetes, Hypertension"
			gen gs_comorbid2 = "I10" if gs_comorbid == "Hypertension" | gs_comorbid == "Diabetes, Hypertension"
			replace gs_level = 1 if regexm(gs_diagnosis,"ZZ") == 1
			rename g1_10 g1_10_unit
			gen SR=0
			tempfile UP_General
			save `UP_General', replace
		noisily display as error _newline(2) "`site' - Adult"
			use "`site'_ADU.dta", clear
			rename va_id sid
			noisily merge 1:1 sid using `UP_General', nogen keep(1 3)
			tostring sid, replace
			rename a6_02_10 a6_02_10a
			rename a6_02_11 a6_02_11a
			rename a6_02_13 a6_02_13a
			drop a7_01 a4_03 a4_04
			tempfile UP_Adult
			save `UP_Adult', replace
		noisily display as error _newline(2) "`site' - Child"
			use "`site'_CHI.dta", clear
			rename va_id sid
			noisily merge 1:1 sid using `UP_General', nogen keep(1 3)
			tostring sid, replace
			foreach var of varlist c1_15 {
				replace `var' = "0" if `var' == "No"
				replace `var' = "1" if `var' == "Yes"
				destring `var', replace
			}
			drop c6_01
			tempfile UP_Child
			save `UP_Child', replace
		noisily display as error _newline(2) "`site' - translations"
			clear
			gen sid = ""
			tempfile temp
			save `temp', replace
			local files: dir "`in_dir'/GC13_VA_`site'/INT/" files "*.csv"
			foreach file of local files {
				insheet using "`file'", comma clear names
				capture drop v*
				tostring sid, replace
				drop if sid == ""
				merge 1:1 sid using `temp', nogen
				tempfile temp
				save `temp', replace
			}
			tempfile UP_translations
			save `UP_translations', replace
	}
}

**************************************************************************************************************************************************
**************************************************************************************************************************************************
**
**	COMPILE SITES
**
**************************************************************************************************************************************************
**************************************************************************************************************************************************

// OPEN CODEBOOK AND SAVE IN MATRIX
** if c(os) == "Windows" {
	** capture erase "${code_dir}/Master Codebook.dta"
	** capture confirm file "${code_dir}/Master Codebook.xlsx"
	** if ! _rc {
		** ! "C:/Apps/StatTransfer11-64/st.exe" "${code_dir}/Master Codebook.xlsx" "${code_dir}/Master Codebook.dta"
		** sleep 300
	** }
** }

import excel using "${code_dir}/Master Codebook.xlsx", first clear
tostring fill, replace
** foreach var of varlist * {
	** local name = `var'[1]
	** rename `var' `name'
** }
** drop in 1

foreach module in Adult Child {
	preserve
	keep if module == "General" | module == "`module'"
	local `module'_obs = _N
	foreach var of varlist * {
		putmata `module'_`var'=(`var')
	}
	restore
}

// LOOP THROUGH MODULES
local module Adult
** foreach module in Adult Child {
	clear
	gen site = ""
	tempfile `module'
	save ``module'', replace
	// LOOP THROUGH SITES   AP AP_SR Bohol Bohol_SR Dar Mexico Pemba UP
    local site Bohol
    foreach site in AP AP_SR Bohol Bohol_SR Dar Mexico Pemba UP {
		use ``site'_`module'', clear
		gen site = "`site'"
		replace site = subinstr(site,"_CO","",.)
		replace site = subinstr(site,"_SR","",.)
		local heading = "`site'"
		if ("`site'" == "AP_SR") local heading = "AP"
		if ("`site'" == "Bohol_SR") local heading = "Bohol"
		// LOOP THROUGH VARIABLES
	
		foreach obs of numlist 7/``module'_obs' {
			mata: st_local("variable",`module'_variable[`obs'])
			mata: st_local("type",`module'_type[`obs'])
			mata: st_local("rename",`module'_`heading'_variable[`obs'])
			mata: st_local("recode",`module'_`heading'_recode[`obs'])
			// RENAME VARIABLES
				if substr("`rename'",1,4) == "gen " {
					`rename'
				}
				if "`rename'" == "[missing]" {
					capture gen `variable' = .
				}
				if substr("`rename'",1,4) != "gen " & "`rename'" != "[missing]" & "`variable'" != "`rename'" {
					rename `rename' `variable'
				}
			// FORMAT VARIABLES
				if "`type'" != "str" {
					destring `variable', replace
				}
				if "`type'" == "str" {
					tostring `variable', replace
					replace `variable' = "" if `variable' == "."
				}
			// RECODE VARIABLES
 				if substr("`recode'", 1, 8) == "replace " & "`recode'" != "" {
					tokenize `recode', parse(";")
					`1'
					`3'
					`5'
					`7'
					`9'
					`11'
					`13'
					`15'
				}
				if substr("`recode'", 1, 8) != "replace " & "`recode'" != "" {
					recode `variable' `recode'
				}
		}
		// MERGE TRANSLATIONS
		if "`site'" == "AP" | "`site'" == "Bohol" | "`site'" == "Dar" | "`site'" == "Mexico" | "`site'" == "Pemba" | "`site'" == "UP" | "`site'"=="Bohol_SR" {
			merge 1:1 sid using ``site'_translations', update nogen keep(1 3 4 5)
		}
		// ORDER AND DROP VARIABLES
		if "`module'" == "Adult" {
			order site sid gs_diagnosis gs_comorbid1 gs_comorbid2 gs_level g1_01d g1_01m g1_01y g1_05 g1_06d g1_06m g1_06y g1_07a g1_07b g1_07c g1_08 g1_09 g1_10 g2_01 g2_02 g2_03ad g2_03am g2_03ay g2_03bd g2_03bm g2_03by g2_03cd g2_03cm g2_03cy g2_03dd g2_03dm g2_03dy g2_03ed g2_03em g2_03ey g2_03fd g2_03fm g2_03fy g3_01 g4_02 g4_03a g4_03b g4_04 g4_05 g4_06 g4_07 g4_08 g5_01d g5_01m g5_01y g5_02 g5_03d g5_03m g5_03y g5_04a g5_04b g5_04c g5_05 g5_06a g5_06b g5_07 g5_08 a1_01_1 a1_01_2 a1_01_3 a1_01_4 a1_01_5 a1_01_6 a1_01_7 a1_01_8 a1_01_9 a1_01_10 a1_01_11 a1_01_12 a1_01_13 a1_01_14 a2_01a a2_01b a2_02 a2_03a a2_03b a2_04 a2_05 a2_06 a2_07 a2_08a a2_08b a2_09_1a a2_09_1b a2_09_2a a2_09_2b a2_10 a2_11 a2_12 a2_13 a2_14 a2_15a a2_15b a2_16 a2_17 a2_18 a2_19 a2_20 a2_21 a2_22a a2_22b a2_23 a2_24a a2_24b a2_25 a2_26a a2_26b a2_27 a2_28a a2_28b a2_29 a2_30 a2_31 a2_32 a2_33a a2_33b a2_34 a2_35 a2_36 a2_37a a2_37b a2_38 a2_39_1 a2_39_2 a2_40 a2_41a a2_41b a2_42 a2_43 a2_44 a2_45 a2_46a a2_46b a2_47 a2_48a a2_48b a2_49 a2_50 a2_51 a2_52 a2_53 a2_54a a2_54b a2_55 a2_56 a2_57 a2_58a a2_58b a2_59 a2_60 a2_61 a2_62a a2_62b a2_63_1 a2_63_2 a2_64 a2_65a a2_65b a2_66 a2_67 a2_68a a2_68b a2_69 a2_70a a2_70b a2_71 a2_72 a2_73a a2_73b a2_74 a2_75 a2_76a a2_76b a2_77 a2_78 a2_79a a2_79b a2_80 a2_81 a2_82 a2_83a a2_83b a2_84 a2_85 a2_86a a2_86b a2_87_1 a2_87_2 a2_87_3 a2_87_4 a2_87_5 a2_87_6 a2_87_7 a2_87_8 a2_87_9 a2_87_10a a2_87_10b a3_01 a3_02 a3_03 a3_04 a3_05 a3_06 a3_07 a3_08a a3_08b a3_09 a3_10 a3_11a a3_11b a3_12 a3_13 a3_14 a3_15 a3_16a a3_16b a3_17 a3_18 a3_19 a3_20 a4_01 a4_02_1 a4_02_2 a4_02_3 a4_02_4 a4_02_5a a4_02_5b a4_02_6 a4_02_7 a4_03 a4_04 a4_05 a4_06 a5_01_1 a5_01_2 a5_01_3 a5_01_4 a5_01_5 a5_01_6 a5_01_7 a5_01_8 a5_01_9a a5_01_9b a5_02 a5_03 a5_04a a5_04b a6_01 a6_02_1 a6_02_2 a6_02_3 a6_02_4 a6_02_5 a6_02_6 a6_02_7 a6_02_8 a6_02_9 a6_02_10 a6_02_11 a6_02_12a a6_02_12b a6_02_13 a6_02_14 a6_02_15 a6_03 a6_04 a6_05 a6_06_1d a6_06_1m a6_06_1y a6_06_2d  a6_06_2m a6_06_2y a6_07d a6_07m a6_07y a6_08 a6_09 a6_10 a6_11 a6_12 a6_13 a6_14 a6_15 a7_01 a7_02 a7_03 a7_04 a7_05 a7_06 a7_07 a7_08 a7_09 a7_10 a7_11 a7_12 a7_13 a7_14
			keep SR site sid gs_diagnosis gs_comorbid1 gs_comorbid2 gs_level g1_01d g1_01m g1_01y g1_05 g1_06d g1_06m g1_06y g1_07a g1_07b g1_07c g1_08 g1_09 g1_10 g2_01 g2_02 g2_03ad g2_03am g2_03ay g2_03bd g2_03bm g2_03by g2_03cd g2_03cm g2_03cy g2_03dd g2_03dm g2_03dy g2_03ed g2_03em g2_03ey g2_03fd g2_03fm g2_03fy g3_01 g4_02 g4_03a g4_03b g4_04 g4_05 g4_06 g4_07 g4_08 g5_01d g5_01m g5_01y g5_02 g5_03d g5_03m g5_03y g5_04a g5_04b g5_04c g5_05 g5_06a g5_06b g5_07 g5_08 a1_01_1 a1_01_2 a1_01_3 a1_01_4 a1_01_5 a1_01_6 a1_01_7 a1_01_8 a1_01_9 a1_01_10 a1_01_11 a1_01_12 a1_01_13 a1_01_14 a2_01a a2_01b a2_02 a2_03a a2_03b a2_04 a2_05 a2_06 a2_07 a2_08a a2_08b a2_09_1a a2_09_1b a2_09_2a a2_09_2b a2_10 a2_11 a2_12 a2_13 a2_14 a2_15a a2_15b a2_16 a2_17 a2_18 a2_19 a2_20 a2_21 a2_22a a2_22b a2_23 a2_24a a2_24b a2_25 a2_26a a2_26b a2_27 a2_28a a2_28b a2_29 a2_30 a2_31 a2_32 a2_33a a2_33b a2_34 a2_35 a2_36 a2_37a a2_37b a2_38 a2_39_1 a2_39_2 a2_40 a2_41a a2_41b a2_42 a2_43 a2_44 a2_45 a2_46a a2_46b a2_47 a2_48a a2_48b a2_49 a2_50 a2_51 a2_52 a2_53 a2_54a a2_54b a2_55 a2_56 a2_57 a2_58a a2_58b a2_59 a2_60 a2_61 a2_62a a2_62b a2_63_1 a2_63_2 a2_64 a2_65a a2_65b a2_66 a2_67 a2_68a a2_68b a2_69 a2_70a a2_70b a2_71 a2_72 a2_73a a2_73b a2_74 a2_75 a2_76a a2_76b a2_77 a2_78 a2_79a a2_79b a2_80 a2_81 a2_82 a2_83a a2_83b a2_84 a2_85 a2_86a a2_86b a2_87_1 a2_87_2 a2_87_3 a2_87_4 a2_87_5 a2_87_6 a2_87_7 a2_87_8 a2_87_9 a2_87_10a a2_87_10b a3_01 a3_02 a3_03 a3_04 a3_05 a3_06 a3_07 a3_08a a3_08b a3_09 a3_10 a3_11a a3_11b a3_12 a3_13 a3_14 a3_15 a3_16a a3_16b a3_17 a3_18 a3_19 a3_20 a4_01 a4_02_1 a4_02_2 a4_02_3 a4_02_4 a4_02_5a a4_02_5b a4_02_6 a4_02_7 a4_03 a4_04 a4_05 a4_06 a5_01_1 a5_01_2 a5_01_3 a5_01_4 a5_01_5 a5_01_6 a5_01_7 a5_01_8 a5_01_9a a5_01_9b a5_02 a5_03 a5_04a a5_04b a6_01 a6_02_1 a6_02_2 a6_02_3 a6_02_4 a6_02_5 a6_02_6 a6_02_7 a6_02_8 a6_02_9 a6_02_10 a6_02_11 a6_02_12a a6_02_12b a6_02_13 a6_02_14 a6_02_15 a6_03 a6_04 a6_05 a6_06_1d a6_06_1m a6_06_1y a6_06_2d  a6_06_2m a6_06_2y a6_07d a6_07m a6_07y a6_08 a6_09 a6_10 a6_11 a6_12 a6_13 a6_14 a6_15 a7_01 a7_02 a7_03 a7_04 a7_05 a7_06 a7_07 a7_08 a7_09 a7_10 a7_11 a7_12 a7_13 a7_14
		}
		if "`module'" == "Child" {
			order site sid gs_diagnosis gs_comorbid1 gs_comorbid2 gs_level g1_01d g1_01m g1_01y g1_05 g1_06d g1_06m g1_06y g1_07a g1_07b g1_07c g1_08 g1_09 g1_10 g2_01 g2_02 g2_03ad g2_03am g2_03ay g2_03bd g2_03bm g2_03by g2_03cd g2_03cm g2_03cy g2_03dd g2_03dm g2_03dy g2_03ed g2_03em g2_03ey g2_03fd g2_03fm g2_03fy g3_01 g4_02 g4_03a g4_03b g4_04 g4_05 g4_06 g4_07 g4_08 g5_01d g5_01m g5_01y g5_02 g5_03d g5_03m g5_03y g5_04a g5_04b g5_04c g5_05 g5_06a g5_06b g5_07 g5_08 c1_01 c1_02 c1_03 c1_04 c1_05a c1_05b c1_06a c1_06b c1_07 c1_08a c1_08b c1_09 c1_10 c1_10d c1_10m c1_10y c1_11 c1_12 c1_13 c1_14 c1_15 c1_16 c1_17 c1_18 c1_19_1 c1_19_2 c1_19_3 c1_19_4a c1_19_4b c1_19_5 c1_19_6 c1_20a c1_20b c1_21a c1_21b c1_22a c1_22b c1_23 c1_24 c1_24d c1_24m c1_24y c1_25a c1_25b c1_26 c2_01_1 c2_01_2 c2_01_3 c2_01_4 c2_01_5 c2_01_6 c2_01_7 c2_01_8 c2_01_9 c2_01_10 c2_01_11 c2_01_12 c2_01_13 c2_01_14 c2_02a c2_02b c2_03 c2_04 c2_05a c2_05b c2_06 c2_07 c2_08a c2_08b c2_09 c2_10a c2_10b c2_11 c2_12 c2_13a c2_13b c2_14 c2_15a c2_15b c2_17 c2_18 c3_01 c3_02 c3_03_1 c3_03_2 c3_03_3 c3_03_4a c3_03_4b c3_03_5 c3_03_6 c3_04 c3_05 c3_06 c3_07 c3_08 c3_09 c3_10 c3_11 c3_12 c3_13 c3_14a c3_14b c3_15 c3_16 c3_17 c3_18a c3_18b c3_19a c3_19b c3_20 c3_21a c3_21b c3_22a c3_22b c3_23 c3_24 c3_25 c3_26 c3_27a c3_27b c3_28a c3_28b c3_29 c3_30a c3_30b c3_31a c3_31b c3_32 c3_33 c3_34 c3_35 c3_36 c3_37 c3_38 c3_39 c3_40 c3_41 c3_42 c3_43 c3_44 c3_45a c3_45b c3_46 c3_47 c3_48 c3_49 c4_01 c4_02a c4_02b c4_03 c4_04 c4_05 c4_06 c4_07a c4_07b c4_08a c4_08b c4_09 c4_10a c4_10b c4_11 c4_12 c4_13a c4_13b c4_14 c4_15 c4_16 c4_17a c4_17b c4_18 c4_19a c4_19b c4_20 c4_22 c4_23 c4_24 c4_25 c4_26 c4_27 c4_28 c4_29 c4_30 c4_31_1 c4_31_2 c4_32 c4_33a c4_33b c4_34 c4_35 c4_36 c4_37a c4_37b c4_38 c4_39 c4_40 c4_41 c4_42 c4_43 c4_44 c4_45 c4_46 c4_47_1 c4_47_2 c4_47_3 c4_47_4 c4_47_5 c4_47_6 c4_47_7 c4_47_8a c4_47_8b c4_47_9 c4_47_10 c4_47_11 c4_48 c4_49a c4_49b c5_01 c5_02_1 c5_02_2 c5_02_3 c5_02_4 c5_02_5 c5_02_6 c5_02_7 c5_02_8 c5_02_9 c5_02_10 c5_02_11a c5_02_11b c5_02_12 c5_02_13 c5_02_14 c5_03 c5_04 c5_05 c5_06_1d c5_06_1m c5_06_1y c5_06_2d c5_06_2m c5_06_2y c5_07_1 c5_07_2 c5_08d c5_08m c5_08y c5_09 c5_10 c5_11 c5_12 c5_13 c5_14 c5_15 c5_16 c5_17 c5_18 c5_19 c6_01 c6_02 c6_03 c6_04 c6_05 c6_06 c6_07 c6_08 c6_09 c6_10 c6_11 c6_12 c6_13 c6_14
			keep SR site sid gs_diagnosis gs_comorbid1 gs_comorbid2 gs_level g1_01d g1_01m g1_01y g1_05 g1_06d g1_06m g1_06y g1_07a g1_07b g1_07c g1_08 g1_09 g1_10 g2_01 g2_02 g2_03ad g2_03am g2_03ay g2_03bd g2_03bm g2_03by g2_03cd g2_03cm g2_03cy g2_03dd g2_03dm g2_03dy g2_03ed g2_03em g2_03ey g2_03fd g2_03fm g2_03fy g3_01 g4_02 g4_03a g4_03b g4_04 g4_05 g4_06 g4_07 g4_08 g5_01d g5_01m g5_01y g5_02 g5_03d g5_03m g5_03y g5_04a g5_04b g5_04c g5_05 g5_06a g5_06b g5_07 g5_08 c1_01 c1_02 c1_03 c1_04 c1_05a c1_05b c1_06a c1_06b c1_07 c1_08a c1_08b c1_09 c1_10 c1_10d c1_10m c1_10y c1_11 c1_12 c1_13 c1_14 c1_15 c1_16 c1_17 c1_18 c1_19_1 c1_19_2 c1_19_3 c1_19_4a c1_19_4b c1_19_5 c1_19_6 c1_20a c1_20b c1_21a c1_21b c1_22a c1_22b c1_23 c1_24 c1_24d c1_24m c1_24y c1_25a c1_25b c1_26 c2_01_1 c2_01_2 c2_01_3 c2_01_4 c2_01_5 c2_01_6 c2_01_7 c2_01_8 c2_01_9 c2_01_10 c2_01_11 c2_01_12 c2_01_13 c2_01_14 c2_02a c2_02b c2_03 c2_04 c2_05a c2_05b c2_06 c2_07 c2_08a c2_08b c2_09 c2_10a c2_10b c2_11 c2_12 c2_13a c2_13b c2_14 c2_15a c2_15b c2_17 c2_18 c3_01 c3_02 c3_03_1 c3_03_2 c3_03_3 c3_03_4a c3_03_4b c3_03_5 c3_03_6 c3_04 c3_05 c3_06 c3_07 c3_08 c3_09 c3_10 c3_11 c3_12 c3_13 c3_14a c3_14b c3_15 c3_16 c3_17 c3_18a c3_18b c3_19a c3_19b c3_20 c3_21a c3_21b c3_22a c3_22b c3_23 c3_24 c3_25 c3_26 c3_27a c3_27b c3_28a c3_28b c3_29 c3_30a c3_30b c3_31a c3_31b c3_32 c3_33 c3_34 c3_35 c3_36 c3_37 c3_38 c3_39 c3_40 c3_41 c3_42 c3_43 c3_44 c3_45a c3_45b c3_46 c3_47 c3_48 c3_49 c4_01 c4_02a c4_02b c4_03 c4_04 c4_05 c4_06 c4_07a c4_07b c4_08a c4_08b c4_09 c4_10a c4_10b c4_11 c4_12 c4_13a c4_13b c4_14 c4_15 c4_16 c4_17a c4_17b c4_18 c4_19a c4_19b c4_20 c4_22 c4_23 c4_24 c4_25 c4_26 c4_27 c4_28 c4_29 c4_30 c4_31_1 c4_31_2 c4_32 c4_33a c4_33b c4_34 c4_35 c4_36 c4_37a c4_37b c4_38 c4_39 c4_40 c4_41 c4_42 c4_43 c4_44 c4_45 c4_46 c4_47_1 c4_47_2 c4_47_3 c4_47_4 c4_47_5 c4_47_6 c4_47_7 c4_47_8a c4_47_8b c4_47_9 c4_47_10 c4_47_11 c4_48 c4_49a c4_49b c5_01 c5_02_1 c5_02_2 c5_02_3 c5_02_4 c5_02_5 c5_02_6 c5_02_7 c5_02_8 c5_02_9 c5_02_10 c5_02_11a c5_02_11b c5_02_12 c5_02_13 c5_02_14 c5_03 c5_04 c5_05 c5_06_1d c5_06_1m c5_06_1y c5_06_2d c5_06_2m c5_06_2y c5_07_1 c5_07_2 c5_08d c5_08m c5_08y c5_09 c5_10 c5_11 c5_12 c5_13 c5_14 c5_15 c5_16 c5_17 c5_18 c5_19 c6_01 c6_02 c6_03 c6_04 c6_05 c6_06 c6_07 c6_08 c6_09 c6_10 c6_11 c6_12 c6_13 c6_14
		}
		// APPEND MODULES
		append using ``module''
		tempfile `module'
		save ``module'', replace
	}
	
	// LABEL VARIABLES AND VALUES, CHECK RANGE AND SKIPS, FILL IN MISSING
	noisily display as result _newline "____________________________________________________________________________________"
	noisily display as result _newline "`module' Module"
	noisily display as result "____________________________________________________________________________________"
	foreach obs of numlist 1/``module'_obs' {
		di in red `obs'
		mata: st_local("variable",`module'_variable[`obs'])
		mata: st_local("question",`module'_question[`obs'])
		mata: st_local("type",`module'_type[`obs'])
		mata: st_local("label",`module'_label[`obs'])
		mata: st_local("coding",`module'_coding[`obs'])
		mata: st_local("range",`module'_range[`obs'])
		mata: st_local("skip",`module'_skip[`obs'])
		mata: st_local("fill",`module'_fill[`obs'])
		noisily display as result _newline "`variable' - `question'"
		// LABEL TEXT
		label variable `variable' "`question'"
		// LABEL VALUES
		if "`label'" != "" {
			label define `label' `coding' , replace
			label value `variable' `label'
		}
		// RANGE CHECKS
		if "`range'" != "" {
			gen check = 1 if `variable' != .
			foreach i of numlist `range' {
				replace check = 0 if `variable' == `i'
			}
			count if check == 1
			if r(N) > 0 {
				noisily display as error _newline "  RANGE: These observations have values outside the range for `variable':"
				noisily list site sid `variable' if check == 1, noobs
				if ("`type'" == "str") replace `variable' = "" if check == 1
				if ("`type'" != "str") replace `variable' = . if check == 1
			}
			drop check
		}
		
		// SKIP CHECKS
		if "`skip'" != "" {
			gen check = 0
			if ("`type'" == "str") replace check = 1 if `variable' != "" & (`skip')
			if ("`type'" != "str") replace check = 1 if `variable' != . & `variable' != `fill' & (`skip')
			if ("`type'" == "dur" & "`label'" == "") {
				local dur_var : subinstr local variable "b" "a", all
				replace check = 1 if `variable' != . & `variable' != `fill' & (`dur_var' == 8 | `dur_var' == 9)
			}
			count if check == 1
			if r(N) > 0 {
				noisily display as error _newline "  SKIP: These observations violate skip patterns for `variable':"
				noisily list site sid `variable' if check == 1, noobs
				if ("`type'" == "str") replace `variable' = "" if check == 1
				if ("`type'" != "str") replace `variable' = `fill' if check == 1
			}
			if ("`type'" != "str") replace `variable' = `fill' if `variable' == .
			drop check
		}
	}
	
	// COLLAPSE DURATIONS
	sort site sid
	drop if gs_diagnosis == "" | gs_level == 9
	local Adult_durs "a2_01 a2_03 a2_08 a2_15 a2_22 a2_24 a2_26 a2_28 a2_33 a2_37 a2_41 a2_48 a2_54 a2_58 a2_62 a2_65 a2_68 a2_70 a2_73 a2_76 a2_79 a2_83 a2_86 a3_08 a3_11 a3_16 a5_04"
	local Child_durs "c1_05 c1_20 c1_21 c1_25 c2_02 c2_05 c2_10 c3_14 c3_18 c3_19 c3_21 c3_22 c3_27 c3_28 c3_30 c3_31 c4_02 c4_08 c4_10 c4_13 c4_17 c4_19 c4_33 c4_37 c4_49"
	foreach var of local `module'_durs {
		gen `var' = `var'b
		replace `var' = `var' * 365 if `var'a == 1
		replace `var' = `var' * 30 if `var'a == 2
		replace `var' = `var' * 7 if `var'a == 3
		replace `var' = `var' / 24 if `var'a == 5
		replace `var' = `var' / 1440 if `var'a == 6
		replace `var' = 0 if `var'a == 9
		order `var', before(`var'a)
		local name : variable label `var'b
		local name = "`name' [days]"
		label variable `var' "`name'"
		drop `var'a `var'b
	}
    
    // Include site in sid so it remains a unique identifier
    replace sid= substr(site,1,1) + "-" + sid
	
	// Catch to make sure duration of illness is not greater than age lived
	gen age_yrs=g5_04a
	replace age_yrs=. if g5_04a==999
	gen age_mos= g5_04b
	replace age_mos=. if g5_04b==99
	gen age_days=g5_04c
	replace age_days=. if g5_04c==99
	gen age=age_yrs*365
	replace age=age_mos*30 if age==.
	replace age=age_days if age==.
	local var c4_02

    foreach var of local `module'_durs {
		replace `var'=0 if `var'>age
	}
    drop age*
	

	// SAVE DATASET - ADULT
	if "`module'" == "Adult" {
		gen module = "Adult"
		replace gs_diagnosis = "A09" if gs_diagnosis == "A091" | gs_diagnosis == "A092"
		quietly include "`code_dir'/VA Map Causes.do"
		order site module sid gs_code34 gs_text34 va34 gs_code46 gs_text46 va46 gs_code55 gs_text55 va55 gs_comorbid1 gs_comorbid2 gs_level
		preserve
			keep if SR == 0
			drop SR
			compress
			save "`out_dir'/VA Final - Adult.dta", replace
		restore
		preserve
			keep if SR == 1
			drop gs* va*
			merge 1:1 site sid using "`out_dir'/VA Final - Adult.dta", keep(1 3) nogen keepusing(gs* va*)
			compress
			save "`out_dir'/VA Recall - Adult.dta", replace
		restore
	}

    tempfile temp
    save `temp'

	// SAVE DATASET - NEONATAL AND CHILD
	if "`module'" == "Child" {
		// remove Bohol death date
		replace g1_06d=99 if g1_06d==2 & site=="Bohol"
		replace g1_06m=99 if g1_06m==1 & site=="Bohol"
		replace g1_06y=9999 if g1_06y==1960 & site=="Bohol"
		
		// prep module map
			preserve
				import excel using "`code_dir'/Master Cause Map.xlsx", first clear
				keep if module == "Child" | module == "Neonate"
				rename gs_code55 gs_diagnosis
				keep module gs_diagnosis
				tempfile map
				save `map', replace
			restore
		// recode a few causes (previous decisions made based on low sample sizes)
			// drop neonatal tetanus
			drop if gs_diagnosis == "A33"
			// combine diarrhea and dysentery
			replace gs_diagnosis = "A09" if gs_diagnosis == "A091" | gs_diagnosis == "A092"
			// these lack specificity
			replace gs_diagnosis = "O601" if gs_diagnosis == "O60"
			replace gs_diagnosis = "P351" if gs_diagnosis == "P35"
		// merge on module map
			merge m:1 gs_diagnosis using `map', keep(1 3) nogen
			
			// check to make sure everything is assigned a module
			** count if module == ""
			** if `r(N)'>0 {
				** break_line_998
			** }
			drop if module == ""
		// map collapsed cause lists
			quietly include "${code_dir}/VA Map Causes.do"
			order site module sid gs_code34 gs_text34 va34 gs_code46 gs_text46 va46 gs_code55 gs_text55 va55
			drop if (module == "Child" & c1_26 != 2) | (module == "Neonate" & c1_26 == 2)
			tempfile child
			save `child', replace
		
	// NEONATAL
		use `child', clear
		order site module sid gs_code34 gs_text34 va34 gs_code46 gs_text46 va46 gs_code55 gs_text55 va55 gs_comorbid1 gs_comorbid2 gs_level
		keep if module == "Neonate"
		drop c4*
		
		// drop if birth asphyxia/sepsis/respiratory distress
		drop if gs_text46=="Preterm Delivery (without RDS) and Sepsis and Birth Asphyxia"
		
		preserve
			keep if SR == 0
			drop SR
			compress
			save "`out_dir'/VA Final - Neonate.dta", replace
		restore
		preserve
			keep if SR == 1
			drop SR
			compress
			save "`out_dir'/VA Recall - Neonate.dta", replace
		restore
	// CHILD
		use `child', clear
		keep if module == "Child"
		drop c2* c3*
		
		** final stool logic check
		replace c4_10=0 if c4_10>c4_08
		replace c4_08=0 if c4_10>c4_08
		
		preserve
			keep if SR == 0
			drop SR
			compress
			save "`out_dir'/VA Final - Child.dta", replace
		restore
		preserve
			keep if SR == 1
			drop SR
            compress
			save "`out_dir'/VA Recall - Child.dta", replace
		restore
	}
}

capture log close
}

