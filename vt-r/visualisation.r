#################
# visualisation #
#################

library('ggplot2')
library('plyr')
library('reshape2')

## interface heat maps

ftdf <- flat.touch.df[seq(1, dim(flat.touch.df)[1], 10000),]

p <- ggplot(ftdf, aes(x, y))

p.scatter <- p + geom_point(aes(colour=factor(touch.count), alpha=ifelse(delta.t<=1, delta.t, 1))) + opts(aspect.ratio=3/2) + scale_colour_brewer(pal = "Set1")
p.scatter + facet_grid(. ~ name, labeller=label_both)
p.scatter + facet_wrap(~ name, drop=FALSE, as.table=TRUE, ncol=6)

################
## feature.df ##
################

## touches per session

p <- compscatter(ftdf, "test", .5)
p <- groupscatter(group1, "test", .5)
p <- allheatmap(ftdf, "test", .5)
p + scale_fill_gradient2(limits=c(0, 70), low="black", mid="red", high="yellow", space="Lab")



make.frames(ftdf, groupscatter, c("g", "j"), path.to.frames(30, "test"), 30, 5, .5)


p <- ggplot(feature.df, aes(x=touches.down.per.sec))

p.dens <- p + geom_density(alpha=0.4, aes(y=..density.., kernel="epanechnikov", colour=name)) + xlim(0,2) + opts(title="Touch-down density", plot.title=theme_text(size=20, face="bold")) + labs(x="touches down per second", y="proportion of session")
p.dens + facet_grid(s ~ g, labeller=label_both)

p.dens <- p + geom_density(alpha=0.4, aes(y=..density.., kernel="epanechnikov", colour=s)) + xlim(0,2) + opts(title="Touch-down density", plot.title=theme_text(size=20, face="bold")) + labs(x="touches down per second", y="proportion of session")
p.dens + facet_grid(. ~ name, labeller=label_both)

ggsave(file="figures/touch-down-density-by-group.pdf")

p.hist <- p + geom_histogram(aes(y=..density.., fill=name), binwidth = .25, position="dodge") + xlim(0,2) + opts(title="Touch activity", plot.title=theme_text(size=20, face="bold")) + labs(x="touches down per second", y="proportion of session")
p.hist + facet_grid(s ~ name, labeller=label_both)

p.hist <- p + geom_histogram(aes(y=..density.., fill=s), binwidth = .25, position="dodge") + xlim(0,2) + opts(title="Touch activity", plot.title=theme_text(size=20, face="bold")) + labs(x="touches down per second", y="proportion of session")
p.hist + facet_grid(s ~ name, labeller=label_both)

ggsave(file="figures/touch-down-histograms-individual.pdf")

# new feature df

p <- ggplot(feature.df, aes(x=factor(name), y=touches.moved.per.sec))
p + geom_boxplot(aes(fill=g)) + facet_grid(.~s, labeller=label_both, drop=TRUE)

p <- ggplot(feature.df, aes(x=factor(g), y=touches.down.per.sec))
p <- p + geom_boxplot(aes(fill=name)) + coord_flip()
## p <- p + facet_grid(s~., labeller=label_both)
p

p <- ggplot(feature.df, aes(x=touches.moved.per.sec, y=accel.motion))
p <- p + geom_point(aes(colour=factor(g)), size = 2.5)
## p <- p + facet_grid(s~., labeller=label_both)
p

p <- ggplot(feature.df, aes(x=sd.theta))
p <- p + geom_density(alpha=0.3, aes(fill=name))
p <- p + facet_grid(g~s, labeller=label_both)
p

p <- ggplot(feature.df, aes(x=mean.x, y=mean.y))
p <- p + geom_point(aes(colour=factor(j)))
p <- p + facet_grid(g~s, labeller=label_both)
p

qplot(factor(s), accel.motion, data=feature.df, geom="boxplot", fill=name) + coord_flip() + facet_wrap(~g)

# distribution of all touch position features

## + opts(axis.text.x=theme_text(angle=90, hjust=1))

ggplot(melt(feature.df,
            id.vars=feature.subset("id", num=TRUE),
            measure.vars=feature.subset("touch.pos.cart", num=TRUE)),
       aes(x=variable, y=value)) +
  geom_boxplot(aes(fill=name))

ggplot(melt(feature.df,
            id.vars=feature.subset("id", num=TRUE),
            measure.vars=feature.subset("touch.pos.cart", num=TRUE)),
       aes(x=variable, y=value)) +
  geom_jitter(alpha=.04) +
  facet_grid(g~., labeller=label_both)  + coord_flip()

ggplot(melt(feature.df,
            id.vars=feature.subset("id", num=TRUE),
            measure.vars=feature.subset("touch.pos.cart", num=TRUE)),
       aes(x=variable, y=value)) +
  geom_jitter(alpha=.04) + coord_flip()

