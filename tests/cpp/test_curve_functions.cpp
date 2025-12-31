/**
 * @file test_curve_functions.cpp
 * @brief Unit tests for curve interpolation functions (get_flow and get_pos)
 *
 * Tests the template functions used for non-linear valve mixing.
 */

#include <gtest/gtest.h>
#include <cmath>

// Include the header under test (includes mock ESPHome headers)
#include "../../components/three_way_valve/valve/three_wah_valve.h"

using namespace esphome::three_way_valve;

/**
 * Test fixture for curve function tests
 */
class CurveFunctionsTest : public ::testing::Test
{
protected:
  // Tolerance for floating point comparisons
  static constexpr float EPSILON = 1e-6f;

  bool near_equal(float a, float b, float epsilon = EPSILON)
  {
    return std::abs(a - b) < epsilon;
  }
};

/**
 * Test exact curve points for get_flow
 */
TEST_F(CurveFunctionsTest, GetFlowExactCurvePoints)
{
  // Test all exact points in the mixer curve
  for (size_t i = 0; i < sizeof(mixer_curve) / sizeof(mixer_curve[0]); ++i)
  {
    float result = get_flow(mixer_curve[i].x, mixer_curve);
    EXPECT_TRUE(near_equal(result, mixer_curve[i].y))
        << "get_flow(" << mixer_curve[i].x << ") = " << result
        << ", expected " << mixer_curve[i].y;
  }
}

/**
 * Test get_flow with position below minimum
 */
TEST_F(CurveFunctionsTest, GetFlowBelowMinimum)
{
  float result = get_flow(-0.5f, mixer_curve);
  EXPECT_EQ(result, mixer_curve[0].y);
}

/**
 * Test get_flow with position above maximum
 */
TEST_F(CurveFunctionsTest, GetFlowAboveMaximum)
{
  float result = get_flow(1.5f, mixer_curve);
  EXPECT_EQ(result, mixer_curve[sizeof(mixer_curve) / sizeof(mixer_curve[0]) - 1].y);
}

/**
 * Test get_flow interpolation at midpoint
 */
TEST_F(CurveFunctionsTest, GetFlowInterpolationMidpoint)
{
  // Between 0.0 and 0.1: midpoint should give average of y values
  float result = get_flow(0.05f, mixer_curve);
  float expected = (0.0f + 0.01f) / 2.0f;
  EXPECT_TRUE(near_equal(result, expected))
      << "get_flow(0.05) = " << result << ", expected " << expected;
}

/**
 * Test get_flow interpolation at quarter point
 */
TEST_F(CurveFunctionsTest, GetFlowInterpolationQuarter)
{
  // Between 0.0 (y=0.0) and 0.1 (y=0.01): at x=0.025 (25%)
  float result = get_flow(0.025f, mixer_curve);
  float expected = 0.0f + 0.25f * (0.01f - 0.0f);
  EXPECT_TRUE(near_equal(result, expected))
      << "get_flow(0.025) = " << result << ", expected " << expected;
}

/**
 * Test get_flow at zero position
 */
TEST_F(CurveFunctionsTest, GetFlowZeroPosition)
{
  float result = get_flow(0.0f, mixer_curve);
  EXPECT_EQ(result, 0.0f);
}

/**
 * Test get_flow at full position
 */
TEST_F(CurveFunctionsTest, GetFlowFullPosition)
{
  float result = get_flow(1.0f, mixer_curve);
  EXPECT_EQ(result, 1.0f);
}

/**
 * Test get_flow monotonic increase
 */
TEST_F(CurveFunctionsTest, GetFlowMonotonicIncrease)
{
  float prev = get_flow(0.0f, mixer_curve);
  for (int i = 1; i <= 100; ++i)
  {
    float x = i * 0.01f;
    float current = get_flow(x, mixer_curve);
    EXPECT_GE(current, prev)
        << "Flow not monotonic at position " << x;
    prev = current;
  }
}

/**
 * Test exact curve points for get_pos
 */
TEST_F(CurveFunctionsTest, GetPosExactCurvePoints)
{
  // Test all exact points in the mixer curve
  for (size_t i = 0; i < sizeof(mixer_curve) / sizeof(mixer_curve[0]); ++i)
  {
    float result = get_pos(mixer_curve[i].y, mixer_curve);
    EXPECT_TRUE(near_equal(result, mixer_curve[i].x))
        << "get_pos(" << mixer_curve[i].y << ") = " << result
        << ", expected " << mixer_curve[i].x;
  }
}

