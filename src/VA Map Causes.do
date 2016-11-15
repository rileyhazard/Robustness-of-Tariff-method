**************************************************************************************************************************************************
**************************************************************************************************************************************************
**
**	Project:	GC13 Verbal Autopsy
**	Purpose:	This code aggregates the cause list for the gold standard database.
**	Author:	Charles Atkinson
**
**************************************************************************************************************************************************
**************************************************************************************************************************************************

if c(os) == "Windows" {
	local prefix "J:"
}
if c(os) == "Unix" {
	local prefix "/home/j"
}
local code_dir ${code_dir}
tempfile data
save `data', replace

import excel using "`code_dir'/Master Cause Map.xlsx", first clear

** capture erase "`code_dir'/Master Cause Map.dta"
** capture confirm file "`code_dir'/Master Cause Map.xlsx"
** if ! _rc {
	** ! "C:/Apps/StatTransfer11-64/st.exe" "`code_dir'/Master Cause Map.xlsx" "`code_dir'/Master Cause Map.dta"
	** sleep 300
** }
** use "`code_dir'/Master Cause Map.dta", clear

local max = _N
tostring va34 va46 va55, replace
foreach var of varlist * {
	putmata `var'=(`var'), replace
}

use `data', clear
rename gs_diagnosis gs_code55
gen gs_code46 = gs_code55
gen gs_code34 = gs_code55
gen va55 = ""
gen va46 = ""
gen va34 = ""
gen gs_text55 = ""
gen gs_text46 = ""
gen gs_text34 = ""
label var gs_code55 "Gold Standard Code 55"
label var gs_code46 "Gold Standard Code 46"
label var gs_code34 "Gold Standard Code 34"
label var va55 "VA 55"
label var va46 "VA 46"
label var va34 "VA 34"
label var gs_text55 "Gold Standard Text 55"
label var gs_text46 "Gold Standard Text 46"
label var gs_text34 "Gold Standard Text 34"
label var module "Module"

foreach obs of numlist 1/`max' {
	mata: st_local("module_map",module[`obs'])
	mata: st_local("gs_code55",gs_code55[`obs'])
	mata: st_local("gs_code46",gs_code46[`obs'])
	mata: st_local("gs_code34",gs_code34[`obs'])
	mata: st_local("va55",va55[`obs'])
	mata: st_local("va46",va46[`obs'])
	mata: st_local("va34",va34[`obs'])
	mata: st_local("gs_text55",gs_text55[`obs'])
	mata: st_local("gs_text46",gs_text46[`obs'])
	mata: st_local("gs_text34",gs_text34[`obs'])
	replace gs_code46 = "`gs_code46'" if gs_code46 == "`gs_code55'" & module == "`module_map'"
	replace gs_code34 = "`gs_code34'" if gs_code34 == "`gs_code55'" & module == "`module_map'"
	replace va55 = "`va55'" if gs_code55 == "`gs_code55'" & module == "`module_map'"
	replace va46 = "`va46'" if gs_code46 == "`gs_code46'" & module == "`module_map'"
	replace va34 = "`va34'" if gs_code34 == "`gs_code34'" & module == "`module_map'"
	replace gs_text55 = "`gs_text55'" if gs_code55 == "`gs_code55'"
	replace gs_text46 = "`gs_text46'" if gs_code46 == "`gs_code46'"
	replace gs_text34 = "`gs_text34'" if gs_code34 == "`gs_code34'"
}
destring va34 va46 va55, replace

