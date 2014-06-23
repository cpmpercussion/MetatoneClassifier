import oscP5.*;
import netP5.*;

// Drawing Code
PImage fader;
PFont f;
PGraphics pg;

OscP5 oscServer;

String[] stored_devices;
float[] stored_x;
float[] stored_y;
float[] stored_vel;

void setup() {
  //frameRate(30);
  size(1024, 768,P2D);
  pg = createGraphics( width, height );
  f = loadFont("HelveticaNeue-18.vlw"); // Arial, 16 point, anti-aliasing on
  textFont(f,18);
  pg.textFont(f,18);
  background(8);
  fader = get();
  background(0);
  fill(255);

  oscServer = new OscP5(this,61200);
  oscServer.plug(this,"touchHandler","/metatone/touch");
}

public void touchHandler(String device_id, float x_pos, float y_pos, float vel) {
  println ("Touch: " + device_id + " " + x_pos + " " + y_pos + " " + vel);
  drawTouch(device_id,x_pos,y_pos,vel);
}



void drawTouch(String device_id, float x_pos, float y_pos, float vel) {
  pg.beginDraw();
  pg.stroke(255,0);
  String lastTwo = device_id.substring(device_id.length()-2);
  int num = Integer.parseInt(lastTwo,16);
  //int hue = num * 255 / 300;
  println(num);
  int hue = num;
  
  pg.colorMode(HSB);
  pg.fill(hue,255,255);
  pg.ellipse(x_pos,y_pos,30,30);
  pg.colorMode(RGB);
  pg.endDraw();
}

void draw() {
  background(255);
  pg.beginDraw();
  pg.blend(fader,0,0,width,height,0,0,width,height,SUBTRACT);
  pg.endDraw();
  image(pg, 0,0);  
  fill(255);
}

void oscEvent(OscMessage message) {
  if(message.isPlugged()==false) {
    println("### received an osc message.");
    println("### addrpattern\t"+message.addrPattern());
    println("### typetag\t"+message.typetag());
  }
}
