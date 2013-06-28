## required args:
## - df.name
## - plotter.name
## - split.cols
## - window.length
## - window.lag
## - alph

args=(commandArgs(TRUE))

if(length(args)==0) {
  print("No arguments supplied.")
}else{
  for(i in 1:length(args)) {
    eval(parse(text=args[[i]]))
  }
}

load(paste("RData/", gsub(".", "-", df.name, fixed=TRUE), ".RData", sep=""))

library('ggplot2')
library('plyr')
library('Cairo')
library('vcd')

#######################
## for making videos ##
#######################

path.to.frames <- function(window.length, plot.name) {
  paste("video/", plot.name, "/", as.character(window.length), "sec/", sep="")
}

hd1080.cairo <- function(fpath) {
  CairoPNG(filename=fpath, width=1920, height=1080, dpi=150, units="px", bg = "white")
}

hd1080.quartz <- function(fpath) {
  png(file=fpath, width=1920, height=1080, res=150, units="px")
}

most.recent.frame <- function(dir) {
  l <- list.files(dir, pattern="*.png")
  if(length(l)==0) {
    0
  }else{
    as.numeric(strsplit(l[length(l)], ".", fixed=TRUE)[[1]][1])
  }
}

frame.titler <- function(split.cols, gsjn.row) {
  do.call(paste,
          c(alply(split.cols,
                  1,
                  function(col) {
                    switch(col,
                           g = paste("Group", gsjn.row$g),
                           s = paste("Session", gsjn.row$s),
                           j = paste("Jam", gsjn.row$j))
                  }),
            sep=", "))
}

facet.labeller <- function(variable, value) {
  switch(variable,
         g = paste("Group", value),
         s = paste("Session", value),
         j = paste("Jam", value),
         name = as.character(value))
}

make.frames <- function(df, plotter, split.cols, video.dir, window.length, window.lag, alph) {
  frame.index <- 0
  begin.frame <- most.recent.frame(video.dir)
  time <- Sys.time()
  d_ply(df,
        split.cols,
        function(jam.df) {
          a_ply(seq(0, 300, window.lag)-window.length,
              1,
              function(window.start) {
                if(frame.index >= begin.frame) {
                  in.window <- (jam.df$time>(window.start))&(jam.df$time<=window.start+window.length)
                  hd1080.quartz(sprintf("%s%05d.png", video.dir, frame.index))
                  frame.title <- sprintf("%s, %02d:%05.2f",
                                         frame.titler(split.cols, jam.df[1,c("g","s","j","name")]),
                                         (window.start+window.length) %/% 60,
                                         (window.start+window.length) %% 60)
                  if(TRUE %in% in.window) {
                    print(plotter(jam.df[in.window,],
                                  frame.title,
                                  alph))
                  }else{
                    print(plotter(jam.df[!duplicated(jam.df[,c("g","s","j","name")]),],
                                  frame.title,
                                  0))
                  }
                  dev.off()
                  new.time <- Sys.time()
                  fps <- 1/as.numeric(difftime(new.time, time, units="secs"))
                  sec.remaining <- ((4800/window.lag)-frame.index)/fps
                  print(sprintf("%1d-%1d-%06.2f   %5d   %5.2ffps   %5.1f%%   ETA %02d:%02d:%02.0f",
                                jam.df$s[1],
                                jam.df$j[1],
                                (window.start+window.length),
                                frame.index,
                                fps,
                                (300*(4*(jam.df$s[1]-1)+(jam.df$j[1]-1))+window.start+window.lag)/48,
                                sec.remaining %/% 3600,
                                sec.remaining %% 3600 %/% 60,
                                sec.remaining %% 60))
                  time <<- new.time
                }
                frame.index <<- frame.index+1
              })
      })
}

dummy.touch.df <- id.df[id.df$type=="touch",]

dummy.touch.df$touch.count=rep(1:4, length.out=dim(dummy.touch.df)[1])
dummy.touch.df$x <- 0.5
dummy.touch.df$y <- 0.5

