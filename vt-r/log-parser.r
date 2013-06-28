# for parallel execution with foreach and plyr

library('plyr')
library('foreach')
library('doMC')
registerDoMC(cores=4)

source("vt-header.r")

##########################
# generate paths & names #
##########################

viscotheque.dir <- "/Users/ben/Projects/Viscotheque"
log.dir <- paste(viscotheque.dir, "data/ex2/log", sep = "/")
initial.names <- c("time", "name", "type", "subtype", "touch.count", "touch.ids", "x1", "y1", "x2", "y2", "x3", "y3")

log.paths <- list.files(path = log.dir, recursive = FALSE)
log.paths <- log.paths[grepl("log", log.paths)]
log.paths <- sapply(log.paths, function (path) paste(log.dir, path, sep = "/"))
names(log.paths) <- NULL

# colour data

colourmap.df <- read.csv(paste(viscotheque.dir,  "data/ex2/csv/participant-colours.csv", sep = "/"),
                      header = FALSE,
                      col.names = c("g", "s", "j", "name", "colour"),
                      stringsAsFactors = TRUE)
                        
colourmap.df$name <- sapply(colourmap.df$name, function(x) get.anon.name(get.unique.name(x)))
colourmap.df$name <- as.data.frame(llply(colourmap.df, factor))

get.participant.colour <- function(name, group, session, jam) {
  colourmap.df$colour[colourmap.df$name == name & rowSums(matrix(rep(c(group, session, jam), dim(colourmap.df)[1]), ncol = 3, byrow = TRUE) == colourmap.df[,1:3]) == 3]
}

# engagement likert data

engagement.df <- read.csv(paste(viscotheque.dir, "data/ex2/csv/engagement-likert-responses.csv", sep = "/"),
                      header = FALSE,
                      col.names = c("g", "s", "j", "name", "object", "engagement"),
                      stringsAsFactors = TRUE)
                        
engagement.df$name <- sapply(engagement.df$name, function(x) get.anon.name(get.unique.name(x)))
engagement.df$object <- sapply(engagement.df$object, function(x) get.anon.name(get.unique.name(x)))
engagement.df <- as.data.frame(llply(engagement.df, factor))
engagement.df$engagement <- as.numeric(as.character(engagement.df$engagement))

############################
# id.string-based indexing #
############################

gsj.as.string <- function(group, session, jam) {
  paste(group, session, jam, sep = "-")
}

create.id.string <- function(group, session, jam, name, type) {
  paste(group, session, jam, type, name, type, sep = "-")
}

gsj.string.from.id.string <- function(id.string) {
  do.call(paste, as.list(c(strsplit(id.string, "-")[[1]][1:3], sep = "-")))
}

gsj.vector.from.id.string <- function(id.string) {
  as.numeric(strsplit(id.string, "-")[[1]][1:3])
}

id.df.row.from.id.string <- function(id.string) {
  row <- as.list(strsplit(id.string, "-")[[1]])
  names(row) <- c("g", "s", "j", "name", "type")
  as.data.frame(row)
}

name.from.id.string <- function(id.string) {
  strsplit(id.string, "-")[[1]][4]
}

type.from.id.string <- function(id.string) {
  strsplit(id.string, "-")[[1]][5]
}

# filtering

filter.vt.list <- function(data.list,
                           group = 1:4,
                           session = 1:4,
                           jam = 1:4,
                           name = NULL,
                           type = c("touch", "accel")) {
  session.ids <- Filter(function(id.string)
                        {
                          gsj <- gsj.vector.from.id.string(id.string)
                          if(is.null(name)) name <- unique(namemap.df$anon.name)
                          return(gsj[1] %in% group &&
                                 gsj[2] %in% session &&
                                 gsj[3] %in% jam &&
                                 name.from.id.string(id.string) %in% name &&
                                 type.from.id.string(id.string) %in% type)
                        },
                        names(data.list))
  data.list[session.ids]
}

