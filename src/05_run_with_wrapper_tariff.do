** Pete Serina 
** GC-13 Project: running the tariff method on validation data
** 10122012
** source: do "/home/j/Project/VA/Publication_2015/Models/Tariff/Code/05_run_with_wrapper_tariff.do"

clear all
set more off
if ("`c(os)'"=="Windows") global j	"J:"
else global j "/home/j"
capture restore, not

* ** specify a home directory
global home "$j/Project/VA/Publication_2015/Models/Tariff"			
* ** specify a cluster home directory
if ("`c(os)'"=="Windows") global chome "$j/Project/VA/Publication_2015/Models/Tariff"	
else global chome "/clustertmp/VA/Publication_2015/Models/Tariff"
capture mkdir $chome

local practice=1
if `practice'==1 {
    global split 104
    global hce 1
    global who Adult
    global feat s9999108
    global version  test
    global custom_codebook 1
    global cutoff = 89
    global abs_cutoff = .18
	global reduced 1
    global mrr_text 1
}


** can either be weights_by_split or proportional or weights_500
local reallocate weights_by_split

local split = $split
local hce = $hce
local who $who
local feat $feat
local version $version
local custom_codebook = $custom_codebook
local custom_codebook = $custom_codebook
local cutoff = $cutoff
local abs_cutoff = $abs_cutoff
local reduced = $reduced
local mrr_text = $mrr_text

** Make some directories to save results
     capture mkdir "$chome/Models/"
     capture mkdir "$chome/Models/`version'"
     capture mkdir "$chome/Models/`version'/Cluster"
     capture mkdir "$chome/Models/`version'/Code"		
     capture mkdir "$chome/Models/`version'/Out"
     capture mkdir "$chome/Models/`version'/Out/reallocate"
     capture mkdir "$chome/Models/`version'/Results"
     capture mkdir "$chome/Models/`version'/Results/Splits"

// Locals not identified in the wrapper, but that may be helpful at some point
***********************************************************************
** do you want to log the model run? not useful unless it's crashing and you're trying to figure out why:
    local log=1
** is this data "Published" or "Revised"
	local dataFolder="Revised"
** if you want to change rank of a cause to 10,000 if the tariff score is below zero yes=1 no=0    
    local drop_tariff_below_0=1
** if you want to include logical constraints like no females with prostate cancer
    local constraints=1
** simple versus fancy versus ranking? 
** simple ranking = just sampling the training dataset down to the minimum CSMF size (to produce uniform cmsfs) and ranking the test scores relative to that
** fancy ranking = Alireza's algorithm, samples with replacement from the training dataset to create a uniform cause distribution
    local ranking fancy

* ** here I just set up some specifications that are dependent on the module that you're working with
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

** local for where data is coming from
    local data_dir "$j/Project/VA/Publication_2015/Revised Data"
    local codebook "`data_dir'/Codebook/tariffs_`who'.csv"
    local significance_codebook "`data_dir'/Bootstrap Tariffs/`who'/`who'_significance_matrix_500.dta"
    local freetext_significance_codebook "$j/Project/VA/Publication_2015/FreeText/Bootstrap/`who'/`who'_500_significance_matrix.dta"
    local map_file "`data_dir'/Maps/`who'_map.dta"
    local map_indet_file "`data_dir'/Maps/`who'_map_indet.dta"
    local splits_file "`data_dir'/Splits/`who'_splits_`aggregate_cause_count'.dta"
    local data_file "`data_dir'/Symptom Data/`who'Data.dta"
    local symptom_list "`data_dir'/Maps/`who'_symptoms.dta"

** If using ITEM reduction, reidentify data file, codebook, and symptom list
if `reduced'==1 {
    local codebook "$j/Project/VA/item_reduction_2015/Revised Data/Codebook/tariffs_`who'.csv"
    local data_file "$j/Project/VA/item_reduction_2015/Revised Data/Symptom Data/`who'Data.dta"
    local symptom_list "$j/Project/VA/item_reduction_2015/Revised Data/Maps/`who'_symptoms.dta"
 }   
* ** specify which type of tariff scoring you want to use in the results that are stored
    global type 2
** if doing item reduction, id the features you want
    if `custom_codebook'==1 { 
       local which_codebook "`whonc'_`feat'_hce`hce'_sd"
        ** local which_codebook "`feat'"
        local description = "`description'" + "... codebook = `which_codebook'"
    }
** this doesn't need to change, just stores the scoring type for later use
    local method "T${type}"
** specify how many features (also called symptoms, signs, items, indicators, etc) to use in the data
    local features 40

    * ** this just captures the date and time for archiving/commenting purposes
    local date = date(c(current_date),"DMY")
    global date = string(`date',"%tdCYND") 
** creates log if option is specified
    if `log'==1 {
        local split = $split
        capture mkdir "$chome/Models/`version'/Log"
        capture log close
        log using "$chome/Models/`version'/Log/`who'_log`split'_feat`feat'_hce`hce'", replace
        
    }

