############################
## graphs for publication ##
############################

library('ggplot2')
library('grid')
library('plyr')
library('reshape2')

source("vt-header.r")

# anonymise

feature.df$name <- get.anon.name(feature.df$name)
touch.df$name <- get.anon.name(touch.df$name)

## accel RMS plots

d_ply(feature.df,
      .(g),
      function(g.df){
        thesis.fig.device(paste("figures/accel/group-",
                                g.df$g[1], "-accel.pdf",
                                sep = ""),
                          "fullwidth")
        print(ggplot(g.df, aes(x = time, y = accel.rms)) +
              ## geom_line(aes(colour = name), size = .7, alpha = .7) +
              geom_area(aes(fill = name)) +
              scale_fill_brewer(palette = "Set1") +
              facet_grid(s ~ j, labeller = facet.labeller) +
              ## opts(axis.text.y=theme_blank()) +
              labs(x = "time (s)", y = "device agitation (RMS)", colour = "Musician") +
              opts(title = paste("Device agitation, group", g.df$g[1])))
        dev.off()
      })

## accel feature distributions

melted.accel.features <- melt(feature.df,
                              id.vars = feature.subset("id", num = TRUE),
                              measure.vars = feature.subset("accel", num = TRUE))

l_ply(feature.type.list$accel,
      function(accel.feat){
        message("feature: ", accel.feat)
        ## by name
        thesis.fig.device(paste("figures/accel/",
                   clean.var.name(accel.feat),
                   "-name.pdf", sep = ""),
                          "fullwidth")
            print(ggplot(subset(melted.accel.features, variable == accel.feat),
                         aes(x = variable, y = value)) +
                  geom_violin(aes(fill = factor(g))) +
                  geom_boxplot(aes(fill = factor(g)),
                               fill = "grey50",
                               colour = "white",
                               alpha = 0.5,
                               outlier.size = 0,
                               width = 0.5) +
                  scale_fill_brewer(palette = "Set1") +
                  opts(axis.text.x=theme_blank()) +
                  labs(x = "musician", y = pretty.name[[accel.feat]], fill = "group") +
                  facet_grid(. ~ name, labeller = facet.labeller))
        dev.off()
        thesis.fig.device(paste("figures/accel/",
                                clean.var.name(accel.feat),
                                "-name-by-session.pdf", sep = ""),
                          "fullsquare")
        print(ggplot(subset(melted.accel.features, variable == accel.feat),
                     aes(x = factor(s), y = value)) +
              geom_violin(aes(fill = factor(g))) +
              geom_boxplot(aes(fill = factor(g)),
                               fill = "grey50",
                               colour = "white",
                           alpha = 0.5,
                           outlier.size = 0,
                           width = 0.25) +
              scale_fill_brewer(palette = "Set1") +
              labs(x = "session", y = pretty.name[[accel.feat]], fill = "group") +
              facet_wrap(~ name, nrow = 2))
        dev.off()
        ## by group
        thesis.fig.device(paste("figures/accel/",
                                clean.var.name(accel.feat),
                                "-group.pdf", sep = ""),
                          "halfwidth")
            print(ggplot(subset(melted.accel.features, variable == accel.feat),
                         aes(x = variable, y = value)) +
                  geom_violin(aes(fill = factor(g))) +
                  geom_boxplot(aes(fill = factor(g)),
                               fill = "grey50",
                               colour = "white",
                               alpha = 0.5,
                               outlier.size = 0,
                               width = 0.5) +
                  scale_fill_brewer(palette = "Set1") +
                  opts(axis.text.x=theme_blank()) +
                  labs(x = "musician", y = pretty.name[[accel.feat]], fill = "group") +
                  facet_grid(. ~ g, labeller = facet.labeller))
        dev.off()
        thesis.fig.device(paste("figures/accel/",
                   clean.var.name(accel.feat),
                   "-group-by-session.pdf", sep = ""),
                          "fullwidth")
        print(ggplot(subset(melted.accel.features, variable == accel.feat),
                     aes(x = factor(s), y = value)) +
              geom_violin(aes(fill = factor(g))) +
              geom_boxplot(aes(fill = factor(g)),
                               fill = "grey50",
                               colour = "white",
                           alpha = 0.5,
                           outlier.size = 0,
                           width = 0.25) +
              scale_fill_brewer(palette = "Set1") +
              labs(x = "session", y = pretty.name[[accel.feat]], fill = "group") +
              facet_grid(. ~ g, labeller = facet.labeller))
        dev.off()
      })

## actually used in thesis

thesis.fig.device("~/Documents/School/PhD/ben-thesis/figures/ex3/accel-mean-x-name-by-session.pdf", "fullpage")
print(ggplot(feature.df,
             aes(x = factor(s), y = accel.mean.x)) +
      geom_violin(aes(fill = factor(g))) +
      geom_boxplot(aes(fill = factor(g)),
                   fill = "grey50",
                   colour = "white",
                   alpha = 0.5,
                   outlier.size = 0,
                   width = 0.25) +
      ylim(-1, 1) +
      scale_fill_brewer(palette = "Set1") +
      labs(x = "session", y = "mean accelerometer x position", fill = "group") +
      opts(legend.position = "top") +
      facet_wrap(~ name, nrow = 4))
dev.off()

## total session agitation by musician
thesis.fig.device("~/Documents/School/PhD/ben-thesis/figures/ex3/total-motion-energy.pdf",
                  "tallhalfwidth")
print(ggplot(ddply(feature.df,
                   .(g, s, name),
                   summarize,
                   total.agitation = sum(accel.rms)),
             aes(x = name, y = total.agitation)) +
      geom_bar(aes(fill = factor(g)), stat = "identity") +
      ## ylim(0, 200) +
      scale_fill_brewer(palette = "Set1") +
      labs(x = "musician", y = "total device motion energy (RMS)", fill = "group") +
      opts(axis.text.x = theme_text(angle=90, colour = "grey50", hjust=1)) +
      opts(legend.position = "top") +
      facet_grid(s ~ ., labeller = facet.labeller))      
dev.off()

thesis.fig.device("~/Documents/School/PhD/ben-thesis/figures/ex3/rms-motion-energy.pdf",
                  "keynote")
print(ggplot(ddply(feature.df,
                   .(g, name, s),
                   summarize,
                   total.agitation = sum(accel.rms)),
             aes(x = factor(s), y = total.agitation)) +
      geom_bar(aes(fill = factor(g)), stat = "identity") +
      scale_fill_brewer(palette = "Set1") +
      labs(x = "musician", y = "total device motion energy (RMS)", fill = "group") +
      ## opts(axis.text.x = theme_text(angle=90, colour = "grey50", hjust=1)) +
      opts(legend.position = "top") +
      facet_grid(. ~ name, labeller = facet.labeller))      
dev.off()

## accel arrowheads

accel.arrow.df <- ddply(subset(feature.df, accel.mean.z > -1.15),
                        .(g, s, name),
                        summarize,
                        x = 0,
                        xend = mean(accel.mean.x, na.rm = TRUE),
                        y = 0,
                        yend = mean(accel.mean.y, na.rm = TRUE),
                        z = mean(accel.mean.z, na.rm = TRUE),
                        motion.rms = mean(accel.rms, na.rm = TRUE))

