library('plyr')
library('coin')
library('multcomp')

## adapted from http://www.r-statistics.com/2010/02/post-hoc-analysis-for-friedmans-test-r-code/

rqa.stat.names <- names(rqa.df)[match("eps.value", names(rqa.df)):dim(rqa.df)[2]]

session.rqa.df <- ddply(melt(rqa.df,
                             measure.vars = rqa.stat.names,
                             variable.name = "rqa.stat"),
                        .(metric, delta.t, name, g, s, feature.subset, type, rqa.stat),
                        summarize,
                        value = mean(value))

friedman.test.with.post.hoc <- function(y.name,
                                        x.name,
                                        block.name,
                                        data,
                                        signif.p){
  data[[x.name]] <- factor(data[[x.name]])
  data[[block.name]] <- factor(data[[block.name]])
  sym.test <- symmetry_test(as.formula(paste(y.name, "~", x.name, "|", block.name)),
                            data = data,	### all pairwise comparisons	
                            teststat = "max",
                            xtrafo = function(y.data) {
                              trafo(y.data,
                                    factor_trafo = function(x){
                                      model.matrix(~ x - 1) %*% t(contrMat(table(x), "Tukey"))
                                    })
                            },
                            ytrafo = function(y.data){
                              trafo(y.data,
                                    numeric_trafo = rank,
                                    block = data[,block.name])
                            })
  if(pvalue(sym.test) < signif.p){
    list(friedman = sym.test, post.hoc.p.values = pvalue(sym.test, method = "single-step"))
  }else{
    list(friedman = sym.test)
  }
}

make.friedman.df <- function(session.rqa.df, group.by, signif.p){
  ddply(session.rqa.df,
        .(metric, delta.t, feature.subset, type, rqa.stat),
        function(data.df){
          ft <- friedman.test.with.post.hoc("value",
                                            group.by,
                                            list(g = "s", s = "g")[[group.by]],
                                            data.df,
                                            signif.p)
          if(length(ft) == 1){
            data.frame()
          }else{
            result <- data.frame(ldply(strsplit(row.names(ft$post.hoc.p.values), " "),
                                       function(x) as.numeric(x[c(3,1)])),
                                 p.value = ft$post.hoc.p.values[,1])
            names(result)[1:2] <- sapply(1:2, function(x) paste(group.by, x, sep = ""))
            result
          }
        })
}

friedman.df <- make.friedman.df(session.rqa.df, "g", 0.05)
