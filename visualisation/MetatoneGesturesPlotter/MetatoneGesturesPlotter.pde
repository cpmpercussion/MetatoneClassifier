boolean DEFAULT_INPUT = false; // change to true to use "input.csv"
boolean SAVING_FRAMES = true; // change to true to save tga frames.
boolean OUTPUT_MOVIE = false; // true to convert movie with ffmpeg after all frames processed.

String eventsFileName = "-events.csv";
String gestureFileName = "-gestures.csv";
String transitionsFileName = "-transitions.csv";
boolean gesturePlottingStarted = false;

int year = 0;
int month = 0;
int day = 0;
int startHour = 0;
int startMinute = 0;
int startSecond = 0;

int endFrames = 80;
int margins = 50;
int numberGestures = 9;
int firstFrame = 0;

// Drawing Objects
PGraphics gesturePlot;
PFont f;
int drawingPositionNumber;

Table eventTable;
Table gestureTable;
Table transitionTable;
float currentFrameTime;
float startTotalSeconds;
float performanceLengthSeconds;
float gestureLineDelta;
int plotWidth;
float widthPixelsPerSecond;
TableRow currentGestureRow;
TableRow previousGestureRow;

void fileSelected(File selection) {
  if (selection == null) {
    println("Window was closed or the user hit cancel.");
    exit();
  } else {
    println("User selected " + selection.getAbsolutePath());
    prepareToDrawPerformance(selection.getAbsolutePath());
  }
}

// Starts up the drawing process given a path to a .log file.
void prepareToDrawPerformance(String filePath) {
  println("Initialising the performance files...");
  String fileDirectory = filePath.replace(".log", "");
  eventTable = loadTable(fileDirectory + eventsFileName, "header");
  gestureTable = loadTable(fileDirectory + gestureFileName, "header");
  transitionTable = loadTable(fileDirectory + transitionsFileName, "header");
  String firstGestureTime = gestureTable.getRow(0).getString("time");
  parsePerformanceDate(firstGestureTime);

  startTotalSeconds = (float) startHour * 3600 + startMinute * 60 + startSecond;
  gestureLineDelta = (height-(2 * margins) ) / (float) numberGestures;
  performanceLengthSeconds = parseDateToSeconds(
    gestureTable.getRow(gestureTable.getRowCount()-1).getString("time")) - startTotalSeconds;
  plotWidth = width-(2*margins);
  widthPixelsPerSecond = plotWidth / performanceLengthSeconds;
  currentFrameTime = 0.0;

  println("Initialised - Plotting Performance.");
  println("Performance length is: " + performanceLengthSeconds + " seconds.");
  drawGesturePlot();
  gesturePlottingStarted = true;
  firstFrame = frameCount;
}

void setup() {
  size(1920, 540, P2D);
  //noLoop();

  // Load file from default input or from a selection dialogue.
  if (DEFAULT_INPUT) {
    println("Default input file: input.csv");
    prepareToDrawPerformance("input.csv");
  } else {
    println("Asking for user selected file.");
    selectInput("Select a .log to process:", "fileSelected");
  }

  gesturePlot = createGraphics(1920, 540);
  f = loadFont("HelveticaNeue-18.vlw");
  textFont(f, 18);
  gesturePlot.textFont(f, 18);
}

// drawGesturePlot actually creates the plot that will be used in the animation.
void drawGesturePlot() {
  gesturePlot.beginDraw();
  gesturePlot.background(0);

  // Graph paper for Plot
  gesturePlot.stroke(200);
  gesturePlot.strokeWeight(1);
  gesturePlot.noFill();
  gesturePlot.rect(margins, margins, width-(2 * margins), height-(2 *margins));
  for (int i = 0; i<numberGestures; i++) {
    gesturePlot.line(margins, margins + (i*gestureLineDelta), width - margins, margins + (i*gestureLineDelta));
  }

  // Tick marks and scale
  for (int i=0; i<performanceLengthSeconds; i++) {
    // tick marks every 60 seconds
    if (i % 60 == 0) {
      gesturePlot.line(margins + (i *widthPixelsPerSecond), margins, margins + (i *widthPixelsPerSecond), height-margins);
      String timeLabel = timeStringFromSeconds(i);
      timeLabel = timeLabel.substring(0, 8);
      gesturePlot.text(timeLabel, margins + (i * widthPixelsPerSecond) - 30, height - 30);
    }
  }

  // Plotting the Events Table
  for (TableRow row : eventTable.rows()) {
    gesturePlot.colorMode(RGB);
    gesturePlot.stroke(178, 22, 57, 180);
    gesturePlot.strokeWeight(4);
    float eventTime = parseDateToSeconds(row.getString("time")) - startTotalSeconds;
    gesturePlot.line(margins + (eventTime * widthPixelsPerSecond), margins-5, 
      margins + (eventTime * widthPixelsPerSecond), height-(margins-5));
  }

  // Plotting the Gesture Table
  currentGestureRow = gestureTable.getRow(0);
  previousGestureRow = gestureTable.getRow(0);
  gesturePlot.strokeWeight(1);

  for (TableRow row : gestureTable.rows()) {
    currentGestureRow = row;
    float rowTime = parseDateToSeconds(currentGestureRow.getString("time")) - startTotalSeconds;
    float previousRowTime = parseDateToSeconds(previousGestureRow.getString("time")) - startTotalSeconds;

    for (String column : gestureTable.getColumnTitles()) {
      if (!column.equals("time")) {
        int currentGestureLevel = currentGestureRow.getInt(column);
        int previousGestureLevel = previousGestureRow.getInt(column);
        gesturePlot.colorMode(HSB);
        int[] colour = getColourForName(column);
        gesturePlot.fill(colour[0], colour[1], colour[2], 180);
        gesturePlot.stroke(colour[0], colour[1], colour[2]);
        // New gesture ellipse
        gesturePlot.ellipse(margins + (rowTime * widthPixelsPerSecond), 
          height - margins - (currentGestureLevel * gestureLineDelta), 5, 5);
        // Gesture connecting line.
        gesturePlot.line(margins + (rowTime * widthPixelsPerSecond), 
          height - margins - (currentGestureLevel * gestureLineDelta), 
          margins + (previousRowTime * widthPixelsPerSecond), 
          height - margins - (previousGestureLevel * gestureLineDelta));
        gesturePlot.colorMode(RGB);
      }
    }
    previousGestureRow = gestureTable.matchRow(row.getString("time"), "time");
  }

  gesturePlot.endDraw();
}

