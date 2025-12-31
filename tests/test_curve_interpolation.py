"""Tests for curve interpolation functions (get_flow and get_pos)."""
import sys
from pathlib import Path

# This test file tests the C++ template functions
# Since we can't directly test C++ code from Python without compilation,
# we provide a Python reference implementation and tests for it.

# Python reference implementation matching the C++ template logic
class CurvePoint:
    def __init__(self, x, y):
        self.x = x
        self.y = y


# Reference curve from three_way_valve.h
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
    """
    Python reference implementation of C++ get_flow template function.
    Maps position (x) to flow (y) using linear interpolation.
    """
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
    """
    Python reference implementation of C++ get_pos template function.
    Maps flow (y) to position (x) using linear interpolation (inverse of get_flow).
    """
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


class TestGetFlow:
    """Test suite for get_flow function."""

    def test_exact_curve_points(self):
        """Test that exact curve points return exact flow values."""
        for point in mixer_curve:
            result = get_flow(point.x, mixer_curve)
            assert abs(result - point.y) < 1e-6, \
                f"get_flow({point.x}) = {result}, expected {point.y}"

    def test_below_minimum(self):
        """Test position below curve minimum."""
        result = get_flow(-0.5, mixer_curve)
        assert result == mixer_curve[0].y

    def test_above_maximum(self):
        """Test position above curve maximum."""
        result = get_flow(1.5, mixer_curve)
        assert result == mixer_curve[-1].y

    def test_interpolation_midpoint(self):
        """Test interpolation at segment midpoints."""
        # Between 0.0 and 0.1: midpoint should give average
        result = get_flow(0.05, mixer_curve)
        expected = (0.0 + 0.01) / 2
        assert abs(result - expected) < 1e-6

    def test_interpolation_quarter_point(self):
        """Test interpolation at 25% of segment."""
        # Between 0.0 (y=0.0) and 0.1 (y=0.01): at x=0.025 (25%)
        result = get_flow(0.025, mixer_curve)
        expected = 0.0 + 0.25 * (0.01 - 0.0)
        assert abs(result - expected) < 1e-6

    def test_non_linear_segment(self):
        """Test interpolation in non-linear segment (0.5-0.6)."""
        # Between 0.5 (y=0.5) and 0.6 (y=0.7)
        result = get_flow(0.55, mixer_curve)
        expected = 0.5 + 0.5 * (0.7 - 0.5)  # 50% between points
        assert abs(result - expected) < 1e-6
        assert abs(result - 0.6) < 1e-6

    def test_zero_position(self):
        """Test zero position gives zero flow."""
        result = get_flow(0.0, mixer_curve)
        assert result == 0.0

    def test_full_position(self):
        """Test full position gives full flow."""
        result = get_flow(1.0, mixer_curve)
        assert result == 1.0

    def test_monotonic_increase(self):
        """Test that flow increases monotonically with position."""
        positions = [i * 0.01 for i in range(101)]
        flows = [get_flow(pos, mixer_curve) for pos in positions]
        for i in range(len(flows) - 1):
            assert flows[i] <= flows[i + 1], \
                f"Flow not monotonic at position {positions[i]}"


class TestGetPos:
    """Test suite for get_pos function."""

    def test_exact_curve_points(self):
        """Test that exact flow values return exact positions."""
        for point in mixer_curve:
            result = get_pos(point.y, mixer_curve)
            assert abs(result - point.x) < 1e-6, \
                f"get_pos({point.y}) = {result}, expected {point.x}"

    def test_below_minimum(self):
        """Test flow below curve minimum."""
        result = get_pos(-0.5, mixer_curve)
        assert result == mixer_curve[0].x

    def test_above_maximum(self):
        """Test flow above curve maximum."""
        result = get_pos(1.5, mixer_curve)
        assert result == mixer_curve[-1].x

    def test_interpolation_midpoint(self):
        """Test interpolation at segment midpoints."""
        # Between y=0.0 and y=0.01: midpoint y=0.005 should give x between 0.0 and 0.1
        result = get_pos(0.005, mixer_curve)
        expected = (0.0 + 0.1) / 2
        assert abs(result - expected) < 1e-6

    def test_non_linear_segment(self):
        """Test interpolation in non-linear segment."""
        # Between y=0.5 and y=0.7 (x=0.5 to x=0.6)
        result = get_pos(0.6, mixer_curve)
        # 0.6 is 50% between 0.5 and 0.7
        expected = 0.5 + 0.5 * (0.6 - 0.5)
        assert abs(result - expected) < 1e-6
        assert abs(result - 0.55) < 1e-6

    def test_zero_flow(self):
        """Test zero flow gives zero position."""
        result = get_pos(0.0, mixer_curve)
        assert result == 0.0

    def test_full_flow(self):
        """Test full flow gives full position."""
        result = get_pos(1.0, mixer_curve)
        assert result == 1.0

    def test_monotonic_increase(self):
        """Test that position increases monotonically with flow."""
        flows = [i * 0.01 for i in range(101)]
        positions = [get_pos(flow, mixer_curve) for flow in flows]
        for i in range(len(positions) - 1):
            assert positions[i] <= positions[i + 1], \
                f"Position not monotonic at flow {flows[i]}"


