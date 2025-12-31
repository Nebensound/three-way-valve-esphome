#include "three_wah_valve.h"

namespace esphome
{
  namespace three_way_valve
  {

    void ThreeWayValve::control_valve(float flow)
    {
      if (flow < 0.0f)
        flow = 0.0f;
      if (flow > 1.0f)
        flow = 1.0f;

      float position = get_pos(flow, mixer_curve);
      const int32_t target = int32_t(this->pos_closed_ +
                                     position * (this->pos_open_ - this->pos_closed_));
      this->stepper_->set_target(target);
    }

    float ThreeWayValve::get_valve_state()
    {
      const int32_t cur = this->stepper_->current_position;
      const int32_t range = this->pos_open_ - this->pos_closed_;
      int32_t tol = int32_t(std::abs(range) * 0.001f);
      if (tol < 1)
        tol = 1;

      if (std::abs(cur - this->pos_closed_) < tol)
        return 0.0f;
      if (std::abs(cur - this->pos_open_) < tol)
        return 1.0f;

      float position = float(cur - this->pos_closed_) / float(range);
      if (position < 0.0f)
        position = 0.0f;
      else if (position > 1.0f)
        position = 1.0f;

      return get_flow(position, mixer_curve);
    }

    void ThreeWayValve::park_valve()
    {
      this->stepper_->set_target(this->pos_block_);
    }

    void ThreeWayValve::open_all_valve()
    {
      this->stepper_->set_target(this->pos_all_open_);
    }

    valve::ValveTraits ThreeWayValve::get_traits()
    {
      valve::ValveTraits traits;
      traits.set_is_assumed_state(false);
      traits.set_supports_position(true);
      traits.set_supports_toggle(true);
      return traits;
    }

    void ThreeWayValve::control(const valve::ValveCall &call)
    {
      if (call.get_stop())
      {
        return;
      }
      if (call.get_toggle().has_value())
      {
        float cur = this->get_valve_state();
        this->control_valve(cur < 0.5f ? 1.0f : 0.0f);
        return;
      }
      if (call.get_position().has_value())
      {
        float flow = *call.get_position();
        this->control_valve(flow);
        return;
      }
      this->control_valve(0.0f);
    }

  } // namespace three_way_valve
} // namespace esphome