filter.idx.vector <- function(df,
                              group = 1:4,
                              session = 1:4,
                              jam = 1:4,
                              name = NULL) {
  index.vector <- df$g %in% group & df$s %in% session & df$j %in% jam
  if(!is.null(df$name)) {
      if(is.null(name)) name <- unique(namemap.df$anon.name)
      index.vector <- index.vector & df$name %in% name
    }
  index.vector
}

filter.vt.df <- function(df,
                         group = 1:4,
                         session = 1:4,
                         jam = 1:4,
                         name = NULL) {
  index.vector <- df$g %in% group & df$s %in% session & df$j %in% jam
  if(!is.null(df$name)) {
      if(is.null(name)) name <- unique(namemap.df$anon.name)
      index.vector <- index.vector & df$name %in% name
    }
  df[index.vector,]
}

########################
# read raw data into R #
########################

# data frames #

filter.raw.log.accel <- function(log) {
  df <- log[log[,3]=="accel",c(1:3,5:7)]
  names(df) <- c("time", "name", "type", "accel.x", "accel.y", "accel.z")
  df$name <- factor(sapply(df$name, function(x) get.anon.name(get.unique.name(x))))
  df$type <- factor(df$type)
  df$time <- df$time - min(df$time)
  df <- df[order(df$time),]
  df
}

filter.raw.log.touch <- function(log) {
  touch.only <- log[log[,3]=="touch",]
  df <- data.frame(time = numeric(0),
                   name = character(0),
                   type = character(0),
                   event = character(0),
                   touch.count = numeric(0),
                   x1 = numeric(0),
                   y1 = numeric(0),
                   x2 = numeric(0),
                   y2 = numeric(0),
                   x3 = numeric(0),
                   y3 = numeric(0),
                   x4 = numeric(0),
                   y4 = numeric(0))
  for (num.touches in 0:4) {
    subset <- touch.only[touch.only[,5]==num.touches,c(1:5,seq(from = 6 + num.touches, by = 1, length.out = 8))]
    names(subset) <- c("time", "name", "type", "event", "touch.count", "x1", "y1", "x2", "y2", "x3", "y3", "x4", "y4")
    df <- rbind(subset, df)
  }
  df$name <- factor(sapply(df$name, function(x) get.anon.name(get.unique.name(x))))
  df$type <- factor(df$type)
  df$event <- factor(df$event)
  df$time <- df$time - min(df$time)
  df <- df[order(df$time),]
  df
}

# for reading in all log files into 'df.list' list

make.df.list <- function(path.list) {
  processed.logs <- llply(path.list,
                          function(path) {
                            log.raw <- read.csv(path,
                                                header = FALSE,
                                                col.names = as.character(1:17),
                                                stringsAsFactors = FALSE,
                                                fill = TRUE)
                            list(touch = filter.raw.log.touch(log.raw),
                                 accel = filter.raw.log.accel(log.raw))
                          },
                          .progress = "text",
                          .parallel = TRUE)
  names(processed.logs) <- sapply(path.list, function(str) substring(str, 46, 50))
  processed.logs
}

df.list <- make.df.list(log.paths)

# generate ALL id strings (irrelevant ones get filtered out in the flattening process

generate.id.strings <- function(gsj.strings, namemap.df, types = c("touch", "accel")) {
  candidate.id.strings <- apply(expand.grid(gsj.strings,
                                            namemap.df$name,
                                            types,
                                            stringsAsFactors = FALSE),
                                1,
                                function(row) do.call(paste, c(as.list(row), sep = "-"))
                                )
  candidate.id.strings
}

# flatten list (based on id strings)

flatten.df.list <- function(df.list) {
  flattened.list <- list()
  for (id.string in generate.id.strings(names(df.list), namemap.df)) {
    result <- df.list[[gsj.string.from.id.string(id.string)]][[type.from.id.string(id.string)]]
    flattened.list[[id.string]] <- result[result$name==name.from.id.string(id.string),]
  }
  Filter(function(df) {
    dim(df)[1] != 0
  },
         flattened.list)
}

df.list <- flatten.df.list(df.list) # overwrite df list with flattened list
id.strings <- names(df.list)

