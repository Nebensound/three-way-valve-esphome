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

    constexpr CurvePoint mixer_curve[] = {
        {0.0f, 0.0f},
        {0.1f, 0.01f},
        {0.2f, 0.1f},
        {0.3f, 0.2f},
        {0.4f, 0.3f},
        {0.5f, 0.5f},
        {0.6f, 0.7f},
        {0.7f, 0.8f},
        {0.8f, 0.9f},
        {0.9f, 0.99f},
        {1.0f, 1.0f}};

    template <size_t N>
    float get_flow(float x, const CurvePoint (&curve)[N])
    {
      if (x <= curve[0].x)
        return curve[0].y;
      if (x >= curve[N - 1].x)
        return curve[N - 1].y;
      for (size_t i = 0; i < N - 1; ++i)
      {
        float x0 = curve[i].x, x1 = curve[i + 1].x;
        float y0 = curve[i].y, y1 = curve[i + 1].y;
        if (x >= x0 && x <= x1)
        {
          float t = (x - x0) / (x1 - x0);
          return y0 + t * (y1 - y0);
        }
      }
      return curve[N - 1].y;
    }

    template <size_t N>
    float get_pos(float y, const CurvePoint (&curve)[N])
    {
      if (y <= curve[0].y)
        return curve[0].x;
      if (y >= curve[N - 1].y)
        return curve[N - 1].x;
      for (size_t i = 0; i < N - 1; ++i)
      {
        float y0 = curve[i].y, y1 = curve[i + 1].y;
        float x0 = curve[i].x, x1 = curve[i + 1].x;
        if (y >= y0 && y <= y1)
        {
          float t = (y - y0) / (y1 - y0);
          return x0 + t * (x1 - x0);
        }
      }
      return curve[N - 1].x;
    }

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
