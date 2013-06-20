## useful subsetting functions

namemap.df <- data.frame(input.name = factor(c(
                           "Ben",
                           "ben-latts",
                           "latts",
                           "Latts",
                           "B-Latts",
                           "Elise",
                           "eco",
                           "John",
                           "John-Boy",
                           "Phil",
                           "Laura",
                           "laura",
                           "Richard",
                           "richard", 
                           "Lachlan",
                           "lachie",
                           "Peter",
                           "peter",
                           "seb",
                           "Seb",
                           "Eleanor",
                           "eleanor", 
                           "Ellie",
                           "ellie",
                           "Zac")),
                         name = factor(c(
                           "Ben",
                           "Ben",
                           "Ben",
                           "Ben",
                           "Ben",
                           "Elise",
                           "Elise",
                           "John",
                           "John",
                           "Phil",
                           "Laura",
                           "Laura",
                           "Richard",
                           "Richard",
                           "Lachlan",
                           "Lachlan",
                           "Peter",
                           "Peter",
                           "Seb",
                           "Seb",
                           "Eleanor",
                           "Eleanor",
                           "Ellie",
                           "Ellie",
                           "Zac")),
                         anon.name = factor(c(
                           "Joe",
                           "Joe",
                           "Joe",
                           "Joe",
                           "Joe",
                           "Sarah",
                           "Sarah",
                           "Alex",
                           "Alex",
                           "Greg",
                           "Leah",
                           "Leah",
                           "Alan",
                           "Alan",
                           "Larry",
                           "Larry",
                           "Tim",
                           "Tim",
                           "Chris",
                           "Chris",
                           "Kate",
                           "Kate",
                           "Judy",
                           "Judy",
                           "Roger")))

namemap.df$name <- factor(namemap.df$name, levels = unique(namemap.df$name), ordered = TRUE)

namemap.df$anon.name <- factor(namemap.df$anon.name, levels = unique(namemap.df$anon.name), ordered = TRUE)

get.unique.name <- function(nm) {
  namemap.df$name[match(nm, namemap.df$input.name)]
}

get.anon.name <- function(nm) {
  result <- namemap.df$anon.name[match(nm, namemap.df$name)]
  if(any(is.na(result))) nm else result
}

de.anon.name <- function(anon.name) {
  result <- namemap.df$name[match(anon.name, namemap.df$anon.name)]
  if(any(is.na(result))) anon.name else result
}

get.group.for.name <- function(nm) {
  name.group.list <- list("Ben" = 1,
                           "Elise" = 1,
                           "John" = 1,
                           "Phil" = 2,
                           "Laura" = 2,
                           "Richard" = 2,
                           "Lachlan" = 3,
                           "Peter" = 3,
                           "Seb" = 3,
                           "Eleanor" = 4,
                           "Ellie" = 4,
                           "Zac" = 4)
  if(length(nm) == 1){
    name.group.list[[nm]]
  }else{
    as.numeric(name.group.list[nm])
  }
}

clean.var.name <- function(var.name){
  clean.name <- gsub("\\.|\\,|\\=|\\ |\\:|\\;|\\(|\\)", "-", as.character(var.name))
  clean.name <- gsub("-+", "-", clean.name)
  tolower(clean.name)
}

make.block.region.names <- function(num.blocks){
  sapply(1:num.blocks,
         function(x){
           paste("zone", x, sep = ".")
        })
}

feature.type.list <- list(id = c(
                            "sj.idx",
                            "name",
                            "g",
                            "s",
                            "j",
                            "time",
                            "s.time",
                            "delta.t"),
                          mode = c(
                            "silence",
                            "mode.1", 
                            "mode.2",
                            "mode.3",
                            "mode.4",
                            "sampler",
                            "synth"),
                          touch.activity = c(
                            "touch.down",
                            "touch.moved",
                            "touch.distance",
                            "mode.changes",
                            "inst.changes"),
                          touch.position = c(
                            "mean.x",
                            "mean.y",
                            "sd.x",
                            "sd.y"),
                          touch.zone = make.block.region.names(6),
                          accel = c(
                            "accel.mean.x",
                            "accel.mean.y",
                            "accel.mean.z",
                            "accel.sd.x",
                            "accel.sd.y",
                            "accel.sd.z",
                            "accel.rms"))

