"""Tests for Three-Way Valve configuration validation."""
import pytest
import sys
from pathlib import Path
from types import ModuleType

# Create Invalid exception class that can be raised
class Invalid(Exception):
    pass

# Create a proper mock module for config_validation first
mock_cv = ModuleType('esphome.config_validation')
mock_cv.Invalid = Invalid

# Add float_range mock
def mock_float_range(min=None, max=None):
    def validator(value):
        v = float(value)
        if min is not None and v < min:
            raise Invalid(f"Value {v} is less than minimum {min}")
        if max is not None and v > max:
            raise Invalid(f"Value {v} is greater than maximum {max}")
        return v
    return validator

def mock_one_of(*values, **kwargs):
    def validator(value):
        if kwargs.get('lower'):
            value = value.lower()
        if value not in values:
            raise Invalid(f"Value {value} not in {values}")
        return value
    return validator

# Add functions to mock module
mock_cv.string = lambda value: str(value)
mock_cv.int_ = lambda value: int(value)
mock_cv.float_ = lambda value: float(value)
mock_cv.All = lambda *validators: lambda value: value
mock_cv.float_range = mock_float_range
mock_cv.one_of = mock_one_of
# Add more cv functions needed by the component
mock_cv.GenerateID = lambda: 'generate_id'
mock_cv.declare_id = lambda cls: lambda value: value
mock_cv.use_id = lambda cls: lambda value: value
mock_cv.Required = lambda key: key
mock_cv.Optional = lambda key, default=None: key
mock_cv.COMPONENT_SCHEMA = {}
mock_cv.Schema = lambda schema: schema  # Schema just returns dict as-is

# Mock ESPHome modules before importing component
from unittest.mock import MagicMock

# Create the esphome mock module
mock_esphome = ModuleType('esphome')
mock_esphome.config_validation = mock_cv  # Make cv accessible as attribute
mock_esphome.codegen = MagicMock()
mock_esphome.automation = MagicMock()

# Create components mock
mock_components = ModuleType('esphome.components')
mock_components.valve = MagicMock()
mock_components.stepper = MagicMock()
mock_esphome.components = mock_components

# Create const mock
mock_esphome.const = MagicMock()

# Register all mocks in sys.modules
sys.modules['esphome'] = mock_esphome
sys.modules['esphome.codegen'] = mock_esphome.codegen
sys.modules['esphome.config_validation'] = mock_cv
sys.modules['esphome.components'] = mock_components
sys.modules['esphome.components.valve'] = mock_components.valve
sys.modules['esphome.components.stepper'] = mock_components.stepper
sys.modules['esphome.const'] = mock_esphome.const
sys.modules['esphome.automation'] = mock_esphome.automation

# Add component path
sys.path.insert(0, str(Path(__file__).parent.parent / "components" / "three_way_valve" / "valve"))

# Import functions from __init__.py
import importlib.util
spec = importlib.util.spec_from_file_location(
    "three_way_valve_init",
    Path(__file__).parent.parent / "components" / "three_way_valve" / "valve" / "__init__.py"
)
three_way_valve_init = importlib.util.module_from_spec(spec)
spec.loader.exec_module(three_way_valve_init)

validate_offset = three_way_valve_init.validate_offset
validate_ports = three_way_valve_init.validate_ports
validate_mixer_curve = three_way_valve_init.validate_mixer_curve
validate_curve_point = three_way_valve_init.validate_curve_point
PORT_FUNCTIONS = three_way_valve_init.PORT_FUNCTIONS
ANGLE_MAPPING = three_way_valve_init.ANGLE_MAPPING
MIXER_CURVES = three_way_valve_init.MIXER_CURVES
CONF_MIXER_CURVE = three_way_valve_init.CONF_MIXER_CURVE


