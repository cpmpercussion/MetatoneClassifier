##################
# audio analysis #
##################

library('tuneR')

get.audio.wav.path <- function(group, session, jam) {
  paste("/Users/ben/Code/iPhone-Apps/Viscotheque/data/experiment-2/video/group-",
        group, "/session-", session, "/audio/", group, "-", session, "-", jam, ".wav", sep = "")
}

# to construct

wav.list <- dlply(unique(id.df[,c("group", "session", "jam")]), .(group, session, jam), function(x) readWave(get.audio.wav.path(x$group, x$session, x$jam)),
                  .progress = "text")



## filter and downsample

# saving/reading from disk

save(wav.list, "RData/wav-data.RData")
load("RData/wav-list.RData")
