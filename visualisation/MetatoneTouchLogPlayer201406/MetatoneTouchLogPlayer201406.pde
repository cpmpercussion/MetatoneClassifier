String touchFileName = "/Users/charles/Dropbox/Metatone/20140317/studyinbowls-rehearsal/2014-03-17T17-40-14-MetatoneOSCLog-touches.csv";
boolean saving_frames = false;

// Drawing Objects
PImage fader;
PFont f;
PGraphics pg;
int drawingPositionNumber;


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
int startTotalSeconds;

void setup() {
  size(768, 1024,P2D);
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
  year = 2014;
  month = 3;
  day = 17;
  startHour = 17;
  startMinute = 40;
  startSecond = 14;
  startTotalSeconds = startHour * 3600 + startMinute * 60 + startSecond;

  drawingPositionNumber = 0;
  currentLineTime = 0.0;  
  currentFrameTime = 0.0;
  

  while (!getNextLine()) {
    println("Finding first touch line");
  } // load up the first line ready to draw.
  println(currentLineParts);
  println(currentLineTime);
}
 
String[] processLine(String line) {
  return split(line,",");
}

int[] getColourForName(String name) {
  String lastTwo = name.substring(name.length()-2);
  byte[] bytes = name.getBytes();
  //println(bytes);
  int hueNumber = 0;

  for (int i = 0; i < bytes.length; i++) {
    hueNumber += bytes[i];
  }

  hueNumber = hueNumber % 256; 

  // int hueNumber = Integer.parseInt(lastTwo,16);
  int[] colour = { hueNumber, 255 , 255 };
  return colour;
}

void drawTouch(String[] parts) {
    //0 2014-03-17T17:40:46.074877,
    //1 jonathan,
    //2 433.5,
    //3 461.5,
    //4 0.0
  int[] colour = getColourForName(parts[1]);
  pg.stroke(255,0);
  pg.colorMode(HSB);
  pg.fill(colour[0],colour[1],colour[2]);
  pg.ellipse(Float.parseFloat(parts[2]),Float.parseFloat(parts[3]),20,20);
  pg.colorMode(RGB);
}

void drawNonTouch(String[] parts) {
  int[] colour = getColourForName(parts[1]);
  pg.stroke(255,0.0);
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

Float parseDateToSeconds(String dateString) {
  String time = split(dateString,"T")[1];
  String[] timeParts = split(time,":");
  Float seconds = (Float.parseFloat(timeParts[0]) * 3600) 
    + (Float.parseFloat(timeParts[1]) * 60 )
    + Float.parseFloat(timeParts[2]);
  return seconds;
}


boolean getNextLine() {
  // 2014-03-17T17:40:46.074877,jonathan,433.5,461.5,0.0
  currentLine = "";
  
  try {
    currentLine = reader.readLine();
  } catch (IOException e) {
    currentLine = null;
    println("Reached end of file.");
    noLoop();
    return false;
  }
  
  if (currentLine.contains("time,device_id,x_pos,y_pos,velocity")) {
    return false;
  } else {
    currentLineParts = processLine(currentLine);
    currentLineTime = 1000 * (parseDateToSeconds(currentLineParts[0]) - startTotalSeconds);
    return true;
  }
}
 
void draw() {
  background(255);
  currentFrameTime = frameCount * 1000.0 / 25.0;// Hard coded to 25 frames per second

  // 2014-03-17T17:40:46.074877,jonathan,433.5,461.5,0.0
  pg.beginDraw();
  while (currentLineTime < currentFrameTime) {
    // Draw the line
    if (currentLine != null) {
      drawTouch(currentLineParts);
      // if (currentLineParts[2].equals("/metatone/touch")) { 
      //   drawTouch(currentLineParts); // draw the touch
      // } else {
      //   drawNonTouch(currentLineParts);
      //   println(currentLineParts[0] + " " + currentLineParts[2] + " " + currentLineParts[3]);
      // }
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
  if(saving_frames) {
    saveFrame("/Users/charles/Movies/framestga/metatone-######.png");
  }
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