** make a tempfile from the map:
use "`map_file'", clear 
duplicates drop `cause_var', force
tempfile map
save `map', replace

** make map including indeterminant cause too
use "`map_indet_file'", clear
tempfile map_indet
save `map_indet', replace

* ** pull in splits to determine how many time each death should be used
use "`splits_file'", clear
tempfile splits
save `splits', replace

* ** use the full dataset
use "`data_file'", clear

* ** this builds the test/train splits..
merge 1:1 sid using `splits', nogen keepusing(test`split')

drop if va34==.

preserve
    * ** keep test observations
    keep if test`split'>0

    ** make the test size right
    expand test`split'
    sort sid
    
    drop test*

    * ** save the test file
    tempfile test
    save `test', replace
restore

preserve
    * ** keep the training observations
    keep if test`split'==0
    drop test*
    tempfile train
    save `train', replace
restore

* ** pull in the codebook to determine which items are "hce" and to be used in the tariff analysis
insheet using "`codebook'", clear

if `custom_codebook'==1 {
    keep if `which_codebook'==1
}
if "`feat'"=="checklist" {
	keep if checklist==1
}


// Note: To make custom_codebook 1 and 0 comparable you would need to change mrr to mrr_text (this is different because dropping text is what is pertinent for item reduction)
rename mrr hce
if `hce'==0 {
    drop if hce==1
}	
if `mrr_text'==0 {
    drop if mrr_text==1
}

count
local codebook_count = r(N)
			

tempfile codebook
save `codebook', replace
clear


* ** this is where the list of all the features is generated 
use "`train'", clear

preserve
    * ** i just pull out all of the variables actually in the dataset
    keep in 1
    xpose, clear varname
    drop v1
    rename _varname xs_name
    merge 1:1 xs_name using `codebook', keepusing(hce mrr_text)
	keep if _merge==3
    drop _merge
    if `hce'==0 {
        drop if hce==1
        drop hce
    }
    if `mrr_text'==0 {
        drop if mrr_text==1
        drop mrr_text
    }    
    drop if xs_name=="sid"
    levelsof xs_name, local(medical_items) clean
restore

count if `cause_var'==.
if `r(N)'>0 {
    BREAK_LINE_245
}

* ** this is where tariff calculation starts, ie creating the tariff matrix...this has to be done for each separate train data set...

** endorsement rate by cause
drop sid site
collapse age s*, by(`cause_var') fast

** median and IQR endorsement across causes...with IQR, median, and endorsement rate you can calculate tariff
** replace IQR when 0 as .001

foreach var of local medical_items {
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

tempfile tariffs
save `tariffs', replace

gen first = 0
gen last = 1
order `cause_var' first tariff* last

* ** we observed that the model performed slightly better when we rounded to the nearest .5.. it's probably an insignificant difference though. 
foreach t of varlist  first - last {
    replace `t' = 0 if `t'==.
    replace `t' = round(`t', .5)
}   

drop first last

tempfile tariffs
save `tariffs', replace

// apply bootstrapped significance estimates to the tariffs generated by split
use "`significance_codebook'", clear
merge 1:1 `cause_var' using "`freetext_significance_codebook'", nogen
  ** rename text variables to be s9999`x'
    
	preserve
    use "`symptom_list'", clear
    keep xs_name gc13_label
    keep if substr(xs_name, 1, 5)=="s9999"
    
    count
    local x=1
    forvalues x=1/`r(N)' {
        local var=gc13_label in `x'
        local `var'_name= xs_name in `x'
    }
    restore
    
    foreach var of varlist word* {
        capture rename `var' ``var'_name'
    }   

    foreach var of varlist word* {
        drop `var'
    }
	
	

// save all signficance numbers as locals
    foreach x of local medical_items {
        forvalues s=1/`cause_count' {
            local `x'_`s'=`x' in `s'
        }    
    }

