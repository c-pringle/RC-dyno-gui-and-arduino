
#include <Adafruit_INA219.h>
#include <Wire.h>
#include <Adafruit_BusIO_Register.h>
#include <Servo.h>
#include <CommandParser.h>

Servo ESC;
typedef CommandParser<> MyCommandParser;
MyCommandParser parser;

Adafruit_INA219 ina219;
volatile unsigned long pulseInterval = 0;
const int pulsesPerRev = 3; //for three magnets on the flywheel
volatile unsigned int pulseCount = 0;
unsigned long rpmCalcInterval = 1000; // 1 second
unsigned long lastRpmCalcTime = 0;
unsigned long lastRead = 0;
unsigned long readInterval = 500; // 500 ms
bool running = false;
unsigned long runStartTime = 0;
unsigned long runDuration = 10000; //10 seconds
float rpm = 0;
float Prevrpm  =0;
float power = 0;
int count = 0;
float shuntvoltage = 0;
float busvoltage = 0;
float current_A = 0;
float loadvoltage = 0;
volatile unsigned long lastPulseTime = 0;
void countPulse() {
  unsigned long now = micros();;
  pulseInterval = now - lastPulseTime;
  lastPulseTime = now;
}

void setup() {
  Serial.begin(9600);
  ESC.attach(9);
  ESC.writeMicroseconds(1500);

  pinMode(2, INPUT_PULLUP); // Hall sensor
  attachInterrupt(digitalPinToInterrupt(2), countPulse, FALLING);
  pinMode(13, OUTPUT);      // LED indicator

  ina219.begin();
  ina219.setCalibration_10V_50A();

  Serial.println("Ready");
}

void loop() {
  // Handle serial commands
  if (Serial.available()) {
    String x = Serial.readStringUntil('\n');
    x.trim();

    if (x.startsWith("R") && x.indexOf("/s") != -1) {
      String durationStr = x.substring(1, x.length() - 2);
      runDuration = durationStr.toInt() * 1000;
      Serial.print("Start for ");
      Serial.print(runDuration / 1000);
      Serial.println(" seconds");
      ESC.writeMicroseconds(1700);
      runStartTime = millis();
      running = true;
    } else if (x == "K") {
      Serial.println("Stop");
      ESC.writeMicroseconds(1500);
      count = 0;
      pulseCount = 0;
      pulseInterval = 0;
      power = 0;

      rpm = 0;
      lastRpmCalcTime = millis();
      running = false;
    } else if (x.endsWith("/e")) {
      x.replace("/e", "");
      ESC.writeMicroseconds(x.toInt());
    }
  }

  // Stop motor after duration
  if (running && millis() - runStartTime >= runDuration) {
    ESC.writeMicroseconds(1500);
    running = false;
    count = 0;
    pulseCount = 0;
    pulseInterval = 0;
    power = 0;
    rpm = 0;
    lastRpmCalcTime = millis();

  }

  // Calculate RPM every second
  unsigned long now = micros();
  if (running && pulseInterval > 0 && (now - lastPulseTime) < 500000) {
    rpm = (60.0 * 1000000.0) / (pulseInterval * pulsesPerRev);
    
  } else if (!running || (now - lastPulseTime) >= 500000) {
    rpm = 0;
  }



  // Send data every 500 ms
  if (millis() - lastRead > readInterval) {
    lastRead = millis();

    //power = ina219.getPower_mW();
   
    shuntvoltage = ina219.getShuntVoltage_mV();
    busvoltage = ina219.getBusVoltage_V();
    current_A = ina219.getCurrent_mA(); 
    loadvoltage = busvoltage + (shuntvoltage / 1000);
    power = busvoltage * current_A;

    // Send all data in one block
    Serial.print("RPM: "); Serial.print(rpm); Serial.print("/b\n");
    Serial.print("Voltage: "); Serial.print(busvoltage); Serial.print("/v\n");
    Serial.print("Current: "); Serial.print(current_A); Serial.print("/c\n");
    Serial.print("Power: "); Serial.print(power); Serial.print("/p\n");
    Serial.print("Count: "); Serial.println(count);
  }
}
