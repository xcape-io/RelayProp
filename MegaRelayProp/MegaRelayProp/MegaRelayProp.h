/*
  Name:    MegaRelayProp.h
  Author:  Marie Faure <dev at faure dot systems>
  Editor:  https://github.com/fauresystems
  License: MIT License (c) Marie Faure <dev at faure dot systems>

  Room Relay Prop on Arduino Mega 2560.
*/
#ifndef MEGARELAYPROP_H
#define MEGARELAYPROP_H

#include <BridgeClient.h>
#include <IPAddress.h>
// do not include <ListLib.h>
#include "Prop.h"
#include "PinData.h"
#include <ArduinoJson.h>

class MegaRelayProp : public Prop
{
  public:
    enum Type { Bridge, Ethernet, WiFi };
    MegaRelayProp(Type,
                  const char*,
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
    Type _type;
    BridgeClient _bridgeClient;
    EthernetClient _ethernetClient;
#if defined(ARDUINO_AVR_UNO_WIFI_REV2) || defined(ARDUINO_SAMD_MKRWIFI1010)  || defined(ARDUINO_SAMD_NANO_33_IOT)  || defined(ARDUINO_SAMD_MKRVIDOR4000)
    WiFiClient _wifiClient;
#endif

    StaticJsonDocument<128> _jsondoc; // see memory pool size at https://arduinojson.org/v6/assistant/

    List<PinData*> _pinDataList;
    char* _settingsTopic;
};




#endif