class TestValidateOffset:
    """Test suite for validate_offset function."""

    def test_valid_steps_positive(self):
        """Test valid positive steps offset."""
        result = validate_offset("10steps")
        assert result == {"type": "steps", "value": 10.0}

    def test_valid_steps_negative(self):
        """Test valid negative steps offset."""
        result = validate_offset("-7steps")
        assert result == {"type": "steps", "value": -7.0}

    def test_valid_steps_with_spaces(self):
        """Test valid steps offset with spaces."""
        result = validate_offset("  10 steps  ")
        assert result == {"type": "steps", "value": 10.0}

    def test_valid_degrees_positive(self):
        """Test valid positive degrees offset."""
        result = validate_offset("45.5deg")
        assert result == {"type": "deg", "value": 45.5}

    def test_valid_degrees_negative(self):
        """Test valid negative degrees offset."""
        result = validate_offset("-90deg")
        assert result == {"type": "deg", "value": -90.0}

    def test_valid_degree_singular(self):
        """Test 'degree' singular form."""
        result = validate_offset("1degree")
        assert result == {"type": "deg", "value": 1.0}

    def test_valid_degrees_plural(self):
        """Test 'degrees' plural form."""
        result = validate_offset("180degrees")
        assert result == {"type": "deg", "value": 180.0}

    def test_zero_offset(self):
        """Test zero offset."""
        result = validate_offset("0steps")
        assert result == {"type": "steps", "value": 0.0}

    def test_float_steps(self):
        """Test fractional steps offset."""
        result = validate_offset("3.14159steps")
        assert result == {"type": "steps", "value": 3.14159}

    def test_invalid_unit(self):
        """Test invalid unit suffix."""
        with pytest.raises(Invalid) as excinfo:
            validate_offset("10meters")
        assert "must end with one of" in str(excinfo.value)

    def test_invalid_number(self):
        """Test invalid number format."""
        with pytest.raises(Invalid) as excinfo:
            validate_offset("abcsteps")
        assert "Invalid number" in str(excinfo.value)

    def test_no_unit(self):
        """Test offset without unit."""
        with pytest.raises(Invalid) as excinfo:
            validate_offset("10")
        assert "must end with one of" in str(excinfo.value)


class TestValidatePorts:
    """Test suite for validate_ports function."""

    def test_valid_ports_123(self):
        """Test valid port assignment 1-2-3."""
        ports = {"supply": 1, "buffer": 2, "return": 3}
        result = validate_ports(ports)
        assert result == {"supply": 1, "buffer": 2, "return": 3}

    def test_valid_ports_132(self):
        """Test valid port assignment 1-3-2."""
        ports = {"supply": 1, "return": 2, "buffer": 3}
        result = validate_ports(ports)
        assert result == {"supply": 1, "return": 2, "buffer": 3}

    def test_valid_ports_213(self):
        """Test valid port assignment 2-1-3."""
        ports = {"buffer": 1, "supply": 2, "return": 3}
        result = validate_ports(ports)
        assert result == {"buffer": 1, "supply": 2, "return": 3}

    def test_valid_ports_312(self):
        """Test valid port assignment 3-1-2."""
        ports = {"return": 1, "supply": 2, "buffer": 3}
        result = validate_ports(ports)
        assert result == {"return": 1, "supply": 2, "buffer": 3}

    def test_case_insensitive_keys(self):
        """Test that port keys are case-insensitive."""
        ports = {"SUPPLY": 1, "Buffer": 2, "ReTuRn": 3}
        result = validate_ports(ports)
        # Result should be normalized to lowercase
        assert result == {"supply": 1, "buffer": 2, "return": 3}

    def test_missing_port_key(self):
        """Test missing port key raises error."""
        ports = {"supply": 1, "buffer": 2}  # Missing 'return'
        with pytest.raises(Invalid) as excinfo:
            validate_ports(ports)
        assert "must include exactly" in str(excinfo.value)

    def test_extra_port_key(self):
        """Test extra port key raises error."""
        ports = {"supply": 1, "buffer": 2, "return": 3, "extra": 4}
        with pytest.raises(Invalid) as excinfo:
            validate_ports(ports)
        assert "must include exactly" in str(excinfo.value)

    def test_duplicate_port_numbers(self):
        """Test duplicate port numbers raise error."""
        ports = {"supply": 1, "buffer": 1, "return": 3}
        with pytest.raises(Invalid) as excinfo:
            validate_ports(ports)
        assert "must be used exactly once" in str(excinfo.value)

    def test_invalid_port_numbers(self):
        """Test port numbers other than 1,2,3 raise error."""
        ports = {"supply": 1, "buffer": 2, "return": 4}
        with pytest.raises(Invalid) as excinfo:
            validate_ports(ports)
        assert "must be used exactly once" in str(excinfo.value)


