#####################################
# feature extraction infrastructure #
#####################################

## feature todo list

## polar r, theta mean and variance
## higher order (between window) variances

# for parallel execution with foreach and plyr

library('plyr')
library('foreach')
library('doMC')
registerDoMC(cores=4)

# chunk size & overlap

window.length <- 5
window.lag <- 5

# features will be gradually added as columns of feature.df

feature.df <- ddply(unique(id.df[c("g", "s", "j", "sj.idx", "name")]),
                    .(sj.idx, name),
                    function(df) {
                      time.vec <- seq(0, 300 - window.length, by = window.lag)
                      cbind(df[c("g", "s", "j")],
                            data.frame(time = time.vec,
                                       s.time = time.vec + (df$j - 1) * 300,
                                       delta.t = window.length))
                    })

levels(touch.df$event) <- c(levels(touch.df$event), "none")

time.window <- function(x, window.start, window.length) {
  if (is.data.frame(x)) {
    chunk <- x[x$time >= window.start & x$time < window.start + window.length,]
    ## add 'blank' chunks before any touches
    if("event" %in% names(chunk)){
      if(window.start < x$time[1]){
        chunk <- rbind(x[1,], chunk)
        chunk$touch.count[1] <- 0
        chunk[1, -(1:match("touch.count", names(chunk)))] <- NA
      }else{
        ## beginning of chunk should be window-aligned
        chunk <- rbind(x[match(FALSE, x$time < window.start)-1,], chunk)
      }
      chunk$event[1] <- factor("none")
      chunk$delta.t[1] <- ifelse(dim(chunk)[1] == 1, window.length, min(c(window.length, chunk$time[2] - window.start)))
      chunk$time[1] <- window.start
      ## end chunk at window boundary
      if(((chunk$time[length(chunk$time)] %% window.length) +
          chunk$delta.t[length(chunk$delta.t)]) > window.length){
        chunk$delta.t[length(chunk$delta.t)] <- window.length - (chunk$time[length(chunk$time)] %% window.length)
      }
    }
    if(dim(chunk)[1]==0){
      chunk <- x[1,]
      chunk$time <- window.start
      chunk[1, -(1:match("time", names(chunk)))] <- NA
      chunk
    }else{
      chunk
    }
  }else if (is.ts(x)) {
    window(x, window.start, window.start + window.length)
  }else if (class(x) == "Wave") {
    time <- seq(0, by = 1/x@samp.rate, length.out = length(x@left))
    x[time >= window.start & time < window.start + window.length,]
  }else{
    stop("unrecognised object, can't get time window")
  }
}

filter.on.sj.idx.and.name <- function(df, sj.idx, name) {
  df[df$sj.idx == sj.idx & as.character(df$name) == as.character(name),]
}

## necessary to get around the ordered factor bug in plyr

reorder.rdc <- function(rdc, feature.df) {
  rdc[aaply(feature.df, 1, function(x) paste(x$sj.idx, x$name, x$time, x$delta.t, sep="."), .expand=FALSE)]
}

raw.data.chunks <- function(data, feature.df) {
  rdc <- do.call(c,
                 dlply(data,
                       .(sj.idx, name),
                       function(jam.df) {
                         dlply(filter.on.sj.idx.and.name(feature.df,
                                                         jam.df$sj.idx[1],
                                                         jam.df$name[1]),
                               c("time", "delta.t"),
                               function(window) {
                                 time.window(jam.df, window$time, window$delta.t)
                               })
                       },
                       .progress = "text",
                       .parallel = FALSE))
  reorder.rdc(rdc, feature.df)
}

get.raw.data.chunk <- function(chunk.list, sj.idx, name, time, delta.t) {
  chunk.list[[paste(sj.idx, name, time, delta.t, sep=".")]]
}

sweep.out.feature <- function(feature.df,
                              chunk.list,
                              feature.fun) {
  do.call(rbind, alply(feature.df,
                       1,
                       function(row) {
                         chunk <- chunk.list[[paste(row$sj.idx,
                                                    row$name,
                                                    row$time,
                                                    row$delta.t,
                                                    sep=".")]]
                         feature.fun(chunk)
                       },
                       ## .expand = FALSE,
                       .progress = "text",
                       .parallel = FALSE))
}

