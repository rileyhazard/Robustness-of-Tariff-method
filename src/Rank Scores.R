# author: Alireza, deciphered by Pete Serina and Andrea Stewart
# date: sometime in early 2011, deciphered 8/12
# purpose: rank within causes and sample up to the largest cause size as to not skew the rankings
# Andrea Stewart updated on 2/20/2013 so that the uniform train is ordered, not sorted


# a sample list of object inputs coming from a stata file
# rm(list=ls())
# require(foreign)
# set.seed(123)
# module = 'Neonate'
# MRR = '0'
# NUMITER = 6
# spl = 100
# feat = 'age'
# prefix = paste('J:/Project/VA/Publication/Models/Tariff/Models/test_345234_andrea_figures_out_problems/Out/', sep='')
# cause.var = 'va34'
# train = read.dta(paste(prefix, 'train_t2_sp100_Neonate_hce0_featage.dta', sep=''))
# test = read.dta(paste(prefix, 'test_t2_sp100_Neonate_hce0_featage.dta', sep=''))

# function to rank test tariff/RF score against list of uniform train tariff/RF scores
rankDeath <- function(scores, deathscore){
    scores <- sort(scores, decreasing=TRUE)
    x <- which(abs(scores-deathscore)==min(abs(scores-deathscore)))
	return(mean(x))
}    

print(NUMITER)
print(module)
print(MRR)

numCauses = NUMITER

# making a uniform train set 
# use all deaths for a certain cause
# then sample w/ replacement up to the number of deaths for the cause with the highest number of deaths (sample_num)

x <- table(train[, cause.var])
sample_num = max(x)

# Create uniform train along with ranks
uniformtrainindex = c()

for (i in 1:numCauses){
	cause_specific_num <- length(which(train[,cause.var]==i))
	uniformtrainindex = c(uniformtrainindex, which(train[, cause.var] == i))
    uniformtrainindex = c(uniformtrainindex, sample(which(train[, cause.var] == i) , sample_num - cause_specific_num, replace=TRUE) )
}
uniformtrain = train[uniformtrainindex, ]

dir.create(paste(prefix, "/uniformtrain", sep=""))

if (exists("feat")==1) {
    featx = paste("_feat", as.character(feat), sep="")
}
if (exists("feat")==0) {
    featx = "_featx"
}
# write.csv(uniformtrain, paste(prefix, "/uniformtrain/", module, "_MRR", MRR, "_split", spl, featx, "_uniformtrain.csv", sep=""), row.names=FALSE)


# Creating ranks
cause=1
 for (cause in 1:numCauses){
	uniformtrain <- uniformtrain[order(uniformtrain[, paste("cause",cause, sep="")], decreasing=TRUE),]
	uniformtrain[, paste("uniform_rank", cause, sep="")] <- seq(1,nrow(uniformtrain),1)
 }
dir.create(paste(prefix, "/uniformtrain", sep=""))

if (exists("feat")==1) {
    featx = paste("_feat", as.character(feat), sep="")
}
if (exists("feat")==0) {
    featx = "_featx"
}

# use this in the Tariff code later
write.csv(uniformtrain, paste(prefix, "/uniformtrain/", module, "_MRR", MRR, "_split", spl, featx, "_uniformtrain.csv", sep=""), row.names=FALSE)

# # make matrix causerank with same number of rows as test with number of causes and column #, fill in with 100000
causerank = matrix(100000, nrow=nrow(test), ncol=numCauses)

# create ranking for each tariff score by ranking it against the uniform data set we created earlier
#i=1
 for (i in 1:nrow(test)){
 #  cause=6
   for (cause in 1:numCauses){
        r = rankDeath(uniformtrain[,paste("cause",cause, sep="")], test[i, paste("cause",cause, sep="")])	
		causerank[i, cause] = r      
  }
}

colnames(causerank) = paste("rank_", 1:numCauses)

write.csv(cbind(test, causerank), paste(prefix, "tariff_ranks_module_", module, "_MRR", MRR, "_split", spl, featx, ".csv", sep=""), row.names=FALSE)
