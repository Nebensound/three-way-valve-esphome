# ESPHome Three-Way Valve Component - AI Agent Instructions

## Project Overview
Custom ESPHome component for controlling a stepper-motor-driven three-way mixing valve. Integrates Python configuration schema with C++ runtime control, using a non-linear mixer curve to map flow values (0-1) to valve positions.

## Hardware Documentation
This componenet ist based on the hardware describeed in this [folder](../docs/hardware/).

## Readme File
The [README file](../README.md) provides the configuration options within esphome YAML files. Everything specifies there should be reflected in the code and vice versa. changes of this file may explicitly be authorized by User.

## Tests
All code need to have corresponding tests within the [tests folder](../tests/). Tests should cover all edge cases and typical use cases. Tests should be written in a way that they can be run automatically.