boolean DEFAULT_INPUT = true;
boolean saving_frames = true;
boolean portrait = false;
boolean OUTPUT_MOVIE = true;

int year = 1;
int month = 1;
int day = 1;

int startHour = 0;
int startMinute = 0;
int startSecond = 0;

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

//// overriding main now!
//static public void main(String args[]) {
//    println("Trying to access arguments.");
//    println(args.length);
//    println(args);
//    for (String a : args) {
//      println(a);
//    };
//    println("Ok, now starting the sketch.");
//    PApplet.main("MetatoneTouchLogPlayer");
//}

void setup() {
  size(1024, 768, P2D);
  //if (portrait) {
  //  size(768, 1024);
  //} else {
  //  size(1024, 768);
  //}
  //println("Trying to access arguments.");
  //println(args.length);
  //for (String a : args) {
  ////  println(a);
  ////};
  //println("Ok, now selecting file.");

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

  // Load file from default input or from a selection dialogue.
  if (DEFAULT_INPUT) {
    println("Default input file: input.csv");
    prepareToDrawPerformance("input.csv");
    loop();
  } else {
    println("Asking for user selected file.");
    selectInput("Select a file to process:", "fileSelected");
  }
}

void fileSelected(File selection) {
  if (selection == null) {
    println("Window was closed or the user hit cancel.");
    exit();
  } else {
    println("User selected " + selection.getAbsolutePath());
    prepareToDrawPerformance(selection.getAbsolutePath());
    loop();
  }
}

void prepareToDrawPerformance(String filePath) {
  touchTable = loadTable(filePath, "header");
  totalRows = touchTable.getRowCount();
  currentRow = 0;
  String firstTouchTime = touchTable.getRow(currentRow).getString("time");
  parsePerformanceDate(firstTouchTime);
  startTotalSeconds = startHour * 3600.0 + startMinute * 60.0 + startSecond;
  startTotalSeconds -= 10; // start 10seconds before first touch.
  currentLineTime = (parseDateToSeconds(firstTouchTime) - startTotalSeconds);
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
      if (OUTPUT_MOVIE) makeMovie();
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

//int[] getColourForName(String name) {
//  byte[] bytes = name.getBytes();
//  int hueNumber = 0;
//  for (int i = 0; i < bytes.length; i++) {
//    hueNumber += bytes[i];
//  }
//  hueNumber = hueNumber % 256; 
//  int[] colour = { 
//    hueNumber, 255, 255
//  };
//  return colour;
//}

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
 //<>//
/////
//
// Framerate method
//
/////

void mouseReleased() {
  println("Framerate is: " + frameRate);
}

void makeMovie() {
  println("Going to try to make movie");
  String movieName = year + "-" + month + "-" + day + "T" + startHour + "-" + startMinute + "-" + startSecond + "-TouchAnimation.mov";
  //String movieName = "TouchAnimationNew.mov";
  println("Filename will be: " + movieName);
  String inputDir = "/Users/charles/Movies/framestga";
  String outputDir = "/Users/charles/Movies/processing-output/";
  String command = "/usr/local/bin/ffmpeg -f image2 -framerate 25 -i " + inputDir + "/%06d.tga -vcodec libx264 -r 25 -pix_fmt yuv420p -crf 16 " + outputDir + movieName;
  println(command);
  //String command = "/usr/local/bin/ffmpeg -f image2 -framerate 25 -i /Users/charles/Movies/framestga/%06d.tga -vcodec qtrle -r 25 /Users/charles/Movies/framestga/" + movieName;
  Process p;
  try {
   p = Runtime.getRuntime().exec(command);
   p.waitFor();
  } catch(Exception e) {
   e.printStackTrace();
  }
  println("done encoding.");
  println("now removing tga files.");
  command = "rm -r " + inputDir;
  println(command);
  try {
    p = Runtime.getRuntime().exec(command);
    p.waitFor();
  } catch(Exception e) {
    e.printStackTrace();
  }
  println("done.");
}