class TestAngleMapping:
    """Test suite for ANGLE_MAPPING logic."""

    def test_angle_mapping_exists_for_valid_configs(self):
        """Test that angle mappings exist for all valid port configurations."""
        valid_configs = [
            (0, 1, 2),  # supply, buffer, return
            (0, 2, 1),  # supply, return, buffer
            (1, 0, 2),  # buffer, supply, return
            (2, 0, 1),  # return, supply, buffer
        ]
        for config in valid_configs:
            assert config in ANGLE_MAPPING
            angles = ANGLE_MAPPING[config]
            assert "open" in angles
            assert "closed" in angles
            assert "blocked" in angles

    def test_angle_mapping_open_closed_90_degrees_apart(self):
        """Test that open and closed positions are 90 degrees apart."""
        for config, angles in ANGLE_MAPPING.items():
            # Calculate the minimum angular difference (accounting for 360° wrap)
            diff = abs(angles["open"] - angles["closed"])
            # Normalize to range [0, 360]
            if diff > 180:
                diff = 360 - diff
            assert diff == 90, f"Config {config} has open/closed diff of {diff}°, expected 90°"

    def test_angle_mapping_blocked_positions(self):
        """Test blocked positions are correct (0 or 180)."""
        for config, angles in ANGLE_MAPPING.items():
            assert angles["blocked"] in [0, 180], \
                f"Config {config} has blocked={angles['blocked']}, expected 0 or 180"

    def test_supply_port_1_configs(self):
        """Test configurations where supply is at port 1."""
        # (0, 1, 2): supply at index 0 -> port 1
        angles = ANGLE_MAPPING[(0, 1, 2)]
        assert angles == {"open": 270, "closed": 180, "blocked": 0}

        # (0, 2, 1): supply at index 0 -> port 1
        angles = ANGLE_MAPPING[(0, 2, 1)]
        assert angles == {"open": 180, "closed": 270, "blocked": 0}

    def test_buffer_port_1_config(self):
        """Test configuration where buffer is at port 1."""
        # (1, 0, 2): buffer at index 0 -> port 1
        angles = ANGLE_MAPPING[(1, 0, 2)]
        assert angles == {"open": 270, "closed": 0, "blocked": 180}

    def test_return_port_1_config(self):
        """Test configuration where return is at port 1."""
        # (2, 0, 1): return at index 0 -> port 1
        angles = ANGLE_MAPPING[(2, 0, 1)]
        assert angles == {"open": 0, "closed": 270, "blocked": 180}


class TestPortFunctions:
    """Test suite for PORT_FUNCTIONS constant."""

    def test_port_functions_mapping(self):
        """Test that PORT_FUNCTIONS maps correctly."""
        assert PORT_FUNCTIONS == {"supply": 0, "buffer": 1, "return": 2}

    def test_port_functions_keys(self):
        """Test all required keys exist."""
        assert "supply" in PORT_FUNCTIONS
        assert "buffer" in PORT_FUNCTIONS
        assert "return" in PORT_FUNCTIONS

    def test_port_functions_values_unique(self):
        """Test that function indices are unique."""
        values = list(PORT_FUNCTIONS.values())
        assert len(values) == len(set(values))


class TestEdgeCases:
    """Test edge cases and boundary conditions."""

    def test_very_large_offset(self):
        """Test very large offset values."""
        result = validate_offset("999999steps")
        assert result == {"type": "steps", "value": 999999.0}

    def test_very_small_negative_offset(self):
        """Test very small negative offset."""
        result = validate_offset("-0.0001deg")
        assert result == {"type": "deg", "value": -0.0001}

    def test_scientific_notation_offset(self):
        """Test offset with scientific notation."""
        result = validate_offset("1.5e2steps")
        assert result == {"type": "steps", "value": 150.0}

    def test_ports_as_strings(self):
        """Test ports given as string numbers."""
        ports = {"supply": "1", "buffer": "2", "return": "3"}
        result = validate_ports(ports)
        assert result == {"supply": 1, "buffer": 2, "return": 3}


