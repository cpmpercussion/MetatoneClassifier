####################
## random forests ##
####################

library('randomForest')
library('reshape2')
library('plyr')
library('ggplot2')

## setting up the feature data frame

rf.feature.df <- cbind(feature.df[feature.subset("id")], na.roughfix(feature.df[feature.subset("all")]))

## construct synth features

synth.feature.df <- cbind(feature.df[feature.subset("id")], feature.df[sample(1:dim(feature.df)[1], replace = FALSE), feature.subset("all")])

## RFs by session

rf.on.name <- randomForest(x=rf.feature.df[feature.subset("noaudio")],
                           y=rf.feature.df$name,
                           ntree = 2000,
                           importance = TRUE)

rf.on.group <- randomForest(x=rf.feature.df[feature.subset("all")],
                            y=factor(rf.feature.df$g),
                            ntree = 2000,
                            importance = TRUE)

make.rf.by.session.list <- function(rf.feature.df, class.target){
  dlply(rf.feature.df,
        .(s),
        function(s.df){
          switch(class.target,
                 name = randomForest(x=s.df[feature.subset("noaudio")],
                   y=s.df$name,
                   ntree = 2000,
                   importance = TRUE),
                 group = randomForest(x=s.df[feature.subset("all")],
                   y=factor(s.df$g),
                   ntree = 2000,
                   importance = TRUE))
        })
}

rfs.on.name <- make.rf.by.session.list(rf.feature.df, "name")
rfs.on.group <- make.rf.by.session.list(rf.feature.df, "group")

## for rf confusion plots

make.conf.df <- function(confusion.data){
  if(class(confusion.data) == "matrix"){
    conf.df <- melt(confusion.data[,-dim(confusion.data)[2]])
  }else{
    message("faceting by session")
    conf.df <- ldply(confusion.data,
                     function(conf.mat){
                       melt(conf.mat[,-dim(conf.mat)[2]])
                     })
    names(conf.df)[1] <- "s"
    conf.df
  }
  on.group <- length(unique(conf.df$Var1)) == 4
  if(on.group){
    conf.df$Var1 <- factor(conf.df$Var1)
    conf.df$Var2 <- factor(conf.df$Var2)
    conf.df$error.type <- factor(ifelse(conf.df$Var1 == conf.df$Var2,
                                        "correct",
                                        "incorrect"))
  }else{
    conf.df$Var1 <- get.unique.name(conf.df$Var1)
    conf.df$Var2 <- get.unique.name(conf.df$Var2)
    conf.df$error.type <- factor(unlist(alply(conf.df[c("Var1", "Var2")], 1,
                                            function(nms){
                                              if(get.group.for.name(nms[1,1]) ==
                                                 get.group.for.name(nms[1,2])){
                                                if(nms[1,1] == nms[1,2]){
                                                  "correct"
                                                }else{
                                                  "same.group"
                                                }
                                              }else{
                                                "diff.group"
                                              }
                                            })),
                                 levels = c("correct", "same.group", "diff.group"),
                                 ordered = TRUE)
  }
  conf.df
}

## for rf feature importance plots

make.imp.df <- function(imp.data){
  imp.mat.to.df <- function(imp.mat){
    imp.df <- data.frame(feature = factor(rownames(imp.mat),
                           ordered = TRUE,
                           levels = rownames(imp.mat)),
                         type = factor(sapply(rownames(imp.mat), feature.type),
                           levels = names(feature.type.list)[-1],
                           ordered = TRUE),
                         mean.decrease.accuracy = imp.mat[,dim(imp.mat)[2] - 1])
    rownames(imp.df) <- NULL
    imp.df
  }
  if(class(imp.data) == "matrix"){
    imp.df <- imp.mat.to.df(imp.data)
  }else{
    imp.df <- ldply(imp.data,
                     function(imp.mat){
                       imp.mat.to.df(imp.mat)
                     })
    names(imp.df)[1] <- "s"
    imp.df
  }
  imp.df
}