##################
# touch features #
##################

rdc <- raw.data.chunks(touch.df, feature.df)

# mode/instrument breakdowns

# there is some error in these atm, due to aliasing over window boundaries

feature.df[c("silence",
             "mode.1", 
             "mode.2",
             "mode.3",
             "mode.4")] <- sweep.out.feature(feature.df,
                                             rdc,
                                             function(chunk) {
                                               aaply(0:4,
                                                     1,
                                                     function(tc) {
                                                       sum(chunk$delta.t[chunk$touch.count==tc])
                                                       })
                                             })/feature.df$delta.t

feature.df[c("sampler", "synth")] <- sweep.out.feature(feature.df,
                                                       rdc,
                                                       function(chunk) {
                                                         aaply(1:2,
                                                               1,
                                                               function(inst) {
                                                                 sum(chunk$delta.t[chunk$touch.count==inst])
                                                               })
                                                       })/feature.df$delta.t

# touches down/moved per second

feature.df$touch.down <- sweep.out.feature(feature.df,
                                           rdc,
                                           function(chunk) {
                                             sum(chunk$event == "down")
                                           })/feature.df$delta.t[1]
feature.df$touch.down <- as.numeric(feature.df$touch.down)

feature.df$touch.moved <- sweep.out.feature(feature.df,
                                            rdc,
                                            function(chunk) {
                                              sum(chunk$event == "moved")
                                            })/feature.df$delta.t[1]
feature.df$touch.moved <- as.numeric(feature.df$touch.moved)

feature.df$touch.distance <- sweep.out.feature(feature.df,
                                               rdc,
   function(chunk) {
     if(NA %in% chunk$touch.count){
       0
     }else{
       sum(daply(chunk,
                 .(touch.count),
                 function(x){
                   if(dim(x)[1] < 2){
                     0
                   }else{
                     sqdiffs <- (apply(x[c("x1", "y1", "x2", "y2", "x3", "y3")], 2, diff))^2
                     sum(sqrt(sqdiffs[c(1,3,5)] + sqdiffs[c(2,4,6)]), na.rm=TRUE)
                 }
               }))
     }
   })/feature.df$delta.t[1]
feature.df$touch.distance <- as.numeric(feature.df$touch.distance)

# mode/instrument change stats

feature.df[c("mode.changes",
             "inst.changes")] <- sweep.out.feature(feature.df,
                                                   rdc,
                                                   function(chunk) {
                                                     c(sum(diff(chunk$touch.count[chunk$touch.count!=0])!=0),
                                                       sum(diff(as.numeric(chunk$instrument))!=0))
                                                   })/feature.df$delta.t

#######################
# flat touch features #
#######################

rdc <- raw.data.chunks(flat.touch.df, feature.df)

# cartesian

feature.df[c("mean.x", "mean.y",
             "sd.x", "sd.y")] <- sweep.out.feature(feature.df,
                                                     rdc,
                                                     function(chunk) {
                                                       xy <- chunk[c("x", "y")]
                                                       c(apply(xy,
                                                               2,
                                                               mean,
                                                               na.rm = TRUE),
                                                         apply(xy,
                                                               2,
                                                               sd,
                                                               na.rm = TRUE))
                                                     })

block.region.density <- function(xy.df, num.x.blocks){
  xy.df <- xy.df[!is.na(xy.df$x),]
  num.y.blocks <- num.x.blocks * (3/2)
  xb <- (xy.df$x * num.x.blocks) %/% 1
  yb <- (xy.df$y * num.y.blocks) %/% 1
  head(hist(xb + num.x.blocks * yb,
            breaks = 0:(num.x.blocks * num.y.blocks + 1),
            right = FALSE,
            plot = FALSE)$density,
       -1)
}

feature.df[make.block.region.names(2)] <- sweep.out.feature(feature.df,
                                                            rdc,
                                                            function(chunk) {
                                                              block.region.density(chunk[c("x","y")], 2)
                                                            })

## # polar

