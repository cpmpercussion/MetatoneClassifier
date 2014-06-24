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

public class MetatoneTouchLogPlayer201406 extends PApplet {

//String touchFileName = "/Users/charles/Dropbox/Metatone/20140317/studyinbowls-rehearsal/2014-03-17T17-40-14-MetatoneOSCLog-touches.csv";
String touchFileName = "/Users/charles/Dropbox/Metatone/20140317/studyinbowls-rehearsal/testTouchDataShort.csv";

boolean saving_frames = false;

int year = 2014;
int month = 3;
int day = 17;
int startHour = 17;
int startMinute = 40;
int startSecond = 45;

int endFrames = 80;

// Drawing Objects
PImage fader;
PFont f;
PGraphics pg;
int drawingPositionNumber;

BufferedReader reader;
Table touchTable;
String currentLine;
String[] currentLineParts;
Float currentLineTime;
Float currentFrameTime;
int startTotalSeconds;
int currentRow;
int totalRows;

public void setup() {
  size(768, 1024,P2D);
  pg = createGraphics( width, height );
  f = loadFont("HelveticaNeue-18.vlw");
  textFont(f,18);
  pg.textFont(f,18);

  // Setup the fader.
  background(8);
  fader = get();
  background(0);
  fill(255);

  touchTable = loadTable(touchFileName,"header");
  totalRows = touchTable.getRowCount();
  currentRow = 0;
  currentLineTime = (parseDateToSeconds(
    touchTable.getRow(currentRow).getString("time")) - startTotalSeconds);

  startTotalSeconds = startHour * 3600 + startMinute * 60 + startSecond;
  drawingPositionNumber = 0;
  currentLineTime = 0.0f;  
  currentFrameTime = 0.0f;

  // println("Table first line:");
  // TableRow firstRow = touchTable.getRow(0);
  // println(firstRow.getString("time"));
  // println(firstRow.getString("device_id"));
  // println(firstRow.getFloat("x_pos"));
  // println(firstRow.getFloat("y_pos"));
}
 
public void draw() {
  background(255);
  currentFrameTime = frameCount / 25.0f;// Hard coded to 25 frames per second
  // 2014-03-17T17:40:46.074877,jonathan,433.5,461.5,0.0
  pg.beginDraw();
  while ((currentLineTime < currentFrameTime) && (currentRow < totalRows)) {
    println("Drawing the row.");
    drawTouch(touchTable.getRow(currentRow));
    currentRow++;

    if (currentRow < totalRows) {
      currentLineTime = (parseDateToSeconds(
        touchTable.getRow(currentRow).getString("time")) - startTotalSeconds);
    } else {
      println("End of file.");
      //noLoop();
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
    }
  }

  
  // fade towards white
  pg.blend(fader,0,0,width,height,0,0,width,height,SUBTRACT);
  pg.endDraw();
  image(pg,0,0);  
  fill(255);

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

public void drawTouch(TableRow row) {
  int[] colour = getColourForName(row.getString("device_id"));
  pg.stroke(255,0);
  pg.colorMode(HSB);
  pg.fill(colour[0],colour[1],colour[2]);
  pg.ellipse(row.getFloat("x_pos"),row.getFloat("y_pos"),20,20);
  pg.colorMode(RGB);
}

public void drawNonTouch(String[] parts) {
  int[] colour = getColourForName(parts[1]);
  pg.stroke(255,0.0f);
  pg.colorMode(HSB);
  pg.fill(colour[0],colour[1],colour[2]);
  String messageString = parts[2] + " ";
  if (parts.length == 6) {
    messageString += parts[4] + " " + parts[5];
  }
  pg.text(messageString,10,(drawingPositionNumber * 15) + 15);
  drawingPositionNumber = (drawingPositionNumber + 1) % 5;
  pg.colorMode(RGB);
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



  static public void main(String[] passedArgs) {
    String[] appletArgs = new String[] { "MetatoneTouchLogPlayer201406" };
    if (passedArgs != null) {
      PApplet.main(concat(appletArgs, passedArgs));
    } else {
      PApplet.main(appletArgs);
    }
  }
}
