######################
## recurrence plots ##
######################

library('reshape')
library('plyr')
library('ggplot2')
library('randomForest')
library('foreach')
library('doMC')
registerDoMC()

load("RData/features-1s.RData")

source("vt-header.r")

## RP generation

distance.matrix <- function(feature.df, type = "rf", only = "all"){
  if(only == "all"){
    idx <- !feature.subset("id")
  }else if(only == "noaudio"){
    idx <- !feature.subset("id") & !feature.subset("audio")
  }else{
    idx <- !feature.subset("id") & feature.subset(only)
  }
  if(type == "rf"){
    rf <- randomForest(na.roughfix(feature.df[,idx]), ntree = 2000, proximity = TRUE)
    dm <- (1 - rf$proximity)^2
  }else if(type == "euclid"){
    dm <- as.matrix(dist(feature.df[idx]))
    dm <- dm / max(dm)
  }
  else{
    stop("Unrecognised metric for distance matrix")
  }
  rownames(dm) <- NULL
  colnames(dm) <- NULL
  dm
}

cross.distance.matrix <- function(x.df, y.df, type = "rf", only = "all"){
  which.df <- factor(rep(c("x", "y"), times = c(dim(x.df)[1], dim(y.df)[1])))
  dm <- distance.matrix(rbind(x.df, y.df), type, only)
  (dm[which.df == "x", which.df == "y"] + dm[which.df == "y", which.df == "x"]) / 2
}

recurrence.matrix <- function(diss.mat, eps){
  eps.points <- diss.mat < eps
  diss.mat[eps.points] <- 1
  diss.mat[!eps.points] <- 0
  diss.mat
}

## RP plotting

RP.plot.string <- function(gsjnf,
                           base.dir,
                           feat.subsets,
                           type,
                           rp.type = "RP",
                           name.pair = NULL){
  return.str <- paste(gsjnf$g, gsjnf$s, gsjnf$j, sep = "-")
  feat.str <- gsub(".", "-", feat.subsets, fixed = TRUE)
  if(type == "path"){
    if(rp.type == "RP"){
      return.str <- paste(base.dir,
                          return.str, "-",
                          gsjnf$name, "-",
                          feat.str, ".pdf",
                          sep = "")
    }else if(rp.type == "CRP"){
      return.str <- paste(base.dir,
                          return.str, "-",
                          name.pair, "-C-",
                          feat.str, ".pdf",
                          sep = "")
    }else if(rp.type == "JRP"){
      return.str <- paste(base.dir,
                          return.str, "-",
                          name.pair, "-J-",
                          feat.str, ".pdf",
                          sep = "") 
    }
  }else if(type == "title"){
    if(rp.type == "RP"){
      return.str <- paste("RP  ",
                          gsjnf$name, ", ",
                          return.str, " ",
                          feat.str,
                          sep = "")
    }else if(rp.type == "CRP"){
      return.str <- paste("CRP: ",
                          name.pair, ", ",
                          return.str, " ",
                          feat.str,
                          sep = "")
    }else if(rp.type == "JRP"){
      return.str <- paste("JRP: ",
                          name.pair, ", ",
                          return.str, " ",
                          feat.str,
                          sep = "")
    }
  }
  return.str
}

recurrence.plot <- function(recurr.mat, delta.t, plot.title, fpath = NULL){
  melted.recurr.mat <- melt(recurr.mat)
  melted.recurr.mat[,1:2] <- delta.t * melted.recurr.mat[,1:2]
  names(melted.recurr.mat)[1:2] <- c("x", "y")
  p <- ggplot(melted.recurr.mat, aes(x, y)) + geom_tile(aes(fill = value)) + scale_fill_gradient(low="white", high="black", limits=c(0,1), guide = "none") + opts(title = plot.title, aspect.ratio = 1, axis.title.x = theme_blank(), axis.title.y = theme_blank())
  if(is.null(fpath)){
    p
  }else{
    pdf(fpath, width = 6, height = 6)
    print(p)
    dev.off()
  }
}

#########
## RQA ##
#########

zero.mat <- function(size){
  matrix(0, nrow = size, ncol = size)
}

shear.matrix <- function(mat){
  d <- dim(mat)[2]
  mat <- rbind(zero.mat(d),
               mat,
               zero.mat(d))
  shorn.mat <- alply(seq_len(d),
                     1,
                     function(x){
                       mat[seq(d - x + 2, length.out = (2 * d - 1)), x]
                     })
  do.call(cbind, shorn.mat)
}

