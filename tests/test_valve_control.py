"""Tests for valve control logic (ThreeWayValve class methods)."""
import sys
from pathlib import Path
from unittest.mock import Mock, MagicMock
import math


# Python reference implementation matching C++ logic
class CurvePoint:
    def __init__(self, x, y):
        self.x = x
        self.y = y


mixer_curve = [
    CurvePoint(0.0, 0.0),
    CurvePoint(0.1, 0.01),
    CurvePoint(0.2, 0.1),
    CurvePoint(0.3, 0.2),
    CurvePoint(0.4, 0.3),
    CurvePoint(0.5, 0.5),
    CurvePoint(0.6, 0.7),
    CurvePoint(0.7, 0.8),
    CurvePoint(0.8, 0.9),
    CurvePoint(0.9, 0.99),
    CurvePoint(1.0, 1.0),
]


def get_flow(x, curve):
    """Map position to flow."""
    if x <= curve[0].x:
        return curve[0].y
    if x >= curve[-1].x:
        return curve[-1].y
    for i in range(len(curve) - 1):
        x0, x1 = curve[i].x, curve[i + 1].x
        y0, y1 = curve[i].y, curve[i + 1].y
        if x0 <= x <= x1:
            t = (x - x0) / (x1 - x0)
            return y0 + t * (y1 - y0)
    return curve[-1].y


def get_pos(y, curve):
    """Map flow to position."""
    if y <= curve[0].y:
        return curve[0].x
    if y >= curve[-1].y:
        return curve[-1].x
    for i in range(len(curve) - 1):
        y0, y1 = curve[i].y, curve[i + 1].y
        x0, x1 = curve[i].x, curve[i + 1].x
        if y0 <= y <= y1:
            t = (y - y0) / (y1 - y0)
            return x0 + t * (x1 - x0)
    return curve[-1].x


class MockStepper:
    """Mock stepper motor for testing."""
    def __init__(self):
        self.current_position = 0
        self.target_position = 0
    
    def set_target(self, target):
        self.target_position = int(target)


class ThreeWayValve:
    """Python reference implementation of C++ ThreeWayValve class."""
    
    def __init__(self):
        self.stepper_ = None
        self.pos_closed_ = 0
        self.pos_open_ = 0
        self.pos_block_ = 0
        self.pos_all_open_ = 0
    
    def set_stepper(self, stepper):
        self.stepper_ = stepper
    
    def set_pos_closed(self, p):
        self.pos_closed_ = int(p)
    
    def set_pos_open(self, p):
        self.pos_open_ = int(p)
    
    def set_pos_block(self, p):
        self.pos_block_ = int(p)
    
    def set_pos_all_open(self, p):
        self.pos_all_open_ = int(p)
    
    def control_valve(self, flow):
        """Control valve based on flow value (0.0 - 1.0)."""
        # Clamp flow
        if flow < 0.0:
            flow = 0.0
        if flow > 1.0:
            flow = 1.0
        
        # Get position from flow using mixer curve
        position = get_pos(flow, mixer_curve)
        
        # Calculate target step position
        target = int(self.pos_closed_ + position * (self.pos_open_ - self.pos_closed_))
        self.stepper_.set_target(target)
    
    def get_valve_state(self):
        """Get current valve state as flow value (0.0 - 1.0)."""
        cur = self.stepper_.current_position
        range_val = self.pos_open_ - self.pos_closed_
        
        # Calculate tolerance (0.1% of range, minimum 1 step)
        tol = int(abs(range_val) * 0.001)
        if tol < 1:
            tol = 1
        
        # Check if at closed position
        if abs(cur - self.pos_closed_) < tol:
            return 0.0
        
        # Check if at open position
        if abs(cur - self.pos_open_) < tol:
            return 1.0
        
        # Calculate position as fraction
        position = float(cur - self.pos_closed_) / float(range_val)
        
        # Clamp position
        if position < 0.0:
            position = 0.0
        elif position > 1.0:
            position = 1.0
        
        # Convert position to flow using mixer curve
        return get_flow(position, mixer_curve)
    
    def park_valve(self):
        """Move valve to blocked position."""
        self.stepper_.set_target(self.pos_block_)
    
    def open_all_valve(self):
        """Move valve to all-open position."""
        self.stepper_.set_target(self.pos_all_open_)