class TestMixerCurveValidation:
    """Test suite for mixer_curve validation."""

    def test_predefined_curve_evenes_easyflow(self):
        """Test predefined 'evenes easyflow' curve type."""
        result = validate_mixer_curve("evenes easyflow")
        assert result['type'] == 'evenes easyflow'
        assert len(result['points']) == 11
        assert result['points'][0] == (0.0, 0.0)
        assert result['points'][-1] == (1.0, 1.0)

    def test_predefined_curve_linear(self):
        """Test predefined 'linear' curve type."""
        result = validate_mixer_curve("linear")
        assert result['type'] == 'linear'
        assert len(result['points']) == 2
        assert result['points'] == [(0.0, 0.0), (1.0, 1.0)]

    def test_predefined_curve_case_insensitive(self):
        """Test that predefined curve types are case insensitive."""
        result1 = validate_mixer_curve("LINEAR")
        result2 = validate_mixer_curve("Linear")
        result3 = validate_mixer_curve("  linear  ")
        assert result1['type'] == 'linear'
        assert result2['type'] == 'linear'
        assert result3['type'] == 'linear'

    def test_unknown_predefined_curve(self):
        """Test that unknown curve type raises error."""
        with pytest.raises(Invalid) as exc_info:
            validate_mixer_curve("unknown")
        assert "Unknown mixer curve type" in str(exc_info.value)
        assert "'evenes easyflow'" in str(exc_info.value)
        assert "'linear'" in str(exc_info.value)

    def test_valid_custom_curve_list_notation(self):
        """Test valid custom mixer curve with list notation."""
        curve = [
            [0.0, 0.0],
            [0.5, 0.3],
            [1.0, 1.0]
        ]
        result = validate_mixer_curve(curve)
        assert result['type'] == 'custom'
        assert result['points'] == [(0.0, 0.0), (0.5, 0.3), (1.0, 1.0)]

    def test_valid_custom_curve_dict_flow_position_notation(self):
        """Test valid custom curve with dict flow/position notation."""
        curve = [
            {'flow': 0.0, 'position': 0.0},
            {'flow': 0.5, 'position': 0.3},
            {'flow': 1.0, 'position': 1.0}
        ]
        result = validate_mixer_curve(curve)
        assert result['type'] == 'custom'
        assert result['points'] == [(0.0, 0.0), (0.5, 0.3), (1.0, 1.0)]

    def test_valid_custom_curve_dict_xy_notation(self):
        """Test valid custom curve with dict x/y notation."""
        curve = [
            {'x': 0.0, 'y': 0.0},
            {'x': 0.5, 'y': 0.3},
            {'x': 1.0, 'y': 1.0}
        ]
        result = validate_mixer_curve(curve)
        assert result['type'] == 'custom'
        assert result['points'] == [(0.0, 0.0), (0.5, 0.3), (1.0, 1.0)]

    def test_custom_curve_must_have_at_least_two_points(self):
        """Test that curve with less than 2 points raises error."""
        with pytest.raises(Invalid) as exc_info:
            validate_mixer_curve([(0.0, 0.0)])
        assert "at least 2 points" in str(exc_info.value)

    def test_custom_curve_must_start_at_zero(self):
        """Test that curve must start at flow=0.0."""
        curve = [[0.1, 0.0], [1.0, 1.0]]
        with pytest.raises(Invalid) as exc_info:
            validate_mixer_curve(curve)
        assert "start at flow=0.0" in str(exc_info.value)

    def test_custom_curve_must_end_at_one(self):
        """Test that curve must end at flow=1.0."""
        curve = [[0.0, 0.0], [0.9, 0.9]]
        with pytest.raises(Invalid) as exc_info:
            validate_mixer_curve(curve)
        assert "end at flow=1.0" in str(exc_info.value)

    def test_custom_curve_points_must_be_sorted(self):
        """Test that curve points must be sorted by flow value."""
        curve = [[0.0, 0.0], [1.0, 1.0], [0.5, 0.5]]  # Out of order
        with pytest.raises(Invalid) as exc_info:
            validate_mixer_curve(curve)
        assert "sorted by flow value" in str(exc_info.value)

    def test_custom_curve_duplicate_flow_values(self):
        """Test that duplicate flow values are rejected."""
        curve = [[0.0, 0.0], [0.5, 0.3], [0.5, 0.4], [1.0, 1.0]]
        with pytest.raises(Invalid) as exc_info:
            validate_mixer_curve(curve)
        assert "sorted by flow value" in str(exc_info.value)

    def test_custom_curve_flow_values_out_of_range(self):
        """Test that flow values outside 0-1 range are rejected."""
        curve = [[0.0, 0.0], [1.5, 0.5]]
        with pytest.raises(Invalid):
            validate_mixer_curve(curve)

    def test_custom_curve_position_values_out_of_range(self):
        """Test that position values outside 0-1 range are rejected."""
        curve = [[0.0, -0.1], [0.5, 0.5], [1.0, 1.0]]
        with pytest.raises(Invalid):
            validate_mixer_curve(curve)

    def test_custom_curve_invalid_point_format(self):
        """Test that invalid point format is rejected."""
        curve = [[0.0, 0.0], [0.5], [1.0, 1.0]]  # Second point has only one value
        with pytest.raises(Invalid) as exc_info:
            validate_mixer_curve(curve)
        assert "must be a list" in str(exc_info.value) or "must have" in str(exc_info.value)

    def test_predefined_curves_exist(self):
        """Test that predefined mixer curves are properly defined."""
        assert 'evenes easyflow' in MIXER_CURVES
        assert 'linear' in MIXER_CURVES
        
        # Validate evenes easyflow curve
        evenes_curve = MIXER_CURVES['evenes easyflow']
        assert len(evenes_curve) == 11
        assert evenes_curve[0] == (0.0, 0.0)
        assert evenes_curve[-1] == (1.0, 1.0)
        
        # Validate linear curve
        linear_curve = MIXER_CURVES['linear']
        assert len(linear_curve) == 2
        assert linear_curve[0] == (0.0, 0.0)
        assert linear_curve[-1] == (1.0, 1.0)


