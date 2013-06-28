## R CMD BATCH --vanilla class-error.r class-error.out &

library('randomForest')
library('reshape')
library('plyr')
library('kernlab')
library('e1071')
library('foreach')
library('doMC')
registerDoMC()

load("RData/features-5s.RData")

source("vt-header.r")

class.error.by.subset <- function(feature.df, group.var){
  rf.feature.df <- cbind(feature.df[feature.subset("id")],
                         na.roughfix(feature.df[feature.subset("all")]))
  non.NA.idx <- apply(feature.df, 1, function(x) sum(is.na(x)) == 0)
  norm.feature.df <- cbind(feature.df[non.NA.idx, feature.subset("id")],
                           lapply(feature.df[non.NA.idx, feature.subset("all")],
                                  function(x) {
                                    (x-mean(x, na.rm = TRUE))/sd(x, na.rm = TRUE)
                                  }))
  ldply(c("all", names(feature.type.list)[-1], "noaccel"),
        function(feat){
          print(paste("calculating, feature type:", feat))
          if(group.var == "name" && feat == "all"){
            feat <- "noaudio"
          }
          ldply(0:4,
                function(test.idx){
                  ldply(c("s", "j"),
                        function(test.by){
                          print(paste("feature subset:", feat,
                                      "test subgroup:", test.idx,
                                      "test by:", test.by))
                          if(test.idx == 0){
                            ## rf
                            rf.time <- system.time(rf <- randomForest(x = rf.feature.df[, feature.subset(feat)],
                                                                      y = factor(rf.feature.df[[group.var]])))
                            rf.error.rate <- mean(rf$confusion[,dim(rf$confusion)[2]])
                            ## svm
                            svm.time <- system.time(svm.error.rate <- ksvm(x = as.matrix(norm.feature.df[feature.subset(feat)]), y = factor(norm.feature.df[[group.var]]), cross = 5)@cross)
                            ## naive bayes
                            naiveBayes.time <- system.time(feat.naiveBayes <- naiveBayes(x = as.matrix(norm.feature.df[feature.subset(feat)]), y = factor(norm.feature.df[[group.var]])))
                            naiveBayes.error.rate <- 1 - mean(as.character(predict(feat.naiveBayes,
                                                                            norm.feature.df[feature.subset(feat)],
                                                                            type = "class")) ==
                                                       as.character(norm.feature.df[[group.var]]))
                            ## results
                            data.frame(feature.subset = feat,
                                       test.by,
                                       test.idx,
                                       rf.error.rate,
                                       svm.error.rate,
                                       naiveBayes.error.rate,
                                       rf.time = rf.time[3],
                                       svm.time = svm.time[3],
                                       naiveBayes.time = naiveBayes.time[3])
                          }else{
                            ## rf
                            train <- rf.feature.df[[test.by]] != test.idx
                            test <- !train
                            rf.time <- system.time(rf <- randomForest(x = rf.feature.df[train, feature.subset(feat)],
                                                                      y = factor(rf.feature.df[[group.var]])[train],
                                                                      xtest = rf.feature.df[test, feature.subset(feat)],
                                                                      ytest = factor(rf.feature.df[[group.var]])[test]))
                            ## svm
                            train <- norm.feature.df[[test.by]] != test.idx
                            test <- !train
                            svm.time <- system.time(feat.svm <- ksvm(x = as.matrix(norm.feature.df[train, feature.subset(feat)]), y = factor(norm.feature.df[[group.var]])[train]))
                            svm.error.rate <- 1 - mean(as.character(predict(feat.svm,
                                                                            norm.feature.df[test, feature.subset(feat)])) ==
                                                       as.character(norm.feature.df[[group.var]][test]))
                            rf.error.rate <- mean(rf$test$confusion[,dim(rf$test$confusion)[2]])
                            ## naive bayes
                            naiveBayes.time <- system.time(feat.naiveBayes <- naiveBayes(x = as.matrix(norm.feature.df[train, feature.subset(feat)]), y = factor(norm.feature.df[[group.var]])[train]))
                            naiveBayes.error.rate <- 1 - mean(as.character(predict(feat.naiveBayes,
                                                                            norm.feature.df[test, feature.subset(feat)],
                                                                            type = "class")) ==
                                                       as.character(norm.feature.df[[group.var]][test]))
                            ## results
                            data.frame(feature.subset = feat,
                                       test.by,
                                       test.idx,
                                       rf.error.rate,
                                       svm.error.rate,
                                       naiveBayes.error.rate,
                                       rf.time = rf.time[3],
                                       svm.time = svm.time[3],
                                       naiveBayes.time = naiveBayes.time[3])
                          }
                        })
                })
        },
        .parallel = TRUE)
}

class.error.df <- rbind(data.frame(real.or.synth = "real",
                                   class.target = "group",
                                   class.error.by.subset(feature.df, "g")),
                        data.frame(real.or.synth = "real",
                                   class.target = "name",
                                   class.error.by.subset(feature.df, "name")),
                        data.frame(real.or.synth = "synth",
                                   class.target = "group",
                                   class.error.by.subset(synth.feature.df, "g")),
                        data.frame(real.or.synth = "synth",
                                   class.target = "name",
                                   class.error.by.subset(synth.feature.df, "name")))

save(class.error.df, file = "RData/class-error-5s.RData")
