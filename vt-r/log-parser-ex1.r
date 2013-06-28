# read and initialise data

library('ggplot2')
library('plyr')
library('reshape2')

source("vt-header.r")

initial.names <- c("time", "name", "type", "subtype", "arg1", "arg2")

fri <- read.csv("/Users/ben/Projects/Viscotheque/data/ex1/log/2010-02-26 20-23-40 +1100.log", col.names = initial.names)
fri <- data.frame(g = factor(1), fri)
sat.early <- read.csv("/Users/ben/Projects/Viscotheque/data/ex1/log/2010-02-27 18-12-55 +1100.log", col.names = initial.names)
sat.early <- data.frame(g = factor(2), sat.early)
sat.late <- read.csv("/Users/ben/Projects/Viscotheque/data/ex1/log/2010-02-27 19-30-23 +1100.log", col.names = initial.names)
sat.late <- data.frame(g = factor(3), sat.late)
ex2.df <- rbind(fri,sat.early,sat.late)

## order and anonymise names

ex2.df$name <- factor(ex2.df$name,
                      levels = c(
                        "Asmono",
                        "holbo",
                        "renee",
                        "Ben Latts",
                        "Phil",
                        "Stewart",
                        "Camilo",
                        "Lawrence",
                        "richard"),
                      labels = c(
                        "Sean",
                        "Andy",
                        "Zoe",
                        "Joe",
                        "Dan",
                        "Will",
                        "Ryan",
                        "Ted",
                        "Alan"),
                      ordered = TRUE)

ex2.df <- ex2.df[order(ex2.df$time),]
ex2.df$event <- rep(NA, dim(ex2.df)[1])
ex2.df$event <- ifelse(ex2.df$subtype == "touch" & is.na(ex2.df$arg2) & ex2.df$arg1 == 1, "touch-down", ex2.df$event)
ex2.df$event <- ifelse(ex2.df$subtype == "touch" & is.na(ex2.df$arg2) & ex2.df$arg1 == 0, "touch-up", ex2.df$event)
ex2.df$event <- ifelse(ex2.df$subtype == "touch" & !is.na(ex2.df$arg2), "touch-position", ex2.df$event)
ex2.df$event <- ifelse(ex2.df$subtype == "push", "push-interface", ex2.df$event)
ex2.df$event <- ifelse(ex2.df$subtype == "pull", "pull-interface", ex2.df$event)
ex2.df$event <- ifelse(ex2.df$type == "mode", "mode-change", ex2.df$event)
ex2.df$event <- factor(ex2.df$event)
ex2.df <- ex2.df[!is.na(ex2.df$event),]
ex2.df$mode <- ifelse(ex2.df$type == "mode", as.numeric(as.character(ex2.df$subtype)), NA)

fill.modes <- function(x) {
  if( is.na(x[1])) x[1] <- 1
  for ( i in 2:(length(x)) ) {
    if( is.na(x[i])) x[i] <- x[i-1]
  }
  x
}

ex2.df$mode <- unsplit(tapply(ex2.df$mode,ex2.df$name,fill.modes),ex2.df$name)
ex2.df$mode <- factor(ex2.df$mode)
ex2.df$x <- ifelse(ex2.df$subtype == "touch" & !is.na(ex2.df$arg2), as.numeric(as.character(ex2.df$arg1)), NA)
ex2.df$y <- ifelse(ex2.df$subtype == "touch" & !is.na(ex2.df$arg2), ex2.df$arg2, NA)

ex2.df <- ddply(ex2.df,
                 .(g),
                 function(group.df){
                   group.df <- group.df[order(group.df$time),]
                   group.df$time <- group.df$time - c( 288869574.0269820094, 288948157.3798440099, 288952790.3861380219)[as.numeric(group.df$g[1])]
                   group.df$delta.t <- c(diff(group.df$time), 0)
                   group.df$phase <- factor(ifelse(group.df$time < 0, "train", "jam"))
                   group.df
                 })

ex2.df <- ddply(ex2.df,
                 .(name),
                 function(name.df){
                   name.df$time <- ifelse(name.df$phase=="train",
                                          name.df$time - min(name.df$time),
                                          name.df$time)
                   name.df
                 })