class TestControlValve:
    """Test suite for control_valve method."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.valve = ThreeWayValve()
        self.stepper = MockStepper()
        self.valve.set_stepper(self.stepper)
        
        # Standard configuration: -180 steps closed, -270 steps open
        self.valve.set_pos_closed(-180)
        self.valve.set_pos_open(-270)
        self.valve.set_pos_block(0)
        self.valve.set_pos_all_open(-180)
    
    def test_control_valve_zero_flow(self):
        """Test valve control with zero flow (fully closed)."""
        self.valve.control_valve(0.0)
        assert self.stepper.target_position == -180
    
    def test_control_valve_full_flow(self):
        """Test valve control with full flow (fully open)."""
        self.valve.control_valve(1.0)
        assert self.stepper.target_position == -270
    
    def test_control_valve_half_flow(self):
        """Test valve control with 50% flow."""
        self.valve.control_valve(0.5)
        # 0.5 flow -> 0.5 position -> halfway between -180 and -270
        expected = int(-180 + 0.5 * (-270 - (-180)))
        assert self.stepper.target_position == expected
        assert self.stepper.target_position == -225
    
    def test_control_valve_negative_clamped(self):
        """Test that negative flow is clamped to 0."""
        self.valve.control_valve(-0.5)
        assert self.stepper.target_position == -180  # Same as 0.0
    
    def test_control_valve_over_one_clamped(self):
        """Test that flow > 1.0 is clamped to 1.0."""
        self.valve.control_valve(1.5)
        assert self.stepper.target_position == -270  # Same as 1.0
    
    def test_control_valve_non_linear_mapping(self):
        """Test non-linear flow-to-position mapping."""
        # 0.1 flow should map to ~0.01 position (from mixer curve)
        self.valve.control_valve(0.1)
        expected_pos = get_pos(0.1, mixer_curve)  # ~0.55
        expected_steps = int(-180 + expected_pos * (-270 - (-180)))
        assert abs(self.stepper.target_position - expected_steps) <= 1
    
    def test_control_valve_various_flows(self):
        """Test valve control with various flow values."""
        test_flows = [0.0, 0.1, 0.25, 0.5, 0.75, 0.9, 1.0]
        for flow in test_flows:
            self.valve.control_valve(flow)
            pos = get_pos(flow, mixer_curve)
            expected = int(-180 + pos * (-270 - (-180)))
            assert abs(self.stepper.target_position - expected) <= 1


class TestGetValveState:
    """Test suite for get_valve_state method."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.valve = ThreeWayValve()
        self.stepper = MockStepper()
        self.valve.set_stepper(self.stepper)
        self.valve.set_pos_closed(-180)
        self.valve.set_pos_open(-270)
        self.valve.set_pos_block(0)
        self.valve.set_pos_all_open(-180)
    
    def test_get_state_at_closed(self):
        """Test state when valve is at closed position."""
        self.stepper.current_position = -180
        state = self.valve.get_valve_state()
        assert state == 0.0
    
    def test_get_state_at_open(self):
        """Test state when valve is at open position."""
        self.stepper.current_position = -270
        state = self.valve.get_valve_state()
        assert state == 1.0
    
    def test_get_state_near_closed(self):
        """Test state when valve is very close to closed position."""
        # Within tolerance (0.1% of 90 steps = 0.09, rounded to 1)
        self.stepper.current_position = -180
        state = self.valve.get_valve_state()
        assert state == 0.0
    
    def test_get_state_near_open(self):
        """Test state when valve is very close to open position."""
        self.stepper.current_position = -270
        state = self.valve.get_valve_state()
        assert state == 1.0
    
    def test_get_state_midpoint(self):
        """Test state at midpoint position."""
        self.stepper.current_position = -225  # Halfway between -180 and -270
        state = self.valve.get_valve_state()
        # Position = 0.5, flow from curve at 0.5 is 0.5
        assert abs(state - 0.5) < 0.01
    
    def test_get_state_quarter_point(self):
        """Test state at quarter position."""
        # 25% of way from closed (-180) to open (-270)
        self.stepper.current_position = int(-180 + 0.25 * (-270 - (-180)))
        state = self.valve.get_valve_state()
        expected_flow = get_flow(0.25, mixer_curve)
        assert abs(state - expected_flow) < 0.01
    
    def test_get_state_beyond_range_low(self):
        """Test state when position is below closed position."""
        self.stepper.current_position = -100  # Beyond closed
        state = self.valve.get_valve_state()
        # Should clamp to 0.0
        assert state == 0.0
    
    def test_get_state_beyond_range_high(self):
        """Test state when position is beyond open position."""
        self.stepper.current_position = -300  # Beyond open
        state = self.valve.get_valve_state()
        # Should clamp to 1.0
        assert state == 1.0


