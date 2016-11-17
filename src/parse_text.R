##############################################################
# Author: 	Peter serina
# Date:	08162012
# Notes: 	id free text in data, apply mohsen's dictionary to find words, then parse apart the words
# source: source("/home/j/Project/VA/external_va/FreeText/Code/00_text_mining_external.R")
#
# DO NOT USE THE LATEST VERSION OF `tm`
# There is a change in tm v0.6 which breaks this code (also I don't know how different the algorithm is)
# install.packages("http://cran.r-project.org/bin/windows/contrib/3.0/tm_0.5-10.zip",repos=NULL)
##############################################################

library(tm)
library(rJava)
library(foreign)
library(readstata13)

if (length(args)==0) {
    working_dir = paste(args[1], "data/working/")
} else {
    working_dir = "C:/Users/josephj7/Desktop/repos/va/tariff_2/data/working/"
}

for (who in c("Neonate", "Child", "Adult")) {
    
	targetFile = paste(working_dir, "freetext/", who, "_words_all_variables_50freq.csv", sep="")
    
    data = read.dta13(paste(working_dir, "VA Final - ", who, ".dta", sep=""))

    # specify the minimum word count for the feature to be tokenized
	targetFreq = 50

	keepWords = read.csv(paste(working_dir, "freetext/keepWords.csv", sep=""), stringsAsFactors=FALSE)
	
    # subset keepWords for only particular module
    keepWords = keepWords[,c(who)]
    
    attach(data)

    #keep free text, and bring all text variables under one with unique identifier
    if (who=="Adult") {
        text = paste(a5_01_9b, a6_08,  a6_11, a6_12, a6_13, a6_14, a6_15, a7_01, a7_02, a7_03, a7_04, a7_05, a7_06, a7_07, a7_08, a7_09, a7_10)
        all.txt = data.frame(sid, text)
    }

    if (who=="Child") {
        text = paste(c5_09,  c5_12, c5_13, c5_14, c5_15, c5_16, c6_01, c6_02, c6_03, c6_04, c6_05, c6_06, c6_07, c6_08, c6_09, c6_10)
        all.txt = data.frame(sid, text)
    }
            
    if (who=="Neonate") {
        text = paste(c3_43,  c5_09,  c5_12, c5_13, c5_14, c5_15, c5_16, c6_01, c6_02, c6_03, c6_04, c6_05, c6_06, c6_07, c6_08, c6_09, c6_10)
        all.txt = data.frame(sid, text)
    }

    detach(data)
    
    write.csv(all.txt, paste(working_dir, "freetext/", who, "_all_words_pre_dictionary.csv", sep=""))

    #This is where we used to bring in Mohsen's Dictionary, I have updated it to include spell check and clinical stuff we have uncovered through this process
    dict = read.csv(paste(working_dir, "freetext/DICT-5.csv", sep=""), stringsAsFactors=FALSE)

    # replace words based on dictionary, but not going to catch everything.  Just stuff by commas, periods, semicolons, and spaces.
    i=1
    for(i in 1:nrow(dict)) {
        all.txt[,2] = gsub(paste(" ", dict$old[i], " ", sep=""), paste(" ", dict$new[i], " ", sep=""), all.txt[,2], ignore.case = TRUE)
        all.txt[,2] = gsub(paste(" ", dict$old[i], "\\.", sep=""), paste(" ", dict$new[i], " ", sep=""), all.txt[,2], ignore.case = TRUE)
        all.txt[,2] = gsub(paste(" ", dict$old[i], ",", sep=""), paste(" ", dict$new[i], " ", sep=""), all.txt[,2], ignore.case = TRUE)
        all.txt[,2] = gsub(paste(" ", dict$old[i], ";", sep=""), paste(" ", dict$new[i], " ", sep=""), all.txt[,2], ignore.case = TRUE)
        all.txt[,2] = gsub(paste(" ", dict$old[i], "/", sep=""), paste(" ", dict$new[i], " ", sep=""), all.txt[,2], ignore.case = TRUE)
        all.txt[,2] = gsub(paste(" ", dict$old[i], "'", sep=""), paste(" ", dict$new[i], " ", sep=""), all.txt[,2], ignore.case = TRUE)
    }

    write.csv(all.txt, paste(working_dir, "freetext/", who, "_all_words.csv", sep=""))

	#specify the unique identifier
	id = all.txt$sid
	
    text= data.frame(all.txt$text)
    
	DFS = DataframeSource(text)
		
	ovid = Corpus(DFS, readerControl = list(language = "en"))

	###Process Text and Generate TDM and DTM
	ovid = tm_map(ovid, tolower)
	# removing stop words (ie "the")... this is a standard text mining operation
	ovid = tm_map(ovid, removeWords, stopwords("en"))
	ovid = tm_map(ovid, removePunctuation)
	ovid = tm_map(ovid, stripWhitespace)
	ovid = tm_map(ovid, removeNumbers)
	ovid = tm_map(ovid, stemDocument, language = "english")


	dtm_tf = DocumentTermMatrix(ovid)
	wordFreq = colSums(as.matrix(dtm_tf))
	dtm_tf = dtm_tf[, (wordFreq>targetFreq) | colnames(dtm_tf) %in% keepWords]
	output = cbind(data.frame(id), as.matrix(dtm_tf))
	colnames(output) = paste("word_", colnames(output), sep="")

	#save the output in the working directory:
	write.csv(output, targetFile, row.names=FALSE)
}