thesis.fig.device("~/Documents/School/PhD/ben-thesis/figures/ex3/accel-arrowheads.pdf", "fullpage")
print(ggplot(accel.arrow.df) +
      geom_point(x = 0, y = 0,
                 aes(colour = z, size = 2 * motion.rms)) +
      geom_segment(aes(x = x, y = y,
                       xend = xend, yend = yend,
                       colour = z,
                       size = motion.rms),
                   arrow=arrow(length=unit(0.3,"cm"))) +
      scale_x_continuous(limits = c(-0.1, 0.6), breaks = (0:1)/2) +
      scale_y_continuous(limits = c(-0.8, 0.1), breaks = (0:1)/-2) +
      scale_size_continuous(breaks = (0:4)/4) +
      scale_colour_gradient(low="#984EA3", high="#FF7F00") +
      labs(x = "mean accel x value",
           y = "mean accel y value",
           colour = "mean accel z value",
           size = "average RMS motion energy") +
      opts(legend.position = "top") + 
      ## opts(axis.text.x = theme_text(angle=90, colour = "grey50", hjust=1)) +
      facet_grid(name + g ~ s, labeller = facet.labeller))
dev.off()

thesis.fig.device("~/Documents/School/PhD/ben-thesis/figures/ex3/accel-arrowheads-landscape.pdf", "fullwidth")
print(ggplot(accel.arrow.df) +
      geom_point(x = 0, y = 0,
                 aes(colour = z, size = 2 * motion.rms)) +
      geom_segment(aes(x = x, y = y,
                       xend = xend, yend = yend,
                       colour = z,
                       size = motion.rms),
                   arrow=arrow(length=unit(0.3,"cm"))) +
      scale_x_continuous(limits = c(-0.1, 0.6), breaks = (0:1)/2) +
      scale_y_continuous(limits = c(-0.8, 0.1), breaks = (0:1)/-2) +
      scale_size_continuous(breaks = (0:4)/4) +
      scale_colour_gradient(low="#984EA3", high="#FF7F00") +
      labs(x = "mean accel x value",
           y = "mean accel y value",
           colour = "mean accel z value",
           size = "average RMS motion energy") +
      opts(legend.position = "top") + 
      ## opts(axis.text.x = theme_text(angle=90, colour = "grey50", hjust=1)) +
      facet_grid(s ~ g + name, labeller = facet.labeller))
dev.off()

## screen scatterplots

make.touch.scatterplot <- function(touch.df, type, alpha, title, faceting, fig.width){
  dummy.df <- touch.df[1:3,]
  dummy.df$touch.count <- 1:3
  dummy.df$x <- -1
  thesis.fig.device(paste("~/Documents/School/PhD/ben-thesis/figures/ex3/",
                          type, "/",
                          title,
                          ifelse(length(unique(touch.df$touch.count)) == 1,
                                 touch.df$touch.count[1],
                                 ""),
                          ".png", sep = ""),
                    fig.width,
                    type = "png")
  if(type == "heatmap"){
    p <- ggplot(subset(touch.df,
                       touch.df$touch.count != 4 &
                       touch.df$x > 0 & touch.df$x < 1 &
                       touch.df$y > 0 & touch.df$y < 1),
                aes(x = x, y = y)) +
                  geom_bin2d(binwidth=c(1.5,1)/50) +
                    scale_fill_gradient(low="#000080", high="#CD6600", guide = "none", trans = "sqrt")
  }else if(type == "scatter"){
    p <- ggplot(rbind(dummy.df,
                      touch.df[touch.df$touch.count!=4,]),
                aes(x, y)) +
                  geom_point(aes(colour = factor(touch.count)),
                             size = 1,
                             alpha = alpha) +    
                               scale_colour_brewer(palette = "Set1",
                                                   guide = "none")
    if(1 %in% touch.df$touch.count){
      p <- p + guides(colour = guide_legend(override.aes = list(alpha = 1, size = 4))) +
        opts(legend.position = "top") +
          opts(legend.position = "top") +
            labs(colour = "touch count")
      }
  }
  print(p + xlim(0,1) + ylim(0,1) + opts(aspect.ratio=3/2) +
        opts(axis.text.x=theme_blank(),
             axis.text.y=theme_blank(),
             axis.title.x=theme_blank(),
             axis.title.y=theme_blank(),
             axis.ticks=theme_blank(),
             panel.background=theme_blank()) +
        faceting)
  dev.off()
}

make.touch.scatterplot(flat.touch.df,
                       "scatter",
		       0.01,
                       "group",
                       facet_grid(s ~ g, labeller=facet.labeller),
                       "halfwidth")

make.touch.scatterplot(flat.touch.df,
                       "scatter",
		       0.018,
                       "name",
                       facet_grid(s ~ g + name, labeller=facet.labeller),
                       "fullwidth")

make.touch.scatterplot(flat.touch.df,
                       "scatter",
		       0.01,
                       "group-touchcount",
                       facet_grid(touch.count ~ g, labeller=facet.labeller),
                       "halfwidth")

make.touch.scatterplot(flat.touch.df,
                       "scatter",
		       0.012,
                       "name-touchcount",
                       facet_grid(touch.count ~ g + name, labeller=facet.labeller),
                       "fullwidth")

## split by touch count

d_ply(flat.touch.df,
      .(touch.count),
      function(tc.df){
        make.touch.scatterplot(tc.df,
                               "scatter",
                               0.03,
                               "name",
                               facet_grid(s ~ g + name, labeller=facet.labeller),
                               "fullwidth")
      })

d_ply(flat.touch.df,
      .(touch.count),
      function(tc.df){
        make.touch.scatterplot(tc.df,
                               "scatter",
                               0.005,
                               "group",
                               facet_grid(s ~ g, labeller=facet.labeller),
                               "halfwidth")
      })

## screen heatmaps

make.touch.scatterplot(flat.touch.df,
                       "heatmap",
		       0.01,
                       "group",
                       facet_grid(s ~ g, labeller=facet.labeller),
                       "halfwidth")

make.touch.scatterplot(flat.touch.df,
                       "heatmap",
                       0.018,
                       "name",
                       facet_grid(s ~ g + name, labeller=facet.labeller),
                       "fullwidth")

make.touch.scatterplot(flat.touch.df,
                       "heatmap",
		       0.01,
                       "group-touchcount",
                       facet_grid(touch.count ~ g, labeller=facet.labeller),
                       "halfwidth")

make.touch.scatterplot(flat.touch.df,
                       "heatmap",
		       0.012,
                       "name-touchcount",
                       facet_grid(touch.count ~ g + name, labeller=facet.labeller),
                       "fullwidth")

## split by touch count

d_ply(flat.touch.df,
      .(touch.count),
      function(tc.df){
        make.touch.scatterplot(tc.df,
                               "heatmap",
                               0.03,
                               "name",
                               facet_grid(s ~ g + name, labeller=facet.labeller),
                               "fullwidth")
      })

d_ply(flat.touch.df,
      .(touch.count),
      function(tc.df){
        make.touch.scatterplot(tc.df,
                               "heatmap",
                               0.005,
                               "group",
                               facet_grid(s ~ g, labeller=facet.labeller),
                               "halfwidth")
      })



make.touch.heatmap <- function(touch.df, plot.title){
  thesis.fig.device(paste("~/Documents/School/PhD/ben-thesis/figures/ex3/heatmap/",
                          clean.var.name(plot.title), sep = "",
                          ".png"),
                    "fullwidth",
                    type = "png")
  print(ggplot(subset(touch.df,
                      touch.df$x > 0 & touch.df$x < 1 &
                      touch.df$y > 0 & touch.df$y < 1),
                      aes(x = x, y = y)) +
        geom_bin2d(binwidth=c(1.5,1)/50) +
        scale_fill_gradient(low="#000080", high="#CD6600") + #, trans = "log10") +
        xlim(0,1) + ylim(0,1) + opts(aspect.ratio=3/2) +
        opts(axis.text.x=theme_blank(), axis.text.y=theme_blank(), axis.title.x=theme_blank(), axis.title.y=theme_blank(), axis.ticks=theme_blank()) +
        facet_grid(. ~ name, labeller=facet.labeller))
  dev.off()
}