allscatter <- function(df, frame.title, alph) {
  p <- ggplot(df, aes(x, y))
  ## p <- p + theme_grey(base_size = 28)
  p <- p + geom_point(aes(colour=factor(touch.count), size=ifelse(delta.t<=1, delta.t, 1)), alpha=alph)
  p <- p + geom_point(aes(colour=factor(touch.count)), data=dummy.touch.df, alpha=0)
  p <- p + xlim(0,1) + ylim(0,1) + opts(aspect.ratio=3/2)
  p <- p + opts(axis.text.x=theme_blank(), axis.text.y=theme_blank(), axis.title.x=theme_blank(), axis.title.y=theme_blank())
  p <- p + opts(title=frame.title)
  p <- p + scale_colour_brewer(name="touches",
                               breaks=factor(1:4),
                               palette="Set1")
  p <- p + scale_area("Duration (s)", breaks=c(0, .1, .3, 1), limits=c(0,1), guide="none")
  p <- p + facet_wrap(~ name, drop=FALSE, as.table=TRUE, ncol=6)  
  p
}

groupscatter <- function(df, frame.title, alph) {
  p <- ggplot(df, aes(x, y))
  ## p <- p + theme_grey(base_size = 24)
  p <- p + geom_point(aes(colour=factor(touch.count), size=ifelse(delta.t<=1, delta.t, 1)), alpha=alph)
  p <- p + geom_point(aes(colour=factor(touch.count)), data=dummy.touch.df[dummy.touch.df$g==df$g[1],], alpha=0)
  p <- p + xlim(0,1) + ylim(0,1) + opts(aspect.ratio=3/2)
  p <- p + opts(axis.text.x=theme_blank(), axis.text.y=theme_blank(), axis.title.x=theme_blank(), axis.title.y=theme_blank())
  p <- p + opts(title=frame.title)
  p <- p + scale_colour_brewer(name="touches",
                               breaks=factor(1:4),
                               palette="Set1")
  p <- p + scale_area("Duration (s)", breaks=c(0, .1, .3, 1), limits=c(0,1), guide="none")
  p <- p + facet_grid(name ~ s, shrink=FALSE, margins=FALSE, labeller=facet.labeller)
  p
}

allheatmap <- function(df, frame.title, alph) {
  p <- ggplot(df, aes(x, y))
  p <- p + theme_grey(base_size = 28)
  p <- p + stat_binhex(binwidth=c(1.5,1)/100)
  p <- p + scale_fill_gradientn(colours=diverge_hcl(7))
  p <- p + xlim(0,1) + ylim(0,1) + opts(aspect.ratio=3/2)
  p <- p + opts(axis.text.x=theme_blank(), axis.text.y=theme_blank(), axis.title.x=theme_blank(), axis.title.y=theme_blank())
  p <- p + opts(title=frame.title)
  p <- p + facet_wrap(~ touch.count, drop=FALSE, ncol=4)
  p
}

comptouchdensity <- function(df, frame.title, alph) {
  p <- ggplot(df, aes(x=touches.down.per.sec))
  p <- p + theme_grey(base_size = 28)
  p <- p + geom_density(alpha=alph, size=0.8, aes(y=..density.., kernel="epanechnikov", colour=name))
  p <- p + xlim(0,3) + ylim(0,2.5) + opts(aspect.ratio=9/16)
  p <- p + opts(title=frame.title) + labs(x="touches down per second", y="density")
  p <- p + facet_wrap(~ g, drop=FALSE, as.table=TRUE, ncol=1)
  ## p <- p + facet_grid(s ~ g, labeller=label_both)
  p
}

comptouchhistogram <- function(df, frame.title, alph) {
  p <- ggplot(df, aes(x=touches.down.per.sec))
  p <- p + theme_grey(base_size = 28)
  p <- p + geom_histogram(aes(y=..density.., fill=name), binwidth = .25, position="dodge")
  p <- p + xlim(0,3) + ylim(0,2.5)# + opts(aspect.ratio=9/16)
  p <- p + opts(title=frame.title, legend.position="none") + labs(x="touches down per second", y="density")
  p <- p + facet_wrap(~ name, drop=FALSE, as.table=TRUE, ncol=6)
  ## p <- p + facet_grid(s ~ g, labeller=label_both)
  p
}

make.frames(get(df.name), get(plotter.name), split.cols, path.to.frames(window.length, plotter.name), window.length, window.lag, alph)
