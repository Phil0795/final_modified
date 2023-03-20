#include "dc_engine.h"

DC_Engine::DC_Engine(byte pin_A, byte pin_B, byte pin_EF)
{
    this->pin_A = pin_A;
    this->pin_B = pin_B;
    this->pin_EF = pin_EF;

    pinMode(pin_A, OUTPUT);
    pinMode(pin_B, OUTPUT);
    pinMode(pin_EF, INPUT); // for arduino, pinA and pinB send the high or low signal, receive the EF from DC treiber
    digitalWrite(pin_A, 0);
    digitalWrite(pin_B, 0); // dig.write: send a low or high in the pin
}

//sets a speed value from -128 to 127 to a pwm signal on the right pin
//                                                       from 0 to 255
void DC_Engine::setSpeed(char speed)
{   
    analogWrite(pin_A, 0); // write PWM in the pin
    analogWrite(pin_B, 0);

    if (speed > 0)
    {
        analogWrite(pin_A, 0);
        analogWrite(pin_B, 2 * speed + 1); //A low, B high, counerclockwise
    }
    else if (speed < 0)
    {
        analogWrite(pin_A, 2 * abs(speed) - 1);
        analogWrite(pin_B, 0); //A high, B low, clockwise
    }
}



bool DC_Engine::getErrorFlag()
{
    if (digitalRead(pin_EF) == HIGH)
        return true;
    else
        return false;
}
