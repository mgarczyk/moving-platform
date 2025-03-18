# Project description

The project involves the creation of an autonomous mobile platform capable of avoiding obstacles and moving a specified distance in a set direction. The robot uses LIDAR technology to detect obstacles and analyze its surroundings.

## Main components

Raspberry Pi - control unit, responsible for data processing and motion management. </br>

Arduino - intermediary between Raspberry Pi and stepper motors. </br>

Stepper motors - drive the robot, controlled through Arduino. </br>

LIDAR - a system that scans the environment to detect obstacles. </br>

Power supply - suitable power modules for Raspberry Pi, Arduino and motors. </br>

## Software

Python - the main programming language used to process LIDAR data and control the robot's movement. </br>

Arduino (C++) - software responsible for controlling stepper motors. </br>

## Functionality
Analysis of the environment - LIDAR collects data about obstacles and transmits it to the Raspberry Pi. </br>

Data processing - Python scripts analyze the data and make route decisions. </br>

Motion control - the Raspberry Pi sends commands to the Arduino, which controls the stepper motors. </br>

Obstacle avoidance - the robot detects obstacles and corrects the route to avoid them. </br>

Movement over a specified distance - the route can be programmed based on set parameters. </br>
