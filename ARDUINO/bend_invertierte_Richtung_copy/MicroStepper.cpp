#include "MicroStepper.h"

//-- constructors --
MicroStepper::MicroStepper(int numStepsPerCycle, byte notEnable, byte notReset, byte notSleep, // function 1
                           byte step, byte dir, byte ms1, byte ms2, byte ms3)
{
  this->notEnable = notEnable; //pin, point to the parameter
  this->notReset = notReset;
  this->notSleep = notSleep;
  this->hasEnable = true;
  this->currentMicrostepsAbsPosition = 0;
  pinMode(notEnable, OUTPUT); //pin setting, Arduino send signal to Antreiber
  pinMode(notReset, OUTPUT);
  pinMode(notSleep, OUTPUT);
  digitalWrite(notEnable, LOW); //initial input pin voltage
  digitalWrite(notReset, HIGH);
  digitalWrite(notSleep, HIGH);

  this->init(numStepsPerCycle, step, dir, ms1, ms2, ms3);
}

MicroStepper::MicroStepper(int numStepsPerCycle, byte step, byte dir, byte ms1, byte ms2, byte ms3)
{ // function 2
  this->hasEnable = false;
  this->init(numStepsPerCycle, step, dir, ms1, ms2, ms3);
}

//-- Methods --
void MicroStepper::init(int numStepsPerCycle, byte step, byte dir, byte ms1, byte ms2, byte ms3)
{
  this->numStepsPerCycle = numStepsPerCycle;
  this->step = step;
  this->dir = dir;
  this->ms1 = ms1;
  this->ms2 = ms2;
  this->ms3 = ms3;
  pinMode(step, OUTPUT);
  pinMode(dir, OUTPUT);
  pinMode(ms1, OUTPUT);
  pinMode(ms2, OUTPUT);
  pinMode(ms3, OUTPUT);
  this->setMicrostepsMode(16);
  this->lastStepTime = micros(); //Gibt die Anzahl der Mikrosekunden zurück, seit das Arduino-Board das aktuelle Programm gestartet hat
}

void MicroStepper::setSpeed(int speed)
{ //transate the speed in RPM to the speed in Arduino
  this->speed = speed;
  //    this->stepDelay = (1000000/(this->numStepsPerCycle * this->microstepsMode * speed / 60)); Arduino's not a calculator :(  haha
  this->stepDelay = 1000000 / this->numStepsPerCycle; //1million us = 1 second
  this->stepDelay /= this->microstepsMode;
  this->stepDelay /= speed;
  this->stepDelay *= 60; //60seconds per minute
}

