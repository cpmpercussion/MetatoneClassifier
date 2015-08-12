// String touchFileName = "/Users/charles/Dropbox/Metatone/20140317/studyinbowls-performance/2014-03-17T18-09-46-MetatoneOSCLog-touches.csv";
//String touchFileName = "/Users/charles/Dropbox/Metatone/20140317/studyinbowls-rehearsal/2014-03-17T17-40-14-MetatoneOSCLog-touches.csv";

//String touchFileDir = "/Users/charles/Dropbox/Metatone/20140505/20-39-StudyInBowls/";
//String touchFileName = touchFileDir + "2014-05-05T20-39-43-MetatoneOSCLog-touches.csv";

boolean saving_frames = true;
boolean portrait = true;

int year = 1;
int month = 1;
int day = 1;

int endFrames = 80;
// Drawing Objects
PImage fader;
PFont f;
PGraphics pg;
int drawingPositionNumber;
Table touchTable;
float currentLineTime;
float currentFrameTime;
float startTotalSeconds;
int currentRow;
int totalRows;

void setup() {
  selectInput("Select a file to process:", "fileSelected");

  if (portrait) {
    size(768, 1024);
  } else {
    size(1024, 768);
  }

  pg = createGraphics( width, height );
  f = loadFont("HelveticaNeue-18.vlw");
  textFont(f, 18);
  pg.textFont(f, 18); 

  // Setup the fader.
  background(8);
  fader = get();
  background(0);
  fill(255);
  noLoop();
}

void fileSelected(File selection) {
  if (selection == null) {
    println("Window was closed or the user hit cancel.");
    exit();
  } else {
    println("User selected " + selection.getAbsolutePath());
    prepareToDrawPerformance(selection);
    loop();
  }
}

void prepareToDrawPerformance(File touchFile) {
  touchTable = loadTable(touchFile.getAbsolutePath(), "header");
  totalRows = touchTable.getRowCount();
  currentRow = 0;
  String firstTouchTime = touchTable.getRow(currentRow).getString("time");
  parsePerformanceDate(firstTouchTime);
  currentLineTime = (parseDateToSeconds(firstTouchTime) - 10);
  currentFrameTime = 0.0;
  drawingPositionNumber = 0;

  println("Ready to draw - total rows is: " + 
    totalRows + " and first line time is: " + 
    touchTable.getRow(currentRow).getString("time"));
  println("CurrentFrame: " + currentFrameTime + " currentLineTime: " + currentLineTime);
}

void draw() {
  background(255);
  currentFrameTime = frameCount / 25.0;// Hard coded to 25 frames per second

  pg.beginDraw();
  while ( (currentLineTime < currentFrameTime) && (currentRow < totalRows)) {
    drawTouch(touchTable.getRow(currentRow));
    currentRow++;
    if (currentRow < totalRows) {
      currentLineTime = (parseDateToSeconds(
      touchTable.getRow(currentRow).getString("time")) - startTotalSeconds);
    } else {
      println("End of file.");
      break;
    }
  }

  // End frames counter
  if (currentRow >= totalRows) {
    if (endFrames > 0) {
      println("Drawing end frame...");
      endFrames--;
    } else {
      noLoop();
      exit();
    }
  }

  // fade towards white
  pg.blend(fader, 0, 0, width, height, 0, 0, width, height, SUBTRACT);
  pg.endDraw();
  image(pg, 0, 0);  
  fill(255);

  // Write timestamp String on the screen.
  text(makeDateString(currentFrameTime), 10, height - 10);

  if (saving_frames) {
    saveFrame("/Users/charles/Movies/framestga/######.tga");
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
  int[] colour = { 
    hueNumber, 255, 255
  };
  return colour;
}

void drawTouch(TableRow row) {
  int[] colour = getColourForName(row.getString("device_id"));
  pg.stroke(255, 0);
  pg.colorMode(HSB);
  pg.fill(colour[0], colour[1], colour[2]);
  pg.ellipse(row.getFloat("x_pos"), row.getFloat("y_pos"), 20, 20);
  pg.colorMode(RGB);
}

void drawNonTouch(String[] parts) {
  int[] colour = getColourForName(parts[1]);
  pg.stroke(255, 0.0);
  pg.colorMode(HSB);
  pg.fill(colour[0], colour[1], colour[2]);
  String messageString = parts[2] + " ";
  if (parts.length == 6) {
    messageString += parts[4] + " " + parts[5];
  }
  pg.text(messageString, 10, (drawingPositionNumber * 15) + 15);
  drawingPositionNumber = (drawingPositionNumber + 1) % 5;
  pg.colorMode(RGB);
}


///////////////////////////////////////
//                                   //
// dateString to seconds             //
//                                   //
///////////////////////////////////////

Float parseDateToSeconds(String dateString) {
  String time = split(dateString, "T")[1];
  String[] timeParts = split(time, ":");
  Float seconds = (Float.parseFloat(timeParts[0]) * 3600) 
    + (Float.parseFloat(timeParts[1]) * 60 )
      + Float.parseFloat(timeParts[2]);
  return seconds;
}

void parsePerformanceDate(String dateString) {
  String date = split(dateString, "T")[0];
  String[] dateParts = split(date, "-");
  year = int(dateParts[0]);
  month = int(dateParts[1]);
  day = int(dateParts[2]);
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


/////
//
// Framerate method
//
/////

void mouseReleased() {
  println("Framerate is: " + frameRate);
}

