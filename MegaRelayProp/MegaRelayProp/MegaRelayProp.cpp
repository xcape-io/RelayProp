/*
  Name:    MegaRelayProp.cpp
  Author:  Marie Faure <dev at faure dot systems>
  Editor:  https://github.com/fauresystems
  License: MIT License (c) Marie Faure <dev at faure dot systems>

  Room Relay Prop on Arduino Mega 2560 with and Dragino Yun shield.
*/

#include "ArduinoProps.h"
#include "MegaRelayProp.h"

MegaRelayProp::MegaRelayProp(Type type,
                             const char* client_id,
                             const char* in_box,
                             const char* out_box,
                             const char* topic_settings,
                             const char* broker,
                             const int port)
  : Prop
    (client_id, in_box, out_box, broker, port)
{
  _type = type;
  _settingsTopic = topic_settings;
  _client.setClient(_bridgeClient);
}

void MegaRelayProp::begin(void(*on_message)(String))
{
  if (on_message) onInboxMessageReceived = on_message;
}

void MegaRelayProp::loop()
{
  if (_client.connected())
  {
    _client.loop();
  }
  else if (millis() > _nextReconAttempt)
  {
    _nextReconAttempt += 5000L;

    if (_client.connect(clientId, outbox, 2, true, "DISCONNECTED"))
    {
      _client.publish(outbox, "CONNECTED", true);
      _client.subscribe(inbox, 1);  // max QoS is 1 for PubSubClient subsciption
      _client.subscribe(String(_settingsTopic).c_str(), 1);
      _nextReconAttempt = 0L;
    }
  }

  if (_sendDataAction.tick()) checkDataChanges(); // send data changes if any
}

void MegaRelayProp::addPin(String message)
{
  deserializeJson(_jsondoc, message);

  int pin = _jsondoc["p"];
  int initial = _jsondoc["i"];
  char variable[32];
  char high[18];
  char low[18];

  strlcpy(variable, _jsondoc["v"], sizeof(variable));
  strlcpy(high, _jsondoc["a"][0], sizeof(high));
  strlcpy(low, _jsondoc["a"][1] , sizeof(low));

  // QoS is 1 so teh prop can receive the message more than once
  for (int i = 0; i < _pinDataList.Count(); i++)
  {
    PinData* data = _pinDataList[i];

    if (data->pin() == pin) removePin(pin);
  }

  PinData* data = new PinData(pin, variable, high, low, initial);
  _pinDataList.Add(data);
  addData(data->propData);
  pinMode(pin, OUTPUT);
  sendMesg(String(u8"Add pin: ") + message);
}

void MegaRelayProp::command(String a)
{
  int semicol = a.lastIndexOf(':');
  String predicate = a.substring(0, semicol);
  String command = a.substring(semicol + 1);

  if (!predicate.length() || !command.length()) {
    sendOmit(a);
  } else  if (command != u8"1" && command != u8"0") {
    sendOmit(a);
  } else if (predicate.endsWith(u8"/*")) {
    predicate.remove(predicate.length() - 1, 1);
    for (int i = 0; i < _pinDataList.Count(); i++)
    {
      PinData* d = _pinDataList[i];
      if (d->variable().startsWith(predicate)) {
        if (command == u8"1") {
          digitalWrite(d->pin(), HIGH);
          d->propData->setValue(true);
        } else if (command == u8"0") {
          digitalWrite(d->pin(), LOW);
          d->propData->setValue(false);
        }
      }
    }
    sendDataChanges();
    sendDone(a);
    return;
  } else {
    for (int i = 0; i < _pinDataList.Count(); i++)
    {
      PinData* d = _pinDataList[i];
      if (d->variable() == predicate) {
        if (command == u8"1") {
          digitalWrite(d->pin(), HIGH);
          d->propData->setValue(true);
          sendDataChanges();
          sendDone(a);
        } else if (command == u8"0") {
          digitalWrite(d->pin(), LOW);
          d->propData->setValue(false);
          sendDataChanges();
          sendDone(a);
        } else {
          sendOmit(a);
        }

        return;
      }
    }
    sendOmit(a);
  }
}

int MegaRelayProp::pinCount()
{
  return _pinDataList.Count();
}

void MegaRelayProp::removeAllPins()
{
  List<PinData*> list_of_references;

  for (int i = 0; i < _pinDataList.Count(); i++)
  {
    PinData* data = _pinDataList[i];
    list_of_references.Add(data);

    for (int j = 0; j < _dataTable.Count(); j++)
    {
      if (_dataTable[j] == data->propData)
      {
        _dataTable.Remove(j);
        break;
      }
    }
  }

  _pinDataList.Clear();

  for (int k = 0; k < list_of_references.Count(); k++)
  {
    delete list_of_references[k];
  }
}

void MegaRelayProp::removePin(int pin)
{
  String action("clear:D");
  action += String(pin);
  removePin(action);
}

void MegaRelayProp::removePin(String action)
{
  int pin = action.substring(7).toInt();  // clear:D

  if (pin || action.endsWith(u8"D0")) {
    for (int i = 0; i < _pinDataList.Count(); i++)
    {
      PinData* data = _pinDataList[i];

      if (data->pin() == pin)
      {
        for (int j = 0; j < _dataTable.Count(); j++)
        {
          if (_dataTable[j] == data->propData)
          {
            _dataTable.Remove(j);
            break;
          }
        }

        _pinDataList.Remove(i);
        delete data;
        pinMode(pin, INPUT);
        return;
      }
    }
  }

  sendMesg(u8"Warning: pin not found in settings for " + action);
  return;
}

void MegaRelayProp::setBrokerIpAddress(IPAddress ip, uint16_t port)
{
  _brokerIpAddress = ip;
  _client.setServer(_brokerIpAddress, port);
}
