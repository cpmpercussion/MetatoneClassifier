# points of 'flow', as reported in discussion groups

video.offset <- list(7*60+50,5*60+18,4*60+53) # times on each tape when the performance started

flow.points <- mapply(function(x,y,z) x - (y - z),
	list(
	c(7*60+29,10*60+15,12*60+26,16*60+20), # session 1
	c(10*60+2,10*60+37,11*60+14,13*60+47,14*60+51,16*60+15,18*60+36,20*60+22,21*60+47), # session 2
	c(4*60+58,7*60+20,9*60+7,11*60,13*60+26,14*60+33,14*60+55,17*60+31,18*60+53)), # session 3
	video.offset,perf.start)
