##############################################################
# Author: 	Pete Serina
# Date:		09/07/2012
# Notes: 	This file generates test/train splits for running VA methods
# source:   source("/home/j/Project/VA/Publication/Revised Data/Code/04_generate_splits.R")
##############################################################

# Set OS
if (.Platform$OS.type=="windows") prefix = "J:"  else if (.Platform$OS.type=="unix") prefix = "/home/j" else cat("ERROR IN PLATFORM...")

library(foreign)
set.seed(123)

who="Neonate"
for (who in c("Neonate")) {
    if (who=="Adult") {
		cause_var = "va34"
		cause_count = 34
    }
		
    if (who=="Neonate") {
		cause_var = "va34"
		cause_count = 6
    }


    if (who=="Child") {
        cause_count = 21
		cause_var = "va34"
	}
    
    # get population size in data set to sample up to
    data = read.dta(paste(prefix, "/Project/VA/Publication/Revised Data/Symptom Data/", who, "Data.dta", sep=""))
    pop_size = nrow(data)
    
    # create an empty matrix to fill in with split counts
    splits= matrix(-1, nrow=nrow(data), ncol=500)
    colnames(splits) = paste("test", 1:500, sep="")
    
    # read in dirichlet draws (random csmfs)
    home = paste(prefix, "/Project/VA/Publication/Revised Data/", sep="")
    dirichlet = read.csv(paste(home, "Splits/dirichlet_draw_", cause_count, ".csv", sep=""), stringsAsFactors=FALSE)
    # turn CSMFs into estimated number of deaths per cause per split
    dirichlet_pop = round(pop_size*dirichlet)
    
    draw=1
    for (draw in 1:500) {
        cause=6
        for (cause in 1:cause_count) {
            # get the 75/25, train/test split
            p25 = round(sum(data[, cause_var]==cause )/4)
            test_binary_index = sample(which(data[, cause_var] == cause) , p25, replace=FALSE)

            # keep train and test separate.  put all test obs as -1 for now
            splits[test_binary_index,draw] = -1
            
            # sample with replacement from test up to CSMF specified in dirichlet to pop size of the data set    
            test_index=sample(test_binary_index, dirichlet_pop[draw,cause], replace=TRUE)
            
            # # get freq of how much each obs shows up
            test = table(test_index)
			
            # loop through and add these observations to the particular split
            for (ii in names(test)) splits[as.numeric(ii),draw] <- test[ii]
            

        }
        
        cat(paste("Finished Draw", who, draw, "\n"))
        flush.console()
    }
    
    # grab sids
    sids= as.matrix(data$sid)
    colnames(sids)="sid"
    # format the numbers to be smaller
    splits_format=format(splits, digits=1)
    # combine splits and sids
    splits_df = as.data.frame(cbind(sids, splits))
    splits_df$sid=as.character(splits_df$sid)
    write.dta(splits_df, paste(prefix, "/Project/VA/Publication/Revised Data/Splits/", who, "_splits_", cause_count, ".dta", sep=""), convert.factors="numeric")
    cat(paste("Saved", who, "\n"))
}
