BufferedReader reader;
String currentLine;
String[] currentLineParts;
Float currentLineTime;
Float currentFrameTime;
PImage fader;
PFont f;

 
void setup() {
  //frameRate(30);
  size(1024, 768,P2D);
  
  // text
  f = createFont("Helvetica",12,true); // Arial, 16 point, anti-aliasing on
  textFont(f,12);
  
  // Setup the fader.
  background(8);
  fader = get();
  
  background(0);
  fill(255);
  // Open the file from the createWriter() example
  reader = createReader("/Users/charles/Dropbox/Metatone/20130701/OSCLog20130701-17h20m46s.txt");
  currentLineTime = 0.0;  
  currentFrameTime = 0.0;
 
//  String line = "152.146475138 [ /metatone/touch, 6769FE40-5F64-455B-82D4-814E26986A99, 938.5, 696, 0 ] a NetAddr(10.0.1.6, 57120)";
//  line = line.replace("[","");
//  line = line.replace("]","");
//  line = line.replace(",","");
//  line = line.replace("a NetAddr(","");
//  line = line.replace(")","");
//  line = line.replace("  "," ");
//  println(line);
//  String[] pieces = split(line, " "); 
//  println(pieces[1]);
}
 
String[] processLine(String line) {
  line = line.replace("\n","");
  line = line.replace("<OSCMutableMessage (","");
  line = line.replace(") (","");
  line = line.replace(")>","");
  line = line.replace("\"","");
  line = line.replace("    "," ");
  line = line.replace(",","");
  //line = line.replace("  "," ");
  println(line);
  return split(line," ");
}

 
void draw() {
  //background(255); // clear background from previous frame.
  // Grab the next line from the file
  // while current millis()
  
  //currentFrameTime = millis() // real time version.
  currentFrameTime = frameCount * 1000.0 / 30.0; // accurate saveFrames version.
  // Hard coded to 30 frames per second
  
  while (currentLineTime < currentFrameTime) {
    
    String currentLine = "";
    
    while (!(currentLine.contains(">"))) {
          try {
            currentLine += reader.readLine();
          } catch (IOException e) {
            break;
          }
    }
    
    if (currentLine == "") {
      // Stop looping when we get to the end of the file.
      noLoop();
    } else {
      String[] parts = processLine(currentLine);
      currentLineTime = 1000 * (Float.parseFloat(parts[0]));
      
      // Choose colours for each iPad
      if (parts[3].equals("1D7BCDC1-5AAB-441B-9C92-C3F00B6FF930")) {
        fill(224,23,26);
      } else if (parts[3].equals("6769FE40-5F64-455B-82D4-814E26986A99")) {
        fill(23,27,224);
      } else if (parts[3].equals("2678456D-9AE7-4DCC-A561-688A4766C325")) {
        fill(23,224,105);
      } else if (parts[3].equals("97F37307-2A95-4796-BAC9-935BF417AC42")) {
        fill(224,204,23);
      } else {
        fill(255);
      }
      
      if (parts[2].equals("/metatone/touch")) {
        // Drawing Part!
        ellipse(Float.parseFloat(parts[4]),Float.parseFloat(parts[5]),20,20);
      }
    }
  }
  
  // Save frame to make movie later.
  
  saveFrame("/Users/charles/Movies/framestga/metatone-######.tga");
  
  // fade towards white
  blend(fader,0,0,width,height,0,0,width,height,ADD);
  
  
  fill(0);
  text(frameRate, 10,100);
}

// 152.146475138 [ /metatone/touch, 6769FE40-5F64-455B-82D4-814E26986A99, 938.5, 696, 0 ] a NetAddr(10.0.1.6, 57120) 

//
//  try {
//    line = reader.readLine();
//  } catch (IOException e) {
//    e.printStackTrace();
//    line = null;
//  }
//  if (line == null) {
//    // Stop reading because of an error or file is empty
//    noLoop();  
//  } else {
//    String[] pieces = split(line, TAB);
//    int x = int(pieces[0]);
//    int y = int(pieces[1]);
//    point(x, y);
//  }
