import java.util.Random; //<>//
import java.util.Arrays;
import ddf.minim.*;
import ddf.minim.ugens.*;
import oscP5.*;
import netP5.*;

Minim minim;
AudioOutput out;
Oscil wave;
Damp envelope;
AudioPlayer applausePlayer;

OscP5 oscServer;
NetAddress classifierAddress;

String CLASSIFIER_HOST = "10.0.1.2";
int CLASSIFIER_PORT = 9000;
String TARGET_GESTURE_OSC_ADDRESS = "/metatone/targetgesture";

String REST_TEXT = "Rest";
int CURRENT_TIME_LEFT = 0;
String CURRENT_GESTURE = "Accel. Swipes";
String NEXT_GESTURE = "Rest";
  // , Accel. Swipes, , , , , , . 

int GESTURE_INTERVAL = 60;
int REST_INTERVAL = 20;
int GESTURE_MESSAGE_INTERVAL = 200; // 200 milliseconds

String[] GESTURE_NAMES = {"Nothing","Fast Taps","Slow Taps","Fast Swipes","Accel. Swipes","V. Slow Swirl","Big Swirl","Small Swirl","Combination"};
String[] GESTURE_CODES = {"N","FT","ST","FS","FSA","VSS","BS","SS","C"};
int[] GESTURE_NUMBERS = {0,1,2,3,4,5,6,7,8};

int[] gestureSurveyOrder;
int currentSurveyIndex = 0;
int lastPhaseStartTime = 0;
boolean currentlySurveying;
int currentPhaseTime = 0;
int currentTimeLeft = 0;
int lastCurrentTimeLeft = 0;
int lastGestureMessageSend = 0;


void setup() {
  size(1200, 800);
  oscServer = new OscP5(this,61200);
//  oscServer.plug(this,"touchHandler","/metatone/touch");
  CLASSIFIER_HOST = oscServer.ip();
  println("Setting Classifier Address to: " + CLASSIFIER_HOST);
  classifierAddress = new NetAddress(CLASSIFIER_HOST,CLASSIFIER_PORT);
  
  minim = new Minim(this);
  out = minim.getLineOut();
  
  wave = new Oscil(440, 0.5f, Waves.SINE);
  envelope = new Damp(0.03, 0.6);
  wave.patch(envelope);
  envelope.patch(out);
  applausePlayer = minim.loadFile("applause.mp3");

  println("Loading Gesture Survey");
  gestureSurveyOrder = GESTURE_NUMBERS.clone();
  shuffleArray(gestureSurveyOrder);
  println("Survey order will be:");
  println(gestureSurveyOrder);
  currentSurveyIndex = 0; 
  startRest(currentSurveyIndex);
  applausePlayer.play();
}

void updateInterface() {
  currentTimeLeft = currentPhaseTime - (millis() - lastPhaseStartTime)/1000;

  if (millis() - lastGestureMessageSend > GESTURE_MESSAGE_INTERVAL) {
//   println(millis() - lastGestureMessageSend);
   sendGestureToLog(); 
  }

  if (currentTimeLeft < 1) {
    // start new phase
    if (currentlySurveying) {
      currentSurveyIndex++;
      if (currentSurveyIndex > gestureSurveyOrder.length - 1) {
        endPhase();
        return;  
      }
      startRest(currentSurveyIndex);
      return;
    } else {
      startSurvey(currentSurveyIndex);
      return;
    }
  }
  
  if ((currentTimeLeft != lastCurrentTimeLeft) && (currentTimeLeft < 6)) {
    playCountdownSound();
  }
  lastCurrentTimeLeft = currentTimeLeft;
}

void sendGestureToLog() {
  OscMessage gestureMessage = new OscMessage(TARGET_GESTURE_OSC_ADDRESS);
  if (currentlySurveying) {
    gestureMessage.add(gestureSurveyOrder[currentSurveyIndex]);
  } else {
    gestureMessage.add(100);
  }
  oscServer.send(gestureMessage,classifierAddress);
  lastGestureMessageSend = millis();
}

void endPhase() {
  CURRENT_GESTURE = "Finished!";
  NEXT_GESTURE = "--";
  currentPhaseTime = 1000;
  currentTimeLeft = currentPhaseTime;
  currentlySurveying = false;
  lastPhaseStartTime = millis();
  
  // Play applause sound!
  applausePlayer.rewind();
  applausePlayer.play();
}

void startRest(int index) {
  playStartSound();
  CURRENT_GESTURE = REST_TEXT;
  NEXT_GESTURE = GESTURE_NAMES[gestureSurveyOrder[index]];
  currentPhaseTime = REST_INTERVAL;
  currentTimeLeft = currentPhaseTime;
  currentlySurveying = false;
  lastPhaseStartTime = millis();
}

void startSurvey(int index) {
  playStartSound();
  CURRENT_GESTURE = GESTURE_NAMES[gestureSurveyOrder[index]];
  NEXT_GESTURE = REST_TEXT;
  currentPhaseTime = GESTURE_INTERVAL;
  currentTimeLeft = currentPhaseTime;
  currentlySurveying = true; 
  lastPhaseStartTime = millis();
}

void playCountdownSound() {
  wave.setFrequency(440);
  envelope.activate();
}

void playStartSound() {
  wave.setFrequency(880);
  envelope.activate();
}


void draw() {
  updateInterface();
  background(0);
  
  textAlign(LEFT,TOP);
  textSize(64);
  fill(180);
  text("Current Gesture:",10,10);
  
  textSize(180);
  fill(255);
  text(CURRENT_GESTURE,10,200);
  textAlign(LEFT,BOTTOM);
  
  textSize(64);
  fill(180);
  text("Next Gesture:",10,height-200);

  textAlign(RIGHT,BOTTOM);
  textSize(64);
  fill(180);
  text("Time Left:",width-10,height-200);
  
  textAlign(LEFT,BOTTOM);
  textSize(120);
  fill(255);
  text(NEXT_GESTURE,10,height-10);
  
  textAlign(RIGHT,BOTTOM);
  textSize(120);
  if (currentTimeLeft < 6) {
    fill(255,0,0);
  } else {
    fill(0,255,0);
  }
  text(currentTimeLeft,width-10,height-10); //<>//
}

void shuffleArray(int[] array) { 
  // with code from WikiPedia; Fisher–Yates shuffle 
  Random rng = new Random();
  // i is the number of items remaining to be shuffled.
  for (int i = array.length; i > 1; i--) {
    // Pick a random element to swap with the i-th element.
    int j = rng.nextInt(i);  // 0 <= j <= i-1 (0-based array)
    // Swap array elements.
    int tmp = array[j];
    array[j] = array[i-1];
    array[i-1] = tmp;
  }
}

void oscEvent(OscMessage message) {
  if(message.isPlugged()==false) {
//    println("### received an osc message.");
//    println("### addrpattern\t"+message.addrPattern());
//    println("### typetag\t"+message.typetag());
  }
}
