/**
 * @file automation.h
 * @brief Mock ESPHome automation header
 */

#pragma once

namespace esphome
{
  template <typename... Ts>
  class Action
  {
  public:
    virtual void play(Ts... x) = 0;
    virtual ~Action() = default;
  };
}
