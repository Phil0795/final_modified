#ifndef MICROSTEPPER_H
#define MICROSTEPPER_H

#include <Arduino.h>

class MicroStepper
{

protected:
  bool hasEnable;                                               //determins if MicroStepper has Enable,Reset and Sleep pins
  int numStepsPerCycle;                                         //number of full steps per revolution
  int numMicrostepsPerCycle;                                    //number of micro steps per revolution
  byte notEnable, notReset, notSleep, step, dir, ms1, ms2, ms3; //pin declaration
  int speed;                                                    //speed in RPM
  byte direction;                                               // 0, 1
  unsigned int currentMicrostepsAbsPosition;                    //microstep counter
  byte microstepsMode;                                          //selected microstep mode
  unsigned long stepDelay;                                      //time between two steps in us
  unsigned long lastStepTime;                                   //timestamp in us the last step was taken

  void init(int, byte, byte, byte, byte, byte);

public:
  MicroStepper(int, byte, byte, byte, byte, byte, byte, byte, byte); //function 1, 9 papameter
  MicroStepper(int, byte, byte, byte, byte, byte);                   //function 2, 6 papameter

  void setSpeed(int);
  void setDirection(byte);

  void setMicrostepsMode(byte);
  byte getMicrostepsMode(); //pin setting

  void setCurrentMicrostepsAbsPosition(int);
  int getCurrentMicrostepsAbsPosition();

  int getNumMicrostepsPerCycle();

  void enable(bool);
  void reset();
  void sleep(bool);

  void takeSteps(int);
  void takeStepshome(int);
  void gotoStep(unsigned int);
};
#endif