ex2.df <- ex2.df[c("name", "g", "phase", "time", "delta.t", "event", "mode", "x", "y")]

video.offset <- list(7*60+50,5*60+18,4*60+53) # times on each tape when the performance started

## make flat touch df

ex2.touch.df <- ex2.df[ex2.df$event == "touch-position",
                       c("name", "g", "phase", "time", "delta.t", "mode", "x", "y")]

## plotting

dummy.df <- ex2.df[!duplicated(ex2.df$mode),]
dummy.df$time <- -10000

## training

thesis.fig.device("~/Documents/School/PhD/ben-thesis/figures/ex2/touch-jitter-training.png", "fullwidth", type = "png")
print(ggplot(subset(ex2.df, phase=="train"),
             aes(x = time, y = "value")) +
      geom_jitter(aes(colour = mode), alpha = 0.1) +
      geom_jitter(data = dummy.df,
                  aes(x = time,
                      y = "value",
                      colour = mode),
                  alpha = 1,
                  size = 3) + # dummy df for legend purposes
      scale_colour_brewer(palette = "Set1",
                          breaks = 1:5,
                          labels = c(
                            "loop start/length",
                            "pan/volume",
                            "loop offset/period",
                            "envelope/pitch",
                            "cutoff/resonance")) +
      scale_x_continuous(limits = c(0, 181),
                         breaks = seq(0, 180, 60),
                         labels = 0:3) +
      opts(axis.text.y=theme_blank()) +
      labs(x = "time (min)",
           y = "musician",
           colour = "x/y mapping") +
      facet_grid(name + g ~ ., labeller = facet.labeller, drop = TRUE))
dev.off()

## jam

thesis.fig.device("~/Documents/School/PhD/ben-thesis/figures/ex2/touch-jitter-jam.png", "fullwidth", type = "png")
print(ggplot(subset(ex2.df, phase=="jam"),
             aes(x = time, y = "value")) +
      geom_jitter(aes(colour = mode), alpha = 0.02) +
      geom_jitter(data = dummy.df,
                  aes(x = time,
                      y = "value",
                      colour = mode),
                  alpha = 1,
                  size = 3) + # dummy df for legend purposes
      scale_colour_brewer(palette = "Set1",
                          breaks = 1:5,
                          labels = c(
                            "loop start/length",
                            "pan/volume",
                            "loop offset/period",
                            "envelope/pitch",
                            "cutoff/resonance")) +
      scale_x_continuous(limits = c(0, 960),
                         breaks = seq(0, 960, 60),
                         labels = 0:16) +
      opts(axis.text.y=theme_blank()) +
      labs(x = "time (min)",
           y = "musician",
           colour = "x/y mapping") +
      facet_grid(name + g ~ ., labeller = facet.labeller, drop = TRUE))
dev.off()

# mode breakdown

thesis.fig.device("~/Documents/School/PhD/ben-thesis/figures/ex2/mode-breakdown.pdf", "halfwidth")
print(ggplot(ddply(ex2.df,
                   .(mode),
                   summarize,
                   total.time = sum(delta.t)),
             aes(x = mode, y = total.time)) +
      geom_bar(aes(fill = mode,
                   stat="identity")) +
      scale_fill_brewer(palette = "Set1",
                          breaks = 1:5,
                          labels = c(
                            "loop start/loop length",
                            "pan/volume",
                            "loop offset/loop period",
                            "envelope/pitch",
                            "cutoff/resonance")) +
      scale_y_continuous(limits = c(0, 1080),
                         breaks = seq(0, 1080, 300),
                         labels = seq(0, 15, 5)) +
      opts(legend.position= "top") +
      guides(fill = guide_legend(ncol = 1)) +
      labs(x = "",
           y = "time spent in mode (min)",
           fill = "x/y mapping"))
dev.off()

