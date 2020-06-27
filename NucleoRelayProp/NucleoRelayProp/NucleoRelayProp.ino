/* NucleoRelayProp.ino
   MIT License (c) Faure Systems <dev at faure dot systems>

   Requirements:
   - install ArduinoProps.zip library and dependencies (https://github.com/fauresystems/ArduinoProps)
   - 
*/
#include <LwIP.h>
#include <STM32Ethernet.h>
#include "ArduinoProps.h"
#include "Stm32Millis.h"
extern Stm32MillisClass Stm32Millis;

#include "NucleoRelayProp.h"

// If you're running xcape.io Room software you have to respect prop inbox/outbox
// topicw syntax: Room/[escape room name]/Props/[propsname]/inbox|outbox
// https://xcape.io/go/room

NucleoRelayProp prop(u8"Relay Nucleo", // as MQTT client id, should be unique per client for given broker
                   u8"Room/My room/Props/Relay Nucleo/inbox",
                   u8"Room/My room/Props/Relay Nucleo/outbox",
                   u8"Room/My room/Props/Relay Nucleo/wiring/#",
                   "192.168.1.42", // your MQTT server IP address
                   1883); // your MQTT server port;

byte mac[] = { 0x46, 0x4F, 0xEA, 0x10, 0x20, 0x04 }; //<<< MAKE SURE IT'S UNIQUE IN YOUR NETWORK!!! and not a reserved MAC
IPAddress ip(192, 168, 1, 177); //<<< Set to (0,0,0,0) to get an address from DHCP
// if you don't want to use DNS (and reduce your sketch size)
// use the numeric IP instead of the name for the server:
IPAddress server(192, 168, 1, 42); // numeric IP for Google (no DNS)
//char server[] = "broker.mqtt-dashboard.com";    // name address for mqtt broker (using DNS)

PropDataText board(u8"board");
PropDataInteger wiring(u8"wiring"); // number of outputs configured

void setup()
{
  if (ip == IPAddress(0,0,0,0)) {
    if (!Ethernet.begin(mac)) {
      // if DHCP fails, start with a hard-coded address:
      Ethernet.begin(mac, IPAddress(10, 90, 90, 239));
    }
  }
  else {
    Ethernet.begin(mac, ip);
  }

  delay(1500); // allow the hardware to sort itself out

  // millis() missing in STM32duino
  Stm32Millis.begin();
  
  prop.addData(&board);
  prop.addData(&wiring);

  prop.begin(InboxMessage::run);

  board.setValue(u8"STM32 Nucleo 144");

  // At this point, the broker is not connected yet
}

void loop()
{
  prop.loop();
}

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
