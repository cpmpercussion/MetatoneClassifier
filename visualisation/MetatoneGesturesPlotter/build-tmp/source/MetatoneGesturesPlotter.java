import processing.core.*; 
import processing.data.*; 
import processing.event.*; 
import processing.opengl.*; 

import java.util.HashMap; 
import java.util.ArrayList; 
import java.io.File; 
import java.io.BufferedReader; 
import java.io.PrintWriter; 
import java.io.InputStream; 
import java.io.OutputStream; 
import java.io.IOException; 

public class MetatoneGesturesPlotter extends PApplet {

// String fileDirectory = "/Users/charles/Dropbox/Metatone/20140317/studyinbowls-performance/2014-03-17T18-09-46-MetatoneOSCLog-";
// String fileDirectory = "/Users/charles/Dropbox/Metatone/20140317/metatoneset-performance/2014-03-17T18-30-57-MetatoneOSCLog-";
String fileDirectory = "/Users/charles/Dropbox/Metatone/20140505/20-39-StudyInBowls/2014-05-05T20-39-43-MetatoneOSCLog-";

// String fileDirectory = "/Users/charles/Dropbox/Metatone/20140317/studyinbowls-rehearsal/2014-03-17T17-40-14-MetatoneOSCLog-";
String eventsFileName = "events.csv";
String gestureFileName = "gestures.csv";
String transitionsFileName = "transitions.csv";

boolean saving_frames = true;

int year = 2014;
int month = 5;
int day = 5;
int startHour = 20;
int startMinute = 39;
int startSecond = 43;

int endFrames = 80;
int margins = 50;
int numberGestures = 9;


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

public void setup() {
  size(1920,540);
  gesturePlot = createGraphics(1920,540);
  f = loadFont("HelveticaNeue-18.vlw");
  textFont(f,18);
  gesturePlot.textFont(f,18);

  eventTable = loadTable(fileDirectory + eventsFileName,"header");
  gestureTable = loadTable(fileDirectory + gestureFileName,"header");
  transitionTable = loadTable(fileDirectory + transitionsFileName,"header");

  startTotalSeconds = (float) startHour * 3600 + startMinute * 60 + startSecond;
  gestureLineDelta = (height-(2 * margins) ) / (float) numberGestures;

  performanceLengthSeconds = parseDateToSeconds(
  	gestureTable.getRow(gestureTable.getRowCount()-1).getString("time")) - startTotalSeconds;
  plotWidth = width-(2*margins);
  widthPixelsPerSecond = plotWidth / performanceLengthSeconds;
  currentFrameTime = 0.0f;

  println("Initialised - Plotting Performance.");
  println("Performance length is: " + performanceLengthSeconds + " seconds.");
  drawGesturePlot();
}

public void drawGesturePlot() {
  gesturePlot.beginDraw();
  gesturePlot.background(0);

  // Graph paper for Plot
  gesturePlot.stroke(200);
  gesturePlot.strokeWeight(1);
  gesturePlot.noFill();
  gesturePlot.rect(margins,margins,width-(2 * margins),height-(2 *margins));
  for (int i = 0; i<numberGestures; i++) {
    gesturePlot.line(margins, margins + (i*gestureLineDelta), width - margins, margins + (i*gestureLineDelta)); 
  }

  // Tick marks and scale
  for (int i=0; i<performanceLengthSeconds; i++) {
    // tick marks every 60 seconds
    if (i % 60 == 0) {
      gesturePlot.line(margins + (i *widthPixelsPerSecond), margins, margins + (i *widthPixelsPerSecond), height-margins);
      String timeLabel = timeStringFromSeconds(i);
      timeLabel = timeLabel.substring(0,8);
      gesturePlot.text(timeLabel, margins + (i * widthPixelsPerSecond) - 30, height - 30);
    }
  }

    // Plotting the Events Table
  for (TableRow row : eventTable.rows()) {
    gesturePlot.colorMode(RGB);
    gesturePlot.stroke(178,22,57,180);
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
        gesturePlot.fill(colour[0],colour[1],colour[2],180);
        gesturePlot.stroke(colour[0],colour[1],colour[2]);
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
    previousGestureRow = gestureTable.matchRow(row.getString("time"),"time");
  }

  gesturePlot.endDraw();
}

public void draw() {
  background(0);
  currentFrameTime = frameCount / 25.0f;// Hard coded to 25 frames per second

  if (currentFrameTime > performanceLengthSeconds) {
    noLoop();
    exit();
  }

  // Draw the gesturePlot offscreen image
  image(gesturePlot,0,0);

  // Draw Transport Locator
  stroke(255, 0, 0,180);
  strokeWeight(5);
  line(margins + (currentFrameTime * widthPixelsPerSecond), margins-10, 
    margins + (currentFrameTime * widthPixelsPerSecond), height-(margins-10));

  // Write Plot Title
  stroke(200);
  strokeWeight(1);
  fill(200);
  text("Gesture Plot with \"New Idea\" Events",10,20);

  // Write timestamp String on the screen.
  stroke(200);
  strokeWeight(1);
  fill(200);
  text(makeDateString(currentFrameTime),10,height - 10); 
  
  if(saving_frames) {
    saveFrame("/Users/charles/Movies/framestga/######.tga");
  }
}

public void mouseReleased() {
  println("Framerate is: " + frameRate);
}

///////////////////////////////////////
//                                   //
// drawing Helper functions          //
//                                   //
///////////////////////////////////////

public int[] getColourForName(String name) {
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

public Float parseDateToSeconds(String dateString) {
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

public String makeDateString(float nowTime) {
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

public String makeTimeString(float nowTime) {
  int nowSeconds = floor(nowTime);
  int nowHundredths = floor((nowTime - nowSeconds) * 100);
  String timeString = nowSeconds + "." + nowHundredths;
  return timeString;
}

public String timeStringFromSeconds(float nowTime) {
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


  static public void main(String[] passedArgs) {
    String[] appletArgs = new String[] { "MetatoneGesturesPlotter" };
    if (passedArgs != null) {
      PApplet.main(concat(appletArgs, passedArgs));
    } else {
      PApplet.main(appletArgs);
    }
  }
}