if(exists("feature.df")){
  feature.type.list$audio <- names(feature.df)[(match("accel.rms", names(feature.df)) + 1):dim(feature.df)[2]]

  feature.subset <- function(subset.names, num = FALSE, feature.names = NULL) {
    if("all" %in% subset.names){
      idx <- !feature.subset("id")
    }else if("noaccel" %in% subset.names){
      idx <- feature.subset("all") & !feature.subset("accel")
    }else if("noaudio" %in% subset.names){
      idx <- feature.subset("all") & !feature.subset("audio")
    }else{
      idx <- names(feature.df) %in% unlist(feature.type.list[subset.names])
    }
    if(num)
      (1:length(idx))[idx]
    else
      idx
  }

  feature.type <- function(feature) {
    Filter(function(feature.subset){
      feature %in% feature.type.list[[feature.subset]]
    },
           names(feature.type.list))
  }
}

pretty.name <- list("recur.rate" = "recurrence rate",
                    "determinism" = "determinism",
                    "laminarity" = "laminarity",
                    "avg.diag.length" = "average diagonal length",
                    "trap.time" = "trapping time",
                    "divergence" = "divergence",
                    "reg" = "RP",
                    "cross" = "CRP",
                    "joint" = "JRP",
                    "OBSIR.1" = "octave band signal intensity ratio 1",
                    "OBSIR.2" = "octave band signal intensity ratio 2",
                    "OBSIR.3" = "octave band signal intensity ratio 3",
                    "OBSIR.4" = "octave band signal intensity ratio 4",
                    "ZCR" = "zero crossing rate",
                    "autoCor.1" = "autocorrelation 1",
                    "autoCor.2" = "autocorrelation 2",
                    "autoCor.3" = "autocorrelation 3",
                    "autoCor.4" = "autocorrelation 4",
                    "energy" = "energy",
                    "loudness" = "loudness",
                    "onsets.1" = "onsets (mean)",
                    "onsets.2" = "onsets (variance)",
                    "sharpness" = "sharpness",
                    "specFlatness" = "spectral flatness",
                    "specFlux" = "spectral flux",
                    "specRolloff" = "spectral rolloff",
                    "specSlope" = "spectral slope",
                    "1-1" = "touch zone (1,1)",
                    "2-1" = "touch zone (2,1)",
                    "1-2" = "touch zone (1,2)",
                    "2-2" = "touch zone (2,2)",
                    "1-3" = "touch zone (1,3)",
                    "2-3" = "touch zone (3,3)",
                    "accel.mean.x" = "mean accelerometer x position",
                    "accel.mean.y" = "mean accelerometer y position",
                    "accel.mean.z" = "mean accelerometer z position",
                    "accel.sd.x" = "s.d. accelerometer x position",
                    "accel.sd.x" = "s.d. accelerometer y position",
                    "accel.sd.z" = "s.d. accelerometer z position",
                    "accel.rms" = "accelerometer motion energy (RMS)")

pluralise <- function(object.name.str, number){
  ifelse(number == 1, object.name.str, paste(object.name.str, "es", sep = ""))
}

facet.labeller <- function(variable, value) {
  switch(variable,
         g = paste("Group", value),
         s = paste("Session", value),
         j = paste("Jam", value),
         sj.idx = paste("S: ", (value %/% 4) + 1, " J: ", (value %% 4) + 1, sep = ""),
         name = as.character(value),
         touch.count = paste(value, pluralise("touch", value)),
         delta.t = paste(value, "s window", sep = ""),
         type = pretty.name[as.character(value)],
         as.character(value))
}

thesis.fig.device <- function(fpath, geometry, type = "pdf"){
  golden.ratio <- 1.61803399
  fig.width <- 8
  fig.dim <- fig.width * switch(geometry,
                                fullwidth = c(1, 1/golden.ratio),
                                halfwidth = c(0.5, 1/golden.ratio),
                                tallhalfwidth = c(0.4, 1.1),
                                halfsquare = c(0.5, 0.5),
                                fullsquare = c(1, 1),
                                fullpage = c(0.9, 1.25),
                                three2page = c(1, 0.4),
                                keynote = c(0.75, 0.75/golden.ratio))
  quartz(width = fig.dim[1],
         height = fig.dim[2],
         pointsize = 12,
         type = type,
         file = fpath,
         dpi = 300,
         bg = "white")
}
