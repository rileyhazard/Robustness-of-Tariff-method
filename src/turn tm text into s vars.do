** author: Pete Serina
** date: 8/27/12
** purpose: take the output of tm text and turn it into s variables.

clear all
set more off
set matsize 700
capture restore, not

local who Adult
foreach who in Neonate Adult Child {
    local dataFolder Revised
    local input_data "J:/Project/VA/Publication/FreeText/Words/`who'_words_all_variables_50freq.csv"
    local out_dir "J:/Project/VA/Publication/FreeText/Words/"

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


    ************************
    ** DROP UNWANTED WORDS BASED ON DICTIONARIES
    *****************************
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

    ** drop all observations no longer in the data set and get COD

    merge 1:1 sid using "J:/Project/VA/Publication/`dataFolder' Data/Symptom Data/`who'Data.dta", keepusing(`cause_var')

    keep if _merge==3

    order sid `cause_var'
    drop _m

    ** Get tariffs for each one of these text variabeles 
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
                   
    ** reshape 
    reshape long tariff_, j(xs_name) i(`cause_var') string
    rename tariff cause
    reshape wide cause, j(`cause_var') i(xs_name)

    ** drop any non-significant items (as determined by bootstrapping) and get sd
    levelsof xs_name, local(xs_name)

    preserve
    use "J:\Project\VA\Publication\FreeText\Bootstrap\\`who'\\`who'_500_significance_matrix.dta", clear
            foreach x of local xs_name {
                forvalues s=1/`cause_count' {
                    local `x'_`s'=`x' in `s'
                }    
            }
    restore

    foreach x of local xs_name {
        forvalues s=1/`cause_count' {
            replace cause`s'=. if xs_name=="`x'" & ``x'_`s''==0
        }
    }

    forvalues x=1/`cause_count' {
        replace cause`x'=0 if cause`x'==.
    }	

    egen sd=rowsd(cause*)
    gsort - sd

    ** drop if no info from that text var
    drop if sd==0

    gen mrr=1
    gen mrr_text=1

    ** get some locals set up as well as xs_name like a map
    rename xs_name gc13_label

    levelsof gc13_label, local(words) clean
    
    sort gc13_label
    gen xs_name=""
    local f = 1
    local var word_msb
    foreach var of local words {
        replace xs_name= "s9999`f'" in `f'
        local s9999`f'_name `var'
        local `var'_name s9999`f'
        local f = `f' + 1
    }
 

    ** save all text vars in codebook folder
    outsheet using "`out_dir'/`who'_text_tariffs.csv", c replace
    tempfile `who'_tmtext
    save ``who'_tmtext', replace

     **************************
    ** MAKE a map of the new text vars
    ******************************
    keep gc13_label xs_name mrr mrr_text
    tempfile map
    save `map'
    use "J:\Project\VA\Publication\Revised Data\Maps/`who'_symptoms.dta", clear
    drop if substr(xs_name,1,5)=="s9999"
    append using `map'
    
    // save "J:\Project\VA\Publication\Revised Data\Maps/`who'_symptoms.dta", replace

    **************************
    ** MAKE A list of the new words to be appended onto the rest of the data set
    ***************************
    insheet using "`input_data'", clear

    rename word_id sid

    ** keep only words ided in earlier section
    keep `words' sid
    
    ** turn everything binary
    foreach var of varlist word* {
        replace `var'=1 if `var'!=0
    }


    foreach var of varlist word* {
        label var `var' "`var'"
        replace `var'  = 1 if `var' > 1 & `var' != .
        replace `var' = 0 if `var' != 1
        rename `var' ``var'_name'
    }	

    tempfile new_text
    save `new_text'

    save "`out_dir'/`who'_text.dta", replace
}