/**
 * Test get_pos with flow below minimum
 */
TEST_F(CurveFunctionsTest, GetPosBelowMinimum)
{
  float result = get_pos(-0.5f, mixer_curve);
  EXPECT_EQ(result, mixer_curve[0].x);
}

/**
 * Test get_pos with flow above maximum
 */
TEST_F(CurveFunctionsTest, GetPosAboveMaximum)
{
  float result = get_pos(1.5f, mixer_curve);
  EXPECT_EQ(result, mixer_curve[sizeof(mixer_curve) / sizeof(mixer_curve[0]) - 1].x);
}

/**
 * Test get_pos interpolation at midpoint
 */
TEST_F(CurveFunctionsTest, GetPosInterpolationMidpoint)
{
  // Between y=0.0 and y=0.01: midpoint y=0.005 should give x between 0.0 and 0.1
  float result = get_pos(0.005f, mixer_curve);
  float expected = (0.0f + 0.1f) / 2.0f;
  EXPECT_TRUE(near_equal(result, expected))
      << "get_pos(0.005) = " << result << ", expected " << expected;
}

/**
 * Test get_pos at zero flow
 */
TEST_F(CurveFunctionsTest, GetPosZeroFlow)
{
  float result = get_pos(0.0f, mixer_curve);
  EXPECT_EQ(result, 0.0f);
}

/**
 * Test get_pos at full flow
 */
TEST_F(CurveFunctionsTest, GetPosFullFlow)
{
  float result = get_pos(1.0f, mixer_curve);
  EXPECT_EQ(result, 1.0f);
}

/**
 * Test get_pos monotonic increase
 */
TEST_F(CurveFunctionsTest, GetPosMonotonicIncrease)
{
  float prev = get_pos(0.0f, mixer_curve);
  for (int i = 1; i <= 100; ++i)
  {
    float y = i * 0.01f;
    float current = get_pos(y, mixer_curve);
    EXPECT_GE(current, prev)
        << "Position not monotonic at flow " << y;
    prev = current;
  }
}

/**
 * Test inverse functions: position -> flow -> position
 */
TEST_F(CurveFunctionsTest, InverseFunctionsPosToFlowToPos)
{
  for (int i = 0; i <= 10; ++i)
  {
    float pos = i * 0.1f;
    float flow = get_flow(pos, mixer_curve);
    float pos_back = get_pos(flow, mixer_curve);
    EXPECT_TRUE(near_equal(pos, pos_back, 1e-5f))
        << "Round trip failed: " << pos << " -> " << flow << " -> " << pos_back;
  }
}

/**
 * Test inverse functions: flow -> position -> flow
 */
TEST_F(CurveFunctionsTest, InverseFunctionsFlowToPosToFlow)
{
  for (int i = 0; i <= 10; ++i)
  {
    float flow = i * 0.1f;
    float pos = get_pos(flow, mixer_curve);
    float flow_back = get_flow(pos, mixer_curve);
    EXPECT_TRUE(near_equal(flow, flow_back, 1e-5f))
        << "Round trip failed: " << flow << " -> " << pos << " -> " << flow_back;
  }
}

/**
 * Test curve non-linearity
 */
TEST_F(CurveFunctionsTest, CurveIsNonLinear)
{
  // At x=0.1, flow should be much less than linear (0.1)
  float result = get_flow(0.1f, mixer_curve);
  EXPECT_LT(result, 0.05f) << "Curve should be non-linear at low positions";

  // At x=0.9, flow should be much more than would be linear from (0.5, 0.5)
  result = get_flow(0.9f, mixer_curve);
  EXPECT_GT(result, 0.95f) << "Curve should be non-linear at high positions";
}

/**
 * Test curve midpoint balance
 */
TEST_F(CurveFunctionsTest, CurveMidpointBalance)
{
  float result = get_flow(0.5f, mixer_curve);
  EXPECT_TRUE(near_equal(result, 0.5f))
      << "Curve should pass through (0.5, 0.5)";
}

int main(int argc, char **argv)
{
  ::testing::InitGoogleTest(&argc, argv);
  return RUN_ALL_TESTS();
}