thesis.fig.device("~/Documents/School/PhD/ben-thesis/figures/ex2/mode-breakdown-by-name.pdf", "halfwidth")
print(ggplot(ddply(ex2.df,
                   .(g, name, mode),
                   summarize,
                   total.time = sum(delta.t)),
             aes(x = name, y = total.time)) +
      geom_bar(aes(fill = mode,
                   stat="identity",
                   colour = g),
               size = 0.6) +
      scale_fill_brewer(palette = "Set1",
                          breaks = 1:5,
                          labels = c(
                            "loop start/length",
                            "pan/volume",
                            "loop offset/period",
                            "envelope/pitch",
                            "cutoff/resonance"),
                        guide = "none") +
      scale_colour_manual(values= c("black", "white", "black"),
                         guide = "none") +
      scale_y_continuous(limits = c(0, 660),
                         breaks = seq(0, 660, 60),
                         labels = 0:11) +      
      opts(axis.text.x = theme_text(angle=90, colour = "grey50", hjust=1)) +
      labs(x = "musician",
           y = "time spent in mode (min)",
           fill = "x/y mapping"))
dev.off()

## touch scatterplots

thesis.fig.device("~/Documents/School/PhD/ben-thesis/figures/ex2/touch-scatter-name.png", "fullwidth", type = "png")
print(ggplot(ex2.touch.df, aes(x, y)) +
      geom_point(aes(colour = factor(mode)),
                 size = 1.4,
                 alpha = 0.2,
                 guide = "none") +
      guides(colour = guide_legend(override.aes = list(alpha = 1, size = 4))) +
      labs(colour = "mode") +
      scale_colour_brewer(palette = "Set1",
                          breaks = 1:5,
                          labels = c(
                            "loop start/loop length",
                            "pan/volume",
                            "loop offset/loop period",
                            "envelope/pitch",
                            "cutoff/resonance")) +
      xlim(0,1) + ylim(0,1) + opts(aspect.ratio=3/2) +
      labs(colour = "x/y mapping") +
      opts(axis.text.x=theme_blank(), axis.text.y=theme_blank(), axis.title.x=theme_blank(), axis.title.y=theme_blank(), axis.ticks=theme_blank()) +
      opts(legend.position = c(0.75, 0.25)) +
      facet_wrap(~ name, ncol = 6))
dev.off()

thesis.fig.device("~/Documents/School/PhD/ben-thesis/figures/ex2/touch-scatter-group.png", "fullwidth", type = "png")
print(ggplot(ex2.touch.df, aes(x, y)) +
      geom_point(aes(colour = factor(mode)),
                 size = 1.7,
                 alpha = 0.2,
                 guide = "none") +
      labs(colour = "mode") +
      scale_colour_brewer(palette = "Set1",
                          breaks = 1:5,
                          labels = c(
                            "loop start/length",
                            "pan/volume",
                            "loop offset/period",
                            "envelope/pitch",
                            "cutoff/resonance"),
                          guide = "none") +
      xlim(0,1) + ylim(0,1) + opts(aspect.ratio=3/2) +
      labs(colour = "x/y mapping") +
      opts(axis.text.x=theme_blank(), axis.text.y=theme_blank(), axis.title.x=theme_blank(), axis.title.y=theme_blank(), axis.ticks=theme_blank()) +  
      facet_grid(. ~ g, labeller=facet.labeller))
dev.off()

## touch time-traces

ex2.touch.df <- ex2.df[ex2.df$event == "touch-position",
                       c("name", "g", "phase", "time", "delta.t", "mode", "x", "y")]

ex2.touch.df <- ddply(ex2.touch.df,
                           .(g, name, phase, mode),
                           function(a){
                             b <- melt(a, measure.vars = 7:8)
                             b$param <- factor(as.numeric(a$mode) * 2 - as.numeric(b$variable == "x"))
                             b
                           })

