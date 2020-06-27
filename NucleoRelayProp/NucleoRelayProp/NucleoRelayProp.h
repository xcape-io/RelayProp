/*
  Name:    NucleoRelayProp.h
  Author:  Faure Systems <dev at faure dot systems>
  Editor:  https://github.com/fauresystems
  License: MIT License (c) Faure Systems <dev at faure dot systems>

  Room Relay Prop on STM32 Nucleo 144 (tested with F767ZI).
*/
#ifndef NUCLEORELAYPROP_H
#define NUCLEORELAYPROP_H

#include <LwIP.h>
#include <STM32Ethernet.h>
#include "Prop.h"
#include "PinData.h"
#include <ArduinoJson.h>

class NucleoRelayProp : public Prop
{
  public:
    NucleoRelayProp(const char*,
                  const char*,
                  const char*,
                  const char*,
                  const char*,
                  const int);
    void begin(void(*)(String) = NULL);
    void loop();
    void addPin(String);
    void command(String);
    int pinCount();
    void removeAllPins();
    void removePin(int);
    void removePin(String);
    void setBrokerIpAddress(IPAddress, uint16_t port = 1883);

  private:
    EthernetClient _ethernetClient;

    StaticJsonDocument<1024> _jsondoc; // see memory pool size at https://arduinojson.org/v6/assistant/

    List<PinData*> _pinDataList;
    const char* _settingsTopic;
};

#endif