use `tariffs', clear

foreach x of local medical_items {
    forvalues s=1/`cause_count' {
        replace tariff_`x'=0 in `s' if ``x'_`s''==0
    }
}

** generating matrix of all symptom-cause tariff scores
** save these numbers in locals rather than matrices in the future...could save time (like significance option)
mkmat  tariff*, matrix(tariffs) rownames(`cause_var')
stop
* ** here the tariff scoring starts. it is unncessary to loop through all four types, but it doesn't take that long, so i just left the calculations in for each type
local type=2
** forvalues type = 2/2 {
    * ** loop through both train and test since the final cause assignment depends on ranking the two relative to each other
    local group test
    foreach group in train test  {
        
        use "``group''", clear

        levelsof `cause_var', local(cause)
        local n=1
        forvalues n = 1/`cause_count' {
            
            * ** this generates a cause-specific codebook based on ranking the tariffs for the cause on absolute value.
            
            preserve
                use `codebook', clear
                replace cause`n' = abs(cause`n')
                gsort - cause`n' xs_name
                if `codebook_count' > `features' keep in 1/`features'
                levelsof xs_name, local(medical_items)
            restore
            
            gen score_`n' = 0
            
            * ** here's where the magic happens... calculating tariff scores based on the feature responses
            if `type'==1 {
                * ** model with symptom = 1, postive tariff scores only

                foreach s of local medical_items {
                    matrix A = tariffs["`n'", "tariff_`s'"]
                    matrix list A
                    local a = A[1,1]
                    if `a' != . {
                        replace score_`n' = score_`n' + A[1,1] if `s'==1 & A[1,1] >= 0
                    }
                    matrix drop A
                }
            }

            if `type'==2 {
                * ** model with symptom = 1, either tariff score

                foreach s of local medical_items {
                    matrix A = tariffs["`n'", "tariff_`s'"]
                    matrix list A
                    local a = A[1,1]
                    if `a' != . {
                        replace score_`n' = score_`n' + A[1,1] if `s'==1
                    }
                    matrix drop A
                }
            }

            if `type'==3 {
                * **  model with symptom = 1, use tariff score (if positive), symptom = 0, use negative of tariff score if the tariff score is postive to begin with
                foreach s of local medical_items {
                    matrix A = tariffs["`n'", "tariff_`s'"]
                    matrix list A
                    local a = A[1,1]
                    if `a' != . {
                        replace score_`n' = score_`n' + A[1,1] if `s'==1 & A[1,1]>=0
                        replace score_`n' = score_`n' - A[1,1] if `s'==0 & A[1,1]>=0
                    }
                    matrix drop A
                }
            }
    
        
            if `type'==4 {
                * ** model with symptom = 1, use tariff score, symptom = 0, use negative of tariff score
                foreach s of local medical_items {
                    matrix A = tariffs["`n'", "tariff_`s'"]
                    matrix list A
                    local a = A[1,1]
                    if `a' != . {
                        replace score_`n' = score_`n' + A[1,1] if `s'==1
                        replace score_`n' = score_`n' - A[1,1] if `s'==0
                    }
                    matrix drop A
                }
            }

        }
        * ** end causes
        
        forvalues n = 1/`cause_count' {
            rename score_`n' cause`n'
        }
        
        ** going into the ranking step, we only want one observation per sid, so there is no confusion to what is COD
        ** could be an issue due to the randomness of the procedure
        if "`group'"=="test" {
            duplicates drop
        }
        
        tempfile `group'_scores_`type'
        save ``group'_scores_`type'', replace
        * ** I have to save hard copies for fancy ranking since it uses R and can't rely on tempfiles..
        saveold "$chome/Models/`version'/Out/`group'_t`type'_sp`split'_`who'_hce`hce'_feat`feat'.dta", replace
        
    
    }
    * ** end group           
** }
* ** end type		

local type = $type		
*************************************
** Rank the tariff scores
******************************************            

* ** for simple ranking, i just sample the train dataset down to the lowest CSMF size to create a training set of uniform distribution. 
if "`ranking'"=="simple" {
    ** use the unranked validation/real scores and determine the frequency of each cause:
    use "`train_scores_`type''", clear
    preserve
        contract `cause_var'
        summarize _freq
        local min = r(min)
        local sampletarget = `cause_count'*`min'
    restore

    * ** conduct the sampling and save the file:
    sample `min', by(`cause_var') count
    tempfile simple_ranked
    save `simple_ranked', replace
    
    * ** use the field/communiy data:
    use "`test_scores_`type''", clear

    * ** add on the validation data:
    gen field = 1
    append using `simple_ranked'
    ** append using "$modelhome/`who'_real_scores_unranked.dta"
    replace field = 0 if field ==.

    * ** generate the ranks:
    forvalues ii = 1/`cause_count' {
        gsort - cause`ii'
        gen rank_`ii'=_n
    }
    
    * ** drop out the validation data:
    keep if field==1
    drop field
    keep sid `cause_var' cause* rank*
    order sid
    * ** save the file:
    tempfile ranks
    save `ranks', replace

}
* ** end simple ranking

* ** start fancy ranking... this just writes an R file that then runs the fancy ranking
if "`ranking'"=="fancy" {
	capture confirm file "$chome/Models/`version'/Out/tariff_ranks_module_`who'_MRR`hce'_split`split'_feat`feat'_train.csv"
	
	if _rc { 
		noisily di "ranking for `who'_MRR`hce'_split`split'_feat`feat' running"
		local filename "$chome/Models/`version'/Out/Rank`split'_`who'_hce`hce'_feat`feat'_train" 
		capture erase "`filename'.R"
		file open R_file using "`filename'.R", write replace text
		file write R_file "rm(list=ls())" _n		
		file write R_file "require(foreign)" _n		
		file write R_file "set.seed(123)" _n	
		file write R_file "module = '`who''" _n
		file write R_file "MRR = '`hce''" _n		
		file write R_file "NUMITER = `cause_count'" _n	
		file write R_file "spl = `split'" _n
		file write R_file "feat = '`feat''" _n				
		file write R_file "prefix = paste('$chome/Models/`version'/Out/', sep='')" _n	
		file write R_file "cause.var = '`cause_var''" _n
		file write R_file "train = read.dta(paste(prefix, 'train_t`type'_sp`split'_`who'_hce`hce'_feat`feat'.dta', sep=''))" _n		
		file write R_file "test = read.dta(paste(prefix, 'test_t`type'_sp`split'_`who'_hce`hce'_feat`feat'.dta', sep=''))" _n		
		file write R_file "source('$j/Project/VA/Publication/Code/Rank Scores.R')" _n			
		file close R_file

		if ("`c(os)'"=="Windows") {
			!"C:/Program Files/R/R-3.2.0/bin/R" <"`filename'.R" --no-save
		}
		
		else {
			!"/usr/local/R-current/bin/R" <"`filename'.R" --no-save
		}
    
		* ** capture erase "`filename'.R"
	}
}
* ** end fancy ranking

clear

if "`ranking'"=="fancy" {
    insheet using "$chome/Models/`version'/Out/tariff_ranks_module_`who'_MRR`hce'_split`split'_feat`feat'.csv", clear
    ** unsure why but s vars are turning into strings within ranking code.  switch it back
    g lastvar=.
    order va* gs* sid site age
    destring age-lastvar, replace force
    drop lastvar
    
    ** drop va34 out for adults because we don't want to be confused...ALL analysis at va46 level...aggregate for metrics.
    if "`who'"=="Adult" drop `aggr_cl'
    tempfile ranks
    save `ranks', replace
}          


use `ranks', clear         

** identify the lowest possible rank and add one to make a rank that will never be the top
local lowest = 1
foreach var of varlist rank* {
	qui sum `var'
	if (`r(max)' > `lowest') local lowest `r(max)'
}
local lowest = `lowest' + 1

if `drop_tariff_below_0'==1 {
    count
    local count=r(N)
    local x=1
    forvalues x=1/`count' {
        local n=11
        forvalues n=1/`cause_count' {
            replace rank_`n'=`lowest' if cause`n'<0 in `x'
        }
    }
    
   outsheet using "$chome/Models/`version'/Out/drop_below_zero_tariff_ranks_module_`who'_MRR`hce'_split`split'.csv", c replace
}              



