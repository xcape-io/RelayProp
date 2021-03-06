/*
  Name:    PropData.cpp
  Author:  Faure Systems <dev at faure dot systems>
  Editor:  https://github.com/fauresystems
  License: MIT License (c) Faure Systems <dev at faure dot systems>

  Variable wrapper for connected prop.
*/

#include "PinData.h"

PinData::PinData(const int pin, const char * id, const char *trueval, const char *falseval, bool initial) {
  _pin = pin;
  _variable = id;
  _high = trueval;
  _low = falseval;
  propData = new PropDataLogical(_variable.c_str(), _high.c_str(), _low.c_str(), initial);
}

int PinData::pin() const {
  return _pin;
}

String PinData::variable() const {
  return _variable;
}
