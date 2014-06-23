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

String touchFileName = "/Users/charles/Dropbox/Metatone/20140317/studyinbowls-rehearsal/2014-03-17T17-40-14-MetatoneOSCLog-touches.csv";
// Drawing Code
PImage fader;
PFont f;
PGraphics pg;

// Reading Vars:
BufferedReader reader;

String currentLine;
String[] currentLineParts;
Float currentLineTime;
Float currentFrameTime;

int year;
int month;
int day;
int startHour;
int startMinute;
int startSecond;
 
public void setup() {
  size(1024, 768,P2D);
  pg = createGraphics( width, height );
  f = loadFont("HelveticaNeue-18.vlw"); // Arial, 16 point, anti-aliasing on
  textFont(f,18);
  pg.textFont(f,18);

  // Setup the fader.
  background(8);
  fader = get();
  background(0);
  fill(255);

  reader = createReader(touchFileName);
  year = 2013;
  month = 5;
  day = 4;
  startHour = 12;
  startMinute = 12;
  startSecond = 0;

  currentLineTime = 0.0f;  
  currentFrameTime = 0.0f;
  getNextLine(); // load up the first line ready to draw.
}
 
public String[] processLine(String line) {
  return split(line,",");
}

public int[] getColourForName(String name) {
  int[] colour = { 225, 0 , 0 };
  return colour;

  // // Choose colours for each iPad
  // if (parts[3].equals("1D7BCDC1-5AAB-441B-9C92-C3F00B6FF930")) {
  //   pg.fill(224,23,26);
  // } else if (parts[3].equals("6769FE40-5F64-455B-82D4-814E26986A99")) {
  //   pg.fill(23,27,224);
  // } else if (parts[3].equals("2678456D-9AE7-4DCC-A561-688A4766C325")) {
  //   pg.fill(23,224,105);
  // } else if (parts[3].equals("97F37307-2A95-4796-BAC9-935BF417AC42")) {
  //   pg.fill(224,204,23);
  // } else {
  //   pg.fill(255);
  // }
}

public void drawTouch(String[] parts) {
  int[] colour = getColourForName(parts[3]);
  pg.stroke(255,0);
  pg.fill(colour[0],colour[1],colour[2]);
  pg.ellipse(Float.parseFloat(parts[4]),Float.parseFloat(parts[5]),20,20);
}

public void drawNonTouch(String[] parts) {
  int[] colour = getColourForName(parts[3]);
  pg.stroke(255,0.0f);
  pg.fill(colour[0],colour[1],colour[2]);
  int number = 0;
  if (parts[3].equals("1D7BCDC1-5AAB-441B-9C92-C3F00B6FF930")) {
    number = 0;
  } else if (parts[3].equals("6769FE40-5F64-455B-82D4-814E26986A99")) {
    number = 1;
  } else if (parts[3].equals("2678456D-9AE7-4DCC-A561-688A4766C325")) {
    number = 2;
  } else if (parts[3].equals("97F37307-2A95-4796-BAC9-935BF417AC42")) {
    number = 3;
  }
  String messageString = parts[2] + " ";
  if (parts.length == 6) {
    messageString += parts[4] + " " + parts[5];
  }
  pg.text(messageString,10,(number * 15) + 15);
}

public Double parseDateToSeconds(String dateString) {
  // 2014-03-17T17:40:46.074877,jonathan,433.5,461.5,0.0
  String time = split(dateString,"T")[1];
  String[] timeParts = split(time,":");
  Double seconds = (Double.parseDouble(timeParts[0]) * 3600) 
    + (Double.parseDouble(timeParts[1]) * 60 )
    + Double.parseDouble(timeParts[2]);
  return seconds;
}


public void getNextLine() {
  currentLine = "";
  
  try {
    currentLine = reader.readLine();
  } catch (IOException e) {
    currentLine = null;
  }
  
  if (currentLine == null) {
    noLoop();  // Stop looping when we get to the end of the file.
  } else {
    currentLineParts = processLine(currentLine);
    currentLineTime = 1000 * (Float.parseFloat(currentLineParts[0]));
  }
}
 
public void draw() {
  background(255);
  currentFrameTime = frameCount * 1000.0f / 25.0f;// Hard coded to 25 frames per second


  pg.beginDraw();
  while (currentLineTime < currentFrameTime) {
    // Draw the line
    if (currentLine != null) {
      if (currentLineParts[2].equals("/metatone/touch")) { 
        drawTouch(currentLineParts); // draw the touch
      } else {
        drawNonTouch(currentLineParts);
        println(currentLineParts[0] + " " + currentLineParts[2] + " " + currentLineParts[3]);
      }
      // get next line
      getNextLine();
    } else {
      noLoop();
    }
  }
  // fade towards white
  pg.blend(fader,0,0,width,height,0,0,width,height,SUBTRACT);
  pg.endDraw();
  image(pg,0,0);  
  fill(255);
  //text("Framerate: " + frameRate, 10,height - 10);
  text("Log Time: " + makeTimeString(currentFrameTime/1000), 10, height - 10);
  text(makeDateString(currentFrameTime/1000),10,height - 35);
  
  // Save frame to make movie later.
  // Turn on for saving mode...
  saveFrame("/Users/charles/Movies/framestga/metatone-######.png");
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
