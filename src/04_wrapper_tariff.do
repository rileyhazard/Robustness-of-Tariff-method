* ** Pete Serina 
* ** GC-13 Project: wrapper for running the tariff method on validation data
* ** 03292012
* ** source: do "/home/j/Project/VA/Publication_2015/Models/Tariff/Code/04_wrapper_tariff.do"


clear all
set more off
if ("`c(os)'"=="Windows") global j	"J:"
else global j "/home/j"

* ** specify a home directory
global home "$j/Project/VA/Publication_2015/Models/Tariff"			
* ** specify a cluster home directory
if ("`c(os)'"=="Windows") global chome "$j/Project/VA/Publication_2015/Models/Tariff"	
else global chome "/clustertmp/VA/Publication_2015/Models/Tariff"
capture mkdir $chome

set mem 10g

local text "yes"
if "`text'"=="yes" {
	local text_num 1
}
if "`text'"=="no" {
	local text_num 0
}

** in the model itself. for example, you might want to test simple vs fancy ranking, and it'll be easier to keep track of the performance of both if you specify different versions
    local version run_07032015
// do you want to run or compile
    local run=1
    local compile=1
** is this item reduction (final product)?
	local reduced 0
	** the splitcount indicates how many splits you want to run the model on.
** for publication purposes, it should be run on 500. 
    local splitcount 500
** which age module? Adult, Child, or Neonate? (When running it on the cluster)
    local modules "Adult Child Neonate"
** use health care experience? this is called hce, used to be called mrr,e
    ** local whichhce="0 1"    
	local whichhce="0 1"
    
** keep mrr_text? yes=1 no=0
** mrr_text=1 hce=1 keep all variables
** mrr_text=0 hce=1 drop only text
** mrr_text=1 hce=0 drop all hce
** mrr_text=0 hce=0 drop all hce
    local whichmrr_text="`text_num'"
    
// options for item reduction, well the systemmatic reduction (final product is just the local reduced up top)
    local custom_codebook=0
    if `custom_codebook'==1 {
        ** adults- 170
        local Adult_feat "1 10 20 30 40 50 60 70 80 90 100 110 120 130 140 150 160 170"
        ** child- 84
        local Child_feat "1 10 20 30 40 50 60 70 80 84"
        ** neonate- 117
        local Neonate_feat "1 10 20 30 40 50 60 70 80 90 100 110 117"
		
        // say which one of these feature lists I want to use
        local feat_list="``modules'_feat'"
        ** local feat_list="10"
        
        ** use "$j/Project/VA/item_reduction/Revised Data/Maps/`modules'_symptoms.dta", clear
        ** keep if mrr_text==1
        ** ** drop if substr(xs_name, 1, 7)=="s999910"
        ** ** drop if substr(xs_name, 1, 7)=="s999911"
        ** ** drop if substr(xs_name, 1, 7)=="s999912"
        ** levelsof xs_name, clean local(feat_list)
        ** local feat_list= "checklist"
    }
    if `custom_codebook'==0 {
        local feat_list="x"
    }

** if you uncomment this, you will end up with checklist.  Leave hce=1, text=yes, custom_codebook=0, reduced=1 with this option	
	** local feat_list checklist
	
** briefly describe what is unique about this model. this information will be stored in the "lab notebook"
    local description ""

** this just captures the date and time for archiving/commenting purposes
    local date = date(c(current_date),"DMY")
    global date = string(`date',"%tdCYND") 

** Make some directories to save results
    capture mkdir "$chome/Models/"
    capture mkdir "$chome/Models/`version'"
    capture mkdir "$chome/Models/`version'/Cluster"
    capture mkdir "$chome/Models/`version'/Code"		
    capture mkdir "$chome/Models/`version'/Out"
    capture mkdir "$chome/Models/`version'/Results"
    capture mkdir "$chome/Models/`version'/Results/Splits"

    capture mkdir "$home/Models/"
    capture mkdir "$home/Models/`version'"
    capture mkdir "$home/Models/`version'/Cluster"
    capture mkdir "$home/Models/`version'/Code"		
    capture mkdir "$home/Models/`version'/Out"
    capture mkdir "$home/Models/`version'/Results"
    capture mkdir "$home/Models/`version'/Results/Splits"    

