#pragma once

#include "esphome.h"
#include "esphome/components/valve/valve.h"
#include "esphome/components/stepper/stepper.h"
#include "esphome/core/automation.h"

namespace esphome
{
  namespace three_way_valve
  {

    using stepper::Stepper;

    struct CurvePoint
    {
      float x;
      float y;
    };

    class ThreeWayValve : public valve::Valve, public Component
    {
    public:
      void set_stepper(Stepper *stepper) { this->stepper_ = stepper; }

      int32_t pos_closed_{0};
      int32_t pos_open_{0};
      int32_t pos_block_{0};
      int32_t pos_all_open_{0};

      void set_pos_closed(int32_t p) { this->pos_closed_ = p; }
      void set_pos_open(int32_t p) { this->pos_open_ = p; }
      void set_pos_block(int32_t p) { this->pos_block_ = p; }
      void set_pos_all_open(int32_t p) { this->pos_all_open_ = p; }

      // Curve management
      void add_curve_point(float flow, float position)
      {
        this->mixer_curve_.push_back({flow, position});
      }

      void setup() override {}

      valve::ValveTraits get_traits() override;
      void control(const valve::ValveCall &call) override;

      // Steuerung mit Flusswert 0..1
      void control_valve(float flow);
      void park_valve();
      void open_all_valve();

      // Status als Fluss 0..1
      float get_valve_state();

    protected:
      Stepper *stepper_{nullptr};
      std::vector<CurvePoint> mixer_curve_;

      // Helper methods for curve interpolation
      float get_flow(float x) const
      {
        if (this->mixer_curve_.empty())
          return x; // Fallback to linear if no curve set
        if (x <= this->mixer_curve_[0].x)
          return this->mixer_curve_[0].y;
        if (x >= this->mixer_curve_.back().x)
          return this->mixer_curve_.back().y;
        for (size_t i = 0; i < this->mixer_curve_.size() - 1; ++i)
        {
          float x0 = this->mixer_curve_[i].x, x1 = this->mixer_curve_[i + 1].x;
          float y0 = this->mixer_curve_[i].y, y1 = this->mixer_curve_[i + 1].y;
          if (x >= x0 && x <= x1)
          {
            float t = (x - x0) / (x1 - x0);
            return y0 + t * (y1 - y0);
          }
        }
        return this->mixer_curve_.back().y;
      }

      float get_pos(float y) const
      {
        if (this->mixer_curve_.empty())
          return y; // Fallback to linear if no curve set
        if (y <= this->mixer_curve_[0].y)
          return this->mixer_curve_[0].x;
        if (y >= this->mixer_curve_.back().y)
          return this->mixer_curve_.back().x;
        for (size_t i = 0; i < this->mixer_curve_.size() - 1; ++i)
        {
          float y0 = this->mixer_curve_[i].y, y1 = this->mixer_curve_[i + 1].y;
          float x0 = this->mixer_curve_[i].x, x1 = this->mixer_curve_[i + 1].x;
          if (y >= y0 && y <= y1)
          {
            float t = (y - y0) / (y1 - y0);
            return x0 + t * (x1 - x0);
          }
        }
        return this->mixer_curve_.back().x;
      }
    };

    // Custom actions for three-way valve control
    template <typename... Ts>
    class ThreeWayValveBlockAction : public Action<Ts...>
    {
    public:
      explicit ThreeWayValveBlockAction(ThreeWayValve *valve) : valve_(valve) {}

      void play(Ts... /*x*/) override { this->valve_->park_valve(); }

    protected:
      ThreeWayValve *valve_;
    };

    template <typename... Ts>
    class ThreeWayValveOpenAllAction : public Action<Ts...>
    {
    public:
      explicit ThreeWayValveOpenAllAction(ThreeWayValve *valve) : valve_(valve) {}

      void play(Ts... /*x*/) override { this->valve_->open_all_valve(); }

    protected:
      ThreeWayValve *valve_;
    };

  } // namespace three_way_valve
} // namespace esphome