## MDS

name.mds.df <- ldply(rf.by.session.list,
                     function(rf){
                       diss.mat <- rf$confusion[,-dim(rf$confusion)[2]]/apply(rf$confusion[,-dim(rf$confusion)[2]], 1, sum)
                       diss.mat[diag(dim(diss.mat)[1])==1] <- 0
                       diss.mat <- sqrt(1 - diss.mat)
                       mds.points <- data.frame(isoMDS(diss.mat, k=2)$points)
                       mds.points <- cbind(get.group.for.name(row.names(mds.points)),
                                           get.unique.name(row.names(mds.points)),
                                           mds.points)
                       row.names(mds.points) <- NULL
                       names(mds.points) <- c("g", "name", "x", "y")
                       mds.points
                     })

name.mds.df <- ldply(rf.by.session.list,
                     function(rf){
                       diss.mat <- rf$confusion[,-dim(rf$confusion)[2]]/apply(rf$confusion[,-dim(rf$confusion)[2]], 1, sum)
                       diss.mat[diag(dim(diss.mat)[1])==1] <- 0
                       diss.mat <- sqrt(1 - diss.mat)
                       mds.points <- data.frame(isoMDS(diss.mat, k=2)$points)
                       mds.points <- cbind(get.group.for.name(row.names(mds.points)),
                                           get.unique.name(row.names(mds.points)),
                                           mds.points)
                       row.names(mds.points) <- NULL
                       names(mds.points) <- c("g", "name", "x", "y")
                       mds.points
                     })

# mixed up groups

rf.feature.df <- cbind(feature.df[feature.subset("id")],
                  na.roughfix(feature.df[!feature.subset("id")]))

mus.names <- unique(id.df$name)
mus.groups <- id.df$g[!duplicated(id.df$name)]
names(mus.groups) <- as.character(mus.names)

subset.combinations <- do.call(c,
                               llply(1:5,
                                     function(x){
                                       combn(names(feature.type.list)[2:6], x, simplify = FALSE)
                                     }))

save(rf.feature.df, mus.names, mus.groups, feature.subset, feature.info, subset.combinations, file = "RData/mixup-init-30s.RData")

## source("mixups.r")

mixups.df <- mixed.groups.modelling(rf.feature.df, 2, feature.subsets = subset.combinations)

mixups.df <- ddply(mixups.df,
                   .(feat.subset),
                   function(x){
                     subset.cols <- as.list(names(feature.type.list) %in% strsplit(as.character(x$feat.subset[1]), "&", fixed = TRUE)[[1]])
                     names(subset.cols) <- names(feature.type.list)
                     data.frame(subset.cols, x[-1])
                   })

## plotting

ggplot(mixups.df, aes(x = factor(total.mixups), y = err.rate)) + geom_jitter(alpha=0.2, aes(colour=factor(feat.subset)))

lm(err.rate ~ total.mixups, mixups.df)

qplot(melt(syhtnetic.df, id.vars="diversity.1", measure.vars="touch.distance")), ordered=TRUE, levels=rownames(rf$importance)), rf$importance[,1], geom="bar", stat="identity", fill=sapply(rownames(rf$importance), feature.type)) + opts(axis.text.x=theme_text(angle=90, hjust=1))

## alternate column naming schemes

group.change.map <- llply(splits,
                          function(x){
                            result <- mus.names[x]
                            names(result) <- mus.names
                            result
                          },
                          .progress = "text")

## test set

test <- sort(sample.int(dim(feature.df)[1], dim(feature.df)[1] %/% 10))
train <- -test

rf <- randomForest(x=feature.df[train, feature.subset("audio")], y=factor(feature.df$name)[train], xtest=feature.df[test, feature.subset("audio")], ytest=factor(feature.df$name)[test])

## rf plots

ggplot(data = NULL, aes(x = factor(rownames(rf$importance), ordered=TRUE, levels=rownames(rf$importance)), y = rf$importance[,1])) + geom_bar(stat="identity", aes(fill = sapply(rownames(rf$importance), feature.type))) + opts(axis.text.x=theme_text(angle=90, hjust=1))