void MicroStepper::setDirection(byte direction)
{ //stpper direction, low -> 0, high -> 1;
  this->direction = direction;
  if (direction == 0)
    digitalWrite(this->dir, LOW);
  else
    digitalWrite(this->dir, HIGH);
}
void MicroStepper::setMicrostepsMode(byte microstepsMode)
{ //1,2,4,8,16 microstepsMode modes
  //only valid microstep resolutions are accepted
  if (microstepsMode != 1 && microstepsMode != 2 && microstepsMode != 4 && microstepsMode != 8 && microstepsMode != 16)
    return;
  byte prevMicrostepsMode = this->microstepsMode; //middle value to tempery store
  this->microstepsMode = microstepsMode;
  this->numMicrostepsPerCycle = this->numStepsPerCycle * microstepsMode; //numMicrostepsPerCycle will according to the microstepsMode changes
  this->currentMicrostepsAbsPosition = this->currentMicrostepsAbsPosition * microstepsMode / prevMicrostepsMode;
  switch (microstepsMode)
  {
  case 1: //full step
    digitalWrite(this->ms1, LOW);
    digitalWrite(this->ms2, LOW);
    digitalWrite(this->ms3, LOW);
    break;
  case 2: //half step
    digitalWrite(this->ms1, HIGH);
    digitalWrite(this->ms2, LOW);
    digitalWrite(this->ms3, LOW);
    break;
  case 4: //Quarter step
    digitalWrite(this->ms1, LOW);
    digitalWrite(this->ms2, HIGH);
    digitalWrite(this->ms3, LOW);
    break;
  case 8: //eighth step
    digitalWrite(this->ms1, HIGH);
    digitalWrite(this->ms2, HIGH);
    digitalWrite(this->ms3, LOW);
    break;
  case 16: //sixteenth step
    digitalWrite(this->ms1, HIGH);
    digitalWrite(this->ms2, HIGH);
    digitalWrite(this->ms3, HIGH);
    break;
  }
}
void MicroStepper::setCurrentMicrostepsAbsPosition(int currentMicrostepsAbsPosition) { this->currentMicrostepsAbsPosition = currentMicrostepsAbsPosition; }
int MicroStepper::getCurrentMicrostepsAbsPosition() { return this->currentMicrostepsAbsPosition; }
int MicroStepper::getNumMicrostepsPerCycle() { return this->numMicrostepsPerCycle; }
byte MicroStepper::getMicrostepsMode() { return this->microstepsMode; }
void MicroStepper::enable(bool enable)
{
  if (this->hasEnable)
  {
    if (enable)
      digitalWrite(this->notEnable, LOW);
    else
      digitalWrite(this->notEnable, HIGH);
  }
}

void MicroStepper::reset()
{
  if (this->hasEnable)
  {
    digitalWrite(this->notReset, LOW);
    digitalWrite(this->notReset, HIGH);
  }
}

void MicroStepper::sleep(bool sleep)
{
  if (this->hasEnable)
  {
    if (sleep)
      digitalWrite(this->notSleep, LOW);
    else
      digitalWrite(this->notSleep, HIGH);
  }
}

void MicroStepper::takeSteps(int mSteps)
{
  if (mSteps < 0)
    setDirection(1);
  else
    setDirection(1);

  int mStepsLeft = abs(mSteps);
  int nowMStep = 0;
  while (mStepsLeft > 0)
  {
    unsigned long now = micros(); //Gibt die Anzahl der Mikrosekunden zurück, seit das Arduino-Board das aktuelle Programm gestartet hat
    if (now - this->lastStepTime >= this->stepDelay)
    {
      this->lastStepTime = now;
      digitalWrite(this->step, HIGH);
      mStepsLeft--;
      nowMStep += 1;
      digitalWrite(this->step, LOW);
      currentMicrostepsAbsPosition++;
      if (currentMicrostepsAbsPosition > this->numMicrostepsPerCycle)
        currentMicrostepsAbsPosition -= numMicrostepsPerCycle;
    }
  }
}
//----------take steps for home--------
void MicroStepper::takeStepshome(int mSteps)
{
  setDirection(0);
  int mStepsLeft = abs(mSteps);
  while (mStepsLeft > 0)
  {
    unsigned long now = micros(); //Gibt die Anzahl der Mikrosekunden zurück, seit das Arduino-Board das aktuelle Programm gestartet hat
    if (now - this->lastStepTime >= this->stepDelay)
    {
      this->lastStepTime = now;
      digitalWrite(this->step, HIGH);
      mStepsLeft--;
      digitalWrite(this->step, LOW);
      currentMicrostepsAbsPosition--;
    }
  }
}
//-------------take steps for home------------
void MicroStepper::gotoStep(unsigned int gotoMStepNumber)
{
  gotoMStepNumber %= this->numMicrostepsPerCycle;
  int steps = gotoMStepNumber - this->currentMicrostepsAbsPosition;
  if (abs(steps) > numMicrostepsPerCycle / 2)
  {
    if (steps < 0)
      steps += this->numMicrostepsPerCycle;
    else
      steps -= this->numMicrostepsPerCycle;
  }
  this->takeSteps(steps);
}