** add constraints such that males can have breast cancer etc
if `constraints'==1 {
    if "`who'"=="Adult" {
        ** males CAN'T have breast cancer, cervical cancer, anaemia, haemorrhage, hypertensive disease, other pregnancy-related, or sepsis
        local maternal_causes "3 6 7 20 22 36 42"
        capture destring sex, replace force
        foreach n of local maternal_causes {
            replace rank_`n'=`lowest' if sex==0
        }

        ** If female, can’t be prostate cancer
        replace rank_39=`lowest' if sex==1

    }
    if "`who'"=="Neonate" {
        ** can't be stillbirth if age over 0 days
        cap replace rank_6=`lowest' if s4991==0                     
    }
    
    // no malaria in Bohol or Mexico
    if "`site'"=="Bohol" | "`site'"=="Mexico" {
        if "`who'"=="Adult" {
            replace rank_29=`lowest'
        }
        if "`who'"=="Child" {
            replace rank_9=`lowest' 
        }
    } 
    ** no measles in Mexico
    if "`site'"=="Mexico" {
        if "`who'"=="Child" {
            replace rank_10=`lowest' 
        }
    }                 
}
** end constraints

    ** id pct cutoff by cause....helps for drowning and bite
    preserve
	insheet using "$chome/Models/`version'/Out/uniformtrain/`who'_MRR`hce'_split`split'_feat`feat'_uniformtrain.csv", clear
	count
	local total_ranks=`r(N)'  
	local n=1
	
	rename uniform_rank* rank_*
	
    collapse (p`cutoff') rank*, by(`cause_var')    
    forvalues x=1/`cause_count' {
        local cut_`cutoff'_`x'=rank_`x' in `x'
    }      
    
    restore
    
    // assign `lowest' if cutoff of particular cause is above 95th percentile, useful for drowing and bite
    forvalues x=1/`cause_count' {
        replace rank_`x'=`lowest' if rank_`x'>`cut_`cutoff'_`x''
    } 
    
    // assign `lowest' if rank is above `abs_cutoff'*population size of uniform train.  this helps with less exact causes like malaria to get rid of bias
    local abs2_cutoff=`total_ranks'*`abs_cutoff'
        forvalues x=1/`cause_count' {
           replace rank_`x'=`lowest' if rank_`x'>`abs2_cutoff'
        }                                         

    local k = 1				
    egen maxchoice`k' = rowmin(rank_*)
    gen choice`k' = .
    * ** gen correct = 0
    forvalues e = 1/`cause_count' {
        replace choice`k' = `e' if rank_`e'==maxchoice`k' & rank_`e' !=.
        ** replace rank_`e' = . if rank_`e'==maxchoice`k'
    }
    local count_plus=`cause_count'+1
    replace choice`k'=`count_plus' if maxchoice`k'==`lowest'

    tempfile with_indet
    save `with_indet', replace

    ** store individual cause assignment
    preserve
    keep sid `cause_var' rank_* choice1
    save "$chome/Models/`version'/Out/Individual_Cause_Assignment_`who'`hce'_`split'.dta", replace
    restore
    
    merge 1:1 sid using `splits', keepusing(test`split')
    keep if _merge==3
    drop _merge

    expand test`split'
    count
    local total=`r(N)'

    // get pct that is indeterminant to show at end
    preserve
    count
    local total_count=`r(N)'
    keep if choice1==`count_plus'
    count
    local count=`r(N)'
    local pct_indet=`count'/`total_count'  
    clear
    set obs 1
    g pct_indet=`pct_indet'
    tempfile pct_indet
    save `pct_indet', replace
    restore

     ** REALLOCATION METHODS for Indeterminates
        gen temp=_n
