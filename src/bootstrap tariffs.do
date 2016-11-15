** author: Pete Serina
** date: 6/29/12
** purpose: bootstrap tariffs in order to determine if they are signficant, create a matrix that will inform the final tariff matrix.
** Edited 11/19 to restrict to 99% confidence

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
local home "`prefix'/Project/VA/Publication_2015/Revised Data/Bootstrap Tariffs"
local codebook "`prefix'/Project/VA/Publication_2015/Revised Data/Codebook"
local iters 500

local who Adult
** foreach who in Adult {

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

        local input_data "`prefix'/Project/VA/Publication_2015/Revised Data/Symptom Data/`who'Data.dta"
        
        ** Try creating a just age
        use "`input_data'", clear
        
        ** only do this for non-free text and append the free text after
            drop s9999* 

        ** loop through iterations
        local i 2
        forvalues i = 1/`iters' {
            preserve
                ** sample with replacement to the size of the dataset
                bsample, strata(`cause_var')	

                ** endorsement by cause
                drop sid site
                collapse age s*, by(`cause_var') fast

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
                rename *_ *`iter'

                ** save
                save "`home'/`who'/draws/tariff_`i'.dta", replace

                di in red "FINISHED ITERATION # `i' - `who'"
                
             restore
        }

        clear all
        ** combine all tempfiles
        use "`home'/`who'/draws/tariff_1.dta", clear

        forvalues i=2/`iters' {
            merge 1:1 `cause_var' xs_name using "`home'/`who'/draws/tariff_`i'.dta", nogen
        }
            
        ** calculate confidence interval to determine significance    
        egen pctile_0_5 = rowpctile(tariff*), p(0.5)
        egen pctile_99_5 = rowpctile(tariff*), p(99.5)
        egen mean = rowmean(tariff*)

        gen significant=0
        replace significant=1 if pctile_0_5<0 & pctile_99_5<0 | pctile_0_5>0 & pctile_99_5>0

        save "`home'/`who'/`iters' compiled tariff draws.dta", replace

***************************************************
** make significance matrix with this information--
***************************************************

    ** create matrix of indicator of significance for symptoms by cause, save these all as locals
    use "`home'/`who'/`iters' compiled tariff draws.dta", clear
    levelsof xs_name, local(xs_name)

    keep `cause_var' xs_name significant
    rename significant significant_
    reshape wide significant_, i(`cause_var') j(xs_name) string

    renpfix significant_


    foreach x of local xs_name {
        forvalues s=1/`cause_count' {
            local `x'_`s'=`x' in `s'
        }    
    }  

    

    save "`home'/`who'/`who'_significance_matrix_`iters'.dta", replace
	global who `who'
	
    ** do "J:\Project\VA\Publication\Revised Data\Bootstrap Tariffs\transpose significance matrix for RF.do"
}




  