ggplot(melt(rf$test$confusion[,-13]), aes(Var1, Var2)) + geom_tile(aes(fill = value)) + scale_fill_gradient(low="white", high="black") + opts(aspect.ratio = 1)

## unsupervised

rf <- randomForest(x=rf.feature.df[!feature.subset("id")], ntree = 2000, proximity = TRUE)
diss.mat <- sqrt(1 - rf$proximity)
mds.results <- isoMDS(diss.mat, k=2)

clusters <- pam(diss.mat, k = 4, diss = TRUE)

qplot(factor(feature.df$time), clusters$clustering, geom="boxplot")

x <- cmdscale(d = rf$proximity, k=2)

qplot(factor(clusters$clustering), geom="bar", fill=factor(feature.df$g))

#########
## svm ##
#########

library('kernlab')

## discriminant analysis

ld <- lda(norm.feature.df[feature.subset("all")], norm.feature.df$name, CV = TRUE)
qd <- qda(norm.feature.df[feature.subset("all")], norm.feature.df$name, CV = TRUE)

rf <- randomForest(x=feature.df[!feature.subset("id") & !feature.subset("accel")], y=factor(feature.df$g))

## svm

smp.idx <- seq(1, dim(norm.feature.df)[1], by = 10)
smp.train <- seq(1, length(smp.idx), by = 3)
smp.train <- rep(c(TRUE, FALSE), length.out = length(smp.idx))

feat.svm <- ksvm(x = as.matrix(feature.df[smp.idx, feature.subset("all")]), y = feature.df$name[smp.idx])
fdf <- feature.df[smp.idx, feature.subset("all")]
fdf <- fdf[apply(fdf, 1, function(x) sum(is.na(x)) == 0),]
mean(as.character(predict(feat.svm, as.matrix(feature.df[smp.idx, feature.subset("all")][apply(fdf, 1, function(x) sum(is.na(x)) == 0),]))) == as.character(feature.df$name[smp.idx + 1][apply(fdf, 1, function(x) sum(is.na(x)) == 0)]))

#########
## knn ##
#########

library('class')

knn.pred <- knn(norm.feature.df[smp.idx, feature.subset("all")], norm.feature.df[smp.idx + 1, feature.subset("all")], feature.df$name[smp.idx], 5)
mean(as.character(knn.pred) == as.character(norm.feature.df$name[smp.idx + 1]))

mean(as.character(knn.cv(norm.feature.df[smp.idx, feature.subset("all")], norm.feature.df$name[smp.idx], 5)) == as.character(norm.feature.df$name[smp.idx]))

####################
## kernel methods ##
####################

train <- sort(sample.int(dim(norm.feature.df)[1], dim(norm.feature.df)[1] %/% 2))

kpc <- kpca(~., data = norm.feature.df[!feature.subsets[["id"]]], kernel = "rbfdot", kpar = list(sigma = 0.01), features = 2)

kpc.df <- norm.feature.df[feature.subsets[["id"]]]
kpc.df[c("x", "y")] <- kpc@rotated

sc <- specc(as.matrix(norm.feature.df[train, -id.cols]), centers=4)

qplot(x, y, data=kpc.df, geom="point", colour=as.factor(g))
qplot(x, y, data=kpc.df, geom="point", colour=as.factor(sc), shape=as.factor(g), size=1.5)

############
## kmeans ##
############

library('flexclust')

feature.clusters <- kcca(norm.feature.df[,-(1:7)], k = 4)
feature.clusters <- kcca(norm.feature.df[,-c(1:7, dim(norm.feature.df)[2])], k = 4)
norm.feature.df$cluster <- attr(feature.clusters, "cluster")

library('cluster')

feature.clusters <- kmeans(as.matrix(norm.feature.df[-(1:7)]), centers = 4, nstart = 100)
