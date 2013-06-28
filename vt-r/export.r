# for Amir

export <- vt.filter.by.event(vtdata, "touch-position")
export$name <- as.numeric(export$name)
export$session <- as.numeric(export$session)
export$mode <- as.numeric(export$mode)
names(export) <- c("time", "uid", "gid", "mode", "x", "y")

write.csv(export, file = "fingertraces.csv", row.names = FALSE)

# for Aengus

library('plyr')

create.id.df.block <- function(id.string, num.rows) {
  gsj <- gsj.vector.from.id.string(id.string)
  print(gsj)
  data.frame(group = gsj[1],
             session = gsj[2],
             jam = gsj[3],
             name = name.from.id.string(id.string))[rep(1, times = num.rows),1:4]
}

df.for.export <- function(df.list) {
  ldply(names(df.list),
        function(id.string) {
          df <- df.list[[id.string]]
          cbind(create.id.df.block(id.string, dim(df)[1]),
                df)
        },
        .progress = "text")[,-6]
}

write.csv(df.for.export(filter.vt.list(df.list, type = "touch")),
          "export/rawtouch.Rdata",
          row.names = FALSE)

write.csv(df.for.export(filter.vt.list(df.list, type = "accel")),
          "export/rawaccel.Rdata",
          row.names = FALSE)

write.ts.for.export <- function(touch.ts.list, accel.ts.list, csv.filename) {
  if(length(touch.ts.list)!=length(accel.ts.list)) {
    print("Lists must be of equal length.")
    break
  }
  append.to.file <- function(df.to.append) {
    write.table(df.to.append,
                sep = ",",
                append = TRUE,
                csv.filename,
                row.names = FALSE,
                col.names = FALSE,
                qmethod = "double")
  }
  append.to.file(matrix(c("time",
                   colnames(touch.ts.list[[1]]),
                   colnames(accel.ts.list[[1]])),
                 nrow = 1))
  for (i in 1:length(touch.ts.list)) {
    ts <- ts.intersect(touch.ts.list[[i]], accel.ts.list[[i]])
    df <- cbind(create.id.df.block(names(touch.ts.list)[i], dim(ts)[1]),
                as.data.frame(cbind(time(ts),ts)))
    inst.col <- 7
    df[[inst.col]] <- as.factor(df[[inst.col]]) # the instrument column = 3
    levels(df[[inst.col]]) <- c("sampler", "synth")
    append.to.file(df)
  }
}

write.ts.for.export(filter.vt.list(ts.list, type = "touch"),
                    filter.vt.list(ts.list, type = "accel"),
                    "aengus/processed.csv")

## for Jin

export.df <- rqa.df[c("metric", "delta.t", "feature.subset", "name", "g", "s", "j", "type", "determinism", "avg.diag.length", "laminarity", "trap.time")]
names(export.df) <- c("metric", "delta.t", "featureSubset", "musician", "group", "session", "jam", "rpType", "determinism", "avgDiagonalLength", "laminarity", "trappingTime")

write.csv(export.df,
          "export/rqa.csv",
          row.names = FALSE)

export.df <- synth.rqa.df[c("metric", "delta.t", "feature.subset", "name", "g", "s", "j", "type", "determinism", "avg.diag.length", "laminarity", "trap.time")]
names(export.df) <- c("metric", "delta.t", "featureSubset", "musician", "group", "session", "jam", "rpType", "determinism", "avgDiagonalLength", "laminarity", "trappingTime")

write.csv(export.df,
          "export/synth-rqa.csv",
          row.names = FALSE)

export.df <- feature.df[feature.subset("id") | feature.subset("accel")][-c(1,7:8)]
names(export.df)[1:4] <- c("musician", "group", "session", "jam")

write.csv(export.df,
          "export/accelerometer.csv",
          row.names = FALSE)

export.df <- feature.df[!duplicated(feature.df[c("g", "s", "j", "time")]), c("g", "s", "j", "time", "loudness")]
names(export.df)[1:3] <- c("group", "session", "jam")

write.csv(export.df,
          "export/loudness.csv",
          row.names = FALSE)