# add delta.t column

add.delta.t <- function(df.list) {
  llply(df.list,
        function(df) {
          if(is.null(df$touch.count)) { # only work on touch data frames
            df
          }else{
            df$delta.t <- c(diff(df$time), 0)
            df[,c("name", "type", "event", "time", "delta.t", "touch.count", "x1", "y1", "x2", "y2", "x3", "y3", "x4", "y4")]
          }
        },
        .progress = "text",
        .parallel = TRUE)
}

df.list <- add.delta.t(df.list)

# add which-instrument column

instrument.df <- read.csv(paste(viscotheque.dir, "data/ex2/csv/starting-interfaces.csv", sep = "/"),
                      header = FALSE,
                      col.names = c("g", "s", "j", "name", "initial.instrument"),
                      stringsAsFactors = TRUE)

instrument.df$name <- sapply(instrument.df$name, function(x) get.anon.name(get.unique.name(x)))
instrument.df <- as.data.frame(llply(instrument.df, factor))

# add column about instrument type to data frame

create.instrument.column <- function(touch.counts, init.inst, inst.options) {
  # determine where the 4-finger touches are
  four.touches <- touch.counts==4
  # calculate the difference between successive 4-touch onsets
  onset.intervals <- diff((1:length(touch.counts))[c(TRUE,four.touches[-1] & !(four.touches[-length(four.touches)]))])
  onset.intervals <- c(onset.intervals, length(touch.counts) - sum(onset.intervals))
  factor(rep(rep(unique(c(as.character(init.inst),
                          inst.options)),
                 length.out = length(onset.intervals)),
             onset.intervals))
}

add.instrument.column.to.df <- function(df.list, instrument.df) {
  result <- llply(names(df.list),
                  function(id.string) {
                    indiv.df <-df.list[[id.string]]
                    indiv.df$instrument <- create.instrument.column(indiv.df$touch.count,
                                                                    merge(instrument.df[,1:5], id.df.row.from.id.string(id.string))[1,5],
                                                                    levels(instrument.df[,5]))
                    indiv.df[,c(1:5,15,6:14)] # rearrange cols
                  },
                  .progress = "text",
                  .parallel = TRUE)
  names(result) <- names(df.list)
  result
}

df.list <- c(add.instrument.column.to.df(filter.vt.list(df.list, type = "touch"), instrument.df), filter.vt.list(df.list, type = "accel"))

get.sj.idx <- function(gsj.vec) {
  sum((gsj.vec[2:3]-1)*4^(1:0))
}

make.touch.df <- function(df.list) {
  adply(names(df.list),
        1,
        function(id.string) {
          gsj.vec <- gsj.vector.from.id.string(id.string)
          id.df <- data.frame(as.list(c(gsj.vector.from.id.string(id.string),get.sj.idx(gsj.vec))))
          names(id.df) <- c("g", "s", "j", "sj.idx")
          cbind(id.df, #[rep(1,dim(df.list[[id.string]])[1]),]
                df.list[[id.string]])
        },
        .progress = "text",
        .parallel = FALSE)[-1]
}

touch.df <- make.touch.df(filter.vt.list(df.list, type = "touch"))

make.flat.touch.df <- function(touch.df) {
  touch.down.df <- touch.df[touch.df$touch.count!=0,]
  x1.offset <- match("x1", names(touch.down.df))
  x.index <- x1.offset + do.call(c, lapply(touch.down.df$touch.count, function(x) 2*((1:x)-1)))
  row.index <- rep(1:dim(touch.down.df)[1],touch.down.df$touch.count)

  result <- touch.down.df[row.index,c("g",
                                      "s",
                                      "j",
                                      "sj.idx",
                                      "name",
                                      "time",
                                      "delta.t",
                                      "instrument",
                                      "touch.count")]
  result$x <- as.numeric(touch.down.df[cbind(row.index,x.index)])
  result$y <- as.numeric(touch.down.df[cbind(row.index,x.index+1)])
  result
}

flat.touch.df <- make.flat.touch.df(touch.df)

# make accel df

