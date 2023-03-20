/*Artur Kazickij finisched code*/
/* 2016.08.12*/
/* Yang Wang modified*/
/* 2022.01*/
/*P. Hoop modified*/
/*2023.02*/
#include <MsTimer2.h>
#include "MicroStepper.h"
#include "DC_Engine.h"
#include "HomeSwitch.h"
#include <Wire.h>

/******************************************************************************
 * Constants
 *******************************************************************************/
#define STEPS 200 //The stepper motor has 200 steps

//Pins used
#define PIN_N_ENABLE 11 //Stepper control inputs
#define PIN_N_SLEEP 4   //Sleepsetting,  sleep when Low
#define PIN_N_RESET 5   //Stepper step pins
#define PIN_MS_1 8      //Microstep selection pins
#define PIN_MS_2 7      //Stepper brake pins always LOW
#define PIN_MS_3 6
#define PIN_STEP 3 //Stepper current sense pins
#define PIN_DIR 2
//DC Motor
#define PIN_DC_A 9 //DC-Engine PWM pins on Timer 1
#define PIN_DC_B 10
#define PIN_DC_EF 12 //DC-Engine Error Flag
//home switch
#define PIN_HOME 13


#define TELEGRAM_TYPE_LAUNCH_TEST_REQUEST       "00"
#define TELEGRAM_TYPE_LAUNCH_TEST_RESPONSE      "01"
#define TELEGRAM_TYPE_PROGRESS_CONTROL_REQUEST    "02"
#define TELEGRAM_TYPE_PROGRESS_CONTROL_RESPONSE   "03"
#define TELEGRAM_TYPE_PARAMETER_SETTING_REQUEST   "04"
#define TELEGRAM_TYPE_PARAMETER_SETTING_RESPONSE  "05"
#define TELEGRAM_TYPE_ERROR                       "99"
// Progress status
#define STOPPED  0
#define STARTED  1
#define PAUSED   2

#define BENDING_DIRECTION_POSITIVE 0
#define BENDING_DIRECTION_NEGATIVE 1
#define BENDING_DIRECTION_DOUBLE 2

/******************************************************************************
 * Global variables
 *******************************************************************************/
 struct  
{
  int bendingDirection; //0:positive ,1:negative, 2:double
  int stepperSpeed; // in r/min
  int cycles; 
  int steps;  
} testParameter = {0, 10, 1, 3200};

int progressStatus = STOPPED;  // 0:stopped 1:started 2:paused 

bool launchTestEnable = false;

///Variables used
int stepperSpeed = 60;
int cycles = 1;
int bending_direction;
int steps;

char dc_direction = -100; //-128 to 127

MicroStepper *stepper;
DC_Engine *dc_engine;
HomeSwitch *H_switch;

/******************************************************************************
 * Functions
 *******************************************************************************/
void requestEvent()
{
  char buf[8];
  snprintf(buf, sizeof(buf), "%d", stepper->getCurrentMicrostepsAbsPosition());
  Wire.write(buf);
}
void timerEvent() {
  sendResponse(TELEGRAM_TYPE_LAUNCH_TEST_RESPONSE);
 }
 
void setup()
{
  H_switch = new HomeSwitch(PIN_HOME);
  dc_engine = new DC_Engine(PIN_DC_A, PIN_DC_B, PIN_DC_EF);
  stepper = new MicroStepper(STEPS, PIN_N_ENABLE, PIN_N_RESET, PIN_N_SLEEP, PIN_STEP, PIN_DIR, PIN_MS_1, PIN_MS_2, PIN_MS_3); // 9 parameter
  stepper->setMicrostepsMode(16);                                                                                             //microstep resolutions within 1,2,4,8,16
  Serial.begin(115200);
  Serial.flush();
  Wire.begin(4);                // join i2c bus with address #5
  Wire.onRequest(requestEvent); // register event
}

void loop()
{
  dc_engine->setSpeed(0); // dc engine speed = 0
  goHome(10);
  stepper->sleep(true);
  while (Serial.available() == 0)
  ;
  receiveCommand();
  stepper->sleep(false);
  
  if(launchTestEnable) {
    progressStatus = STARTED;
    MsTimer2::set(20, timerEvent); 
    MsTimer2::start();
    launchTest();
    progressStatus = STOPPED;
    launchTestEnable = false;
    delay(100);
    MsTimer2::stop();
   }
}


//Home switch function
void goHome(int speed)
{
  stepper->setSpeed(speed); // stepper Speed is 20 RPM
  // stepper move 1 step by step, until reach the Home
  while (!H_switch->isHome())
  {
    stepper->takeStepshome(1);
  }
  stepper->setCurrentMicrostepsAbsPosition(0);
}


