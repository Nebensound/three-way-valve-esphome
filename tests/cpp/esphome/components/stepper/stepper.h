/**
 * @file stepper.h
 * @brief Mock ESPHome stepper component header
 */

#pragma once

#include <cstdint>

namespace esphome
{
  namespace stepper
  {
    class Stepper
    {
    public:
      int32_t current_position = 0;
      int32_t target_position = 0;

      void set_target(int32_t target) { target_position = target; }
    };
  }
}