thesis.fig.device("~/Documents/School/PhD/ben-thesis/figures/ex2/touch-trace-training.png", "fullpage", type = "png")
print(ggplot(subset(ex2.touch.df, phase=="train"),
             aes(x = time, y = value)) +
      geom_point(aes(colour = param),
                  alpha = 0.1,
                  size = 1.3) +
      geom_point(data = dummy.df,
                  aes(x = time,
                      y = value,
                      colour = mode),
                  alpha = 1,
                  size = 3) + # dummy df for legend purposes
      scale_colour_manual(values = scale_colour_brewer(type = "qual", palette = 3)$palette(10)[c(5,6,1:4,9,10,7,8)],
                        breaks = 1:10,
                        labels = c(
                          "start",
                          "length",
                          "pan",
                          "volume",
                          "offset",
                          "period",
                          "envelope",
                          "pitch",
                          "cutoff",
                          "resonance")) +
      ylim(0, 1) +
      scale_x_continuous(limits = c(0, 181),
                         breaks = seq(0, 180, 60),
                         labels = 0:3) +
      scale_y_continuous(limits = c(-0.1, 1.1),
                         breaks = seq(0, 1, .5)) +
      opts(legend.position= "top") +
      labs(x = "time (min)",
           y = "musician",
           colour = "parameter") +
      facet_grid(name + g ~ ., labeller = facet.labeller, drop = TRUE))
dev.off()

thesis.fig.device("~/Documents/School/PhD/ben-thesis/figures/ex2/touch-trace-jam.png", "fullpage", type = "png")
print(ggplot(subset(ex2.touch.df, phase=="jam"),
             aes(x = time, y = value)) +
      geom_point(aes(colour = param),
                  alpha = 0.05,
                  size = 1.3) +
      geom_point(data = dummy.df,
                  aes(x = time,
                      y = value,
                      colour = mode),
                  alpha = 1,
                  size = 3) + # dummy df for legend purposes
      scale_colour_manual(values = scale_colour_brewer(type = "qual", palette = 3)$palette(10)[c(5,6,1:4,9,10,7,8)],
                        breaks = 1:10,
                        labels = c(
                          "start",
                          "length",
                          "pan",
                          "volume",
                          "offset",
                          "period",
                          "envelope",
                          "pitch",
                          "cutoff",
                          "resonance")) +
      ylim(0, 1) +
      scale_x_continuous(limits = c(0, 960),
                         breaks = seq(0, 900, 300),
                         labels = seq(0, 15, 5)) +
      scale_y_continuous(limits = c(-0.1, 1.1),
                         breaks = seq(0, 1, .5)) +
      opts(legend.position= "top") +
      labs(x = "time (min)",
           y = "musician",
           colour = "parameter") +
      facet_grid(name + g ~ ., labeller = facet.labeller, drop = TRUE))
dev.off()

thesis.fig.device("~/Documents/School/PhD/ben-thesis/figures/ex2/parameter-sd-by-group.pdf", "halfwidth")
print(ggplot(ddply(ex2.touch.df,
                   .(g, name, param),
                   summarize,
                   sd.value = sd(value)),
             aes(x = param, y = sd.value)) +
      geom_bar(aes(fill = param),
               stat="identity",
               position="dodge") +
      scale_fill_brewer(type = "qual",
                          palette = 3,
                        guide = "none") +
      scale_x_discrete(breaks = 1:10,
                        labels = c(
                          "loop start",
                          "loop length",
                          "pan",
                          "volume",
                          "loop offset",
                          "loop period",
                          "envelope",
                          "pitch",
                          "cutoff",
                          "resonance")) +
      labs(x = "",
           y = "standard deviation in parameter value",
           fill = "parameter") +
      opts(axis.text.x = theme_text(angle=90, colour = "grey50", hjust=1)) +
      facet_grid(g ~ ., labeller = facet.labeller))
dev.off()

thesis.fig.device("~/Documents/School/PhD/ben-thesis/figures/ex2/parameter-time-by-group.pdf", "halfwidth")
print(ggplot(ddply(ex2.touch.df,
                   .(g, name, param),
                   summarize,
                   total.time = sum(delta.t)),
             aes(x = param, y = total.time)) +
      geom_bar(aes(fill = param),
               stat="identity",
               position="dodge") +
      scale_fill_brewer(type = "qual",
                          palette = 3,
                        guide = "none") +
      scale_x_discrete(breaks = 1:10,
                        labels = c(
                          "loop start",
                          "loop length",
                          "pan",
                          "volume",
                          "loop offset",
                          "loop period",
                          "envelope",
                          "pitch",
                          "cutoff",
                          "resonance")) +
      labs(x = "parameter",
           y = "time spent manipulating parameter (sec)",
           fill = "parameter") +
      opts(axis.text.x = theme_text(angle=90, colour = "grey50", hjust=1)) +
      facet_grid(g ~ ., labeller = facet.labeller))