make.touch.heatmap(head(flat.touch.df, 100000), "touch heatmap")

d_ply(melt(feature.df,
           id.vars = c("g", "s", "j", "time", "s.time"),
           measure.vars = feature.type.list$audio,
           variable.name = "audio.feature"),
      .(audio.feature),
      function(audio.feature.df){
        thesis.fig.device(paste("figures/audio/",
                  clean.var.name(audio.feature.df$audio.feature[1]),
                  ".pdf", sep = ""),
                          "fullwidth")
        print(ggplot(audio.feature.df,
                     aes(x=s.time, y=value, colour = factor(j))) +
              ## scale_colour_brewer(palette = "Set2") +
              labs(x = "time (s)",
                   y = audio.feature.df$audio.feature[1],
                   colour = "Jam") +
              opts(title = paste("Audio feature time profile:",
                     audio.feature.df$audio.feature[1])) +
              ## stat_smooth(se = TRUE, size = 1) +
              geom_point(alpha = 0.5) +
              facet_grid(g~s, labeller = facet.labeller))
        dev.off()
      })

## specific audio features (the most important ones)

norm.audio.df <- cbind(feature.df[feature.subset("id")],
                       llply(feature.df[c("loudness", "specVariation")],
                             function(x){
                               (x - min(x))/(max(x) - min(x))
                             }))

## loudness visualisation

thesis.fig.device("~/Documents/School/PhD/ben-thesis/figures/ex3/mean-loudness.pdf", "halfwidth")
print(ggplot(ddply(norm.audio.df,
                   .(g, s),
                   summarize,
                   mean.loudness = mean(loudness)),
             aes(x = factor(s), y = mean.loudness)) +
      geom_path(size = 1, alpha = 0.7, aes(colour = factor(g), group = g)) +
      geom_point(size = 3, alpha = 0.7, aes(colour = factor(g))) +
      scale_colour_brewer(palette = "Set1") +
      scale_y_continuous(limits=c(0, .5)) +
      labs(x = "session",
           y = " mean loudness (normalised)",
           colour = "group"))
dev.off()

thesis.fig.device("~/Documents/School/PhD/ben-thesis/figures/ex3/loudness-time-profile.png",
                  "fullpage",
                  type = "png")
print(ggplot(norm.audio.df,
             aes(x = s.time,
                 y = loudness,
                 colour = factor(j))) +
      scale_colour_brewer(palette = "Set1") +
      scale_y_continuous(breaks = c(0, 0.5, 1)) +
      labs(x = "time (seconds)",
           y = "loudness (normalised)",
           colour = "jam") +
      stat_smooth(se = TRUE, size = 1.3, method = "loess") +
      geom_point(alpha = 0.1) +
      opts(axis.text.x = theme_text(angle=90, colour = "grey50", hjust=1)) +
      facet_grid(g ~ s, labeller = facet.labeller))
dev.off()

thesis.fig.device("figures/audio/loudness-sd.pdf",
                  "halfwidth")
print(ggplot(ddply(norm.audio.df,
                   .(s),
                   summarize,
                   loudness.sd = sd(loudness)),
                   aes(x = s,
                       y = loudness.sd)) +
      geom_path(size = 2.5, alpha = 0.7) +
      geom_point(size = 5) +
      ylim(0, .2) +
      scale_x_continuous(breaks = 1:4) +
      labs(x = "session",
           y = "loudness (normalised) standard deviation",
           colour = "jam"))
dev.off()

thesis.fig.device("figures/audio/loudness-sd.pdf",
                  "halfwidth")
print(ggplot(ddply(norm.audio.df,
                   .(g, s),
                   summarize,
                   loudness.sd = sd(loudness)),
                   aes(x = s,
                       y = loudness.sd)) +
      geom_path(size = 1, alpha = 0.7, aes(colour = factor(g))) +
      geom_point(size = 3, alpha = 0.7, aes(colour = factor(g))) +
      stat_summary(fun.y = mean,
                   geom="line",
                   size = 1) +
      ylim(0, .2) +
      scale_x_continuous(breaks = 1:4) +
      labs(x = "session",
           y = "loudness (normalised) standard deviation",
           colour = "group") +
      scale_colour_brewer(palette = "Set1"))
dev.off()

thesis.fig.device("figures/audio/spectral-variation-time-profile.png",
                  "fullwidth", type = "png")
print(ggplot(norm.audio.df,
             aes(x = s.time,
                 y = specVariation,
                 colour = factor(j))) +
      scale_colour_brewer(palette = "Set1") +
      labs(x = "time (seconds)",
           y = "spectral variation (normalised)",
           colour = "jam") +
      stat_smooth(se = TRUE, size = 1.3, method = "loess") +
      geom_point(alpha = 0.15) +
      opts(axis.text.x = theme_text(angle=90, colour = "grey50", hjust=1)))
dev.off()

## audio feature violin plots

thesis.fig.device("~/Documents/School/PhD/ben-thesis/figures/ex3/loudness-violin.pdf",
                  "halfwidth")
print(ggplot(norm.audio.df,
             aes(x = factor(g), y = loudness)) +
      geom_violin(aes(fill = factor(g)), width = 1) +
      geom_boxplot(aes(fill = factor(g)),
                   fill = "grey50",
                   colour = "white",
                   alpha = 0.5,
                   outlier.size = 0,
                   width = 0.5) +
      scale_fill_brewer(palette = "Set1", guide = "none") +
      opts(legend.position = "top") +
      labs(x = "group", y = "loudness (normalised)", fill = "group"))
dev.off()

thesis.fig.device("~/Documents/School/PhD/ben-thesis/figures/ex3/loudness-violin-session.pdf",
                  "fullwidth")
print(ggplot(subset(melt(norm.audio.df,
                         id.vars = feature.subset("id", num = TRUE)),
                    variable == "loudness"),
             aes(x = factor(s), y = value)) +
      geom_violin(aes(fill = factor(g)), width = 1) +
      geom_boxplot(aes(fill = factor(g)),
                   fill = "grey50",
                   colour = "white",
                   alpha = 0.5,
                   outlier.size = 0,
                   width = 0.5) +
      scale_fill_brewer(palette = "Set1", guide = "none") +
      labs(x = "session", y = "loudness (normalised)", fill = "group") +
      facet_grid(. ~ g, labeller = facet.labeller))
dev.off()

thesis.fig.device("figures/audio/spectral-variation-violin.pdf",
                  "halfwidth")
print(ggplot(subset(melt(norm.audio.df,
                         id.vars = feature.subset("id", num = TRUE)),
                    variable == "specVariation"),
             aes(x = variable, y = value)) +
      geom_violin(aes(fill = factor(g))) +
      geom_boxplot(aes(fill = factor(g)),
                   fill = "grey50",
                   colour = "white",
                   alpha = 0.5,
                   outlier.size = 0,
                   width = 0.5) +
      scale_fill_brewer(palette = "Set1") +
      opts(axis.text.x=theme_blank()) +
      labs(x = "musician", y = "loudness (normalised)", fill = "group") +
      facet_grid(. ~ g, labeller = facet.labeller))
dev.off()

thesis.fig.device("figures/audio/spectral-variation-violin-by-session.pdf",
                  "fullwidth")
print(ggplot(subset(melt(norm.audio.df,
                         id.vars = feature.subset("id", num = TRUE)),
                    variable == "specVariation"),
             aes(x = factor(s), y = value)) +
      geom_violin(aes(fill = factor(g))) +
      geom_boxplot(aes(fill = factor(g)),
                   fill = "grey50",
                   colour = "white",
                   alpha = 0.5,
                   outlier.size = 0,
                   width = 0.5) +
      scale_fill_brewer(palette = "Set1") +
      labs(x = "session", y = "loudness (normalised)", fill = "group") +
      facet_grid(. ~ g, labeller = facet.labeller))
