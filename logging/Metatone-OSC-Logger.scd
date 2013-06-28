// /metatone/acceleration
// /metatone/touch
// /metatone/switch
// /metatone/touch/ended
// /metatone/online
// /metatone/offline

( // Get Started
var logFilename = Date.getDate.format("MetatoneOSCLog-%Y%m%d-%Hh%M");
logFilename.post;
~logFile = File(Date.getDate.format("MetatoneOSCLog-%Y%m%d-%Hh%M"),"w");


~logMessage = {|msg,time,addr,recvPort|
	~logFile.write(time.asString + msg.asString + addr.asString + "\n");
	//msg.postln;
};


~startResponders = {
	~logFile = File(Date.getDate.format("MetatoneOSCLog-%Y%m%d-%Hh%M"),"w");
	OSCdef.newMatching(\metatonetouch, ~logMessage, '/metatone/touch', nil);
	OSCdef.newMatching(\metatonetouchended, ~logMessage, '/metatone/switch', nil);
	OSCdef.newMatching(\metatoneswitch, ~logMessage, '/metatone/touch/ended', nil);
	OSCdef.newMatching(\metatoneonline, ~logMessage, '/metatone/online', nil);
	OSCdef.newMatching(\metatoneoffline, ~logMessage, '/metatone/offline', nil);
	OSCdef.newMatching(\metatoneaccel, ~logMessage, '/metatone/acceleration', nil);
};

~cleanUp = {
	OSCdef.freeAll;
	~logFile.close;
};
)


(
~startResponders.value();

)


(
~cleanUp.value();

)




//OSCFunc.trace(true); // Turn posting on

//OSCFunc.trace(false); // Turn posting off