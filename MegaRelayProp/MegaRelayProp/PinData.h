/*
  Name:		PinData.h
  Author:  Marie Faure <dev at faure dot systems>
  Editor:  https://github.com/fauresystems
  License: MIT License (c) Marie Faure <dev at faure dot systems>

  Variable wrapper for connected prop.
*/
#ifndef PINDATA_H
#define PINDATA_H

#include "ArduinoProps.h"

class PinData
{
  public:
    PinData(const int, const char *, const char *trueval = NULL, const char *falseval = NULL, bool initial = false);
    PinData::~PinData();
    int pin() const;
    String variable() const;
    
    PropDataLogical *propData;

  private:
    int _pin;
    String _variable;
    String _high;
    String _low;
};

#endif
