# Project description

Projekt polega na stworzeniu autonomicznej platformy mobilnej, zdolnej do omijania przeszkód oraz przemieszczania się na określoną odległość w zadanym kierunku. Robot wykorzystuje technologię LIDAR do detekcji przeszkód i analizowania otoczenia.

## Main components

Raspberry Pi - control unit, responsible for data processing and motion management.

Arduino - intermediary between Raspberry Pi and stepper motors.

Stepper motors - drive the robot, controlled through Arduino.

LIDAR - a system that scans the environment to detect obstacles.

Power supply - suitable power modules for Raspberry Pi, Arduino and motors.

## Software

Python – główny język programowania używany do przetwarzania danych z LIDAR-a i sterowania ruchem robota.</br>

Arduino (C++) - software responsible for controlling stepper motors.

## Functionality
Analysis of the environment - LIDAR collects data about obstacles and transmits it to the Raspberry Pi.

Data processing - Python scripts analyze the data and make route decisions.

Motion control - the Raspberry Pi sends commands to the Arduino, which controls the stepper motors.

Obstacle avoidance - the robot detects obstacles and corrects the route to avoid them.

Movement over a specified distance - the route can be programmed based on set parameters.
