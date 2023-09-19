#include <Arduino.h>

#define DIR_RIGHT 2
#define DIR_LEFT 4
#define PWM 3

void left(){
 digitalWrite(DIR_RIGHT, HIGH);
 digitalWrite(DIR_LEFT, LOW);
 delay(500);
 analogWrite(PWM, 255);
}

void right(){
 digitalWrite(DIR_RIGHT, LOW);
 digitalWrite(DIR_LEFT, HIGH);
 delay(500);
 analogWrite(PWM, 255);
}

void forward(){
 digitalWrite(DIR_RIGHT, LOW);
 digitalWrite(DIR_LEFT, LOW);
 analogWrite(PWM, 255);
}

void back(){
 digitalWrite(DIR_RIGHT, HIGH);
 digitalWrite(DIR_LEFT, HIGH);
 analogWrite(PWM, 255);
}

void stop(){
 digitalWrite(DIR_RIGHT, HIGH);
 digitalWrite(DIR_LEFT, HIGH);
 analogWrite(PWM, 0);
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
    if (read_data == "forward") forward();
    else if(read_data == "back") back();
    else if(read_data == "left") left();
    else if(read_data == "right") right();
    else stop();
    
    
  }
}
