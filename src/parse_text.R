##############################################################
# Author: 	Peter serina
# Date:	08162012
# Notes: 	id free text in data, apply mohsen's dictionary to find words, then parse apart the words
# source: source("/home/j/Project/VA/external_va/FreeText/Code/00_text_mining_external.R")
##############################################################

who = "Adult"

library(tm)
library(rJava)
library(foreign)

for (who in c("Neonate", "Child", "Adult")) {
	
    setwd("J:/Project/VA/Publication/FreeText/Words")
	targetFile = paste(who, "_words_all_variables_50freq.csv", sep="")
    
    data = read.dta(paste("J:/Project/VA/Publication/Revised Data/Presymptom Data/VA Final - ", who, ".dta", sep=""))

    # specify the minimum word count for the feature to be tokenized
	targetFreq = 50

	keepWords = read.csv("J:/Project/VA/Publication/FreeText/Maps/keepWords.csv", stringsAsFactors=FALSE)
	
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
    
    write.csv(all.txt, paste("J:/Project/VA/Publication/FreeText/Words/", who, "_all_words_pre_dictionary.csv", sep=""))

    #This is where we used to bring in Mohsen's Dictionary, I have updated it to include spell check and clinical stuff we have uncovered through this process
    dict = read.csv("J:/Project/VA/Publication/FreeText/Maps/DICT-5.csv", stringsAsFactors=FALSE)

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

    write.csv(all.txt, paste("J:/Project/VA/Publication/FreeText/Words/", who, "_all_words.csv", sep=""))

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
