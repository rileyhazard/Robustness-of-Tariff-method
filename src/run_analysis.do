clear all
set more off

local repo = "C:/Users/josephj7/Desktop/repos/va/tariff_2"
global wdir = "`repo'/data/working"
global code_dir "`repo'/src"
local iter 5

if ("`c(os)'"=="Windows") global j  "J:"
else global j "/home/j"

local data_dir "$j/Project/VA/Publication_2015/Revised Data"
local old_data_dir "$j/Project/VA/Publication"

foreach dir in dump freetext maps significance splits tariffs {
    cap mkdir "$wdir/`dir'"
}
cap mkdir "$wdir/significance/draws"
cap mkdir "$wdir/freetext/draws"

// Copy codebooks
cap copy "`data_dir'/Code/Master Cause Map.xlsx" "$wdir/maps/Master Cause Map.xlsx"
cap copy "`data_dir'/Code/Master Codebook.xlsx" "$wdir/maps/Master Codebook.xlsx"

// Copy maps
local map_files : dir "`data_dir'/Maps" file "*", respectcase
foreach f of local map_files {
    cap copy "`data_dir'/Maps/`f'" "$wdir/maps/`f'"
}

// Copy dirichlet draw
cap copy "`old_data_dir'/Revised Data/Splits/dirichlet_draw_6.csv" "$wdir/splits/dirichlet_draw_6.csv"
cap copy "`old_data_dir'/Revised Data/Splits/dirichlet_draw_21.csv" "$wdir/splits/dirichlet_draw_21.csv"
cap copy "`old_data_dir'/Revised Data/Splits/dirichlet_draw_34.csv" "$wdir/splits/dirichlet_draw_34.csv"

// Free text dictionaries
cap copy "`old_data_dir'/FreeText/Maps/archive/DICT-5_publication.csv" "$wdir/freetext/DICT-5.csv"
cap copy "`old_data_dir'/FreeText/Maps/dropWords.csv" "$wdir/freetext/dropWords.csv"
cap copy "`old_data_dir'/FreeText/Maps/keepWords.csv" "$wdir/freetext/keepWords.csv"

// Extract raw data
do "$code_dir/VA Final Prep.do" "`repo'"

// Process free text
*** NOTE *** requires `readstata13` and `tm` packages installed in default R installation
!RScript --vanilla $code_dir/parse_text.R "`repo'"
do "$code_dir/bootstrap tariffs of free text vars.do" "`repo'" "Adult" `iter'
do "$code_dir/bootstrap tariffs of free text vars.do" "`repo'" "Child" `iter'
do "$code_dir/bootstrap tariffs of free text vars.do" "`repo'" "Neonate" `iter'
do "$code_dir/turn tm text into s vars.do" "`repo'" `iter'

// Map to symptomss
do "$code_dir/Adult Symptom Var Prep.do" "`repo'"
do "$code_dir/Child Symptom Var Prep.do" "`repo'"
do "$code_dir/Neonate Symptom Var Prep.do" "`repo'"

// Determine significance
*** NOTE *** requires `sxpose` stata packag installed
do "$code_dir/bootstrap tariffs.do" "`repo'" `iter'


do "$code_dir/Tariff Prep.do" "`repo'" `iter'

*** NOTE *** requires `readstata13` package installed in default R installation
!RScript --vanilla $code_dir/04_generate_splits.R