dev.off()

## RQA stats

# to consider all the rqa stats, l_ply over names(rqa.df)[match("eps.value", names(rqa.df)):dim(rqa.df)[2]]

generate.rqa.violin.plots <- function(rqa.df, base.path){
  d_ply(rqa.df,
        .(metric, delta.t, feature.subset, type),
        function(rqa.stat.df){
          a_ply(unique(rqa.df[1:2]),
                1,
                function(x){
                  fpath <- paste(base.path, "/",
                                 x[[2]], "s/",
                                 x[[1]], sep = "")
                  if(!file.exists(fpath)) dir.create(fpath, recursive = TRUE)
                })
          l_ply(c("laminarity", "determinism", "avg.diag.length", "trap.time"),
                function(rqa.stat){
                  qualified.path <- paste(base.path,
                                          rqa.stat.df$delta.t[1], "s/",
                                          rqa.stat.df$metric[1], "/",
                                          clean.var.name(rqa.stat), "-",
                                          rqa.stat.df$feature.subset[1], "-",
                                          rqa.stat.df$type[1], sep = "")
                  ## by name
                  thesis.fig.device(paste(qualified.path,
                                          "-name.pdf",
                                          sep = ""),
                                    "fullwidth")
                  print(ggplot(melt(rqa.stat.df,
                                    measure.vars = rqa.stat),
                               aes(x = variable, y = value)) +
                        geom_violin(aes(fill = factor(g))) +
                        geom_point(colour = "white", alpha = 0.3) +
                        scale_fill_brewer(palette = "Set1", guide = "none") +
                        geom_boxplot(aes(fill = factor(g)),
                                     fill = "grey50",
                                     colour = "white",
                                     alpha = 0.5,
                                     outlier.size = 0,
                                     width = 0.5) +
                        labs(x = "musician",
                             y = pretty.name[[rqa.stat]],
                             fill = "group") +
                        opts(axis.text.x=theme_blank()) +
                        facet_grid(. ~ name, labeller = facet.labeller))
                  dev.off()
                  thesis.fig.device(paste(qualified.path,
                                          "-name-session.pdf",
                                          sep = ""),
                                    "fullwidth")
                  print(ggplot(melt(rqa.stat.df,
                                    measure.vars = rqa.stat),
                               aes(x = factor(s), y = value)) +
                        geom_violin(aes(fill = factor(g))) +
                        geom_point(colour = "white", alpha = 0.3) +
                        scale_fill_brewer(palette = "Set1", guide = "none") +
                        geom_boxplot(aes(fill = factor(g)),
                                     fill = "grey50",
                                     colour = "white",
                                     alpha = 0.5,
                                     outlier.size = 0,
                                     width = 0.5) +
                        labs(x = "session",
                             y = pretty.name[[rqa.stat]],
                             fill = "group") +
                        facet_grid(. ~ name, labeller = facet.labeller))
                  dev.off()
                  ## by group
                  thesis.fig.device(paste(qualified.path,
                                          "-group.pdf",
                                          sep = ""),
                                    "halfwidth")
                  print(ggplot(melt(rqa.stat.df,
                                    measure.vars = rqa.stat),
                               aes(x = variable, y = value)) +
                        geom_violin(aes(fill = factor(g))) +
                        geom_point(colour = "white", alpha = 0.3) +
                        scale_fill_brewer(palette = "Set1", guide = "none") +
                        geom_boxplot(aes(fill = factor(g)),
                                     fill = "grey50",
                                     colour = "white",
                                     alpha = 0.5,
                                     outlier.size = 0,
                                     width = 0.5) +
                        opts(axis.text.x=theme_blank()) +
                        labs(x = "group",
                             y = pretty.name[[rqa.stat]],
                             fill = "group") +
                        facet_grid(. ~ g, labeller = facet.labeller))
                  dev.off()
                  thesis.fig.device(paste(qualified.path,
                                          "-group-session.pdf",
                                          sep = ""),
                                    "fullwidth")
                  print(ggplot(melt(rqa.stat.df,
                                    measure.vars = rqa.stat),
                               aes(x = factor(s), y = value)) +
                        geom_violin(aes(fill = factor(g))) +
                        geom_point(colour = "white", alpha = 0.3) +
                        scale_fill_brewer(palette = "Set1", guide = "none") +
                        geom_boxplot(aes(fill = factor(g)),
                                     fill = "grey50",
                                     colour = "white",
                                     alpha = 0.5,
                                     outlier.size = 0,
                                     width = 0.5) +
                        labs(x = "session",
                             y = pretty.name[[rqa.stat]],
                             fill = "group") +
                        facet_grid(. ~ g, labeller = facet.labeller))
                  dev.off()
                  ## by session
                  thesis.fig.device(paste(qualified.path,
                                          "-session.pdf",
                                          sep = ""),
                                    "halfwidth")
                  print(ggplot(melt(rqa.stat.df,
                                    measure.vars = rqa.stat),
                               aes(x = variable, y = value)) +
                        geom_violin(aes(fill = factor(s))) +
                        geom_point(colour = "white", alpha = 0.3) +
                        scale_fill_brewer(palette = "Set2", guide = "none") +
                        geom_boxplot(aes(fill = factor(s)),
                                     fill = "grey50",
                                     colour = "white",
                                     alpha = 0.5,
                                     outlier.size = 0,
                                     width = 0.5) +
                        opts(axis.text.x=theme_blank()) +
                        labs(x = "session",
                             y = pretty.name[[rqa.stat]],
                             fill = "session") +
                        facet_grid(. ~ s, labeller = facet.labeller))
                  dev.off()
                })
        },
        .progress = "text")
}

generate.rqa.violin.plots(rqa.df, "figures/rqa-stats/real/")
generate.rqa.violin.plots(synth.rqa.df, "figures/rqa-stats/synth/")

# top quartile rqa stat plots

high.lam.df <- ddply(rqa.df,
                     .(metric, delta.t, feature.subset, type, feature.subset, type),
                     function(x.df){
                       ddply(x.df,
                             .(s),
                             function(y.df){
                               data.frame(high.lams = sum(y.df$laminarity > quantile(x.df$laminarity, 0.95)))
                             })
                     })

thesis.fig.device("figures/rqa-stats/high-lam-sessions.pdf",
                  "fullwidth")
ggplot(high.lam.df,
       aes(x = factor(s), y = high.lams)) +
  geom_point(aes(colour = factor(s))) +
  facet_grid(delta.t + metric  ~ feature.subset + type)
dev.off()

# friedman post hoc

friedman.df <- make.friedman.df(session.rqa.df, "g", 0.05)
friedman.df <- make.friedman.df(session.rqa.df, "s", 0.05)

