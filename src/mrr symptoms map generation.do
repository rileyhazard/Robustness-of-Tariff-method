** Pete Serina
** 6/26/12
** generate mmr symptoms map for revised and published data

if ("`c(os)'"=="Windows") local prefix	"J:"
else local prefix "/home/j"

local who $who
insheet using "`prefix'/Project/VA/Publication_2015/Revised Data/Codebook/tariffs_`who'.csv", clear

keep xs_name mrr

tostring mrr, replace

sxpose, clear 

foreach var of varlist * {
    local name = `var'[1]
    rename `var' `name'
}
drop in 1
destring *, replace

order * , alphabetic

outsheet using "`prefix'/Project/VA/Publication_2015/Revised Data/Codebook/MRRsymptoms_`who'.csv", c replace