dev.off()

## mode switching

mode.time.df <- ddply(subset(ex2.df, phase == "jam" & event == "mode-change" & time < 720),
                           .(g, name),
                           function(name.df){
                             name.df$mode.time <- c(diff(name.df$time), 0)
                             name.df[c("name", "g", "time", "mode", "mode.time")]
                           })

## toLatex(head(mode.time.dist.df[order(mode.time.dist.df$mode.time, decreasing = TRUE),], 10))

thesis.fig.device("~/Documents/School/PhD/ben-thesis/figures/ex2/mode-time-dist-mode.pdf", "halfwidth")
print(ggplot(mode.time.df,
             aes(x = mode, y = mode.time)) +
      geom_violin(aes(fill = factor(mode)),
                  width = .9) +
      geom_boxplot(aes(fill = factor(mode)),
                   fill = "grey50",
                   colour = "white",
                   alpha = 0.5,
                   outlier.size = 0,
                   width = 0.5) +
      scale_fill_brewer(palette = "Set1", guide = "none") +
      labs(x = "mode", y = "mode time distribution (sec)") +
      ylim(0,100))
dev.off()

thesis.fig.device("~/Documents/School/PhD/ben-thesis/figures/ex2/mode-time-dist-name.pdf", "halfwidth")
print(ggplot(mode.time.df,
             aes(x = name, y = mode.time)) +
      geom_violin(aes(fill = factor(g)),
                  width = 1.1) +
      geom_boxplot(aes(fill = factor(g)),
                   fill = "grey50",
                   colour = "white",
                   alpha = 0.5,
                   outlier.size = 0,
                   width = 0.5) +
      scale_fill_brewer(palette = "Set1") +
      labs(x = "musician", y = "mode time distribution (sec)", fill = "group") +
      ylim(0,100) +
      opts(axis.text.x = theme_text(angle=90, colour = "grey50", hjust=1)) +
      opts(legend.position = "top"))
dev.off()

thesis.fig.device("~/Documents/School/PhD/ben-thesis/figures/ex2/density-all.pdf", "fullwidth")
print(ggplot(subset(ex2.df, phase=="jam"),
             aes(x = time)) +
      geom_density(aes(fill = mode),
                   kernel = "rectangular",
                   adjust = .3) +
      scale_fill_brewer(palette = "Set1", guide = "none") +
      scale_x_continuous(#limits = c(0, 960),
                         breaks = seq(0, 900, 300),
                         labels = seq(0, 15, 5)) +
      scale_y_continuous(limits = c(0, 0.0058),
                         breaks = seq(0, 0.005, 0.0025)) +
      labs(x = "time (min)",
           y = "activity density",
           fill = "musician") +
      facet_grid(mode ~ g,
                 labeller = function(variable, value){
                   switch(variable,
                          g = paste("Group ", value, sep = ""),
                          mode = c(
                            "x = loop start\ny = loop length",
                            "x = pan\ny = volume",
                            "x = loop offset\ny = loop period",
                            "x = envelope\ny = pitch",
                            "x = cutoff\ny = resonance")[value])
                   }))
dev.off()

## co-ordinate correlation

ex2.reg <- ddply(subset(ex2.touch.df, phase=="jam")[1:100,],
                 .(name),
                 function(name.df){
                   tout <- seq(0, max(ex2.touch.df$time), by = 0.1)
                   data.frame(name = name.df$name[1],
                              g = name.df$g[1],
                              time = tout,
                              x = approx(x = ex2.touch.df$time,
                                y = ex2.touch.df$x,
                                xout = tout,
                                method = "constant",
                                rule = 2)$y,
                              y = approx(x = ex2.touch.df$time,
                                y = ex2.touch.df$y,
                                xout = tout,
                                method = "constant",
                                rule = 2)$y)
                 })

