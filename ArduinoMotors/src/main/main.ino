#include <Arduino.h>

#define DIR_RIGHT 2
#define PWM_R 3
#define DIR_LEFT 4
#define PWM_L 5

void soft_star()

void left() {
  digitalWrite(DIR_RIGHT,LOW);
  digitalWrite(DIR_LEFT, HIGH);
  analogWrite(PWM_R, 120);
  analogWrite(PWM_L, 120);
}

void right() {
  digitalWrite(DIR_RIGHT, HIGH);
  digitalWrite(DIR_LEFT, LOW);
  analogWrite(PWM_R, 120);
  analogWrite(PWM_L, 120);
}

void forward() {
  digitalWrite(DIR_RIGHT, LOW);
  digitalWrite(DIR_LEFT, LOW);
  for(int i=1; i<=200; i+=25){
    analogWrite(PWM_R, i);
    analogWrite(PWM_L, i);
    delay(25);
  }
  analogWrite(PWM_R, 200);
  analogWrite(PWM_L, 200);
}

void back() {
  digitalWrite(DIR_RIGHT, HIGH);
  digitalWrite(DIR_LEFT, HIGH);
  for(int i=1; i<=200; i+=25){
    analogWrite(PWM_R, i);
    analogWrite(PWM_L, i);
    delay(25);
  }
  analogWrite(PWM_R, 200);
  analogWrite(PWM_L, 200);

}

void stop_motors() {
  digitalWrite(DIR_RIGHT, HIGH);
  digitalWrite(DIR_LEFT, HIGH);
  analogWrite(PWM_R, 0);
  analogWrite(PWM_L, 0);
}

void choose_dir(String read_now) {
  if (read_now == "forward") forward();
  else if (read_now == "back") back();
  else if (read_now == "left") left();
  else if (read_now == "right") right();
  else if (read_now == "stop" ) stop_motors();
  else return;
}

void setup() {
  Serial.begin(9600);
  pinMode(DIR_LEFT, OUTPUT);
  pinMode(DIR_RIGHT, OUTPUT);
  pinMode(PWM_R, OUTPUT);
}



void loop() {
  if (Serial.available() > 0) {
    read_now = Serial.readStringUntil('\n');
    Serial.println(read_now);
    if (read_now != read_before) {
      choose_dir(read_now);
    }
    read_before = read_now;


  }
}