ggplot(melt(feature.df,
            id.vars=feature.subset("id", num=TRUE),
            measure.vars=feature.subset("touch.pos.pol", num=TRUE)),
       aes(x=variable, y=value)) +
  geom_boxplot(aes(fill=name))

ggplot(melt(feature.df,
            id.vars=feature.subset("id", num=TRUE),
            measure.vars=feature.subset("touch.pos.pol", num=TRUE)),
       aes(x=variable, y=value)) +
  geom_jitter(alpha=.04) + coord_flip()

ggplot(melt(feature.df,
            id.vars=feature.subset("id", num=TRUE),
            measure.vars=feature.subset("touch.pos.pol", num=TRUE)),
       aes(x=variable, y=value)) +
  geom_jitter(alpha=.04) +
  facet_grid(g~., labeller=label_both)  + coord_flip()

# distribution of all touch activity features

ggplot(melt(feature.df,
            id.vars=feature.subset("id", num=TRUE),
            measure.vars=feature.subset("touch.activity", num=TRUE)),
       aes(x=variable, y=value)) +
  geom_boxplot(aes(fill=name))

ggplot(melt(feature.df,
            id.vars=feature.subset("id", num=TRUE),
            measure.vars=feature.subset("touch.activity", num=TRUE)),
       aes(x=variable, y=value)) +
  geom_jitter(alpha=.04) +
  facet_grid(g~., labeller=label_both)  + coord_flip()

ggplot(melt(feature.df,
            id.vars=feature.subset("id", num=TRUE),
            measure.vars="touch.distance"),
       aes(value, fill=factor(g))) + xlim(0,.3) +
  geom_bar(binwidth = .01, position = "dodge")# +
  ## facet_grid(g~., labeller=label_both)  + coord_flip()

# distribution of all accel features

ggplot(melt(feature.df,
            id.vars=feature.subset("id", num=TRUE),
            measure.vars=feature.subset("accel", num=TRUE)),
       aes(x=variable, y=value)) +
  geom_boxplot(aes(fill=name))

ggplot(melt(feature.df,
            id.vars=feature.subset("id", num=TRUE),
            measure.vars=feature.subset("accel", num=TRUE)),
       aes(x=variable, y=value)) +
  geom_boxplot(aes(fill=factor(s))) + facet_grid(g~., labeller=label_both) +
  coord_flip()

ggplot(melt(feature.df,
            id.vars=feature.subset("id", num=TRUE),
            measure.vars=feature.subset("accel", num=TRUE)),
       aes(x=variable, y=value)) +
  geom_jitter(alpha=.06) +
  facet_grid(s~g, labeller=label_both)

# audio features

ggplot(melt(feature.df, id.vars=1:7, measure.vars="sharpness"), aes(x=variable, y=value)) + geom_boxplot(aes(fill=factor(j))) + facet_grid(s~g, labeller=label_both)

ggplot(melt(feature.df, id.vars=1:7, measure.vars="loudness"), aes(x=variable, y=value)) + geom_jitter(alpha=.1) + facet_grid(.~s, labeller=label_both)

## smoothed time profiles

ggplot(feature.df, aes(x=time, y=loudness, colour = factor(j))) + stat_smooth(se = FALSE) + facet_grid(g~s, labeller=label_both)

# distribution of all aspec features

ggplot(melt(feature.df, id.vars=1:7, measure.vars=49:58), aes(x=variable, y=value)) + geom_boxplot(aes(fill=name))

ggplot(melt(feature.df,
            id.vars=feature.subset("id", num=TRUE),
            measure.vars=feature.subset("audio", num=TRUE)),
       aes(x=variable, y=value)) + scale_y_log10() + 
  geom_jitter(alpha=.04, aes(colour=factor(g))) +
  facet_grid(.~g, labeller=label_both) +
  opts(axis.text.x=theme_text(angle=90, hjust=1))

## smoothed time profiles for audio features

p <- ggplot(feature.df, aes(x=time, colour = factor(j))) + scale_colour_discrete(name = "Jam") + facet_grid(g~s, labeller=facet.labeller)

p + stat_smooth(se = FALSE, aes(y=loudness)) + geom_point(alpha = 0.1, aes(y=loudness))
p + stat_smooth(se = FALSE, aes(y=sharpness)) + geom_point(alpha = 0.1, aes(y=sharpness))

ggplot(melt(feature.df, id.vars = 1:7, measure.vars = get.feature.cols("OBSIR", num = TRUE)), aes(x=time, y=value, colour = factor(variable))) + stat_smooth() + facet_grid(g~s, labeller=facet.labeller)

ggplot(feature.df, aes(x=time, y=specVariation, colour = factor(j))) + stat_smooth(se = FALSE) + facet_grid(g~s, labeller=facet.labeller)

## engagement likerts

ggplot(likert.df, aes(x = g, y = engagement, fill = type)) + geom_boxplot() + facet_grid(.~s)