if "`reallocate'"=="proportional" {    
 
    // get count of deaths ided, the absolute cutoff rank needs to be less than the 95th percentile cause rank in order to get indeterminants reallocated to it
    preserve
        drop if choice1==`count_plus'
       ** generate a new variable, abs_cutoff, that is equal to your overall absolute rank cutoff as a rank (rather than a percent)
        gen abs_cutoff=`abs2_cutoff'
        g pct_cutoff=.
        forvalues x=1/`cause_count' {
            replace pct_cutoff=`cut_`cutoff'_`x'' if choice1==`x'
        }
        count if abs_cutoff < pct_cutoff
        local ided_count= `r(N)'
        // get list of causes that won't get indeterminants reassigned to it
        keep if abs_cutoff > pct_cutoff
        levelsof choice1, local(dont_get) clean
    restore
    ** get csmfs of ided causes
    preserve
        drop if choice1==`count_plus'
        foreach x of local dont_get {
            drop if choice1==`x'
        }
        count
        
        if `r(N)'>0 {
            contract choice1
            rename choice1 `cause_var'                           
            merge 1:1 `cause_var' using `map', nogen
            replace _freq=0 if _freq==.
            sort `cause_var'
            
            replace _freq=_freq/`ided_count'                

            forvalues x=1/`cause_count' {
                local csmf`x'=_freq in `x'
            }
        }
        ** in case all cases are dropped, just do uniform redistribution
        else {
            forvalues x=1/`cause_count' {
                local csmf`x'=1/`cause_count'
            }
        }
        rename _freq reallocate_new_`split'
        tempfile csmfs
        save `csmfs'
        save "$chome/Models/`version'/Out/proportions split`split'_`who'_hce`hce'_feat`feat'.dta", replace
    restore
}

