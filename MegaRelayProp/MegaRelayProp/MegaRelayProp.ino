/* MegaRelayBridgeProp.ino
   MIT License (c) Faure Systems <dev at faure dot systems>

   Requirements:
   - install ArduinoProps.zip library and dependencies (https://github.com/fauresystems/ArduinoProps)
*/
#include <Bridge.h>
#include "ArduinoProps.h"
#include "MegaRelayProp.h"

// Uncomment if the board is connected via WiFi
#define REPORT_WIFI_RSSI

// If you're running xcape.io Room software you have to respect prop inbox/outbox
// topicw syntax: Room/[escape room name]/Props/[propsname]/inbox|outbox
// https://xcape.io/go/room

MegaRelayProp prop(MegaRelayProp::Bridge,
                   u8"Relay Mega", // as MQTT client id, should be unique per client for given broker
                   u8"Room/My room/Props/Relay Mega/inbox",
                   u8"Room/My room/Props/Relay Mega/outbox",
                   u8"Room/My room/Props/Relay Mega/wiring/#",
                   "192.168.1.42", // your MQTT server IP address
                   1883); // your MQTT server port;

#if defined(REPORT_WIFI_RSSI)
PropDataText rssi(u8"rssi");
void readRssi(); // forward
PropAction readRssiAction = PropAction(30000, readRssi);
#endif

PropDataText board(u8"board");
PropDataInteger wiring(u8"wiring"); // number of outputs configured

void setup()
{
  Bridge.begin();
  //updateBrokerAdressFromFile("/root/broker", &prop); // if you're running our Escape Room control software (Room 2.0)

#if defined(REPORT_WIFI_RSSI)
  prop.addData(&rssi);
#endif

  prop.addData(&board);
  prop.addData(&wiring);

  prop.begin(InboxMessage::run);

  board.setValue(u8"Mega with bridge");


#if defined(REPORT_WIFI_RSSI)
  readRssi();
#endif
  // At this point, the broker is not connected yet
}

void loop()
{
  prop.loop();

#if defined(REPORT_WIFI_RSSI)
  readRssiAction.check();
#endif
}

#if defined(REPORT_WIFI_RSSI)
void readRssi()
{
  Process _process; // a process call takes about 50 milliseconds
  _process.runShellCommand("cat /proc/net/wireless | awk 'NR==3 {print $4}'");
  while (_process.running());
  String b;
  while (_process.available() > 0) {
    char c = _process.read();
    b += c;
  }
  b.trim();
  rssi.setValue(b + " dBm");
}
#endif

void InboxMessage::run(String a) {

  if (a.startsWith(u8"{")) // pin JSON wiring
  {
    prop.addPin(a);
    wiring.setValue(prop.pinCount());
    prop.sendAllData();
  }
  else if (a.startsWith(u8"clear:")) // pin to remove
  {
    if (a == u8"clear:all") {
      prop.sendMesg(String(u8"Start"));
      delay(1000);
      prop.removeAllPins();
      prop.sendDone(a);
    } else {
      prop.removePin(a);
      prop.sendDone(a);
    }
    wiring.setValue(prop.pinCount());
    prop.sendAllData();
  }
  else if (a == u8"app:startup" || a == u8"app:data")
  {
    prop.sendAllData();
    prop.sendDone(a);
  }
  else if (a == u8"reset-mcu")
  {
    prop.resetMcu(); // we prefer SSH command: echo %BROKER%> /root/broker && reset-mcu
  }
  else
  {
    prop.command(a);
  }
}

void updateBrokerAdressFromFile(const char* broker_file, BridgeProp* prop)
{
  // broker IP address is stored in Linino file systems and updated with ssh command by Room 2.0
  IPAddress ip;

  Process _process;
  _process.begin("cat");
  _process.addParameter(broker_file); // for ssh remotely set broker address
  _process.run(); // run the process and wait for its termination
  String b;
  while (_process.available() > 0) {
    char c = _process.read();
    b += c;
  }
  b.trim();

  if (ip.fromString(b.c_str())) prop->setBrokerIpAddress(ip);
}