void drawFrameTime(float currentFrameTime) {
  background(0);

  // Draw the gesturePlot offscreen image
  image(gesturePlot, 0, 0);

  // Draw Transport Locator
  stroke(255, 0, 0, 180);
  strokeWeight(5);
  line(margins + (currentFrameTime * widthPixelsPerSecond), margins-10, 
    margins + (currentFrameTime * widthPixelsPerSecond), height-(margins-10));

  // Write Plot Title
  //stroke(200);
  //strokeWeight(1);
  //fill(200);
  //text("Gesture Plot with \"New Idea\" Events", 10, 20);

  // Write timestamp String on the screen.
  stroke(200);
  strokeWeight(1);
  fill(200);
  text(makeDateString(currentFrameTime), 10, height - 10);
}

// Draw assembles the gesture plot, time stamp, and transport locator together for each 25th of a second.
void draw() {
  currentFrameTime = (frameCount - firstFrame) / 25.0; // Hard coded to 25 frames per second
  if (gesturePlottingStarted) {
    drawFrameTime(currentFrameTime);
    if (SAVING_FRAMES) {
      saveFrame("/Users/charles/Movies/framestga/######.tga");
    }
    if (currentFrameTime > performanceLengthSeconds + 1) {
      gesturePlottingStarted = false;
      if (OUTPUT_MOVIE) makeMovie();
      exit();
    }
  } else {
    background(0);
  }
}

void mouseReleased() {
  println("Framerate is: " + frameRate);
}

// 14 Different colours - should last a while.
int[] hues = {
  241, 170, 128, 71, 28, 227, 240, 113, 43, 14, 213, 142, 85, 43
};
int[] sats = {
  255, 255, 170, 170, 255, 255, 170, 170, 255, 255, 170, 255, 255, 170
};
int[] bris = {
  255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255
};
IntDict namesToColours = new IntDict();

// New colour method that just adds names to a dict and accesses preset colours.
int[] getColourForName(String name) {
  if (!namesToColours.hasKey(name)) {
    namesToColours.set(name, namesToColours.size());
  }
  int index = namesToColours.get(name) % hues.length;
  int[] colour = {
    hues[index], sats[index], bris[index]
  };
  return colour;
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
  String time = split(dateString, "T")[1];
  String[] timeParts = split(time, ":");
  String[] dateParts = split(date, "-");
  year = int(dateParts[0]);
  month = int(dateParts[1]);
  day = int(dateParts[2]);

  startHour = int(timeParts[0]);
  startMinute = int(timeParts[1]);
  startSecond = int(timeParts[2]);
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

String timeStringFromSeconds(float nowTime) {
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

  String minuteZero = "";
  if (newMinute < 10) minuteZero = "0";
  String secondZero = "";
  if (newSecond < 10) secondZero = "0";

  String timeString = newHour + ":" + minuteZero + newMinute + ":" + secondZero + newSecond + "." + nowHundredths;
  return timeString;
}

void makeMovie() {
  println("Going to try to make movie");
  String movieName = year + "-" + month + "-" + day + "T" + startHour + "-" + startMinute + "-" + startSecond + "-GesturePlot.mov";
  //String movieName = "TouchAnimationNew.mov";
  println("Filename will be: " + movieName);
  String inputDir = "/Users/charles/Movies/framestga/";
  String outputDir = "/Users/charles/Movies/processing-output/";
  String command = "/usr/local/bin/ffmpeg -f image2 -framerate 25 -i " + inputDir + "/%06d.tga -vcodec libx264 -r 25 -pix_fmt yuv420p -crf 16 " + outputDir + movieName;
  println(command);
  Process p;
  try {
    p = Runtime.getRuntime().exec(command);
    p.waitFor();
  } 
  catch(Exception e) {
    e.printStackTrace();
  }
  println("done encoding.");
  println("now removing tga files.");
  command = "rm -r " + inputDir;
  println(command);
  try {
    p = Runtime.getRuntime().exec(command);
    p.waitFor();
  } 
  catch(Exception e) {
    e.printStackTrace();
  }
  println("done.");
}