** REALLOCATION according to the indeterminate assignment across the 500 test splits
if "`reallocate'"=="weights_500" {
    preserve
	use "$j/Project/VA/Publication/Models/Tariff/Explore/weights/weights 500 tests/indeterminate weights.dta", clear
	keep if hce==`hce'
    keep if who=="`who'"
    sort `cause_var'
    forvalues x=1/`cause_count' {
        local csmf`x'=indeterminate in `x'
    }
    tempfile csmfs
    save `csmfs', replace
    restore
}    

** ** REALLOCATION according to the indeterminate assignment of the uniform train within this particular split
if "`reallocate'"=="weights_by_split" {
    preserve
	
	capture confirm file "$chome/Models/`version'/Out/tariff_ranks_module_`who'_MRR`hce'_split`split'_feat`feat'_train.csv"
	if _rc { 	
		noisily di "reallocation ranking for `who'_MRR`hce'_split`split'_feat`feat' running"
		local filename "$chome/Models/`version'/Out/Rank`split'_`who'_hce`hce'_feat`feat'_train" 
		capture erase "`filename'.R"
		file open R_file using "`filename'.R", write replace text
		file write R_file "rm(list=ls())" _n		
		file write R_file "require(foreign)" _n		
		file write R_file "set.seed(123)" _n	
		file write R_file "module = '`who''" _n
		file write R_file "MRR = '`hce''" _n		
		file write R_file "NUMITER = `cause_count'" _n	
		file write R_file "spl = `split'" _n
		file write R_file "feat = '`feat''" _n				
		file write R_file "prefix = paste('$chome/Models/`version'/Out/', sep='')" _n	
		file write R_file "cause.var = '`cause_var''" _n
		file write R_file "train = read.dta(paste(prefix, 'train_t`type'_sp`split'_`who'_hce`hce'_feat`feat'.dta', sep=''))" _n		
		file write R_file "test = read.dta(paste(prefix, 'test_t`type'_sp`split'_`who'_hce`hce'_feat`feat'.dta', sep=''))" _n		
		file write R_file "source('$j/Project/VA/Publication/Code/Rank Scores_weights.R')" _n			
		file close R_file

		if ("`c(os)'"=="Windows") {
			!"C:/Program Files/R/R-3.2.0/bin/R" <"`filename'.R" --no-save
		}
		
		else {
			!"/usr/local/R-current/bin/R" <"`filename'.R"  --no-save
		}
	}
    insheet using "$chome/Models/`version'/Out/tariff_ranks_module_`who'_MRR`hce'_split`split'_feat`feat'_train.csv", clear

    ** constraints
    if "`who'"=="Adult" {
        ** males CAN'T have breast cancer, cervical cancer, anaemia, haemorrhage, hypertensive disease, other pregnancy-related, or sepsis
        local maternal_causes "3 6 7 20 22 36 42"
        capture destring sex, replace force
        foreach n of local maternal_causes {
            replace rank_`n'=`lowest' if sex==0
        }

        ** If female, can’t be prostate cancer
        replace rank_39=`lowest' if sex==1

    }
    if "`who'"=="Neonate" {
        ** can't be stillbirth if age over 0 days
        cap replace rank_6=`lowest' if s4991==0                     
    }
    
    // no malaria in Bohol or Mexico
    if "`site'"=="Bohol" | "`site'"=="Mexico" {
        if "`who'"=="Adult" {
            replace rank_29=`lowest'
        }
        if "`who'"=="Child" {
            replace rank_9=`lowest' 
        }
    } 
    ** no measles in Mexico
    if "`site'"=="Mexico" {
        if "`who'"=="Child" {
            replace rank_10=`lowest' 
        }
    }                 
    
    ** Apply cutoffs
    // assign `lowest' if cutoff of particular cause is above 95th percentile, useful for drowing and bite
    forvalues x=1/`cause_count' {
        replace rank_`x'=`lowest' if rank_`x'>`cut_`cutoff'_`x''
    } 
    
    // assign `lowest' if rank is above `abs_cutoff'*population size of uniform train.  this helps with less exact causes like malaria to get rid of bias
    local abs2_cutoff=`total_ranks'*`abs_cutoff'
        forvalues x=1/`cause_count' {
           replace rank_`x'=`lowest' if rank_`x'>`abs2_cutoff'
        }                                         

    local k = 1				
    egen maxchoice`k' = rowmin(rank_*)
    gen choice`k' = .
    * ** gen correct = 0
    forvalues e = 1/`cause_count' {
        replace choice`k' = `e' if rank_`e'==maxchoice`k' & rank_`e' !=.
        ** replace rank_`e' = . if rank_`e'==maxchoice`k'
    }
    local count_plus=`cause_count'+1
    replace choice`k'=`count_plus' if maxchoice`k'==`lowest'    

    save "$chome/Models/`version'/Out/uniformtrain assignments_split`split'_`who'_hce`hce'_feat`feat'.dta", replace

    keep if choice1==`count_plus'
    count
    local count=r(N)
    if `count' > 0 {
		contract `cause_var', freq(indeterminate)
	}
    if `count' == 0 {
		gen indeterminate=.
	}	
    merge 1:1 `cause_var' using `map', keepusing(`cause_var')
    replace indeterminate=0 if indeterminate==.
    replace indeterminate=indeterminate/`count'
    
    forvalues x=1/`cause_count' {
        local csmf`x'=indeterminate in `x'
    }
    tempfile csmfs
    save `csmfs', replace
    capture mkdir "$chome/Models/`version'/Out/weights"
    save "$chome/Models/`version'/Out/weights/weights_split`split'_`who'_hce`hce'_feat`feat'.dta", replace
    restore   
    }
   
   // now reassign based on those csmfs
    preserve
        keep if choice1==`count_plus'
        keep sid temp
        gen random=runiform()
        gen choicex=.
        local start=0
        forvalues x=1/`cause_count' {
            local finish=`start' + `csmf`x''
            replace choicex=`x' if random>=`start' & random<`finish'
            local start= `finish'
        }
        tempfile indet_reassign
        save `indet_reassign', replace
    restore
    
    merge 1:1 temp using `indet_reassign', keepusing(choicex)
    replace choice1=choicex if choice1==`count_plus'
    drop choicex _merge
	
	    ** store individual cause assignment
    preserve
    keep sid choice1
    save "$chome/Models/`version'/Out/Reallocated_Individual_Cause_Assignment_`who'`hce'_`split'.dta", replace
    restore
	

    ** NOW WE DO METRICS

    ** get estimated csmfs
    preserve
        contract choice1
        rename _freq est_csmf
        replace est_csmf=est_csmf/`total' 
        rename choice1 `cause_var'
        tempfile est
        save `est', replace
    restore
    ** get true csmfs
    preserve
        contract `cause_var'
        rename _freq true_csmf
        replace true_csmf=true_csmf/`total'  
        tempfile true
        save `true', replace
    restore
    preserve
        * ** merge the true and estimated, calculate the error, collapse the sum of the errors to calculate CMSF accuracy
        clear
        use "`est'", clear
        merge 1:1 `cause_var' using "`true'", nogen
        merge 1:1 `cause_var' using `map', nogen
        replace est_csmf=0 if est_csmf==.
        replace true_csmf=0 if true_csmf==.
        tempfile csmfs
        save `csmfs', replace
        
        ** save "$chome/Models/`version'/Out/csmfs_`who'`hce'_`split'_abs`abs_cutoff'_cut`cutoff'.dta", replace
        save "$chome/Models/`version'/Out/csmfs_`who'`hce'_`split'.dta", replace
        
        * ** collapse the sum of true and estimated CSMFs by the aggregate cause list... this only affects adults
        collapse (sum) est_csmf (sum) true_csmf, by(`aggr_cl')

        * ** absolute error calculation:
        gen absolute_error = abs(true_csmf - est_csmf)
        tempfile csmfs_aggr
        save `csmfs_aggr', replace	

        ** get the min true csmf
        summarize true_csmf
        local min = r(min)	
        collapse (sum) absolute_error					

        * ** calculate CSMF accuracy:
        gen accuracy = 1-(absolute_error/(2*(1-`min')))
        keep accuracy
        tempfile accuracy
        save `accuracy', replace
		
		gen ccsmf_accuracy = (accuracy - .632) / (1 - .632)
		keep ccsmf_accuracy
        tempfile ccsmf_accuracy
        save `ccsmf_accuracy', replace
    restore

    levelsof `cause_var', local(n)
    capture drop correct
    * ** gen correct = 0

    // Start CCC, revert to inclusion of indeterminants
    use `with_indet', clear
    
    * ** this is where i reclassify being "correct" by using the aggregation map. essentially i do a few renames and stuff and then i have the estimated cause by aggregation
    if "`who'"== "Adult" {
        capture drop `aggr_cl'
        rename `cause_var' `cause_var'_p
        rename choice1 `cause_var'

        merge m:1 `cause_var' using `map_indet'

        drop _merge
        gen choice1_grouped = `aggr_cl'

        drop `aggr_cl'
        rename `cause_var' choice1
        rename `cause_var'_p `cause_var'
    }
    * ** end who = Adult
    else if "`who'" != "Adult" {
        gen choice1_grouped = choice1
    }
    
    merge m:1 `cause_var' using `map'
    drop if _merge !=3
    drop _merge

	** *************NEW METRICS AS OF 11/12/2013: straight concordance, sensitivity and specificity by cause
	
	** calculate percent concordance, sensitivity & specificity by cause
	forvalues i=1/`aggregate_cause_count' {
		** first just do straight concordance
		count if choice1_grouped==`i' & `aggr_cl'==`i'
		local total_correct=`r(N)'
		count if `aggr_cl'==`i'
		local total_cause=`r(N)'
		if `total_cause' != 0 {
			local conc_`i'=`total_correct'/`total_cause'
		}
		else {
			local conc_`i'=.
		}

		** sensitivity = total true positives / (total true positives + total false negatives)
		** specificity = total true negatives / (true negatives + false positives)	
		** true positives:
		count if choice1_grouped==`i' & `aggr_cl'==`i'
		local truepos=`r(N)'
		** false negatives
		count if `aggr_cl'==`i' & choice1_grouped!=`i'
		local falseneg=`r(N)'
		** true negatives
		count if choice1!=`i' & `aggr_cl'!=`i'
		local trueneg=`r(N)'
		** false positives
		count if choice1_grouped==`i' & `aggr_cl'!=`i'
		local falsepos=`r(N)'
		local sensitivity_`i' = `truepos'/(`truepos'+`falseneg')
		local specificity_`i' = `trueneg'/(`trueneg'+`falsepos')		
	}
	** save all of those locals in a tempfile to merge onto the other results later
	preserve
	clear
	set obs `aggregate_cause_count'
	gen sensitivity=.
	gen specificity=.
	gen pct_concordance=.
	gen `aggr_cl'=.
	forvalues i=1/`aggregate_cause_count' {
		replace `aggr_cl'=`i' in `i'
		replace sensitivity=`sensitivity_`i'' in `i'
		replace specificity=`specificity_`i'' in `i'
		replace pct_concordance=`conc_`i'' in `i'
	}
	tempfile sens_spec_split
	save `sens_spec_split', replace
	restore
	
	** ALSO calculate kappa statistic from individual-level results to append on at the end like CSMF Accuracy and Pct Indeterminate
	kap choice1_grouped `aggr_cl'
	local kappa_stat=`r(kappa)'
	preserve
	clear
	set obs 1
	gen kappa1=`kappa_stat'
	tempfile kappas
	save `kappas'
	restore
	
    * ** start calculating concordance...
    gen correct = 0
    replace correct = 1 if choice1_grouped==`aggr_cl'

    gen truepositive = 0
    replace truepositive = 1 if correct==1
    gen falsenegative = 0
    replace falsenegative = 1 if correct==0
	
    collapse (sum) truepositive (sum) falsenegative, by(`aggr_cl')
    gen correct = truepositive/(truepositive + falsenegative)
    drop true* false*

    tabstat correct

    preserve
        use `map', clear
        duplicates drop `aggr_cl', force
        tempfile maps_aggr
        save `maps_aggr', replace
        clear
    restore
    
    collapse correct, by(`aggr_cl')
    merge 1:1 `aggr_cl' using `maps_aggr', nogen keepusing(`aggr_cl_text')
    
    // if 0 true deaths for cause we need to impute 0 as sensitivity
    replace correct=0 if correct==.
    
    order correct, last
    di in red "mean concordance across causes, aggregate for number of causes = 1:"
    
    rename correct correct`split'
    
    * ** calculate chance-corrected concordance:
    gen pc3k`split' = ((correct`split' - (1/`aggregate_cause_count')))/(1 - 1/`aggregate_cause_count')
    tabstat pc3k`split', s(mean) save
    matrix A = r(StatTotal)
    
    local meanpc3k = A[1,1]
    count
    local tc = r(N) + 1
    set obs `tc'
    replace pc3k`split' = `meanpc3k' in `tc'
    drop correct
    replace `aggr_cl_text' = "Mean PC3" in `tc'
    
    * ** replace pc3k`split' = round(pc3k`split', .001)
	
	
    rename pc3k`split' pc3k
    merge 1:1 `aggr_cl' using `csmfs_aggr', nogen
	merge 1:1 `aggr_cl' using `sens_spec_split', nogen
    append using `accuracy'
    append using `pct_indet'
	append using `kappas'
	append using `ccsmf_accuracy'
	
    gen abs_cutoff=`abs_cutoff'
    gen cutoff=`cutoff'
    
    replace `aggr_cl_text' = "CCSMF Accuracy" if ccsmf_accuracy !=.
	replace `aggr_cl_text' = "CSMF Accuracy" if accuracy !=.
    replace `aggr_cl_text' = "Percent Indeterminant" if pct_indet !=.
    replace `aggr_cl_text' = "Kappa Statistics" if kappa1 !=.
	capture mkdir "$chome/Models/`version'/Results"
    capture mkdir "$chome/Models/`version'/Results/Splits"
    ** if ("`c(os)'"=="Windows") save "$home/Models/`version'/Results/Splits/split`split'_`who'_hce`hce'_feat`feat'_abs`abs_cutoff'_cut`cutoff'.dta", replace
    ** else save "$chome/Models/`version'/Results/Splits/split`split'_`who'_hce`hce'_feat`feat'_abs`abs_cutoff'_cut`cutoff'.dta", replace

    save "$chome/Models/`version'/Results/Splits/split`split'_`who'_hce`hce'_feat`feat'.dta", replace

    ** clean up after myself
    if `practice'!=1 {
        ** !rmdir "$chome/Models/`version'/Cluster" /q
        ** !rmdir "$chome/Models/`version'/Code" /q
        ** !rmdir "$chome/Models/`version'/Out" /q
    }
    
    levelsof accuracy if `aggr_cl_text'=="CSMF Accuracy", local(accuracy_result)
    levelsof pc3k if `aggr_cl_text'=="Mean PC3", local(pc3k_results)
    levelsof pct_indet if `aggr_cl_text'=="Percent Indeterminant", local(pc3k_results)
    

    
   ** clean up after myself    
   erase "$chome/Models/`version'/Out/test_t`type'_sp`split'_`who'_hce`hce'_feat`feat'.dta"
   erase "$chome/Models/`version'/Out/train_t`type'_sp`split'_`who'_hce`hce'_feat`feat'.dta"
   erase "$chome/Models/`version'/Out/tariff_ranks_module_`who'_MRR`hce'_split`split'_feat`feat'.csv"
   erase "$chome/Models/`version'/Out/uniformtrain/`who'_MRR`hce'_split`split'_feat`feat'_uniformtrain.csv"
   erase "$chome/Models/`version'/Out/tariff_ranks_module_`who'_MRR`hce'_split`split'_feat`feat'_train.csv"
   erase "$chome/Models/`version'/Out/weights/weights_split`split'_`who'_hce`hce'_feat`feat'.dta"
   ** not this one b/c want to compile individual assignments
   ** erase "$chome/Models/`version'/Out/Individual_Cause_Assignment_`who'`hce'_`split'.dta"
   cap erase "$chome/Models/`version'/Out/proportions split`split'_`who'_hce`hce'_feat`feat'.dta"
   erase "$chome/Models/`version'/Out/uniformtrain assignments_split`split'_`who'_hce`hce'_feat`feat'.dta"
   cap erase "$chome/Models/`version'/Out/weights/weights_split`split'_`who'_hce`hce'_feat`feat'.dta"
   erase "$chome/Models/`version'/Out/csmfs_`who'`hce'_`split'.dta"
   erase "$chome/Models/`version'/Out/drop_below_zero_tariff_ranks_module_`who'_MRR`hce'_split`split'.csv"
   cap erase "$chome/Models/`version'/Out/Rank`split'_`who'_hce`hce'_feat`feat'_train.R" 
	capture log close

   ** end of abs_cutoff loop
** }
** }
