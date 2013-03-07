/*
 * Firmata is a generic protocol for communicating with microcontrollers
 * from software on a host computer. It is intended to work with
 * any host computer software package.
 *
 * To download a host software package, please clink on the following link
 * to open the download page in your default browser.
 *
 * http://firmata.org/wiki/Download
 */

/* This sketch accepts strings and raw sysex messages and echos them back.
 *
 * This example code is in the public domain.
 */
#include <Firmata.h>
#include <NewPing.h>
#include <Code7.h>

//CH Added to introduce example sensor
#define TRIGGER_PIN  12  // Arduino pin tied to trigger pin on the ultrasonic sensor.
#define ECHO_PIN     11  // Arduino pin tied to echo pin on the ultrasonic sensor.
#define MAX_DISTANCE 200 // Maximum distance we want to ping for (in centimeters). Maximum sensor distance is rated at 400-500cm.
#define ULTRASONIC_DISTANCE_QUERY 0x01 //the sysex command byte used to indicate a query of the current distance from the ping sensor
#define ULTRASONIC_DISTANCE_RESPONSE 0x01 //the sysex command byte used to indicate the reply, containing the current distance from the ping sensor

NewPing sonar(TRIGGER_PIN, ECHO_PIN, MAX_DISTANCE); // NewPing setup of pins and maximum distance.
Code7 code7;

void stringCallback(char *myString)
{

}


void sysexCallback(byte command, byte argc, byte*argv)
{
  
  switch(command){
    case ULTRASONIC_DISTANCE_QUERY:
    unsigned int us = sonar.ping();
    
    //marshall distance number into 8-bit bytes
    byte unencodedBuffer[4]; //to store the number's separate bytes
    int unencodedCount = 0;
    code7.writeSignedLong(long(us), unencodedBuffer, &unencodedCount);
    
    //encode 8-bit bytes into 7-bit bytes - which requires n + ((n+6)/7) bytes = 5 in this case
    byte encodedBuffer[5]; //to store the 7-bit result of encoding 
    int encodedCount = code7.encodeTo7(unencodedBuffer, unencodedCount, encodedBuffer);

    Serial.write(START_SYSEX);
    Serial.write(ULTRASONIC_DISTANCE_RESPONSE);
    Serial.write(encodedBuffer, encodedCount);
    Serial.write(END_SYSEX);
    
    break;
  }

}

void setup()
{
    Firmata.setFirmwareVersion(0, 1);
    Firmata.attach(STRING_DATA, stringCallback);
    Firmata.attach(START_SYSEX, sysexCallback);
    Firmata.begin(115200);
    
}

void loop()
{
    while(Firmata.available()) {
        Firmata.processInput();
    }
}