void launchTest() {
  stepper->setSpeed(testParameter.stepperSpeed);
  int addon = 0;
  if (testParameter.cycles == 0) addon = 1;
  for (long i = 0; i < testParameter.cycles + addon; ++i)
  {
    for(int j = 0; j < testParameter.steps; ++j) 
    {
      do {
        if(Serial.available()) {
            MsTimer2::stop();
            receiveCommand();
            MsTimer2::start();
        }
        if(progressStatus == STOPPED) return;
      }
      while(progressStatus != STARTED);
      
      switch (testParameter.bendingDirection) {
        case BENDING_DIRECTION_NEGATIVE:
          if (j <= 150 && i == 0) dc_engine->setSpeed(-cos(PI/3200*j)*100);
          else dc_engine->setSpeed(0);
          break;

        case BENDING_DIRECTION_POSITIVE:
          if (j <= 150 && i == 0) dc_engine->setSpeed(cos(PI/3200*j)*100);
          else dc_engine->setSpeed(0);
          break;

        case BENDING_DIRECTION_DOUBLE:
          if (j <= 150 && i%2 == 0) dc_engine->setSpeed(-cos(PI/3200*j) * 100);
          else if (j <= 150 && i%2 != 0) dc_engine->setSpeed(cos(PI/3200*j)*100);
          else if (j > 150) dc_engine->setSpeed(0);
          break;
      }
      stepper->takeSteps(1);
    }
    if (testParameter.cycles!=0) goHome(testParameter.stepperSpeed);
    else{ 
      while(progressStatus != STOPPED)
      {
        if(Serial.available()) 
          {
          MsTimer2::stop();
          receiveCommand();
          MsTimer2::start();
          }       
      }
    }
  }
  
}







void receiveCommand()
{
  String command = Serial.readStringUntil('\n');
  String telegramType = command.substring(0, 2);

  if(telegramType == TELEGRAM_TYPE_PARAMETER_SETTING_REQUEST) 
  {
    int firstCommaIndex = command.indexOf(',');
    int secondCommaIndex = command.indexOf(',', firstCommaIndex + 1);
    int thirdCommaIndex = command.indexOf(',', secondCommaIndex + 1);
    int fourthCommaIndex = command.indexOf(',', thirdCommaIndex + 1);
  
  
    int val2 = command.substring(firstCommaIndex + 1, secondCommaIndex).toInt();
    int val3 = command.substring(secondCommaIndex + 1, thirdCommaIndex).toInt();
    int val4 = command.substring(thirdCommaIndex + 1, fourthCommaIndex).toInt();
    int val5 = command.substring(fourthCommaIndex + 1).toInt();
    
    if(firstCommaIndex < 0 || secondCommaIndex < 0 || thirdCommaIndex<=0 || fourthCommaIndex<0 || val2 < 0 || val3 <= 0 || val4 < 0 || val5 <= 0 || progressStatus != STOPPED) 
    {
      sendResponse(TELEGRAM_TYPE_ERROR);
      return;
    }
    
    testParameter.bendingDirection = val2;
    testParameter.stepperSpeed = val3;
    testParameter.cycles = val4;
    testParameter.steps = val5;
    sendResponse(TELEGRAM_TYPE_PARAMETER_SETTING_RESPONSE);
    
  } else if(telegramType == TELEGRAM_TYPE_PROGRESS_CONTROL_REQUEST) {
      int firstCommaIndex = command.indexOf(',');
      
      int val2 = command.substring(firstCommaIndex + 1).toInt();
      if(firstCommaIndex < 0 || val2 != STOPPED && val2 != STARTED && val2 != PAUSED) 
      {
          sendResponse(TELEGRAM_TYPE_ERROR);
          return;
      }
      progressStatus = val2;
      sendResponse(TELEGRAM_TYPE_PROGRESS_CONTROL_RESPONSE);

  } else if(telegramType == TELEGRAM_TYPE_LAUNCH_TEST_REQUEST) {
      launchTestEnable = true;
  } else sendResponse(TELEGRAM_TYPE_ERROR);
}


void sendResponse(String responseType) 
{    
  if(responseType == TELEGRAM_TYPE_PARAMETER_SETTING_RESPONSE) 
  {
      Serial.print(TELEGRAM_TYPE_PARAMETER_SETTING_RESPONSE);
      Serial.print(',');
      Serial.print(testParameter.bendingDirection);
      Serial.print(',');
      Serial.print(testParameter.stepperSpeed);
      Serial.print(',');
      Serial.print(testParameter.cycles);
      Serial.print(',');
      Serial.print(testParameter.steps);    
      Serial.print("\r\n");
   } else if(responseType == TELEGRAM_TYPE_PROGRESS_CONTROL_RESPONSE) {
      Serial.print(TELEGRAM_TYPE_PROGRESS_CONTROL_RESPONSE);
      Serial.print(',');
      Serial.print(progressStatus);
      Serial.print("\r\n");
   } else if(responseType == TELEGRAM_TYPE_LAUNCH_TEST_RESPONSE) {
      Serial.print(TELEGRAM_TYPE_LAUNCH_TEST_RESPONSE);
      Serial.print(',');
      Serial.print(progressStatus),
      Serial.print(',');
      Serial.print(stepper->getCurrentMicrostepsAbsPosition());
      Serial.print(',');
      Serial.print(testParameter.bendingDirection);
      Serial.print(',');
      Serial.print(testParameter.stepperSpeed);
      Serial.print(',');
      Serial.print(testParameter.cycles);
      Serial.print(',');
      Serial.print(testParameter.steps); 
      Serial.print("\r\n");
   } else if(responseType == TELEGRAM_TYPE_ERROR) {
      Serial.print(TELEGRAM_TYPE_ERROR);
      Serial.print("\r\n");
   }
}
