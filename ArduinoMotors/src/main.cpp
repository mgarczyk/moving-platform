#include <Arduino.h>

#define DIR_RIGHT 2
#define DIR_LEFT 4
#define PWM 3

void left(){
 digitalWrite(DIR_RIGHT, HIGH);
 digitalWrite(DIR_LEFT, LOW);
 analogWrite(PWM, 200);
}

void left(){
 digitalWrite(DIR_RIGHT, HIGH);
 digitalWrite(DIR_LEFT, LOW);
 analogWrite(PWM, 200);
}

void forward(){
 digitalWrite(DIR_RIGHT, LOW);
 digitalWrite(DIR_LEFT, LOW);
 analogWrite(PWM, 200);
}

void forward(){
 digitalWrite(DIR_RIGHT, HIGH);
 digitalWrite(DIR_LEFT, HIGH);
 analogWrite(PWM, 200);
}

void setup() {
  Serial.begin(9600);
  pinMode(DIR_LEFT, OUTPUT);
  pinMode(DIR_RIGHT, OUTPUT);
  pinMode(PWM, OUTPUT);
}

void loop() {
   if(Serial.available() > 0) { 
    String read_data = Serial.readStringUntil('\n'); 
    Serial.println(read_data); 
  }
}

