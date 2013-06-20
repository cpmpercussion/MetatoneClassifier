## R --vanilla CMD BATCH mixups.r r.out

library('randomForest')
library('plyr')
library('foreach')
library('doMC')
registerDoMC()

load("RData/mixup-init-30s.RData")

mixed.groups.modelling <- function(feature.df, num.tests, feature.subsets = "all"){
  result <- ldply(feature.subsets,
        function(features){
          print(sprintf("%5.1f%%   %s",
                        100*(match(features, feature.subsets)/length(feature.subsets)),
                        do.call(paste, c(as.list(features), sep = ", "))))
          mixed.up <- ldply(c(rep(list(1:12), num.tests %/% 10),
                              rlply(num.tests - (num.tests %/% 10), sample.int(12))),
                            function(x){
                              forest <- randomForest(x=feature.df[feature.subset(features)], y=factor(mus.groups[x][feature.df$name]))
                              mixups <- aaply(matrix(x, ncol=3, byrow=TRUE),
                                              1,
                                              function(y){
                                                length(unique(mus.groups[y]))
                                              })
                              c(mus.names[x],
                                mixups,
                                total.mixups = sum(mixups) - 4,
                                err.rate = mean(forest$confusion[,dim(forest$confusion)[2]]))
                      })
          cbind(feat.subset = do.call(paste, c(as.list(features), sep = "&")),
                mixed.up)
        },
                  .parallel = TRUE)
  names(result)[2:17] <- c(sapply(1:12, function(x) paste("M", x, sep="")),
                               sapply(1:4, function(x) paste("G", x, ".div", sep="")))
  result
}

mixups.df <- mixed.groups.modelling(clean.df, 200, feature.subsets = subset.combinations)

save(mixups.df, file = "RData/mixup-results-30s.RData")