class TestInverseFunctions:
    """Test that get_flow and get_pos are inverse functions."""

    def test_round_trip_position_to_flow_to_position(self):
        """Test that pos -> flow -> pos returns original (approximately)."""
        test_positions = [i * 0.1 for i in range(11)]
        for pos in test_positions:
            flow = get_flow(pos, mixer_curve)
            pos_back = get_pos(flow, mixer_curve)
            assert abs(pos - pos_back) < 1e-5, \
                f"Round trip failed: {pos} -> {flow} -> {pos_back}"

    def test_round_trip_flow_to_position_to_flow(self):
        """Test that flow -> pos -> flow returns original (approximately)."""
        test_flows = [i * 0.1 for i in range(11)]
        for flow in test_flows:
            pos = get_pos(flow, mixer_curve)
            flow_back = get_flow(pos, mixer_curve)
            assert abs(flow - flow_back) < 1e-5, \
                f"Round trip failed: {flow} -> {pos} -> {flow_back}"

    def test_round_trip_many_values(self):
        """Test round trip with many intermediate values."""
        for i in range(101):
            pos = i * 0.01
            flow = get_flow(pos, mixer_curve)
            pos_back = get_pos(flow, mixer_curve)
            assert abs(pos - pos_back) < 1e-4


class TestCurveCharacteristics:
    """Test characteristics of the mixer curve."""

    def test_curve_is_non_linear(self):
        """Test that the curve is non-linear (not a straight line)."""
        # Check that middle points don't lie on straight line from start to end
        straight_line_y = lambda x: x  # Linear curve would be y=x
        
        # Check point at x=0.1
        actual = get_flow(0.1, mixer_curve)
        linear = straight_line_y(0.1)
        assert abs(actual - linear) > 0.05, "Curve should be non-linear"

    def test_curve_emphasizes_extremes(self):
        """Test that curve emphasizes low and high values."""
        # At low positions, flow should be much less than linear
        assert get_flow(0.1, mixer_curve) < 0.05
        
        # At high positions, flow should be much more than would be linear
        assert get_flow(0.9, mixer_curve) > 0.95

    def test_curve_midpoint(self):
        """Test that curve passes through (0.5, 0.5) for balance."""
        result = get_flow(0.5, mixer_curve)
        assert abs(result - 0.5) < 1e-6

    def test_curve_symmetry_characteristic(self):
        """Test general symmetry characteristic of the curve."""
        # The curve should have similar but inverse behavior at extremes
        low_deviation = abs(get_flow(0.1, mixer_curve) - 0.1)
        high_deviation = abs(get_flow(0.9, mixer_curve) - 0.9)
        # Both should deviate similarly from linear
        assert abs(low_deviation - high_deviation) < 0.02


class TestEdgeCases:
    """Test edge cases and boundary conditions."""

    def test_very_small_positive_values(self):
        """Test very small positive values."""
        result = get_flow(0.0001, mixer_curve)
        assert 0.0 <= result < 0.001

    def test_very_close_to_one(self):
        """Test values very close to 1.0."""
        result = get_flow(0.9999, mixer_curve)
        assert 0.999 < result <= 1.0

    def test_exactly_at_segment_boundary(self):
        """Test values exactly at segment boundaries."""
        for point in mixer_curve:
            flow = get_flow(point.x, mixer_curve)
            assert abs(flow - point.y) < 1e-10

    def test_single_point_curve(self):
        """Test with minimal curve (single point)."""
        single_curve = [CurvePoint(0.5, 0.7)]
        assert get_flow(0.0, single_curve) == 0.7
        assert get_flow(0.5, single_curve) == 0.7
        assert get_flow(1.0, single_curve) == 0.7

    def test_two_point_linear_curve(self):
        """Test with simple two-point curve (linear)."""
        linear_curve = [CurvePoint(0.0, 0.0), CurvePoint(1.0, 1.0)]
        assert get_flow(0.5, linear_curve) == 0.5
        assert get_pos(0.5, linear_curve) == 0.5


if __name__ == "__main__":
    import pytest
    pytest.main([__file__, "-v"])