corr.mat.x <- cor(dcast(ex2.reg, time ~ name, value.var = "x")[,-1])
corr.mat.y <- cor(dcast(ex2.reg, time ~ name, value.var = "y")[,-1])

# param value violin plots

ex2.touch.df$param <- factor(ex2.touch.df$param,
                             levels = 1:10,
                             labels = c(
                               "loop start",
                               "loop length",
                               "pan",
                               "volume",
                               "loop offset",
                               "loop period",
                               "envelope",
                               "pitch",
                               "cutoff",
                               "resonance"))

ex2.touch.df$param <- factor(ex2.touch.df$param,
                             levels = c(1,6,2,7,3,8,4,9,5,10),
                             labels = c(
                               "loop start",
                               "pan",
                               "loop offset",
                               "envelope",
                               "cutoff",
                               "loop length",
                               "volume",
                               "loop period",
                               "pitch",
                               "resonance"
                               ))

thesis.fig.device("~/Documents/School/PhD/ben-thesis/figures/ex2/param-value.pdf", "fullwidth")
print(ggplot(ex2.touch.df,
             aes(x = "param", y = value)) +
      ylim(0, 1) +
      geom_violin(aes(fill = param),
                  width = .9) +
      geom_boxplot(aes(fill = param),
                   fill = "grey50",
                   colour = "white",
                   alpha = 0.5,
                   outlier.size = 0,
                   width = 0.5) +
      scale_fill_manual(values = scale_colour_brewer(type = "qual", palette = 3)$palette(10)[c(5,1,3,9,7,6,2,4,10,8)],
                        breaks = 1:10,
                        labels = c(
                          "start",
                          "length",
                          "pan",
                          "volume",
                          "offset",
                          "period",
                          "envelope",
                          "pitch",
                          "cutoff",
                          "resonance")) +
      labs(x = "",
           y = "parameter value",
           fill = "group") +
      facet_wrap(~ param, nrow = 2))
dev.off()

thesis.fig.device("~/Documents/School/PhD/ben-thesis/figures/ex2/param-value-group.pdf", "fullwidth")
print(ggplot(ex2.touch.df,
             aes(x = g, y = value)) +
      ylim(0, 1) +
      geom_violin(aes(fill = param),
                  width = .9) +
      geom_boxplot(aes(fill = g),
                   fill = "grey50",
                   colour = "white",
                   alpha = 0.5,
                   outlier.size = 0,
                   width = 0.5) +
      scale_fill_manual(values = scale_colour_brewer(type = "qual", palette = 3)$palette(10)[c(5,1,3,9,7,6,2,4,10,8)],
                        breaks = 1:10,
                        labels = c(
                          "start",
                          "length",
                          "pan",
                          "volume",
                          "offset",
                          "period",
                          "envelope",
                          "pitch",
                          "cutoff",
                          "resonance")) +
      scale_colour_brewer(palette = "Set1") +
      labs(x = "group",
           y = "parameter value",
           fill = "group") +
      facet_wrap(~ param, nrow = 2))
dev.off()

thesis.fig.device("~/Documents/School/PhD/ben-thesis/figures/ex2/param-value-name.pdf", "fullpage")
print(ggplot(ex2.touch.df[rep(1:dim(ex2.touch.df)[1],
                              ceiling(1000*ex2.touch.df$delta.t)),],
             aes(x = name, y = value)) +
      ylim(0, 1) +
      geom_violin(aes(fill = g),
                  width = 1.3) +
      geom_boxplot(aes(fill = g),
                   fill = "grey50",
                   colour = "white",
                   alpha = 0.5,
                   outlier.size = 0,
                   width = 0.5) +
      scale_fill_brewer(palette = "Set1") +
      labs(x = "musician",
           y = "parameter value",
           fill = "group") +
      opts(axis.text.x = theme_text(angle=90, colour = "grey50", hjust=1)) +
      opts(legend.position = "top") +
      facet_wrap(~ param, ncol = 2))
dev.off()