d_ply(friedman.df,
      .(metric, delta.t, rqa.stat),
      function(post.hoc.df){
        gs.col1 <- mean(match(c("g1", "s1"), names(post.hoc.df)), na.rm = TRUE)
        thesis.fig.device(paste("figures/rqa-stats/signif/",
                                post.hoc.df$delta.t[1], "s/",
                                post.hoc.df$metric[1], "/",
                                clean.var.name(post.hoc.df$rqa.stat[1]),
                                ifelse(length(grep("s", names(post.hoc.df)[gs.col1])) == 0, "-group", "-session"),
                                ".pdf", sep = ""),
                          "bigsquare")
        corners.df <- data.frame(x = c(0, 1, 1, 0),
                                 y = c(1, 1, 0, 0))
        ## add the start and endpoints for the line segments
        post.hoc.df$signif <- post.hoc.df$p.value < 0.05
        post.hoc.df[c("x", "y")] <- corners.df[post.hoc.df[[gs.col1]],]
        post.hoc.df[c("xend", "yend")] <- corners.df[post.hoc.df[[gs.col1 + 1]],]
        corners.df$label <- sapply(1:4, function(x) paste(substring(names(post.hoc.df)[gs.col1], 0, 1), x, sep = ""))
        print(ggplot(post.hoc.df) +
              geom_segment(size = 1.2,
                           aes(x = x, y = y, xend = xend, yend = yend, colour = as.numeric(signif))) +
              geom_point(aes(x = x, y = y), size = 8, colour = "black", data = corners.df) +
              geom_text(aes(x = x,
                            y = y,
                            label = label),
                        size = 3,
                        colour = "white",
                        data = corners.df) +
              scale_colour_gradient(low = "black", high = "red", guide = "none") +
              xlim(-0.2, 1.2) + ylim(-0.2, 1.2) + 
              opts(aspect.ratio = 1,
                   axis.title.x = theme_blank(),
                   axis.title.y = theme_blank(),
                   axis.text.x=theme_blank(),
                   axis.text.y=theme_blank()) +
              facet_grid(type ~ feature.subset,
                         drop = FALSE,
                         labeller = facet.labeller))
        dev.off()
      },
      .progress = "text")

# classification error

make.error.df <- function(class.error.df){
  error.cols <- grep("error", names(class.error.df))
  time.cols <- grep("time", names(class.error.df))
  id.cols <- (1:dim(class.error.df)[2])[-c(error.cols, time.cols)]
  error.df <- data.frame(melt(class.error.df,
                              id.vars = id.cols,
                              measure.vars = error.cols,
                              variable.name = "classifier",
                              value.name = "error.rate"),
                         melt(class.error.df,
                              id.vars = id.cols,
                              measure.vars = time.cols,
                              value.name = "cpu.time")["cpu.time"])
  error.df$classifier <- sapply(error.df$classifier, function(x) strsplit(as.character(x), ".", fixed = TRUE)[[1]][1])
  error.df$times.chance <- (1 - error.df$error.rate) * ifelse(error.df$class.target == "name", 12, 4)
  error.df$is.test <- error.df$test.idx != 0
  ddply(error.df,
        .(real.or.synth, class.target, feature.subset, test.by, is.test, classifier),
        summarize,
        mean.error.rate = mean(error.rate),
        mean.times.chance = mean(times.chance),
        sd.error.rate = sd(error.rate),
        sd.times.chance = sd(times.chance),
        mean.cpu.time = mean(cpu.time),
        sd.cpu.time = sd(cpu.time))
}

error.df <- make.error.df(class.error.df)
error.df$feature.subset[error.df$class.target == "name" &
                        error.df$feature.subset == "noaudio"] <- "all"
error.df$classifier <- factor(error.df$classifier, levels = c("naiveBayes", "svm", "rf"))
levels(error.df$classifier) <- c("NB", "SVM", "RF")
error.df <- error.df[error.df$is.test,]

## real data, feat subset == "all" only

dodge <- position_dodge(width=0.9)

thesis.fig.device("~/Documents/School/PhD/ben-thesis/figures/ex3/error-rate.pdf",
                  "three2page")
print(ggplot(subset(error.df, real.or.synth == "real" & feature.subset == "all"),
             aes(x = test.by,
                 y = mean.error.rate,
                 fill = classifier)) +
      geom_bar(stat = "identity",
               position = dodge) +
      geom_errorbar(aes(ymin = mean.error.rate - sd.error.rate,
                        ymax = mean.error.rate + sd.error.rate),
                    colour = "black",
                    position = dodge,
                    width = 0.5) +
      labs(x = "cross-validation partition",
           y = "expected prediction error") +
      scale_fill_brewer(palette = "Set1") +
      scale_x_discrete(breaks = c("s", "j"),
                       labels = c("session", "jam")) +
      facet_grid(. ~ class.target,
                 labeller = function(variable, value) {
                   switch(variable,
                          real.or.synth = ifelse(value == "real", "real data", "synthetic test data"),
                          class.target = ifelse(value == "group", "target variable: group", "target variable: musician"),
                          test.by = ifelse(value == "s", "test partition: session", "test partition: jam"))
                 }))
dev.off()

thesis.fig.device("~/Documents/School/PhD/ben-thesis/figures/ex3/error-times-chance.pdf",
		  "three2page")
print(ggplot(subset(error.df, real.or.synth == "real" & feature.subset == "all"),
	     aes(x = test.by,
		 y = mean.times.chance,
		 fill = classifier)) +
      geom_bar(stat = "identity",
	       position = dodge) +
      geom_errorbar(aes(ymin = mean.times.chance - sd.times.chance,
			ymax = mean.times.chance + sd.times.chance),
		    colour = "black",
		    position = dodge,
		    width = 0.5) +
      labs(x = "cross-validation partition",
	   y = "classification accuracy (vs chance)") +
      scale_fill_brewer(palette = "Set1") +
      scale_x_discrete(breaks = c("s", "j"),
		       labels = c("session", "jam")) +
      geom_hline(y = 1) +
      facet_grid(. ~ class.target,
		 labeller = function(variable, value) {
		   switch(variable,
			  real.or.synth = ifelse(value == "real", "real data", "synthetic test data"),
			  class.target = ifelse(value == "group", "target variable: group", "target variable: musician"),
			  test.by = ifelse(value == "s", "test partition: session", "test partition: jam"))
		 }))
dev.off()

thesis.fig.device("~/Documents/School/PhD/ben-thesis/figures/ex3/error-times-chance-name-keynote.pdf", "keynote")
print(ggplot(subset(error.df,
                    real.or.synth == "real" &
                    feature.subset == "all" &
                    class.target == "name"),
             aes(x = test.by,
                 y = mean.times.chance,
                 fill = classifier)) +
      geom_bar(stat = "identity",
               position = dodge) +
      geom_errorbar(aes(ymin = mean.times.chance - sd.times.chance,
                        ymax = mean.times.chance + sd.times.chance),
                    colour = "black",
                    position = dodge,
                    width = 0.5) +
      labs(x = "cross-validation partition",
           y = "classification accuracy (vs chance)") +
      scale_fill_brewer(palette = "Set1") +
      scale_x_discrete(breaks = c("s", "j"),
                       labels = c("session", "jam")))
dev.off()

thesis.fig.device("~/Documents/School/PhD/ben-thesis/figures/ex3/classifier-cpu-time.pdf",
                  "three2page")
print(ggplot(subset(error.df, real.or.synth == "real" & feature.subset == "all"),
             aes(x = test.by,
                 y = mean.cpu.time,
                 fill = classifier)) +
      geom_bar(stat = "identity",
               position = dodge) +
      geom_errorbar(aes(ymin = mean.cpu.time - sd.cpu.time,
                        ymax = mean.cpu.time + sd.cpu.time),
                    colour = "black",
                    position = dodge,
                    width = 0.5) +
      labs(x = "cross-validation partition",
           y = "classification CPU time (seconds)") +
      scale_fill_brewer(palette = "Set1") +
      scale_x_discrete(breaks = c("s", "j"),
                       labels = c("session", "jam")) +
      facet_grid(. ~ class.target,
                 labeller = function(variable, value) {
                   switch(variable,
                          real.or.synth = ifelse(value == "real", "real data", "synthetic test data"),
                          class.target = ifelse(value == "group", "target variable: group", "target variable: musician"),
                          test.by = ifelse(value == "s", "test partition: session", "test partition: jam"))
                 }))
dev.off()

thesis.fig.device("~/Documents/School/PhD/ben-thesis/figures/ex3/synth-error-times-chance.pdf",
                  "fullwidth")
