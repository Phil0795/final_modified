#ifndef DC_ENGINE_H
#define DC_ENGINE_H

#include <Arduino.h>

class DC_Engine
{
protected:
  byte pin_A, pin_B, pin_EF;

public:
  DC_Engine(byte, byte, byte); // byte: 8-bit zahl von 0-255
  void setSpeed(char);
  bool getErrorFlag();
};
#endif
