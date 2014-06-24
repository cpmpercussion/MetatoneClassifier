String fileDirectory = "/Users/charles/Dropbox/Metatone/20140317/studyinbowls-rehearsal/";
String eventsFileName = "2014-03-17T17-40-14-MetatoneOSCLog-events.csv";
String gestureFileName = "2014-03-17T17-40-14-MetatoneOSCLog-gestures.csv";
String transitionsFileName = "2014-03-17T17-40-14-MetatoneOSCLog-transitions.csv";

boolean saving_frames = false;

int year = 2014;
int month = 3;
int day = 17;
int startHour = 17;
int startMinute = 40;
int startSecond = 14;

int endFrames = 80;

// Drawing Objects
PImage fader;
PFont f;
int drawingPositionNumber;

Table eventTable;
Table gestureTable;
Table transitionTable;

Float currentFrameTime;

Float startTotalSeconds;
Float performanceLengthSeconds;

void setup() {
  size(1920,540);
  f = loadFont("HelveticaNeue-18.vlw");
  textFont(f,18);

  eventTable = loadTable(fileDirectory + eventsFileName,"header");
  gestureTable = loadTable(fileDirectory + gestureFileName,"header");
  transitionTable = loadTable(fileDirectory + transitionsFileName,"header");

  startTotalSeconds = (float) startHour * 3600 + startMinute * 60 + startSecond;
  performanceLengthSeconds = parseDateToSeconds(
  	eventTable.getRow(eventTable.getRowCount()-1).getString("time")) - startTotalSeconds;

  currentFrameTime = 0.0;

  println(startTotalSeconds);
  println(performanceLengthSeconds);

}
 
void draw() {
  background(0);
  currentFrameTime = frameCount / 25.0;// Hard coded to 25 frames per second

  stroke(200);
  noFill();
  // Gestures
  rect(20,20,width-40,150);
  // Transitions
  rect(20,190,width-40,150);
  // States
  rect(20,360,width-40,150);


  // Write timestamp String on the screen.
  text(makeDateString(currentFrameTime),10,height - 10);
  
  if(saving_frames) {
    saveFrame("/Users/charles/Movies/framestga/metatone-######.tga");
  }
}

///////////////////////////////////////
//                                   //
// drawing Helper functions          //
//                                   //
///////////////////////////////////////

int[] getColourForName(String name) {
  byte[] bytes = name.getBytes();
  int hueNumber = 0;
  for (int i = 0; i < bytes.length; i++) {
    hueNumber += bytes[i];
  }
  hueNumber = hueNumber % 256; 
  int[] colour = { hueNumber, 255 , 255 };
  return colour;
}

///////////////////////////////////////
//                                   //
// dateString to seconds             //
//                                   //
///////////////////////////////////////

Float parseDateToSeconds(String dateString) {
  String time = split(dateString,"T")[1];
  String[] timeParts = split(time,":");
  Float seconds = (Float.parseFloat(timeParts[0]) * 3600) 
    + (Float.parseFloat(timeParts[1]) * 60 )
    + Float.parseFloat(timeParts[2]);
  return seconds;
}

///////////////////////////////////////
//                                   //
// Time in seconds to text functions //
//                                   //
///////////////////////////////////////

String makeDateString(float nowTime) {
  int nowSeconds = floor(nowTime);
  int nowHundredths = floor((nowTime - nowSeconds) * 100);
  int addSeconds = nowSeconds % 60;
  int addMinutes = (nowSeconds - addSeconds) / 60;
  int newHour = startHour;
  int newMinute = startMinute;
  int newSecond = startSecond;

  newSecond += addSeconds;
  if (newSecond >= 60) {
    newSecond -= 60;
    newMinute += 1;
  }
  
  newMinute += addMinutes;
  if (newMinute >= 60) {
    newMinute -= 60;
    newHour += 1;
  }
  
  String monthZero = "";
  if (month < 10) monthZero = "0";
  String dayZero = "";
  if (day < 10) dayZero = "0";
  String minuteZero = "";
  if (newMinute < 10) minuteZero = "0";
  String secondZero = "";
  if (newSecond < 10) secondZero = "0";
  
  String dateString = year + "-" + monthZero + month + "-" + dayZero + day + "  " + newHour + ":" + 
    minuteZero + newMinute + ":" + secondZero + newSecond + "." + nowHundredths;
  return dateString;
}

String makeTimeString(float nowTime) {
  int nowSeconds = floor(nowTime);
  int nowHundredths = floor((nowTime - nowSeconds) * 100);
  String timeString = nowSeconds + "." + nowHundredths;
  return timeString;
}