line.lengths <- function(mat){
  distribution <- as.data.frame(table(do.call(c, alply(cbind(mat, 0),
                                                       1,
                                                       function(x){
                                                         y <- diff(c(0, (1:length(x))[!as.logical(x)])) - 1
                                                         y[y!=0]
                                                       }))))
  if(dim(distribution)[1] != 0){
    names(distribution) <- c("line.length", "freq")
    distribution$line.length <- as.numeric(distribution$line.length)
    distribution
  }else{
    data.frame(line.length = 1, freq = 0)
  }
}

line.freq.df <- function(rmat){
  result <- merge(line.lengths(shear.matrix(rmat)),
                  ddply(rbind(line.lengths(rmat),
                              line.lengths(t(rmat))),
                        .(line.length),
                        function(x){
                          sum(x$freq) / 2
                        }),
                  by = "line.length",
                  all = TRUE)
  names(result)[2:3] <- c("diag", "vert")
  result[is.na(result)] <- 0
  result
}

lfreq.above.lmin <- function(lfreq.df, lmin, type){
  lfreq.df[lfreq.df$line.length >= lmin & lfreq.df[[type]] != 0, c("line.length", type)]
}

lfreq.sum <- function(lfreq.df, lmin, type){
  sum(lfreq.above.lmin(lfreq.df, lmin, type)[,2])
}

lfreq.weighted.sum <- function(lfreq.df, lmin, type){
  sum(apply(lfreq.above.lmin(lfreq.df, lmin, type),
            1,
            prod))
}

rqa.statistics <- function(rmat, lmin){
  line.freqs <- line.freq.df(rmat)
  recur.rate <- mean(rmat)
  if(dim(line.freqs)[1] != 0 && recur.rate != 0){
    wsum.diag <- lfreq.weighted.sum(line.freqs, lmin, "diag")
    wsum.vert <- lfreq.weighted.sum(line.freqs, lmin, "vert")
    data.frame(recur.rate = recur.rate,
               determinism = wsum.diag/recur.rate,
               laminarity = wsum.vert/recur.rate,
               avg.diag.length = ifelse(wsum.diag==0, 0, wsum.diag/lfreq.sum(line.freqs, lmin, "diag")),
               trap.time = ifelse(wsum.vert==0, 0, wsum.vert/lfreq.sum(line.freqs, lmin, "vert")),
               divergence = 1/max(c(line.freqs$line.length[line.freqs$diag != 0], 0))
               )
  }else{
    data.frame(recur.rate = recur.rate,
               determinism = 0,
               laminarity = 0,
               avg.diag.length = 0,
               trap.time = 0,
               divergence = 1
               )
  }
}

# calculate RQA statistics

