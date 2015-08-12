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
 
void setup() {
  //frameRate(30);
  size(1024, 768,P2D);
  
  pg = createGraphics( width, height );
  
  // text
  f = loadFont("HelveticaNeue-18.vlw"); // Arial, 16 point, anti-aliasing on
  textFont(f,18);
  pg.textFont(f,18);
  
  // Setup the fader.
  background(8);
  fader = get();
  
  background(0);
  fill(255);
//  // Open the file from the createWriter() example
//  reader = createReader("/Users/charles/Dropbox/Metatone/20130803/performance/OSCLog20130803-18h37m03s.txt");
//  year = 2013;
//  month = 8;
//  day = 3;
//  startHour = 18;
//  startMinute = 37;
//  startSecond = 3;

  // Open the file from the createWriter() example
  reader = createReader("/Users/charles/Dropbox/Metatone/20130803/rehearsal/OSCLog20130803-17h25m19s.txt");
  year = 2013;
  month = 8;
  day = 3;
  startHour = 17;
  startMinute = 25;
  startSecond = 19;

  
  currentLineTime = 0.0;  
  currentFrameTime = 0.0;
  getNextLine(); // load up the first line ready to draw.
}
 
String[] processLine(String line) {
  // 69.115007, 10.0.1.4, < (/metatone/touch) ( 2678456D-9AE7-4DCC-A561-688A4766C325, 53.5, 89.5, 0)>
  line = line.replace("\n","");
  line = line.replace("< (","");
  line = line.replace(") (","");
  line = line.replace(")>","");
  line = line.replace("\"","");
  line = line.replace("    "," ");
  line = line.replace(",","");
  //line = line.replace("  "," ");
  //println(line);
  return split(line," ");
}

void drawTouch(String[] parts) {
  pg.stroke(255,0);
  // Choose colours for each iPad
  if (parts[3].equals("1D7BCDC1-5AAB-441B-9C92-C3F00B6FF930")) {
    pg.fill(224,23,26);
  } else if (parts[3].equals("6769FE40-5F64-455B-82D4-814E26986A99")) {
    pg.fill(23,27,224);
  } else if (parts[3].equals("2678456D-9AE7-4DCC-A561-688A4766C325")) {
    pg.fill(23,224,105);
  } else if (parts[3].equals("97F37307-2A95-4796-BAC9-935BF417AC42")) {
    pg.fill(224,204,23);
  } else {
    pg.fill(255);
  }
  pg.ellipse(Float.parseFloat(parts[4]),Float.parseFloat(parts[5]),20,20);
}

void drawNonTouch(String[] parts) {
  pg.stroke(255,0.0);
  pg.fill(255);
   int number = 0;
  // Choose colours for each iPad
  if (parts[3].equals("1D7BCDC1-5AAB-441B-9C92-C3F00B6FF930")) {
    pg.fill(224,23,26);
    number = 0;
  } else if (parts[3].equals("6769FE40-5F64-455B-82D4-814E26986A99")) {
    pg.fill(23,27,224);
    number = 1;
  } else if (parts[3].equals("2678456D-9AE7-4DCC-A561-688A4766C325")) {
    pg.fill(23,224,105);
    number = 2;
  } else if (parts[3].equals("97F37307-2A95-4796-BAC9-935BF417AC42")) {
    pg.fill(224,204,23);
    number = 3;
  }
  String messageString = parts[2] + " ";
  if (parts.length == 6) {
    messageString += parts[4] + " " + parts[5];
  }
  pg.text(messageString,10,(number * 15) + 15);
}

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

void getNextLine() {
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
 
void draw() {
  background(255);
  currentFrameTime = frameCount * 1000.0 / 25.0; // accurate saveFrames version. // Hard coded to 25 frames per second
  
  // Offset for debugging
  //currentFrameTime += 70000;
  
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
    
//    String currentLine = ""; 
//    try {
//      currentLine = reader.readLine();
//    } catch (IOException e) {
//      currentLine = null;
//    }
//
//    if (currentLine == "") {
//      noLoop();  // Stop looping when we get to the end of the file.
//    } else {
//      String[] parts = processLine(currentLine);
//      currentLineTime = 1000 * (Float.parseFloat(parts[0]));
//      if (parts[2].equals("/metatone/touch")) { 
//        drawTouch(parts); // draw the touch
//      } else {
//        drawNonTouch(parts);
//        println(parts[0] + " " + parts[2] + " " + parts[3]);
//      }
//    }
    
  }
  

  
  // fade towards white
  pg.blend(fader,0,0,width,height,0,0,width,height,SUBTRACT);
  
  pg.endDraw();
  image(pg, 0,0);  
  
  fill(255);
  //text("Framerate: " + frameRate, 10,height - 10);
  text("Log Time: " + makeTimeString(currentFrameTime/1000), 10, height - 10);
  text(makeDateString(currentFrameTime/1000),10,height - 35);
  
  // Save frame to make movie later.
  // Turn on for saving mode...
  saveFrame("/Users/charles/Movies/framestga/metatone-######.png");
}
