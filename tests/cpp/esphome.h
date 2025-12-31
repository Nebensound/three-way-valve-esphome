/**
 * @file esphome.h
 * @brief Mock ESPHome header for standalone C++ testing
 */

#pragma once

// Mock minimal ESPHome core functionality
namespace esphome
{
  class Component
  {
  public:
    virtual void setup() {}
    virtual ~Component() = default;
  };
}
