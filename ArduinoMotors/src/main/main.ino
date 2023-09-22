#include <Arduino.h>

#define DIR_RIGHT 2
#define PWM_R 3
#define DIR_LEFT 4
#define PWM_L 5


const int drift_correction = 5;
const int PWM_step_delay = 100;
const int PWM_val_turn = 150;
const int PWM_max = 200;
const int PWM_step_start = 20;
const int PWM_step_stop = 20;
String read_now = "";
String read_before = "";


void soft_start(){
 for(int i=0; i<=PWM_max; i+=PWM_step_start){
    analogWrite(PWM_R, i + drift_correction);
    analogWrite(PWM_L, i);
    delay(PWM_step_delay);
  }
}

void soft_stop(){
   for(int i=PWM_max; i>=1; i-=PWM_step_stop){
    analogWrite(PWM_R, i);
    analogWrite(PWM_L, i);
    delay(PWM_step_delay);
  }
  analogWrite(PWM_L, 0);
  analogWrite(PWM_R, 0);
}

void left() {
  digitalWrite(DIR_RIGHT,HIGH);
  digitalWrite(DIR_LEFT, LOW);
  analogWrite(PWM_R, PWM_val_turn);
  analogWrite(PWM_L, PWM_val_turn);
}

void right() {
  digitalWrite(DIR_RIGHT, LOW);
  digitalWrite(DIR_LEFT, HIGH);
  analogWrite(PWM_R, PWM_val_turn);
  analogWrite(PWM_L, PWM_val_turn);
}

void forward() {
  digitalWrite(DIR_RIGHT, LOW);
  digitalWrite(DIR_LEFT, LOW);
  soft_start();
 
}

void back() {
  digitalWrite(DIR_RIGHT, HIGH);
  digitalWrite(DIR_LEFT, HIGH);
  soft_start();
}

void stop_motors() {
  soft_stop();
  
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
  Serial.flush();
  pinMode(DIR_LEFT, OUTPUT);
  pinMode(DIR_RIGHT, OUTPUT);
  pinMode(PWM_R, OUTPUT);
  pinMode(PWM_L, OUTPUT);
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
