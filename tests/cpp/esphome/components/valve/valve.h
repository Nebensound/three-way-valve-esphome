/**
 * @file valve.h
 * @brief Mock ESPHome valve component header
 */

#pragma once

namespace esphome
{
  namespace valve
  {
    class ValveCall
    {
    public:
      bool get_stop() const { return stop_; }
      std::optional<bool> get_toggle() const { return toggle_; }
      std::optional<float> get_position() const { return position_; }

      bool stop_ = false;
      std::optional<bool> toggle_;
      std::optional<float> position_;
    };

    class ValveTraits
    {
    public:
      virtual void set_is_assumed_state(bool /*state*/) {}
      virtual void set_supports_position(bool /*supported*/) {}
      virtual void set_supports_toggle(bool /*supported*/) {}
      virtual ~ValveTraits() = default;
    };

    class Valve
    {
    public:
      virtual ValveTraits get_traits() { return ValveTraits(); }
      virtual void control(const ValveCall & /*call*/) {}
      virtual ~Valve() = default;
    };
  }
}
