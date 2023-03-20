#ifndef HOMESWITCH_H
#define HOMESWITCH_H

#include <Arduino.h>

class HomeSwitch
{
protected:
  byte pin;

public:
  HomeSwitch(int pin);
  bool isHome(); // low or high
};
#endif
