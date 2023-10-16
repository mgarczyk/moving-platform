#include <Arduino.h>
#define ENCODER_OPTIMIZE_INTERRUPTS
#include <Encoder.h>

#define ENC_L_A 2
#define ENC_R_A 3
#define DIR_LEFT 4
#define PWM_L 5 
#define PWM_R 6
#define DIR_RIGHT 7 
#define ENC_L_B 8
#define ENC_R_B 9

const int angle_ticks=8600;
const int drift_correction = 5;
const int PWM_step_delay = 100;
const int PWM_val_turn = 150;
const int PWM_max = 200;
const int PWM_step_start = 20;
const int PWM_step_stop = 20;
const float motor_constant = 4752; //encoder PWM freq * motor transmission
const float wheel_diameter = 0.102;
const unsigned int send_dist_ms = 100UL;
unsigned int time_now = millis();
unsigned int time_send = millis();
String read_now = "";
String read_before = "";
long positionLeft  = 0;
long positionRight = 0;
Encoder encLeft(ENC_L_A, ENC_L_B);
Encoder encRight(ENC_R_A, ENC_R_B);


void soft_start(){
 for(int i=0; i<=PWM_max; i+=PWM_step_start){
    analogWrite(PWM_R, i + drift_correction);
    analogWrite(PWM_L, i);
    delay(PWM_step_delay);
  }
}


void drive_correction(){
  long int enc_diff = abs(positionLeft) - positionRight;
  if (read_now=="forward" && enc_diff >= 500){
      analogWrite(PWM_L, PWM_max - drift_correction);
      analogWrite(PWM_R, PWM_max + drift_correction);
  }else if(read_now=="forward" && enc_diff <= -500){
      analogWrite(PWM_L, PWM_max + drift_correction);
      analogWrite(PWM_R, PWM_max - drift_correction);
  }
}

void angle_check(){
  long int avg_enc = (abs(positionLeft) + positionRight)/2;
  if (read_now=="left" && avg_enc>angle_ticks){
    analogWrite(PWM_R, 0);
    analogWrite(PWM_L, 0);
  }
  avg_enc = (abs(positionLeft) + abs(positionRight))/2;
  if (read_now=="right" && avg_enc>angle_ticks){
    analogWrite(PWM_R, 0);
    analogWrite(PWM_L, 0);
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

void stop_now() {
  analogWrite(PWM_R, 0);
  analogWrite(PWM_L, 0);
  
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


int serial_execute(String read_now) {
  if (read_now == "forward") forward();
  else if (read_now == "back") back();
  else if (read_now == "left") left();
  else if (read_now == "right") right();
  else if (read_now == "stop" && (read_before == "right" or read_before == "left")) stop_now();
  else if (read_now == "stop" && (read_before == "forward" or read_before == "back")) soft_stop();
  else if (read_now == "reset"){
    encLeft.write(0);
    encRight.write(0);
  }
  else return 0;
}

void send_dist(long int positionLeft, long int positionRight){
  long int avg_enc = (abs(positionLeft) + positionRight)/2;
  float dist = ((float)avg_enc)/motor_constant * PI * wheel_diameter;
  Serial.println(dist);
  time_send = millis();
}

void read_enc(){
  long int newLeft = encLeft.read();
  long int newRight = encRight.read();
  if (newLeft != positionLeft || newRight != positionRight) {
    positionLeft = newLeft;
    positionRight = newRight;
  }
}

void setup() {
  Serial.flush();
  Serial.begin(115200);
  pinMode(DIR_LEFT, OUTPUT);
  pinMode(DIR_RIGHT, OUTPUT);
  pinMode(PWM_R, OUTPUT);
  pinMode(PWM_L, OUTPUT);
  pinMode(ENC_L_A, INPUT);
  pinMode(ENC_L_B, INPUT);
  pinMode(ENC_R_A, INPUT);
  pinMode(ENC_R_B, INPUT);
}

void loop() {
  time_now = millis();
  if (Serial.available() > 0) {
    read_now = Serial.readStringUntil('\n');
    Serial.flush();
  }
  if (read_now != read_before) serial_execute(read_now);
  read_before = read_now;
  read_enc();
  if(time_now - time_send >= send_dist_ms) send_dist(positionLeft, positionRight);
  drive_correction();
  angle_check();
}
