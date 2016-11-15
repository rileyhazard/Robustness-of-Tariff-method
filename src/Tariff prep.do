** author: Pete Serina
** date: 7/17/12
** purpose: create standardized way of making tariffs for all modules

clear all
set mem 500m
capture restore, not

if ("`c(os)'"=="Windows") local prefix	"J:"
else local prefix "/home/j"

local out_dir "`prefix'/Project/VA/Publication_2015/Revised Data/Symptom Data/"
local tariff_prep "`prefix'/Project/VA/Publication_2015/Revised Data/Codebook"

local who Neonate
foreach who in Adult Child Neonate {

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


    use "`out_dir'/`who'Data.dta", clear
    order sex, last
    gen lastvar = 1

    preserve

    collapse age - lastvar, by(`cause_var')

    drop lastvar
    outsheet using "`tariff_prep'/endorsement_`who'.csv", comma replace



    ** Generate tariff score table that is later used for item reduction

    restore



    clear
    insheet using "`tariff_prep'/endorsement_`who'.csv", clear

    gen lastvar = 1

    foreach var of varlist age-lastvar {
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

    drop tariff_lastvar

    keep va* tariff*

    ** transpose it so cause by columns
    reshape long tariff_, j(xs_name) i(`cause_var') string
    reshape wide tariff_, j(`cause_var') i(xs_name)
    rename tariff_* cause*


    order xs_name

    merge 1:1 xs_name using "J:/Project/VA/Publication/Revised Data/Maps/`who'_symptoms.dta"

    ** break this if doesn't match exactly to original codebook..it's okay if it does. just need to make sure they are legit changes (dropping screeners is legit)
    summ _merge
    if r(mean)!=3 {
        BREAK_Merge_codebook_Failed
    }    

    keep if _merge==3

    drop _m

    ** drop tariffs that have been found to be insignificant 
    levelsof xs_name, local(xs_name)
    
    tempfile tariffs
    save `tariffs', replace


    ** put together free text and other variable bootstrapping
    use "J:/Project/VA/Publication/Revised Data/Bootstrap Tariffs/`who'/`who'_significance_matrix_500", clear
    merge 1:1 `cause_var' using "J:/Project/VA/Publication/FreeText/Bootstrap/`who'/`who'_500_significance_matrix.dta", nogen

    ** rename text variables to be s9999`x'
    preserve
    insheet using "J:/Project/VA/Publication/FreeText/Words/`who'_text_tariffs.csv", clear
    keep xs_name gc13_label
    sxpose, clear 

    local var _var2
    foreach var of varlist * {
        local name = `var'[1]
        rename `var' `name'
    }

    keep in 2

    foreach var of varlist * {
        local `var'_name=`var'
    }    
    restore
    
    foreach var of varlist word* {
        capture rename `var' ``var'_name'
    }   

    foreach var of varlist word* {
        drop `var'
    }
    
    foreach x of local xs_name {
        forvalues s=1/`cause_count' {
            local `x'_`s'=`x' in `s'
        }    
    }
    
    ** now that we have saved significant or not (0/1) in locals, apply them to my tariff matrix
    use `tariffs', clear

    foreach x of local xs_name {
        forvalues s=1/`cause_count' {
            replace cause`s'=. if xs_name=="`x'" & ``x'_`s''==0
        }
    }

    forvalues x=1/`cause_count' {
        replace cause`x'=0 if cause`x'==.
    }	

    ** save the final tariffs
    sort xs_name
    outsheet using "`tariff_prep'/tariffs_`who'.csv", comma replace
    
    ** global who `who'
    
    ** // do "J:/Project/VA/Publication/Revised Data/Code/create va models based on symptoms sd.do"   
    ** do "J:\Project\VA\Publication_2015\Revised Data\Code\mrr symptoms map generation.do"
    
    }