print(ggplot(subset(error.df, real.or.synth == "synth" & feature.subset == "all"),
             aes(x = test.by,
                 y = mean.times.chance,
                 fill = classifier)) +
      geom_bar(stat = "identity",
               position = dodge) +
      geom_errorbar(aes(ymin = mean.times.chance - sd.times.chance,
                        ymax = mean.times.chance + sd.times.chance),
                    colour = "black",
                    position = dodge,
                    width = 0.5) +
      labs(x = "cross-validation partition",
           y = "classification accuracy (vs chance)") +
      scale_fill_brewer(palette = "Set1") +
      scale_x_discrete(breaks = c("s", "j"),
                       labels = c("session", "jam")) +
      geom_hline(y = 1) +
      facet_grid(. ~ class.target,
                 labeller = function(variable, value) {
                   switch(variable,
                          real.or.synth = ifelse(value == "real", "real data", "synthetic test data"),
                          class.target = ifelse(value == "group", "target variable: group", "target variable: musician"),
                          test.by = ifelse(value == "s", "test partition: session", "test partition: jam"))
                 }))
dev.off()

## real data, all feature subsets

dodge <- position_dodge(width=0.9)

class.error.df$feature.subset <- factor(class.error.df$feature.subset,
                                        levels = c(
                                          "mode",
                                          "touch.activity",
                                          "touch.zone",
                                          "touch.position",
                                          "audio",
                                          "noaccel",
                                          "accel",   
                                          "all"))

thesis.fig.device("~/Documents/School/PhD/ben-thesis/figures/ex3/error-times-chance-all-feats.pdf",
                  "fullsquare")
print(ggplot(subset(error.df, real.or.synth == "real"),
             aes(x = feature.subset,
                 y = mean.times.chance,
                 fill = classifier)) +
      geom_bar(stat = "identity",
               position = dodge) +
      geom_errorbar(aes(ymin = mean.times.chance - sd.times.chance,
                        ymax = mean.times.chance + sd.times.chance),
                    colour = "black",
                    position = dodge,
                    width = 0.5) +
      labs(x = "feature subset used for classification",
           y = "classification accuracy (vs chance)") +
      scale_x_discrete(breaks = c(
                         "mode",
                         "touch.activity",
                         "touch.zone",
                         "touch.position",
                         "noaccel",
                         "audio",
                         "accel",   
                         "all"),
                       labels = c(
                         "mode",
                         "touch activity",
                         "touch zone",
                         "touch position",
                         "no accel",
                         "audio",
                         "accel",   
                         "all")) +
      opts(axis.text.x = theme_text(angle=90, colour = "grey50", hjust=1)) +
      scale_fill_brewer(palette = "Set1",
                        breaks = c("naiveBayes", "rf", "svm"),
                        labels = c("NB", "RF", "SVM")) +
      geom_hline(y = 1) +
      facet_grid(test.by ~ class.target,
                 scales = "free_y",
                 labeller = function(variable, value) {
                   switch(variable,
                          real.or.synth = ifelse(value == "real", "real data", "synthetic test data"),
                          class.target = ifelse(value == "group", "target variable: group", "target variable: musician"),
                          test.by = ifelse(value == "s", "test partition: session", "test partition: jam"))
                 }))
dev.off()

rm(dodge)

## rf confusion matrix and barplot

## on group

conf.df <- make.conf.df(rf.on.group$confusion)

thesis.fig.device("~/Documents/School/PhD/ben-thesis/figures/ex3/group-confusion-matrix-log.pdf",
                  "halfwidth")
print(ggplot(conf.df,
             aes(x = Var1, y = Var2)) +
      geom_tile(aes(fill = value), guide = "none") +
      scale_fill_gradient(low="black", high="white", trans = "log10") +
      opts(aspect.ratio = 1) +
      opts(legend.position = "top") +
      labs(y = "actual group", x = "predicted group"))
dev.off()

thesis.fig.device("~/Documents/School/PhD/ben-thesis/figures/ex3/group-confusion-barplot.pdf",
                  "halfwidth")
print(ggplot(ddply(conf.df,
                   .(Var1, error.type),
                   summarize,
                   misclass = sum(value)),
             aes(x = Var1, y = misclass)) +
      geom_bar(aes(fill = error.type), stat = "identity", position = "fill") +
      scale_fill_manual(values = c("#4DAF4A", "#E41A1C")) +
      opts(legend.position = "top") +
      labs(x = "group", y = "classification result", fill = ""))
dev.off()

conf.df <- make.conf.df(llply(rfs.on.group, function(x) x$confusion))

## on name

conf.df <- make.conf.df(rf.on.name$confusion)
conf.df$Var1 <- get.anon.name(conf.df$Var1)
conf.df$Var2 <- get.anon.name(conf.df$Var2)
conf.df$error.type <- factor(conf.df$error.type, levels = c("correct", "same.group", "diff.group"), ordered = TRUE)

thesis.fig.device("~/Documents/School/PhD/ben-thesis/figures/ex3/name-confusion-matrix-log.pdf",
                  "halfwidth")
print(ggplot(conf.df,
             aes(x = Var1, y = Var2)) +
      geom_tile(aes(fill = value), guide = "none") +
      scale_fill_gradient(low="black", high="white", trans = "log10") +
      opts(aspect.ratio = 1,
           axis.text.x = theme_text(angle=90, colour = "grey50", hjust=1)) +
      opts(legend.position = "top") +
      labs(y = "actual musician", x = "predicted musician"))
dev.off()

thesis.fig.device("~/Documents/School/PhD/ben-thesis/figures/ex3/name-confusion-barplot.pdf",
                  "halfwidth")
print(ggplot(ddply(conf.df,
                   .(Var1, error.type),
                   summarize,
                   misclass = sum(value)),
             aes(x = Var1, y = misclass)) +
      geom_bar(aes(fill = error.type), stat = "identity", position = "fill") +
      scale_fill_manual(breaks = c("correct", "same.group", "diff.group"),
                        labels = c("correct", "same group", "different group"),
                        values = c("#4DAF4A", "#377EB8", "#E41A1C")) +
      opts(axis.text.x = theme_text(angle=90, colour = "grey50", hjust=1)) +
      opts(legend.position = "top") +
      labs(x = "musician", y = "classification result", fill = ""))
dev.off()

## rf feature importance

imp.df <- make.imp.df(rf.on.group$importance)

thesis.fig.device("~/Documents/School/PhD/ben-thesis/figures/ex3/group-importance.pdf", "fullwidth")
print(ggplot(imp.df,
             aes(x = feature,
                 y = mean.decrease.accuracy)) +
      geom_bar(stat="identity", aes(fill = type)) +
      labs(x = "feature", y = "mean decrease in accuracy", fill = "feature type") +
      scale_fill_brewer(type = "qual",
                        palette = 2,
                        breaks = c(
                          "mode",          
                          "touch.activity",
                          "touch.position",
                          "touch.zone",
                          "accel",   
                          "audio"),
                        labels = c(
                          "mode",
                          "touch activity",
                          "touch position",
                          "touch zone",
                          "accelerometer",
                          "audio")) +
      opts(axis.text.x = theme_text(angle=90, colour = "grey50", hjust=1)))
dev.off()

thesis.fig.device("~/Documents/School/PhD/ben-thesis/figures/ex3/group-importance-by-type.pdf", "halfwidth")
print(ggplot(ddply(imp.df,
                   .(type),
                   summarize,
                   mean.decrease.accuracy = mean(mean.decrease.accuracy)),
             aes(x = type,
                 y = mean.decrease.accuracy)) +
      geom_bar(stat="identity", aes(fill = type)) +
      labs(x = "feature type", y = "mean decrease in accuracy") +
      scale_fill_brewer(type = "qual",
                        palette = 2,
                        breaks = c(
                          "mode",          
                          "touch.activity",
                          "touch.position",
                          "touch.zone",
                          "accel",   
                          "audio"),
                        labels = c(
                          "mode",
                          "touch activity",
                          "touch position",
                          "touch zone",
                          "accelerometer",
                          "audio"),
                        guide = "none") +
      opts(axis.text.x = theme_text(angle=90, colour = "grey50", hjust=1)))