make.accel.df <- function(df.list) {
  adply(names(df.list),
        1,
        function(id.string) {
          gsj.vec <- gsj.vector.from.id.string(id.string)
          id.df <- data.frame(as.list(c(gsj.vector.from.id.string(id.string),get.sj.idx(gsj.vec))))
          names(id.df) <- c("g", "s", "j", "sj.idx")
          cbind(id.df,
                df.list[[id.string]])
        },
        .progress = "text",
        .parallel = FALSE)[-1]
}

accel.df <- make.accel.df(filter.vt.list(df.list, type = "accel"))

# for convenience, put all id data into a data frame

make.id.df <- function(id.string.list) {
  id.df <- ldply(id.string.list,
                  function(x) {
                    gsj.vec <- gsj.vector.from.id.string(x)
                    c(x,
                      gsj.vec,
                      get.sj.idx(gsj.vec),
                      name.from.id.string(x),
                      type.from.id.string(x))
                  })
  names(id.df) <- c("id.string",
                    "g",
                    "s",
                    "j",
                    "sj.idx",
                    "name",
                    "type")
  id.df$id.string <- factor(id.df$id.string)
  id.df$g <- as.numeric(id.df$g)
  id.df$s <- as.numeric(id.df$s)
  id.df$j <- as.numeric(id.df$j)
  id.df$sj.idx <- as.numeric(id.df$sj.idx)
  id.df$name <- factor(id.df$name, levels = unique(namemap.df$anon.name), ordered = TRUE)
  id.df$type <- factor(id.df$type)
  id.df
}

id.df <- make.id.df(names(df.list))

# time series #

make.ts.list <- function(df.list, delta.t = 1e-2) {
  make.touch.ts <- function(touch.data.frame) {
    raw.ts <- touch.data.frame[,c("time", "event", "touch.count", "instrument", "x1", "y1", "x2", "y2", "x3", "y3", "x4", "y4")]

    raw.ts$mean.x <- rowMeans(raw.ts[,c("x1","x2","x3")], na.rm = TRUE)
    raw.ts$mean.y <- rowMeans(raw.ts[,c("y1","y2","y3")], na.rm = TRUE)
    raw.ts$sd.x <- apply(raw.ts[,c("x1","x2","x3")], 1, sd, na.rm = TRUE)
    raw.ts$sd.y <- apply(raw.ts[,c("y1","y2","y3")], 1, sd, na.rm = TRUE)

    # regularisation
    
    raw.ts$time <- floor(raw.ts$time / delta.t) * delta.t
    idx <- rep(seq(from = 1, length.out = length(raw.ts$time)), c(diff(raw.ts$time) / delta.t, 1))
    raw.ts <- raw.ts[idx,]
    
#    raw.ts[is.na(raw.ts)] <- 0 # for changing NAs to zeroes

#     raw.ts[c("x1", "y1", "x2", "y2", "x3", "y3", "x4", "y4")] <- vector("list", 8)

    ts(raw.ts[,c("touch.count", "instrument", "mean.x", "mean.y", "sd.x", "sd.y", "x1", "y1", "x2", "y2", "x3", "y3", "x4", "y4")], start = 0, deltat = delta.t)
  }
  make.accel.ts <- function(accel.data.frame) {
    raw.ts <- accel.data.frame[,c("time", "accel.x", "accel.y", "accel.z")]
    
    # regularisation
    
    raw.ts$time <- floor(raw.ts$time / delta.t) * delta.t
    idx <- rep(seq(from = 1, length.out = length(raw.ts$time)), c(diff(raw.ts$time) / delta.t, 1))
    raw.ts <- raw.ts[idx,]
    
    ts(raw.ts[,c("accel.x", "accel.y", "accel.z")], start = 0, deltat = delta.t)
  }
  llply(df.list,
        function(data.df) {
          if("x1" %in% names(data.df)) make.touch.ts(data.df) else make.accel.ts(data.df)
        },
        .progress = "text",
        .parallel = TRUE)
}

ts.list <- make.ts.list(df.list, delta.t = 1e-2)
