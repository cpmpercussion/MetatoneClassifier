##
## NIME 2015 Paper Metatone Classifier Evaluations
## 
library("ggplot2")
library("reshape2")
library("ez")
library("gridExtra")
library("grid")
#install.packages("gridExtra")
#Colours
chifig.3colours <- c("#e41a1c", "#377eb8", "#4daf4a")
chifig.2colours <- c("#984ea3", "#ff7f00")
#
# Computational Cost Calculations for NIME2015 Paper
#
performers <- c(0,1,2,3,4)
time <- c(0.00333281,0.0519283,0.0866098,0.126357,0.157818)
lm.computation <- lm(time ~ performers)
summary(lm.computation)
# Plots
time.ms <- c(3.33281,51.9283,86.6098,126.357,157.818)
timeprofile <- data.frame(performers,time.ms)
timeprofile
# Plots
ggplot(timeprofile,aes(performers,time.ms)) + geom_point(shape=1) + geom_smooth(method=lm) +xlab("Number of Performers") + ylab("Mean Time for One Analysis (ms)") + scale_fill_manual(values=chifig.3colours)  +scale_colour_manual(values=chifig.2colours)
ggsave("computational-cost.pdf",dpi=300,width=6,height=3)
#
# Cross-val accuracy comparison
#
classifierEvaluation <- read.csv("RFC-100tests.csv")
categories <- c("Studio 5s Window","Studio 1s Window","Formal Procedure")
simpleCategories <-  c("Studio.5s","Studio.1s","Formal.Proc")
names(classifierEvaluation) <- categories
longClassifierEvaluation <- melt(classifierEvaluation,measure.vars = 1:3,variable.name="Collection.Method",value.name = "Accuracy")
summary(aov(Accuracy ~ Collection.Method,data=longClassifierEvaluation))
# Plots
ggplot(longClassifierEvaluation,aes(Collection.Method,Accuracy,fill=Collection.Method)) + geom_boxplot() + scale_fill_manual(values=chifig.3colours) + xlab("Gesture Data Collection Method") + ylab("Cross-Validation Accuracy") + theme(plot.margin=unit(rep(0,4), "cm"), legend.position = "none", legend.box = "horizontal")
ggsave("cross-val-accuracy.pdf",dpi=300,width=6,height=3)
# Done!