dev.off()

## on name

imp.df <- make.imp.df(rf.on.name$importance)

thesis.fig.device("~/Documents/School/PhD/ben-thesis/figures/ex3/name-importance.pdf", "fullwidth")
print(ggplot(imp.df,
             aes(x = feature,
                 y = mean.decrease.accuracy)) +
      geom_bar(stat="identity", aes(fill = type)) +
      scale_fill_brewer(type = "qual",
                        palette = 2,
                        breaks = c("mode",          
                          "touch.activity",
                          "touch.position",
                          "touch.zone",
                          "accel",   
                          "audio"),
                        labels = c("mode",
                          "touch activity",
                          "touch position",
                          "touch zone",
                          "accelerometer",
                          "audio")) +
      labs(x = "feature", y = "mean decrease in accuracy", fill = "feature type") +
      opts(axis.text.x = theme_text(angle=90, colour = "grey50", hjust=1)))
dev.off()

thesis.fig.device("~/Documents/School/PhD/ben-thesis/figures/ex3/name-importance-by-type.pdf", "halfwidth")
print(ggplot(ddply(imp.df,
                   .(type),
                   summarize,
                   mean.decrease.accuracy = mean(mean.decrease.accuracy)),
             aes(x = type,
                 y = mean.decrease.accuracy)) +
      geom_bar(stat="identity", aes(fill = type)) +
      scale_fill_brewer(type = "qual",
                        palette = 2,
                        breaks = c("mode",          
                          "touch.activity",
                          "touch.position",
                          "touch.zone",
                          "accel",   
                          "audio"),
                        labels = c("mode",
                          "touch activity",
                          "touch position",
                          "touch zone",
                          "accelerometer",
                          "audio"),
                        guide = "none") +
      labs(x = "feature", y = "mean decrease in accuracy", fill = "feature type") +
      opts(axis.text.x = theme_text(angle=90, colour = "grey50", hjust=1)))
dev.off()

## engagement likerts

thesis.fig.device("figures/likert/engagement-likerts-self.pdf",
                  "fullwidth")
print(ggplot(subset(engagement.df, name == object),
             aes(x = name, y = engagement)) +
      geom_boxplot(aes(fill = factor(g))) +
      geom_point(colour = "white", alpha = 0.3) +
      scale_fill_brewer(palette = "Set1") +
      opts(axis.text.x = theme_text(angle=90, colour = "grey50", hjust=1)) +      
      labs(x = "musician",
           y = "how engaged did you feel?",
           fill = "group"))
dev.off()

thesis.fig.device("figures/likert/engagement-likerts-other.pdf",
                  "fullwidth")
print(ggplot(subset(engagement.df, name != object),
             aes(x = name, y = engagement)) +
      geom_boxplot(aes(fill = factor(g))) +
      geom_point(colour = "white", alpha = 0.3) +
      scale_fill_brewer(palette = "Set1") +
      opts(axis.text.x = theme_text(angle=90, colour = "grey50", hjust=1)) +      
      labs(x = "musician",
           y = "how engaged did you feel?",
           fill = "group"))
dev.off()

## misclassification by jam time

thesis.fig.device("figures/class-error/name-error-time-profile.pdf",
                  "fullwidth")
print(ggplot(feature.df[as.character(feature.df$name) == as.character(rf.on.name$predicted),],
             aes(x = time)) +
      ## scale_colour_brewer(palette = "Set1") +
      labs(x = "time (s)",
           y = "misclassification density",
           colour = "jam") +
      geom_density(aes(fill = name), alpha = 0.5) +
      facet_grid(g ~ ., labeller = facet.labeller))
dev.off()

thesis.fig.device("figures/class-error/group-error-time-profile.pdf",
                  "fullwidth")
print(ggplot(feature.df[as.character(feature.df$g) == as.character(rf.on.group$predicted),],
             aes(x = time)) +
      labs(x = "time (s)",
           y = "misclassification density") +
      geom_density(aes(fill = factor(g))) +
      scale_colour_brewer(palette = "Set1") +
      facet_grid(g ~ ., labeller = facet.labeller))
dev.off()

# mode breakdown

thesis.fig.device("~/Documents/School/PhD/ben-thesis/figures/ex3/mode-breakdown.pdf", "halfwidth")
print(ggplot(ddply(subset(touch.df, touch.count != 4),
                   .(touch.count),
                   summarize,
                   total.time = sum(delta.t)/60),
             aes(x = factor(touch.count), y = total.time)) +
      geom_bar(stat="identity", aes(fill = factor(touch.count))) +
      scale_fill_manual(breaks = 0:3,
                       labels = c(
                         "silence",
                         "filter",
                         "speed/volume",
                         "pitch"),
                        values =
                        c("black",
                          "#E41A1C",
                          "#377EB8",
                          "#4DAF4A")) +
      ## scale_y_continuous(limits = c(0, 1080),
      ##                    breaks = seq(0, 1080, 300),
      ##                    labels = seq(0, 15, 5)) +
      ## opts(axis.text.x=theme_blank()) +
      opts(legend.position = "top") +
      labs(x = "mode",
           y = "time spent in mode (min)",
           fill = "mapping"))
dev.off()

thesis.fig.device("~/Documents/School/PhD/ben-thesis/figures/ex3/mode-breakdown-group.pdf", "halfwidth")
print(ggplot(ddply(subset(cbind(touch.df[-1], # hack to get facet_wrap to show the right labels
                                g = sapply(touch.df$g, function(x) paste("Group", x))),
                                touch.count != 4),
                   .(g, touch.count),
                   summarize,
                   total.time = sum(delta.t)/60),
             aes(x = factor(touch.count), y = total.time)) +
      geom_bar(aes(fill = factor(touch.count),
                   stat="identity"),
               size = 0.6) +
      scale_fill_manual(breaks = 0:3,
                       labels = c(
                         "silence",
                         "filter",
                         "speed/volume",
                         "pitch"),
                        values =
                        c("black",
                          "#E41A1C",
                          "#377EB8",
                          "#4DAF4A"),
                        guide = "none") +
      ## scale_y_continuous(limits = c(0, 660),
      ##                    breaks = seq(0, 660, 60),
      ##                    labels = 0:11) +      
      labs(x = "mode",
           y = "time spent in mode (min)",
           fill = "mapping") +
      opts(legend.position = "top") +   
      facet_wrap(~ g, nrow = 2))
dev.off()

thesis.fig.device("~/Documents/School/PhD/ben-thesis/figures/ex3/mode-breakdown-group-session.pdf", "fullpage")
print(ggplot(ddply(subset(touch.df, touch.count != 4),
                   .(g, s, touch.count),
                   summarize,
                   total.time = sum(delta.t)/60),
             aes(x = factor(touch.count), y = total.time)) +
      geom_bar(aes(fill = factor(touch.count),
                   stat="identity"),
               size = 0.6) +
      scale_fill_manual(breaks = 0:3,
                       labels = c(
                         "silence",
                         "filter",
                         "speed/volume",
                         "pitch"),
                        values =
                        c("black",
                          "#E41A1C",
                          "#377EB8",
                          "#4DAF4A")) +
      opts(legend.position = "top") +
      labs(x = "mode",
           y = "time spent in mode (min)",
           fill = "mapping") +
      facet_grid(s ~ g, labeller = facet.labeller))      
dev.off()