if `run'==1 {    
    local who Neonate
    foreach who of local modules {      
        ** reassign ranks if too high based on full validation set
        if "`who'"=="Adult" {
            local cutoff = 89
            local abs_cutoff = .18
        }
            
        if "`who'"=="Neonate"  {
            local cutoff = 91
            local abs_cutoff = .35
        }

        if "`who'"=="Child" {
            local cutoff = 95
            local abs_cutoff = .17
        }   
        ** local cutoff 999
        ** local abs_cutoff 999

        local feat 10
        foreach feat of local feat_list {
            local hce 1
            foreach hce of local whichhce {
                local split 462
                forvalues split=1/`splitcount'  {         
                    ** where does the do file created by this code live?
                    local codelocation "/home/j/Project/VA/Publication_2015/Models/Tariff/Code/05_run_with_wrapper_tariff.do"

                    capture mkdir "$chome/Models/`version'/Cluster"
                    local filename "$chome/Models/`version'/Cluster/`who'_hce`hce'_split`split'_feat`feat'"

                    capture confirm file "$chome/Models/`version'/Results/Splits/split`split'_`who'_hce`hce'_feat`feat'.dta"
                    if !_rc { 
                        di "$chome/Models/`version'/Results/Splits/split`split'_`who'_hce`hce'_feat`feat'.dta exists"
                    }
                    else {
                        di "`filename'"
						global filename = "`filename'"
                        capture erase "`filename'.do"
                        file open do_file using "`filename'.do", write replace text
                        file write do_file "global split `split'"                      _n		
                        file write do_file "global hce `hce'"                          _n	
                        file write do_file "global who `who'" 			                _n	
                        file write do_file "global feat `feat'" 			                _n
                        file write do_file "global version  `version'" 	                _n
                        file write do_file "global custom_codebook `custom_codebook'"   _n
                        file write do_file "global abs_cutoff `abs_cutoff'"                           _n    
                        file write do_file "global cutoff `cutoff'"                   _n   
                        file write do_file "global reduced `reduced'"                   _n  
                        file write do_file "global mrr_text `whichmrr_text'"                   _n  
                        file write do_file `"do "`codelocation'""'                      _n			

                        file close do_file

                        file open sh_file using "`filename'.sh", write replace text
                        file write sh_file "#!/bin/sh" _n																				
                        file write sh_file "#$ -S /bin/sh" _n				
                        file write sh_file `"/usr/local/stata13/stata-mp -q do ${filename}.do"' _n 
                        file close sh_file
						
						** !/usr/local/bin/SGE/bin/lx24-amd64/qsub -N tariff_`who'_`split' "$j/Project/VA/Publication_2015/Models/Tariff/Code/00_master_shell.sh" "`filename'.do"
											
                        !qsub -p va "`filename'.sh" 
                        ** sleep 500
                    }
                    ** end of else loop
                }
                * ** end forvalues split loop
            }
            ** end of hce loop
        }
        ** end feat loop
    }
    ** end who loop
}
** end run loop
  
   
if `compile'==1 {    
        local feat="x"
        foreach feat of local feat_list {
            local who Neonate
            foreach who of local modules {
                local hce=0
                foreach hce of local whichhce {  

                    if "`who'"=="Adult" {
                        local cutoff = 89
                        local abs_cutoff = .18
                    }
                        
                    if "`who'"=="Neonate"  {
                        local cutoff = 91
                        local abs_cutoff = .35
                    }

                    if "`who'"=="Child" {
                        local cutoff = 95
                        local abs_cutoff = .17
                    }            

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
                    
                    local incomplete = 1
                    while `incomplete'==1 {
                        di "waiting for jobs to finish..."
                        clear
                        local done = 0
                        local split 1
                        forvalues split = 1/`splitcount' {
                            capture confirm file "/snfs3/VA/Publication_2015/Models/Tariff/Models/`version'/Results/Splits/split`split'_`who'_hce`hce'_feat`feat'.dta"
                            if !_rc local done = `done' + 1		
                            else {
                                local done = `done'
                                di "can't find $chome/Models/`version'/Results/Splits/split`split'_`who'_hce`hce'_feat`feat'.dta"
                            }
                        }
                    
                        if `done'==`splitcount' {
                            local incomplete = 0
                        }
                        di "currently `done' files are complete for `who' `feat' features `splitcount' splits"
                        ** sleep 10000
                    }
                    ** end incomplete loop
                    
                    ** SAVE CSMFS
                    clear
                    ** forvalues split = 1/`splitcount' {
                        ** append using "$chome/Models/`version'/Out/csmfs_`who'`hce'_`split'.dta"
                        ** capture gen split = .
                        ** replace split = `split' if split==.
                    ** }
                    ** save "$home/Models/`version'/`who' hce`hce' csmfs.dta", replace                
                    
                    ** SAVE INDIVIDUAL ASSIGNMENT
                    ** clear
                    ** gen split=.
                    ** forvalues split = 1/`splitcount' {
                        ** di "SPLIT `split'"
						** append using "$chome/Models/`version'/Out/Individual_Cause_Assignment_`who'`hce'_`split'.dta"
                        ** capture gen split = .
                        ** replace split = `split' if split==.
                        ** ** clean up
                        ** ** erase "$chome/Models/`version'/Out/Individual_Cause_Assignment_`who'`hce'_`split'.dta"
                    ** }
                    ** save "$home/Models/`version'/`who' hce`hce' individual assignments.dta", replace
                    
                    ** COMPILE ALL SPLITS
                    clear
                    capture log close
                    gen split=.
                    ** quietly {
                        forvalues split = 1/`splitcount' {
                            di "append this file $chome/Models/`version'/Results/Splits/split`split'_`who'_hce`hce'_feat`feat'.dta"
							append using "$chome/Models/`version'/Results/Splits/split`split'_`who'_hce`hce'_feat`feat'.dta"
                            capture gen split = .
                            capture gen feat = ""
                            replace split = `split' if split==.
                            replace feat = "`feat'" if feat=="" 
                            ** clean up
                            ** erase "$chome/Models/`version'/Results/Splits/split`split'_`who'_hce`hce'_feat`feat'.dta"
                        }
                    ** }
                    ** save all splits to the j drive
                    save "$home/Models/`version'/`who'_all_splits_hce`hce'_feat`feat'.dta", replace
					capture rename kappa1 kappa
                   
                    ** COMPILE TO ONE METRIC FOR ALL SPLITS
                    ** this if you are trying to do median csmf accuracy
                    ** note: median=1 if you want this to be similar to publication
                    local median=1
                    if `median'==1 {
                        ** calculate uncertainty:
                        local l = floor(((`splitcount'+1)/2) - .98*(`splitcount'^.5))
                        local u = (`splitcount')/2 + (((`splitcount')/2) - `l') + 1
                        gsort `aggr_cl_text' pc3k
                        bysort `aggr_cl_text': gen rank_pc3k = _n
                        
                        gsort `aggr_cl_text' accuracy
                        bysort `aggr_cl_text': gen rank_accuracy = _n
                        
                        gsort `aggr_cl_text' absolute_error
                        bysort `aggr_cl_text': gen rank_abserror = _n
                        
						** NEW METRICS AS OF 11-14-2013
						gsort `aggr_cl_text' sensitivity
						bysort `aggr_cl_text': gen rank_sensitivity = _n
						
						gsort `aggr_cl_text' specificity
						bysort `aggr_cl_text': gen rank_specificity = _n
									
						gsort `aggr_cl_text' pct_concordance
						bysort `aggr_cl_text': gen rank_pct_concordance = _n
						
						gsort `aggr_cl_text' kappa
						bysort `aggr_cl_text': gen rank_kappa = _n
						
                        gsort `aggr_cl_text' ccsmf_accuracy
                        bysort `aggr_cl_text': gen rank_ccsmf_accuracy = _n						
			
                        gen lower_ci_abserror = .
                        gen upper_ci_abserror = .
                        
                        gen lower_ci_pc3k = .
                        gen upper_ci_pc3k = .
                        
                        gen lower_ci_accuracy = .
                        gen upper_ci_accuracy = .
						
						** NEW METRICS AS OF 11-14-2013
						
						gen lower_ci_sensitivity = .
						gen upper_ci_sensitivity = .
								
						gen lower_ci_specificity= .
						gen upper_ci_specificity= .

						gen lower_ci_kappa = .
						gen upper_ci_kappa = .
						
						gen lower_ci_pct_concordance = .
						gen upper_ci_pct_concordance = .
                       
                        gen lower_ci_ccsmf_accuracy = .
                        gen upper_ci_ccsmf_accuracy = .

						levelsof `aggr_cl_text' if `aggr_cl_text' != "CSMF Accuracy" & `aggr_cl_text' != "CCSMF Accuracy" & `aggr_cl_text'!="Kappa Statistics", local(outcomes)

							replace lower_ci_accuracy = accuracy if `aggr_cl_text'=="CSMF Accuracy"  & rank_accuracy==`l' 
							replace upper_ci_accuracy = accuracy if `aggr_cl_text'=="CSMF Accuracy"  & rank_accuracy==`u'

							replace lower_ci_ccsmf_accuracy = ccsmf_accuracy if `aggr_cl_text'=="CCSMF Accuracy"  & rank_ccsmf_accuracy==`l' 
							replace upper_ci_ccsmf_accuracy = ccsmf_accuracy if `aggr_cl_text'=="CCSMF Accuracy"  & rank_ccsmf_accuracy==`u'
                        
						foreach o of local outcomes {
							replace lower_ci_pc3k = pc3k if `aggr_cl_text'=="`o'" & rank_pc3k==`l' & `aggr_cl_text' != "CSMF Accuracy" & `aggr_cl_text' != "CCSMF Accuracy" & `aggr_cl_text'!="Kappa Statistics"
							replace upper_ci_pc3k = pc3k if `aggr_cl_text'=="`o'" & rank_pc3k==`u' & `aggr_cl_text' != "CSMF Accuracy" & `aggr_cl_text' != "CCSMF Accuracy" & `aggr_cl_text'!="Kappa Statistics"

							replace lower_ci_abserror = absolute_error if `aggr_cl_text'=="`o'" & rank_abserror==`l' & `aggr_cl_text' != "Mean PC3"  & `aggr_cl_text'!="Kappa Statistics"
							replace upper_ci_abserror = absolute_error if `aggr_cl_text'=="`o'" & rank_abserror==`u' & `aggr_cl_text' != "Mean PC3"  & `aggr_cl_text'!="Kappa Statistics"
							
							
						** NEW METRICS AS OF 11-14-2013
							replace lower_ci_sensitivity = sensitivity if `aggr_cl_text'=="`o'" & rank_sensitivity==`l' & `aggr_cl_text'!="CSMF Accuracy" & `aggr_cl_text' != "CCSMF Accuracy" & `aggr_cl_text'!="Kappa Statistics" 
							replace upper_ci_sensitivity = sensitivity if `aggr_cl_text'=="`o'" & rank_sensitivity==`u' & `aggr_cl_text'!="CSMF Accuracy" & `aggr_cl_text' != "CCSMF Accuracy" & `aggr_cl_text'!="Kappa Statistics" 
							
							replace lower_ci_specificity = specificity if `aggr_cl_text'=="`o'" & rank_specificity==`l' & `aggr_cl_text'!="CSMF Accuracy" & `aggr_cl_text' != "CCSMF Accuracy" & `aggr_cl_text'!="Kappa Statistics" 
							replace upper_ci_specificity = specificity if `aggr_cl_text'=="`o'" & rank_specificity==`u' & `aggr_cl_text'!="CSMF Accuracy" & `aggr_cl_text' != "CCSMF Accuracy" & `aggr_cl_text'!="Kappa Statistics" 
							
							replace lower_ci_pct_concordance = pct_concordance if `aggr_cl_text'=="`o'" & rank_pct_concordance==`l' & `aggr_cl_text'!="CSMF Accuracy" & `aggr_cl_text' != "CCSMF Accuracy" & `aggr_cl_text'!="Kappa Statistics" 
							replace upper_ci_pct_concordance = pct_concordance if `aggr_cl_text'=="`o'" & rank_pct_concordance==`u' & `aggr_cl_text'!="CSMF Accuracy" & `aggr_cl_text' != "CCSMF Accuracy" & `aggr_cl_text'!="Kappa Statistics" 

							replace lower_ci_kappa = kappa if `aggr_cl_text'=="Kappa Statistics"  & rank_kappa==`l' 
							replace upper_ci_kappa = kappa if `aggr_cl_text'=="Kappa Statistics"  & rank_kappa==`u'
                        }
 
						** NEW METRICS AS OF 11-14-2013                    
						collapse `aggr_cl' (median) pc3k (median) absolute_error (median) accuracy (median) ccsmf_accuracy (median) sensitivity (median) specificity (median) pct_concordance (median) kappa lower_ci* upper_ci* pct_indet, by(`aggr_cl_text')
                        
						order `aggr_cl_text' `aggr_cl' pc3k lower*pc3k upper*pc3k absolute_error lower*error upp*error accuracy low*accuracy up*accuracy sensitivity low*sensitivity up*sensitivity specificity low*specificity up*specificity kappa low*kappa up*kappa pct_concordance low*pct_concordance up*pct_concordance
                                
                        levelsof accuracy if `aggr_cl_text'=="CSMF Accuracy", local(accuracy_result)
                        levelsof lower_ci_accuracy if `aggr_cl_text'=="CSMF Accuracy", local(accuracy_p5_result)
                        levelsof upper_ci_accuracy if `aggr_cl_text'=="CSMF Accuracy", local(accuracy_p95_result)
                        levelsof ccsmf_accuracy if `aggr_cl_text'=="CCSMF Accuracy", local(ccsmf_accuracy_result)
                        levelsof lower_ci_ccsmf_accuracy if `aggr_cl_text'=="CCSMF Accuracy", local(ccsmf_accuracy_p5_result)
                        levelsof upper_ci_ccsmf_accuracy if `aggr_cl_text'=="CCSMF Accuracy", local(ccsmf_accuracy_p95_result)
                        levelsof pc3k if `aggr_cl_text'=="Mean PC3", local(pc3k_results)
                        levelsof lower_ci_pc3k if `aggr_cl_text'=="Mean PC3", local(pc3k_p5_result)
                        levelsof upper_ci_pc3k if `aggr_cl_text'=="Mean PC3", local(pc3k_p95_result)
                        levelsof pct_indet if `aggr_cl_text'=="Percent Indeterminant", local(pct_indet)
                        sort `aggr_cl'
                        save "$home/Models/`version'/Results/Tariff_results_`who'_hce`hce'_feat`feat'.dta", replace
                    
					}
                    ** this is if you are doing mean csmf accuracy
                    if `median'==0 {
                        summarize pc3k, detail
                        local pc3k_results=r(mean)
                        local pc3k_p5_results=r(p5)
                        local pc3k_p95_results=r(p95)
                        summarize accuracy, detail
                        local accuracy_result=r(mean)
                        local accuracy_p5_results=r(p5)
                        local accuracy_p95_results=r(p95)                    
                    }
                    
                    ** PUT INTO LAB NOTEBOOK
                    clear
					di "Add to notebook"
                    insheet using "$home/Results/lab_notebook.csv"
                    capture tostring module, replace
                    capture tostring version, replace
                    capture tostring method, replace
                    capture tostring description, replace
                    capture tostring date, replace
                    capture tostring feature_count, replace
                    capture tostring item_reduction, replace
                    capture tostring data_set, replace
                    capture tostring hce, replace
                    capture tostring mrr_text, replace
                    capture gen splits = 1
                    capture gen hce = `hce'
                    count
                    local count = r(N) + 1
                    set obs `count'
                    di "date"
                    replace date = "$date" in `count'
                    di "module"
                    replace module = "`who'" in `count'
                    di "version"
                    replace version = "`version'" in `count'
                    replace method = "`method'" in `count'
                    replace pc3k = `pc3k_results' in `count'
                    replace accuracy = `accuracy_result' in `count'
                    replace accuracy = round(accuracy, .001)
                    replace pc3k = round(pc3k, .001)
                    replace p5_pc3k = `pc3k_p5_result' in `count'
                    replace p95_pc3k = `pc3k_p95_result' in `count'
                    replace accuracy = `accuracy_result' in `count'
                    replace p5_accuracy = `accuracy_p5_result' in `count'
                    replace p95_accuracy = `accuracy_p95_result' in `count'              
                    replace ccsmf_accuracy = `ccsmf_accuracy_result' in `count'
                    replace p5_ccsmf_accuracy = `ccsmf_accuracy_p5_result' in `count'
                    replace p95_ccsmf_accuracy = `ccsmf_accuracy_p95_result' in `count' 
                    ** replace accuracy = round(accuracy, .001)
                    ** replace pc3k = round(pc3k, .001)                    
                    
                    replace description = "`description'" in `count'
                    di "splits"
                    replace splits = `splitcount' in `count'
                    di "module"
                    replace module = "`who'" in `count' 
                    di "hce"
                    replace pct_indet = `pct_indet' in `count'
                    replace hce = "`hce'" in `count'
                    di "ranking"
                    ** replace ranking = "`ranking'" in `count'
                    di "item_reduction"
                    replace item_reduction = "`custom_codebook'" in `count'
					replace version = "`version'" in `count'
                    replace feature_count = "`feat'" in `count' if `custom_codebook'==1
					replace text = "`text_num'" in `count' 

                    ** replace data_set = "`dataFolder'" in `count'
                    ** ** capture replace p5_pc3k = `pc3k_p5_results' in `count'
                    ** ** capture replace p95_pc3k = `pc3k_p95_results' in `count'
                    ** ** capture replace p5_accuracy = `accuracy_p5_results' in `count'
                    ** ** capture replace p95_accuracy = `accuracy_p95_results' in `count'
                    ** replace cutoff=`cutoff' in `count'
                    ** replace abs_cutoff=`abs_cutoff' in `count'
                    ** replace mrr_text="`mrr_text'" in `count'
                    order version module pc3k p5_pc3k p95_pc3k accuracy p5_accuracy p95_accuracy ccsmf_accuracy p5_ccsmf_accuracy p95_ccsmf_accuracy
                    outsheet using "$home/Results/lab_notebook.csv", comma replace
                }
                ** end hce loop
            }
            ** end who loop
        }
        ** end feat loop	
    }

	** end compile loop
** clean up after myself for with each compile (files get done in the run code)
** if `compile'==1 {
    ** !rm -r "$chome/Models/`version'/Cluster"
    ** !rm -r "$chome/Models/`version'/Code"
** }

    