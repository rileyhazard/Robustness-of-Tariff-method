** author: Pete Serina
** date: 6/29/12
** purpose: bootstrap tariffs using published data and revised data
** source: do "/home/j/Project/VA/Publication/FreeText/bootstrap tariffs of free text.do"

clear all
capture restore, not
set maxvar 15000
set more off
set mem 20g
set seed 123

if c(os) == "Windows" {
	local prefix "J:"
}
if c(os) == "Unix" {
	local prefix "/home/j"
}

** set locals
local iters 500
local who Adult
local home "`prefix'/Project/VA/Publication/FreeText"
local input_data "`home'/Words/`who'_words_all_variables_50freq.csv"

    if "`who'"=="Adult" {
        local whonc = "adult"
        local cause_var = "va46"
        local cause_count = 46
        local text = "gs_text46"
        local aggregate_cause_count = 34
        local aggr_cl = "va34"
        local aggr_cl_text "gs_text34"
    }
        
    if "`who'"=="Neonate"  {
        local whonc = "neonate"
        local cause_var = "va34"
        local cause_count = 6
        local text = "gs_text34"
        local aggregate_cause_count = 6
        local aggr_cl = "va34"
        local aggr_cl_text "gs_text34"
    }

    if "`who'"=="Child" {
        local whonc = "child"
        local cause_count = 21
        local cause_var = "va34"
        local text = "gs_text34"
        local aggregate_cause_count = 21
        local aggr_cl = "va34"
        local aggr_cl_text "gs_text34"	
    }  

  
insheet using "`input_data'", clear
rename word_id sid

** make it binary
foreach var of varlist word* {
    replace `var'=1 if `var'!=0
}

** drop all free text that was deemed clinically insignificant or misleading by "expert knowledge"
preserve
insheet using "J:\Project\VA\Publication\FreeText\Maps\dropWords.csv", clear names
levelsof `whonc', local(drop) clean
restore

** find out which of the variables in the drop list don't exist in the tm output
local list=""
foreach x of local drop {
    capture confirm variable `x'
    if _rc {
        local list="`list' " + "`x'"
    }        
}

preserve
** make a drop list excluding the variables not outputted by tm
insheet using "J:\Project\VA\Publication\FreeText\Maps\dropWords.csv", clear names
foreach var of local list {
    drop if `whonc'=="`var'"
    levelsof `whonc', local(drop) clean
}
restore

** drop variables from the drop list that exist
drop `drop'
    
** merge on the cause_var by sid
merge 1:1 sid using "J:/Project/VA/Publication/Revised Data/Symptom Data/`who'Data.dta", keepusing(`cause_var')

** break the code if there are missing observations either in free text or s vars - have to comment this out for 2/27 run because we did drop some from the svars but we're adding them back in
summ _merge
if r(mean)!=3 {
    BREAK_Merge_codebook_Failed
}    
keep if _merge==3
drop _m
** loop through iterations
local i 2
forvalues i = 1/`iters' {
    preserve
        ** sample with replacement to the size of the dataset
        bsample, strata(`cause_var')	
		
        ** endorsement by cause
        drop sid
        collapse word*, by(`cause_var') fast
			
        ** median and IQR endorsement across causes

        foreach var of varlist * {
            if "`var'" != "`cause_var'" {
                summarize `var', detail
                local median_`var' = `r(p50)'
                local iqr_`var' = `r(p75)'-`r(p25)'
                if `iqr_`var'' != 0 {
                    gen tariff_`var' = (`var' - `median_`var'')/`iqr_`var''
                }
                ** if iqr is zero put it as .001 so it's not undefined
                else {
                    gen tariff_`var' = (`var' - `median_`var'')/.001
                } 
            }
        }
        
        keep `cause_var' tariff*
        
        ** reshape long
        reshape long tariff_, j(xs_name) i(`cause_var') string
        rensfix _ `i'

        ** save
        capture mkdir "`home'/Bootstrap"
        capture mkdir "`home'/Bootstrap/`who'"
        capture mkdir "`home'/Bootstrap/`who'/draws"
        save "`home'/Bootstrap/`who'/draws/tariff_`i'_`who'.dta", replace


        di in red "FINISHED ITERATION # `i' - `who'"
        
     restore
}

clear all
** combine all draws

use "`home'/Bootstrap/`who'/draws/tariff_1_`who'.dta", clear

forvalues x=2/`iters' {
    merge 1:1 `cause_var' xs_name using "`home'/Bootstrap/`who'/draws/tariff_`x'_`who'.dta", nogen
}
    
** calculate confidence interval to determine significance    
** egen pctile_2_5 = rowpctile(tariff*), p(2.5)
** egen pctile_97_5 = rowpctile(tariff*), p(97.5)
egen pctile_0_5 = rowpctile(tariff*), p(0.5)
egen pctile_99_5 = rowpctile(tariff*), p(99.5)
egen mean = rowmean(tariff*)

gen significant=0
** replace significant=1 if pctile_2_5<0 & pctile_97_5<0 | pctile_2_5>0 & pctile_97_5>0
replace significant=1 if pctile_0_5<0 & pctile_99_5<0 | pctile_0_5>0 & pctile_99_5>0


save "`home'/Bootstrap/`who'/`who'_`iters'_bootstrapped_tariff_CIs.dta", replace



***************************************************
** make new tariff matrix with this information
***************************************************

** create matrix of indicator of significance for symptoms by cause, save these all as locals
use "`home'/Bootstrap/`who'/`who'_`iters'_bootstrapped_tariff_CIs.dta", clear
levelsof xs_name, local(xs_name)

keep `cause_var' xs_name sig
rename significant sig_
reshape wide sig_, i(`cause_var') j(xs_name) string

renpfix sig_


foreach x of local xs_name {
    forvalues s=1/`cause_count' {
        local `x'_`s'=`x' in `s'
    }    
}    

save "`home'/Bootstrap/`who'/`who'_`iters'_significance_matrix.dta", replace