create.rqa.df <- function(feature.df,
                          metric.type,
                          lmin,
                          eps.quantile,
                          generate.plots = FALSE,
                          synthetic = FALSE){
  if(synthetic){
    feature.df <- cbind(feature.df[feature.subset("id")],
                        feature.df[sample(dim(feature.df)[1]), feature.subset("all")])
  }
  ddply(feature.df,
        .(sj.idx, g),
        function(jam.df){
          print(paste("group:", jam.df$g[1],
                      "session:", jam.df$s[1],
                      "jam:", jam.df$j[1]))
          ldply(c("all", "accel", "noaccel"),
                function(feats){
                  mus.df.list <- dlply(jam.df,
                                       .(name),
                                       function(mus.df) mus.df)
                  base.dir <- paste("figures/RP/",
                                    ifelse(synthetic, "synth/", ""),
                                    feature.df$delta.t[1],
                                    "s/", metric.type, "/", sep = "")
                  if(!file.exists(base.dir)){
                    dir.create(base.dir, recursive = TRUE)
                  }
                  dmat.list <- llply(mus.df.list,
                                     function(mdf){
                                       distance.matrix(mdf, type = metric.type, only = feats)
                                     })
                  eps.list <- llply(dmat.list, function(x) quantile(x, eps.quantile))
                  rmat.list <- llply(1:length(dmat.list),
                                     function(i){
                                       recurrence.matrix(dmat.list[[i]], eps.list[[i]]) - diag(dim(dmat.list[[i]])[1])
                                     })
                  adply(c(as.list(1:length(mus.df.list)),
                          combn(1:length(mus.df.list), 2, simplify = FALSE)),
                        1,
                        function(mus.idx){
                          if(length(mus.idx) == 1){
                                        # recurrence plot
                            if(generate.plots){
                              gsjnf <- mus.df.list[[mus.idx]][1,c(3:5,2,6)]
                              recurrence.plot(rmat.list[[mus.idx]] + diag(dim(rmat.list[[mus.idx]])[1]),
                                              mus.df.list[[mus.idx]]$delta.t[1],
                                              RP.plot.string(gsjnf,
                                                             base.dir,
                                                             as.character(feats),
                                                             "title"),
                                              RP.plot.string(gsjnf,
                                                             base.dir,
                                                             as.character(feats),
                                                             "path"))
                            }
                            data.frame(mus.df.list[[mus.idx]][1,1:5],
                                       feature.subset = feats,
                                       type = factor("reg"),
                                       eps.value = eps.list[[mus.idx]],
                                       rqa.statistics(rmat.list[[mus.idx]], lmin))
                          }else{
                            name.pair <- paste(names(dmat.list)[mus.idx[1]],
                                               names(dmat.list)[mus.idx[2]],
                                               sep = "-")
                            min.dim <- min(c(dim(rmat.list[[mus.idx[1]]])[1],
                                             dim(rmat.list[[mus.idx[2]]])[1]))
                                        # CRP
                            crdist <- cross.distance.matrix(mus.df.list[[mus.idx[1]]][1:min.dim,],
                                                            mus.df.list[[mus.idx[2]]][1:min.dim,],
                                                            type = metric.type,
                                                            only = ifelse(feats == "all" | feats == "noaccel",
                                                              "noaudio",
                                                              feats))
                            eps.list[[4]] <- quantile(crdist, eps.quantile)
                            crmat <- recurrence.matrix(crdist, eps.list[[4]])
                                        # JRP
                            jrmat <- rmat.list[[mus.idx[1]]][1:min.dim,1:min.dim] * rmat.list[[mus.idx[2]]][1:min.dim,1:min.dim]
                            if(generate.plots){
                              gsjnf <- mus.df.list[[mus.idx[1]]][1,c(3:5,2,6)]
                              recurrence.plot(crmat,
                                              mus.df.list[[mus.idx[1]]]$delta.t[1],
                                              RP.plot.string(gsjnf,
                                                             base.dir,
                                                             as.character(feats),
                                                             "title",
                                                             "CRP",
                                                             name.pair),
                                              RP.plot.string(gsjnf,
                                                             base.dir,
                                                             as.character(feats),
                                                             "path",
                                                             "CRP",
                                                             name.pair))
                              recurrence.plot(jrmat,
                                              mus.df.list[[mus.idx[1]]]$delta.t[1],
                                              RP.plot.string(gsjnf,
                                                             base.dir,
                                                             as.character(feats),
                                                             "title",
                                                             "JRP",
                                                             name.pair),
                                              RP.plot.string(gsjnf,
                                                             base.dir,
                                                             as.character(feats),
                                                             "path",
                                                             "JRP",
                                                             name.pair))
                            }
                            rbind(data.frame(sj.idx = mus.df.list[[mus.idx[1]]][1,1],
                                             name = factor(name.pair),
                                             mus.df.list[[mus.idx[1]]][1,3:5],
                                             feature.subset = feats,
                                             type = factor("cross"),
                                             eps.value = eps.list[[4]],
                                             rqa.statistics(crmat, lmin)),
                                  data.frame(sj.idx = mus.df.list[[mus.idx[1]]][1,1],
                                             name = factor(name.pair),
                                             mus.df.list[[mus.idx[1]]][1,3:5],
                                             feature.subset = feats,
                                             type = factor("joint"),
                                             eps.value = mean(as.numeric(eps.list[mus.idx])),
                                             rqa.statistics(jrmat, lmin)))
                          }
                        })
                })
        },
        .parallel = TRUE)[-1]
}

# real stats

rqa.df <- adply(expand.grid(c("rf", "euclid"), c(1,5), stringsAsFactors = FALSE),
                1,
                function(x){
                  load(paste("RData/",
                             ifelse(x[1] == "rf", "", "norm-"),
                             "features-",
                             x[2],
                             "s.RData",
                             sep = ""))
                  rqa.df <- create.rqa.df(feature.df, "rf", 4, 0.12, TRUE, FALSE)
                  rqa.df <- rqa.df[!(!rqa.df$type=="reg" & rqa.df$feature.subset=="audio"),]
                  rqa.df
                })
names(rqa.df)[1:2] <- c("metric", "delta.t")
save(rqa.df, file = "RData/rqa-stats.RData")

# synthetic stats

synth.rqa.df <- adply(expand.grid(c("rf", "euclid"), c(1,5), stringsAsFactors = FALSE),
                      1,
                      function(x){
                        load(paste("RData/",
                                   ifelse(x[1] == "rf", "", "norm-"),
                                   "features-",
                                   x[2],
                                   "s.RData",
                                   sep = ""))
                        rqa.df <- create.rqa.df(feature.df, "rf", 4, 0.12, TRUE, TRUE)
                        rqa.df <- rqa.df[!(!rqa.df$type=="reg" & rqa.df$feature.subset=="audio"),]
                        rqa.df
                      })
names(synth.rqa.df)[1:2] <- c("metric", "delta.t")
save(synth.rqa.df, file = "RData/synth-rqa-stats.RData")
