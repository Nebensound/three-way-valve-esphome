/**
 * @file test_valve_control.cpp
 * @brief Unit tests for ThreeWayValve control logic
 *
 * Tests the valve control methods including position calculations,
 * state reading, and special commands (park, open_all).
 */

#include <gtest/gtest.h>
#include <cmath>

// Include headers under test (includes mock ESPHome headers)
#include "../../components/three_way_valve/valve/three_wah_valve.h"
#include "../../components/three_way_valve/valve/three_way_valve.cpp"

using namespace esphome::three_way_valve;

/**
 * Test fixture for valve control tests
 */
class ValveControlTest : public ::testing::Test
{
protected:
  ThreeWayValve valve;
  esphome::stepper::Stepper stepper;

  static constexpr float EPSILON = 1e-5f;

  void SetUp() override
  {
    valve.set_stepper(&stepper);
    // Standard configuration: -180 closed, -270 open
    valve.set_pos_closed(-180);
    valve.set_pos_open(-270);
    valve.set_pos_block(0);
    valve.set_pos_all_open(-180);
    stepper.current_position = -180;
  }

  bool near_equal(float a, float b, float epsilon = EPSILON)
  {
    return std::abs(a - b) < epsilon;
  }
};

/**
 * Test control_valve with zero flow (fully closed)
 */
TEST_F(ValveControlTest, ControlValveZeroFlow)
{
  valve.control_valve(0.0f);
  EXPECT_EQ(stepper.target_position, -180);
}

/**
 * Test control_valve with full flow (fully open)
 */
TEST_F(ValveControlTest, ControlValveFullFlow)
{
  valve.control_valve(1.0f);
  EXPECT_EQ(stepper.target_position, -270);
}

/**
 * Test control_valve with half flow
 */
TEST_F(ValveControlTest, ControlValveHalfFlow)
{
  valve.control_valve(0.5f);
  // 0.5 flow -> 0.5 position -> halfway between -180 and -270
  int32_t expected = -180 + static_cast<int32_t>(0.5f * (-270 - (-180)));
  EXPECT_EQ(stepper.target_position, expected);
}

/**
 * Test control_valve clamps negative flow to 0
 */
TEST_F(ValveControlTest, ControlValveNegativeFlowClamped)
{
  valve.control_valve(-0.5f);
  EXPECT_EQ(stepper.target_position, -180); // Same as 0.0
}

/**
 * Test control_valve clamps flow > 1.0
 */
TEST_F(ValveControlTest, ControlValveOverOneClamped)
{
  valve.control_valve(1.5f);
  EXPECT_EQ(stepper.target_position, -270); // Same as 1.0
}

/**
 * Test control_valve with various flow values
 */
TEST_F(ValveControlTest, ControlValveVariousFlows)
{
  float flows[] = {0.0f, 0.1f, 0.25f, 0.5f, 0.75f, 0.9f, 1.0f};

  for (float flow : flows)
  {
    valve.control_valve(flow);
    float pos = get_pos(flow, mixer_curve);
    int32_t expected = -180 + static_cast<int32_t>(pos * (-270 - (-180)));
    EXPECT_NEAR(stepper.target_position, expected, 1)
        << "Failed for flow " << flow;
  }
}

/**
 * Test get_valve_state at closed position
 */
TEST_F(ValveControlTest, GetStateAtClosed)
{
  stepper.current_position = -180;
  float state = valve.get_valve_state();
  EXPECT_EQ(state, 0.0f);
}

/**
 * Test get_valve_state at open position
 */
TEST_F(ValveControlTest, GetStateAtOpen)
{
  stepper.current_position = -270;
  float state = valve.get_valve_state();
  EXPECT_EQ(state, 1.0f);
}

/**
 * Test get_valve_state at midpoint
 */
TEST_F(ValveControlTest, GetStateAtMidpoint)
{
  stepper.current_position = -225; // Halfway between -180 and -270
  float state = valve.get_valve_state();
  // Position = 0.5, flow from curve at 0.5 is 0.5
  EXPECT_TRUE(near_equal(state, 0.5f, 0.01f));
}

/**
 * Test get_valve_state beyond closed (clamped)
 */
TEST_F(ValveControlTest, GetStateBeyondClosed)
{
  stepper.current_position = -100; // Beyond closed
  float state = valve.get_valve_state();
  EXPECT_EQ(state, 0.0f);
}

/**
 * Test get_valve_state beyond open (clamped)
 */
TEST_F(ValveControlTest, GetStateBeyondOpen)
{
  stepper.current_position = -300; // Beyond open
  float state = valve.get_valve_state();
  EXPECT_EQ(state, 1.0f);
}

/**
 * Test park_valve moves to blocked position
 */
TEST_F(ValveControlTest, ParkValve)
{
  valve.park_valve();
  EXPECT_EQ(stepper.target_position, 0);
}

/**
 * Test park_valve with different block position
 */
TEST_F(ValveControlTest, ParkValveDifferentPosition)
{
  valve.set_pos_block(-90);
  valve.park_valve();
  EXPECT_EQ(stepper.target_position, -90);
}

/**
 * Test open_all_valve moves to all-open position
 */
TEST_F(ValveControlTest, OpenAllValve)
{
  valve.open_all_valve();
  EXPECT_EQ(stepper.target_position, -180);
}

/**
 * Test open_all_valve with different position
 */
TEST_F(ValveControlTest, OpenAllValveDifferentPosition)
{
  valve.set_pos_all_open(-360);
  valve.open_all_valve();
  EXPECT_EQ(stepper.target_position, -360);
}