class TestCurvePointValidation:
    """Test suite for individual curve point validation."""

    def test_valid_list_point(self):
        """Test valid point as list."""
        result = validate_curve_point([0.5, 0.3])
        assert result == (0.5, 0.3)

    def test_valid_dict_flow_position_point(self):
        """Test valid point as dict with flow/position."""
        result = validate_curve_point({'flow': 0.5, 'position': 0.3})
        assert result == (0.5, 0.3)

    def test_valid_dict_xy_point(self):
        """Test valid point as dict with x/y."""
        result = validate_curve_point({'x': 0.5, 'y': 0.3})
        assert result == (0.5, 0.3)

    def test_dict_missing_flow_key(self):
        """Test dict point missing flow key (when using flow/position notation)."""
        with pytest.raises(Invalid) as exc_info:
            validate_curve_point({'position': 0.3})
        assert "must have either" in str(exc_info.value)

    def test_dict_missing_x_key(self):
        """Test dict point missing x key (when using x/y notation)."""
        with pytest.raises(Invalid) as exc_info:
            validate_curve_point({'y': 0.3})
        assert "must have either" in str(exc_info.value)

    def test_dict_mixed_notations(self):
        """Test dict point with mixed notations."""
        with pytest.raises(Invalid) as exc_info:
            validate_curve_point({'flow': 0.5, 'y': 0.3})
        assert "must have either" in str(exc_info.value)

    def test_list_wrong_length(self):
        """Test list with wrong number of elements."""
        with pytest.raises(Invalid):
            validate_curve_point([0.5])
        with pytest.raises(Invalid):
            validate_curve_point([0.5, 0.3, 0.1])

    def test_invalid_type(self):
        """Test invalid point type."""
        with pytest.raises(Invalid) as exc_info:
            validate_curve_point("not a point")
        assert "must be a list" in str(exc_info.value) or "dict" in str(exc_info.value)


class TestValveTypeConfiguration:
    """Test suite for backward compatibility and integration."""

    def test_string_curve_types_work(self):
        """Test that string curve types work correctly."""
        linear = validate_mixer_curve("linear")
        evenes = validate_mixer_curve("evenes easyflow")
        
        assert linear['type'] == 'linear'
        assert evenes['type'] == 'evenes easyflow'
        assert isinstance(linear['points'], list)
        assert isinstance(evenes['points'], list)