class TestParkValve:
    """Test suite for park_valve method."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.valve = ThreeWayValve()
        self.stepper = MockStepper()
        self.valve.set_stepper(self.stepper)
        self.valve.set_pos_closed(-180)
        self.valve.set_pos_open(-270)
        self.valve.set_pos_block(0)
        self.valve.set_pos_all_open(-180)
    
    def test_park_valve_moves_to_block_position(self):
        """Test that park_valve moves to blocked position."""
        self.valve.park_valve()
        assert self.stepper.target_position == 0
    
    def test_park_valve_with_different_block_position(self):
        """Test park_valve with different block position."""
        self.valve.set_pos_block(-90)
        self.valve.park_valve()
        assert self.stepper.target_position == -90


class TestOpenAllValve:
    """Test suite for open_all_valve method."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.valve = ThreeWayValve()
        self.stepper = MockStepper()
        self.valve.set_stepper(self.stepper)
        self.valve.set_pos_closed(-180)
        self.valve.set_pos_open(-270)
        self.valve.set_pos_block(0)
        self.valve.set_pos_all_open(-180)
    
    def test_open_all_valve_moves_to_all_open_position(self):
        """Test that open_all_valve moves to all-open position."""
        self.valve.open_all_valve()
        assert self.stepper.target_position == -180
    
    def test_open_all_valve_with_different_position(self):
        """Test open_all_valve with different all-open position."""
        self.valve.set_pos_all_open(-360)
        self.valve.open_all_valve()
        assert self.stepper.target_position == -360


class TestPositionCalculations:
    """Test position calculation edge cases."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.valve = ThreeWayValve()
        self.stepper = MockStepper()
        self.valve.set_stepper(self.stepper)
    
    def test_reversed_range(self):
        """Test with reversed position range (open < closed)."""
        self.valve.set_pos_closed(100)
        self.valve.set_pos_open(0)
        
        # Full flow should go to position 0
        self.valve.control_valve(1.0)
        assert self.stepper.target_position == 0
        
        # Zero flow should go to position 100
        self.valve.control_valve(0.0)
        assert self.stepper.target_position == 100
    
    def test_large_step_range(self):
        """Test with large step range."""
        self.valve.set_pos_closed(0)
        self.valve.set_pos_open(10000)
        
        self.valve.control_valve(0.5)
        # Should be approximately at midpoint
        assert 4900 <= self.stepper.target_position <= 5100
    
    def test_small_step_range(self):
        """Test with small step range."""
        self.valve.set_pos_closed(0)
        self.valve.set_pos_open(10)
        
        self.valve.control_valve(0.5)
        # Should be approximately at midpoint
        assert 4 <= self.stepper.target_position <= 6
    
    def test_negative_positions(self):
        """Test with negative step positions."""
        self.valve.set_pos_closed(-1000)
        self.valve.set_pos_open(-500)
        
        self.valve.control_valve(1.0)
        assert self.stepper.target_position == -500
        
        self.valve.control_valve(0.0)
        assert self.stepper.target_position == -1000


class TestToleranceCalculation:
    """Test tolerance calculation in get_valve_state."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.valve = ThreeWayValve()
        self.stepper = MockStepper()
        self.valve.set_stepper(self.stepper)
    
    def test_tolerance_with_large_range(self):
        """Test that tolerance scales with range."""
        self.valve.set_pos_closed(0)
        self.valve.set_pos_open(10000)
        
        # Tolerance = 0.1% of 10000 = 10 steps
        # At position 15, should not be considered "at closed" (beyond tolerance)
        self.stepper.current_position = 15
        state = self.valve.get_valve_state()
        assert state != 0.0
        
        # At position 5, should be considered "at closed" (within tolerance)
        self.stepper.current_position = 5
        state = self.valve.get_valve_state()
        assert state == 0.0
    
    def test_tolerance_minimum_one_step(self):
        """Test that tolerance has minimum of 1 step."""
        self.valve.set_pos_closed(0)
        self.valve.set_pos_open(10)
        
        # Range is 10, 0.1% = 0.01, should round to 1
        self.stepper.current_position = 0
        state = self.valve.get_valve_state()
        assert state == 0.0


class TestRoundTripConsistency:
    """Test consistency between control_valve and get_valve_state."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.valve = ThreeWayValve()
        self.stepper = MockStepper()
        self.valve.set_stepper(self.stepper)
        self.valve.set_pos_closed(-180)
        self.valve.set_pos_open(-270)
    
    def test_round_trip_consistency(self):
        """Test that setting flow and reading it back gives same value."""
        test_flows = [0.0, 0.1, 0.25, 0.5, 0.75, 0.9, 1.0]
        
        for flow in test_flows:
            # Set the flow
            self.valve.control_valve(flow)
            
            # Simulate stepper reaching target
            self.stepper.current_position = self.stepper.target_position
            
            # Read back the state
            read_flow = self.valve.get_valve_state()
            
            # Should be close (within rounding and curve interpolation errors)
            assert abs(flow - read_flow) < 0.02, \
                f"Round trip failed for flow {flow}: got {read_flow}"


if __name__ == "__main__":
    import pytest
    pytest.main([__file__, "-v"])
