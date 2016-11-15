** author: Pete Serina
** date: 6/25/12
** purpose: Make versions be ten to rank features for item reduction in tariff for revised data
** source: do "J:/Project/VA/Publication_2015/Revised Data/Code/create va models based on symptoms sd.do"    
	
clear all
capture restore, not
local new 1
	
local who $who
local who Neonate
foreach who in Neonate Child Adult {

    local i=1

    if `i'==1 {
    local data "J:/Project/VA/Publication_2015/Revised Data/Codebook/tariffs_`who'.csv"
    }    
    
        if "`who'"=="Adult"  {	
            local whonc = "adult"
            local age 1
        }
        if "`who'"=="Child" {
            local whonc = "child"
            local age 3
        }
        if "`who'"=="Neonate" {
            local whonc = "neonate"
            local age 2
        }
        insheet using "`data'", clear

        keep xs_name-mrr_text
                
        ** turn missings into 0's so that if there because want to get those symptoms that are really good for only one cause
        foreach x of varlist cause* {
            replace `x'=0 if `x'==.
        }
                
                
        ** add sd and mean
        capture drop sd mean
        egen sd= rowsd(cause*)
        capture replace sd=0 if sd==.

        egen mean=rowmean(cause*)
        replace mean=abs(mean)
        
        egen max=rowmax(cause*)
        replace max=abs(max)

        sort mean
        capture drop importance_mean
        g importance_mean= _n

        sort sd
        capture drop importance_sd
        g importance_sd= _n
        
        sort mean
        capture drop importance_max
        g importance_max = _n
        
        // add accuracy for each single feature
        ** preserve
        ** insheet using "J:\Project\VA\Troubleshoot Methods\each feature separate tariff\metrics for each feature separate.csv", clear
        ** rename feature_count xs_name
        ** keep accuracy xs_name
        ** tempfile accuracy
        ** save `accuracy', replace
        ** restore
        ** merge 1:1 xs_name using `accuracy'
        

        ** local x="accuracy"
        foreach x in "sd" {
            forvalues hce = 0/1 {
                preserve
                drop if mrr_text==1
                gsort - `x'
                count
                local count = r(N)
                ** lists of features by tens (NOT FREE TEXT)
                forvalues i = 10(10)`count' {
                    levelsof xs_name in 1/`i', local(symptoms`i')
                }
                ** list of all features (NOT FREE TEXT)
                levelsof xs_name in 1/`count', local(symptoms`count')
                
                ** 1 feature (NOT FREE TEXT)
                forvalues i=1/9 {
                    levelsof xs_name in `i', local(symptoms`i')
                }
                
                restore
                ** only 1 feature
                forvalues i = 1/9 {
                    capture drop `who'_`i'_hce`hce'_`x'
                    gen `who'_`i'_hce`hce'_`x' = 0
                    ** add this here so all free text always counted if hce==1
                        replace `who'_`i'_hce`hce'_`x' = 1 if mrr_text==1 & `hce'==1
                    foreach s of local symptoms`i' {
                        replace `who'_`i'_hce`hce'_`x' = 1 if xs_name=="`s'"
                    }
                }
                ** features by 10
                forvalues i = 10(10)`count' {
                    capture drop `who'_`i'_hce`hce'_`x'
                    gen `who'_`i'_hce`hce'_`x' = 0
                    ** add this here so all free text always counted if hce==1
                        replace `who'_`i'_hce`hce'_`x' = 1 if mrr_text==1 & `hce'==1
                    foreach s of local symptoms`i' {
                        replace `who'_`i'_hce`hce'_`x' = 1 if xs_name=="`s'"
                    }
                }
                ** to get a full set of features....
                forvalues i = `count'/`count' {
                    capture drop `who'_`i'_hce`hce'_`x'
                    gen `who'_`i'_hce`hce'_`x' = 0
                    ** add this here so all free text always counted if hce==1
                        replace `who'_`i'_hce`hce'_`x' = 1 if mrr_text==1 & `hce'==1
                    foreach s of local symptoms`i' {
                        replace `who'_`i'_hce`hce'_`x' = 1 if xs_name=="`s'"
                    }
                }
            }
        }
        levelsof xs_name, clean local(xs_name)
        foreach x of local xs_name {
            g `x'=1
            replace `x'=0 if xs_name=="`x'"
        }
        
        sort xs_name

        ** if "`who'"=="Adult" {
            ** gen checklist=0
            ** replace checklist=1 if substr(xs_name, 1, 5)!="s9999"
            ** foreach s in s9999108 s999969 s999999 s999952 s9999148 s999997 s99994 s9999122 s9999130 s9999104 s999979 {
                ** replace checklist=1 if xs_name=="`s'"
            ** }
        ** }
          
        outsheet using "`data'", comma replace

}