## cart2pol <- function(x.y) {
##   c(sqrt(x.y[1]^2 + x.y[2]^2),
##     atan2(x.y[2], x.y[1]))
## }

## pol2cart <- function(r.theta) {
##   c(r.theta[1] * cos(r.theta[2]),
##     r.theta[1] * sin(r.theta[2]))
## }

## feature.df[c("mean.r",
##              "mean.theta",
##              "sd.r",
##              "sd.theta")] <- sweep.out.feature(feature.df,
##                                                 rdc,
##                   function(chunk) {
##                     if(dim(chunk)[1] == 0) {
##                       rep(0,8)
##                     }else{
##                       rtheta <- t(apply(cbind(chunk$x - 0.5,
##                                               chunk$y - 0.5), 1,
##                                         cart2pol))
##                       c(apply(rtheta, 2, mean, na.rm = TRUE),
##                         apply(rtheta, 2, sd, na.rm = TRUE))
##                     }
##                   })


####################
## accel features ##
####################

rdc <- raw.data.chunks(accel.df, feature.df)

# motion activity

feature.df[c("accel.mean.x",
             "accel.mean.y",
             "accel.mean.z",
             "accel.sd.x",
             "accel.sd.y",
             "accel.sd.z")] <- sweep.out.feature(feature.df,
                                                   rdc,
                                                   function(chunk) {
                                                     c(apply(chunk[c("accel.x", "accel.y", "accel.z")],
                                                           2,
                                                           mean,
                                                           na.rm = TRUE),
                                                       apply(chunk[c("accel.x", "accel.y", "accel.z")],
                                                           2,
                                                           sd,
                                                           na.rm = TRUE))
                                                   })

euclidean.diffs <- function(x) {
  sqrt(rowSums((x[-1,] - x[-dim(x)[1],])^2))
}

feature.df$accel.rms <-sweep.out.feature(feature.df,
                                            rdc,
                                            function(chunk) {
                                              sqrt(sum(euclidean.diffs(as.matrix(chunk[c("accel.x", "accel.y", "accel.z")]))^2))
                                            })/feature.df$delta.t[1]
feature.df$accel.rms <- as.numeric(feature.df$accel.rms)

rm(rdc)

####################
## audio features ##
####################

yaafe.files <- list.files(paste("audio-features/", window.length, "s", sep = ""), full.names = TRUE)
names(yaafe.files) <- aaply(yaafe.files,
                           1,
                           function(x){
                             strsplit(x, ".", fixed = TRUE)[[1]][3]
                           })

feature.df <- ddply(feature.df,
                    .(sj.idx, name),
                    function(df) {
                      feats <- llply(yaafe.files[grep(paste(df$g[1],
                                                            df$s[1],
                                                            df$j[1],
                                                            sep = "-"),
                                                      yaafe.files)],
                                     function(f) read.csv(f, header = FALSE))
                      feat.names <- unlist(sapply(names(feats),
                                                  function(x){
                                                    if(dim(feats[[x]])[2]==1)
                                                      x
                                                    else
                                                      sapply(1:dim(feats[[x]])[2],
                                                             function(y) {
                                                               paste(x, y, sep=".")
                                                             })
                                                  }))
                      feats <- do.call(data.frame, feats)
                      names(feats) <- feat.names
                      feats$time <- seq(0,
                                        by=df$delta.t[1],
                                        length.out=dim(feats)[1])
                      merge(df, feats, by="time", all=FALSE)
                    },
                    .progress = "text",
                    .parallel = FALSE)

## put the time column back in the right place

feature.df <- feature.df[c(2:match("j", names(feature.df)),
                           1,
                           (match("j", names(feature.df)) + 1):dim(feature.df)[2])]

# filter out the empty chunks

feature.df <- feature.df[!is.na(feature.df$silence),]

###############################
## normalise feature vectors ##
###############################

norm.feature.df <- cbind(feature.df[feature.subset("id")],
                         lapply(feature.df[!feature.subset("id")],
                               function(x) {
                                 (x-mean(x, na.rm = TRUE))/sd(x, na.rm = TRUE)
                               }))