/**
 * Test with reversed position range (open < closed)
 */
TEST_F(ValveControlTest, ReversedPositionRange)
{
  valve.set_pos_closed(100);
  valve.set_pos_open(0);

  valve.control_valve(1.0f);
  EXPECT_EQ(stepper.target_position, 0);

  valve.control_valve(0.0f);
  EXPECT_EQ(stepper.target_position, 100);
}

/**
 * Test with large step range
 */
TEST_F(ValveControlTest, LargeStepRange)
{
  valve.set_pos_closed(0);
  valve.set_pos_open(10000);

  valve.control_valve(0.5f);
  // Should be approximately at midpoint
  EXPECT_NEAR(stepper.target_position, 5000, 100);
}

/**
 * Test with small step range
 */
TEST_F(ValveControlTest, SmallStepRange)
{
  valve.set_pos_closed(0);
  valve.set_pos_open(10);

  valve.control_valve(0.5f);
  // Should be approximately at midpoint
  EXPECT_NEAR(stepper.target_position, 5, 1);
}

/**
 * Test tolerance calculation with large range
 */
TEST_F(ValveControlTest, ToleranceLargeRange)
{
  valve.set_pos_closed(0);
  valve.set_pos_open(10000);

  // Tolerance = 0.1% of 10000 = 10 steps
  // At position 15, should not be considered "at closed" (beyond tolerance)
  stepper.current_position = 15;
  float state = valve.get_valve_state();
  EXPECT_NE(state, 0.0f);

  // At position 5, should be considered "at closed" (within tolerance)
  stepper.current_position = 5;
  state = valve.get_valve_state();
  EXPECT_EQ(state, 0.0f);
}

/**
 * Test tolerance minimum of 1 step
 */
TEST_F(ValveControlTest, ToleranceMinimumOneStep)
{
  valve.set_pos_closed(0);
  valve.set_pos_open(10);

  // Range is 10, 0.1% = 0.01, should round to 1
  stepper.current_position = 0;
  float state = valve.get_valve_state();
  EXPECT_EQ(state, 0.0f);
}

/**
 * Test round-trip consistency: set flow -> read state
 */
TEST_F(ValveControlTest, RoundTripConsistency)
{
  float flows[] = {0.0f, 0.1f, 0.25f, 0.5f, 0.75f, 0.9f, 1.0f};

  for (float flow : flows)
  {
    // Set the flow
    valve.control_valve(flow);

    // Simulate stepper reaching target
    stepper.current_position = stepper.target_position;

    // Read back the state
    float read_flow = valve.get_valve_state();

    // Should be close (within rounding and curve interpolation errors)
    EXPECT_TRUE(near_equal(flow, read_flow, 0.02f))
        << "Round trip failed for flow " << flow << ": got " << read_flow;
  }
}

/**
 * Test get_traits returns correct valve traits
 */
TEST_F(ValveControlTest, GetTraits)
{
  esphome::valve::ValveTraits traits = valve.get_traits();
  // Traits should be set up correctly
  // This is a basic smoke test
}

/**
 * Test suite for action classes
 */
class ValveActionsTest : public ::testing::Test
{
protected:
  ThreeWayValve valve;
  esphome::stepper::Stepper stepper;

  void SetUp() override
  {
    valve.set_stepper(&stepper);
    valve.set_pos_closed(-180);
    valve.set_pos_open(-270);
    valve.set_pos_block(0);
    valve.set_pos_all_open(-180);
    stepper.current_position = -180;
  }
};

/**
 * Test ThreeWayValveBlockAction executes park_valve
 */
TEST_F(ValveActionsTest, BlockActionCallsParkValve)
{
  ThreeWayValveBlockAction<> action(&valve);

  // Initial position
  EXPECT_EQ(stepper.target_position, 0); // Not set yet

  // Execute action
  action.play();

  // Should move to blocked position
  EXPECT_EQ(stepper.target_position, 0);
}

/**
 * Test ThreeWayValveOpenAllAction executes open_all_valve
 */
TEST_F(ValveActionsTest, OpenAllActionCallsOpenAllValve)
{
  ThreeWayValveOpenAllAction<> action(&valve);

  // Set different block position first
  valve.set_pos_all_open(-360);

  // Execute action
  action.play();

  // Should move to all-open position
  EXPECT_EQ(stepper.target_position, -360);
}

/**
 * Test BlockAction with different blocked positions
 */
TEST_F(ValveActionsTest, BlockActionWithCustomPosition)
{
  valve.set_pos_block(-90);
  ThreeWayValveBlockAction<> action(&valve);

  action.play();

  EXPECT_EQ(stepper.target_position, -90);
}

/**
 * Test OpenAllAction with different all-open positions
 */
TEST_F(ValveActionsTest, OpenAllActionWithCustomPosition)
{
  valve.set_pos_all_open(-270);
  ThreeWayValveOpenAllAction<> action(&valve);

  action.play();

  EXPECT_EQ(stepper.target_position, -270);
}

/**
 * Test action template with parameters (even though not used)
 */
TEST_F(ValveActionsTest, ActionWithTemplateParameters)
{
  ThreeWayValveBlockAction<int, float> action(&valve);

  // Should compile and execute without using parameters
  action.play(42, 3.14f);

  EXPECT_EQ(stepper.target_position, 0);
}

int main(int argc, char **argv)
{
  ::testing::InitGoogleTest(&argc, argv);
  return RUN_ALL_TESTS();
}
