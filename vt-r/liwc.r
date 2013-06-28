########
# lwic #
########

get.liwc.counts.path <- function(group, session) {
  paste("/Users/ben/Projects/Viscotheque/data/ex2/transcript/liwc/",
        group,
        "-",
        session,
        "-counts.csv",
        sep = "")
}

# create the liwc data frame

library('plyr')

liwc.df <- ddply(id.df,
                 .(g, s),
                 function(x) {
                   fpath <- get.liwc.counts.path(x$g[1], x$s[1])
                   read.csv(fpath, header = TRUE)
                 })

liwc.df$SpeakerId <- sapply(liwc.df$SpeakerId, de.anon.name)
names(liwc.df)[3] <- "name"

# set up levels and orders for factors

liwc.df$g <- ordered(liwc.df$g)
liwc.df$s <- ordered(liwc.df$s)

liwc.df$name <- factor(liwc.df$name,
                       levels = c("ALL", "INT", levels(id.df$name)),
                       ordered = TRUE)

# remove extraneous columns
liwc.df <- liwc.df[1:71]

# remove 'all' and 'int' comments
liwc.df <- liwc.df[!(liwc.df$name %in% c("ALL", "INT")),]

# calculate group word totals
liwc.df <- ddply(liwc.df, .(g, s), function(x) cbind(x[1:4],sum(x$all.words), x[-(1:4)]))
names(liwc.df)[5] <- "group.words"

## normalise

liwc.df <- cbind(liwc.df[1:5], llply(liwc.df[-(1:5)]/liwc.df$group.words, function(x) { x/sd(x) }))
liwc.df <- Filter(function(x) !(TRUE %in% is.nan(x)), liwc.df)

############
# analysis #
############

# visualisation

library('ggplot2')

word.var <- ddply(liwc.df,
                  .(name),
                  function(x) {
                    apply(x[-(1:4)], 2, var)
                  })

melted.liwc <- melt(liwc.df[-c(4:5,68:69)], id.vars=1:3)
ggplot(melted.liwc, aes(x = variable, y = value)) + geom_boxplot() + opts(axis.text.x=theme_text(angle=90, hjust=1)) + coord_flip()
qplot(x=s, y=feel, data=liwc.df, geom="line", group=name, colour=name)

# clustering

library('randomForest')
library('cluster')

## supervised

rf <- randomForest(x=liwc.df[-(1:5)], y=factor(liwc.df$g))

qplot(x=factor(g), y=feel, data=liwc.df, geom="boxplot", fill=name)

test <- sort(sample.int(dim(liwc.df)[1], dim(liwc.df)[1] %/% 10))
train <- -test

sc <- specc(as.matrix(liwc.df[-(1:3)]), centers=4)

## unsupervised

rf <- randomForest(x=liwc.df[-(1:5)], proximity = TRUE)
diss.mat <- sqrt(1 - rf$proximity)
mds <- isoMDS(diss.mat, k=2)
clusters <- pam(diss.mat, k = 3, diss = TRUE)

qplot(x=mds$points[,1], y=mds$points[,2], geom="point", colour=factor(clusters$clustering))

qplot(factor(clusters$clustering), geom="bar", fill=factor(liwc.df$g))
