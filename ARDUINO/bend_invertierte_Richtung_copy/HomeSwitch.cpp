#include "HomeSwitch.h"

HomeSwitch::HomeSwitch(int pin)
{
    this->pin = pin;

    pinMode(pin, INPUT_PULLUP);
}

bool HomeSwitch::isHome()
{
    if (digitalRead(pin) == HIGH)
        return true; // the high volt

    else
        return false;
}