thesis.fig.device("~/Documents/School/PhD/ben-thesis/figures/ex3/mode-breakdown-name.pdf", "fullwidth")
print(ggplot(ddply(subset(touch.df, touch.count != 4),
                   .(g, name, touch.count),
                   summarize,
                   total.time = sum(delta.t)/60),
             aes(x = factor(touch.count), y = total.time)) +
      geom_bar(aes(fill = factor(touch.count),
                   stat="identity"),
               size = 0.6) +
      scale_fill_manual(breaks = 0:3,
                       labels = c(
                         "silence",
                         "filter",
                         "speed/volume",
                         "pitch"),
                        values =
                        c("black",
                          "#E41A1C",
                          "#377EB8",
                          "#4DAF4A"),
                        guide = "none") +
      labs(x = "mode",
           y = "time spent in mode (min)",
           fill = "mapping") +
      facet_wrap(~ name, nrow = 2))
dev.off()

# inst breakdown

thesis.fig.device("~/Documents/School/PhD/ben-thesis/figures/ex3/inst-breakdown.pdf", "halfwidth")
print(ggplot(ddply(touch.df,
                   .(instrument),
                   summarize,
                   total.time = sum(delta.t)/60),
             aes(x = factor(instrument), y = total.time)) +
      geom_bar(stat="identity", aes(fill = factor(instrument))) +
      scale_fill_brewer(palette = "Set1", guide = "none") +
      labs(x = "",
           y = "time spent using synth/sampler (min)"))
dev.off()

thesis.fig.device("~/Documents/School/PhD/ben-thesis/figures/ex3/inst-breakdown-group.pdf", "halfwidth")
print(ggplot(ddply(cbind(touch.df[-1], # hack to get facet_wrap to show the right labels
                                g = sapply(touch.df$g, function(x) paste("Group", x))),
                   .(g, instrument),
                   summarize,
                   total.time = sum(delta.t)/60),
             aes(x = factor(instrument), y = total.time)) +
      geom_bar(aes(fill = factor(instrument),
                   stat="identity"),
               size = 0.6) +
      scale_fill_brewer(palette = "Set1", guide = "none") +
      labs(x = "",
           y = "time spent using synth/sampler (min)") +
      facet_wrap(~ g, nrow = 2))
dev.off()

thesis.fig.device("~/Documents/School/PhD/ben-thesis/figures/ex3/inst-breakdown-session.pdf", "halfwidth")
print(ggplot(ddply(cbind(touch.df[-1], # hack to get facet_wrap to show the right labels
                                s = sapply(touch.df$s, function(x) paste("Session", x))),
                   .(s, instrument),
                   summarize,
                   total.time = sum(delta.t)/60),
             aes(x = factor(instrument), y = total.time)) +
      geom_bar(aes(fill = factor(instrument),
                   stat="identity"),
               size = 0.6) +
      scale_fill_brewer(palette = "Set1", guide = "none") +
      labs(x = "",
           y = "time spent using synth/sampler (min)") +
      facet_wrap(~ s, nrow = 2))
dev.off()

thesis.fig.device("~/Documents/School/PhD/ben-thesis/figures/ex3/inst-breakdown-group-session.pdf", "fullpage")
print(ggplot(ddply(touch.df,
                   .(g, s, instrument),
                   summarize,
                   total.time = sum(delta.t)/60),
             aes(x = factor(instrument), y = total.time)) +
      geom_bar(aes(fill = factor(instrument),
                   stat="identity"),
               size = 0.6) +
      scale_fill_brewer(palette = "Set1", guide = "none") +
      labs(x = "",
           y = "time spent using synth/sampler (min)") +
      facet_grid(s ~ g, labeller = facet.labeller))      
dev.off()

thesis.fig.device("~/Documents/School/PhD/ben-thesis/figures/ex3/inst-breakdown-name.pdf", "fullwidth")
print(ggplot(ddply(touch.df,
                   .(g, name, instrument),
                   summarize,
                   total.time = sum(delta.t)/60),
             aes(x = factor(instrument), y = total.time)) +
      geom_bar(aes(fill = factor(instrument),
                   stat="identity"),
               size = 0.6) +
      scale_fill_brewer(palette = "Set1", guide = "none") +
      labs(x = "",
           y = "time spent using synth/sampler (min)") +
      facet_wrap(~ name, nrow = 2))
dev.off()

# mode switching density

mode.time.df <- ddply(subset(touch.df, event == "down"),
                           .(g, s, j, name),
                           function(name.df){
                             name.df$mode.time <- c(diff(name.df$time), 0)
                             name.df[c("name", "g", "s", "time", "touch.count", "mode.time")]
                           })

thesis.fig.device("~/Documents/School/PhD/ben-thesis/figures/ex3/mode-time-quantile-name.pdf", "keynote")
print(ggplot(ddply(mode.time.df,
                   .(g, name),
                   summarize,
                   mode.time = quantile(mode.time, .9)),
             aes(x = name, y = mode.time)) +
      geom_bar(aes(fill = factor(g)),
               stat="identity") +
      scale_fill_brewer(palette = "Set1", guide = "none") +
      labs(x = "session",
           y = "mode time 90th percentile (sec)"))
dev.off()

thesis.fig.device("~/Documents/School/PhD/ben-thesis/figures/ex3/mode-time-quantile-name-session.pdf", "keynote")
print(ggplot(ddply(mode.time.df,
                   .(g, s, name),
                   summarize,
                   mode.time = quantile(mode.time, .9)),
             aes(x = factor(s), y = mode.time)) +
      geom_bar(aes(fill = factor(g)),
               stat="identity") +
      scale_fill_brewer(palette = "Set1", guide = "none") +
      labs(x = "session",
           y = "mode time 90th percentile (sec)") +
      facet_grid(. ~ name, labeller = facet.labeller))      
dev.off()

thesis.fig.device("~/Documents/School/PhD/ben-thesis/figures/ex3/mode-time-quantile-group-session.pdf", "keynote")
print(ggplot(ddply(mode.time.df,
                   .(g, s),
                   summarize,
                   mode.time = quantile(mode.time, .7)),
             aes(x = factor(s), y = mode.time)) +
      geom_bar(aes(fill = factor(g)),
               stat="identity") +
      scale_fill_brewer(palette = "Set1", guide = "none") +
      labs(x = "session",
           y = "mode time 90th percentile (sec)") +
      facet_grid(. ~ g, labeller = facet.labeller))      
dev.off()

thesis.fig.device("~/Documents/School/PhD/ben-thesis/figures/ex3/mode-cps-group-session.pdf", "keynote")
print(ggplot(touch.df[touch.df$event=="down",],
             aes(x = factor(g), y = mode.time)) +
      geom_violin(aes(fill = factor(g))) +
      geom_boxplot(aes(fill = factor(g)),
                   fill = "grey50",
                   colour = "white",
                   alpha = 0.5,
                   outlier.size = 0,
                   width = 0.5) +
      scale_fill_brewer(palette = "Set1",
                        guide = "none") +
      opts(legend.position = "top") +
      labs(x = "session",
           y = "avg. mode changes per second") +
      facet_grid(. ~ g, labeller = facet.labeller))      
dev.off()

thesis.fig.device("~/Documents/School/PhD/ben-thesis/figures/ex3/mode-cps-session.pdf", "keynote")
print(ggplot(ddply(feature.df,
                   .(s),
                   summarize,
                   mean.time = mean(touch.down)),
             aes(x = factor(s), y = mean.time)) +
      geom_bar(aes(fill = factor(s)),
                   stat="identity") +
      scale_fill_brewer(type = "qual",
                        palette = 2,
                        guide = "none") +
      opts(legend.position = "top") +
      labs(x = "session",
           y = "avg. mode changes per second"))
dev.off()
