import re
import esphome.codegen as cg
import esphome.config_validation as cv
from esphome.components import valve, stepper
from esphome.const import CONF_ID, CONF_NAME
import esphome.automation as auto

three_way_ns = cg.esphome_ns.namespace('three_way_valve')
ThreeWayValve = three_way_ns.class_('ThreeWayValve', cg.Component, valve.Valve)
ThreeWayValveBlockAction = three_way_ns.class_('ThreeWayValveBlockAction', auto.Action)
ThreeWayValveOpenAllAction = three_way_ns.class_('ThreeWayValveOpenAllAction', auto.Action)

PORT_FUNCTIONS = {'supply': 0, 'buffer': 1, 'return': 2}
CONF_STEPPER = 'stepper'
CONF_GEAR_RATIO = 'gear_ratio'
CONF_MOTOR_STEPS_PER_REV = 'motor_steps_per_rev'
CONF_PORTS = 'ports'
CONF_POSITION_OFFSET = 'position_offset'
CONF_MIXER_CURVE = 'mixer_curve'

def validate_position_offset(value):
    """Validate position offset with unit (like servoxxd).
    
    Supports units: steps, rev/revolutions, deg/degrees, rad/radians, 
    arcmin/arcminutes, arcsec/arcseconds
    
    Returns: {"value": float, "unit": str}
    Example: "10steps" -> {"value": 10.0, "unit": "STEPS"}
    """
    value_str = cv.string(value).strip()
    
    # Parse unit suffixes (based on servoxxd implementation)
    unit_map = {
        ("steps", "step"): "STEPS",
        ("rev", "revolutions", "revolution"): "REVOLUTIONS",
        ("deg", "degrees", "degree", "°"): "DEGREES",
        ("rad", "radians", "radian"): "RADIANS",
        ("arcmin", "arcminute", "arcminutes", "'", "amin"): "ARCMINUTES",
        ("arcsec", "arcsecond", "arcseconds", '"', "asec"): "ARCSECONDS",
    }
    
    for suffixes, unit_type in unit_map.items():
        for suffix in suffixes:
            if value_str.lower().endswith(suffix.lower()):
                value_part = value_str[:-len(suffix)].strip()
                try:
                    val = float(value_part)
                except ValueError:
                    raise cv.Invalid(f"Invalid number for offset: {value}")
                return {"value": val, "unit": unit_type}
    
    raise cv.Invalid(
        f"Position offset must end with a valid unit. "
        f"Supported units: steps, rev/revolutions, deg/degrees/°, "
        f"rad/radians, arcmin/arcminutes/', arcsec/arcseconds/\". "
        f"Example: 10steps, 0.5rev, 45deg, 1.57rad, 60arcmin, 3600arcsec"
    )

def validate_ports(value):
    """
    Accepts ports as a dict: function -> port number (1,2,3), function names are case-insensitive.
    Example:
      ports:
        supply: 1
        buffer: 2
        return: 3
    """
    # Accept any case for keys, normalize to lowercase
    key_map = {k.lower(): k for k in value}
    expected = {'supply', 'buffer', 'return'}
    if set(key_map) != expected:
        raise cv.Invalid("The 'ports' mapping must include exactly 'supply', 'buffer', and 'return'.")
    ports = [int(value[key_map[k]]) for k in expected]
    if sorted(ports) != [1, 2, 3]:
        raise cv.Invalid("Each port number (1, 2, 3) must be used exactly once.")
    # Return mapping in lower-case keys
    return {k.lower(): int(value[key_map[k]]) for k in expected}

def ensure_dict(value):
    if not isinstance(value, dict):
        raise cv.Invalid("Must be a mapping (dictionary)!")
    return value

# Predefined mixer curves for known valve types
MIXER_CURVES = {
    'evenes easyflow': [
        (0.0, 0.0),
        (0.1, 0.01),
        (0.2, 0.1),
        (0.3, 0.2),
        (0.4, 0.3),
        (0.5, 0.5),
        (0.6, 0.7),
        (0.7, 0.8),
        (0.8, 0.9),
        (0.9, 0.99),
        (1.0, 1.0),
    ],
    'linear': [
        (0.0, 0.0),
        (1.0, 1.0),
    ],
}

def validate_curve_point(value):
    """Validate a single curve point as [flow, position] or {flow: x, position: y} or {x: x, y: y}."""
    if isinstance(value, dict):
        # Support both flow/position and x/y notation
        if 'flow' in value and 'position' in value:
            flow = cv.float_range(min=0.0, max=1.0)(value['flow'])
            pos = cv.float_range(min=0.0, max=1.0)(value['position'])
            return (flow, pos)
        elif 'x' in value and 'y' in value:
            flow = cv.float_range(min=0.0, max=1.0)(value['x'])
            pos = cv.float_range(min=0.0, max=1.0)(value['y'])
            return (flow, pos)
        else:
            raise cv.Invalid(
                "Curve point dict must have either 'flow' and 'position' keys or 'x' and 'y' keys"
            )
    elif isinstance(value, list) and len(value) == 2:
        flow = cv.float_range(min=0.0, max=1.0)(value[0])
        pos = cv.float_range(min=0.0, max=1.0)(value[1])
        return (flow, pos)
    else:
        raise cv.Invalid(
            "Curve point must be a list [flow, position] or dict {flow: x, position: y} or {x: x, y: y}"
        )

def validate_mixer_curve(value):
    """Validate mixer curve as predefined type (string) or custom list of points."""
    # If it's a string, check if it's a predefined curve type
    if isinstance(value, str):
        curve_type = value.lower().strip()
        if curve_type not in MIXER_CURVES:
            available = ', '.join([f"'{k}'" for k in MIXER_CURVES.keys()])
            raise cv.Invalid(
                f"Unknown mixer curve type '{value}'. Available types: {available}"
            )
        return {'type': curve_type, 'points': MIXER_CURVES[curve_type]}
    
    # Otherwise, validate as custom curve
    if not isinstance(value, list) or len(value) < 2:
        raise cv.Invalid("Mixer curve must be a predefined type (e.g., 'linear') or a list with at least 2 points")
    
    points = [validate_curve_point(p) for p in value]
    
    # Check that points are sorted by flow value
    for i in range(len(points) - 1):
        if points[i][0] >= points[i+1][0]:
            raise cv.Invalid(
                f"Mixer curve points must be sorted by flow value. "
                f"Point {i} (flow={points[i][0]}) >= Point {i+1} (flow={points[i+1][0]})"
            )
    
    # Check that first point starts at 0.0 and last ends at 1.0
    if points[0][0] != 0.0:
        raise cv.Invalid("Mixer curve must start at flow=0.0")
    if points[-1][0] != 1.0:
        raise cv.Invalid("Mixer curve must end at flow=1.0")
    
    return {'type': 'custom', 'points': points}

CONFIG_SCHEMA = valve.valve_schema(ThreeWayValve).extend({
    cv.GenerateID(): cv.declare_id(ThreeWayValve),
    cv.Required(CONF_STEPPER): cv.use_id(stepper.Stepper),
    cv.Required(CONF_GEAR_RATIO): cv.float_,
    cv.Optional(CONF_MOTOR_STEPS_PER_REV): cv.int_,
    cv.Required(CONF_PORTS): cv.All(ensure_dict, validate_ports),
    cv.Optional(CONF_POSITION_OFFSET, default='0steps'): validate_position_offset,
    cv.Optional(CONF_MIXER_CURVE, default='evenes easyflow'): validate_mixer_curve,
}).extend(cv.COMPONENT_SCHEMA)

ANGLE_MAPPING = {
    (0, 1, 2): {'open': 270, 'closed': 180, 'blocked': 0},    # supply, buffer, return
    (0, 2, 1): {'open': 180, 'closed': 270, 'blocked': 0},    # supply, return, buffer
    (1, 0, 2): {'open': 270, 'closed': 0, 'blocked': 180},    # buffer, supply, return
    (2, 0, 1): {'open': 0, 'closed': 270, 'blocked': 180},    # return, supply, buffer
}

async def to_code(config):
    var = cg.new_Pvariable(config[CONF_ID])
    await cg.register_component(var, config)
    await valve.register_valve(var, config)

    # Assign stepper
    stepper_var = await cg.get_variable(config[CONF_STEPPER])
    cg.add(var.set_stepper(stepper_var))

    # Set mixer curve
    curve_data = config[CONF_MIXER_CURVE]
    curve_points = curve_data['points']
    
    # Generate C++ code to set the curve
    for flow, pos in curve_points:
        cg.add(var.add_curve_point(flow, pos))

    # Ports mapping - always lowercase
    ports_map = config[CONF_PORTS]
    # Build inverse: port number -> function name
    inv_map = {v: k for k, v in ports_map.items()}
    # Function assigned to port 1, 2, 3
    func_order = [inv_map[i] for i in (1, 2, 3)]  # e.g. ['supply', 'buffer', 'return']
    funcs_idx = [PORT_FUNCTIONS[f] for f in func_order]

    angles = ANGLE_MAPPING.get(tuple(funcs_idx))
    if angles is None:
        chosen = ", ".join([f"{k}: {ports_map[k]}" for k in ['supply', 'buffer', 'return']])
        valid_layouts = [
            "supply: 1, buffer: 2, return: 3",
            "supply: 1, return: 2, buffer: 3",
            "buffer: 1, supply: 2, return: 3",
            "return: 1, supply: 2, buffer: 3",
        ]
        raise cv.Invalid(
            f"Invalid port assignment!\n"
            f"  Current: {chosen}\n\n"
            f"  Only assignments where 'open' and 'closed' are 90° apart are supported by this valve.\n"
            f"  In the unsupported assignments, they are 180° apart, making mixing impossible.\n\n"
            f"  Allowed examples:\n"
            + "\n".join([f"    - {layout}" for layout in valid_layouts])
            + "\n\nPlease use one of the supported assignments matching your valve's labeling."
        )

    # Calculate motor_steps_per_rev - required for offset unit conversion
    if CONF_MOTOR_STEPS_PER_REV not in config:
        # Check if offset unit is STEPS - if so, motor_steps_per_rev is required
        offset_obj = config[CONF_POSITION_OFFSET]
        if offset_obj["unit"] == "STEPS":
            raise cv.Invalid(
                f"motor_steps_per_rev is required when position_offset unit is 'steps'. "
                f"Please specify motor_steps_per_rev or use a different unit (rev, deg, rad, arcmin, arcsec)."
            )
        # For other units, we can calculate from gear_ratio assuming 200 steps/rev base motor
        motor_steps_per_rev = 200
    else:
        motor_steps_per_rev = config[CONF_MOTOR_STEPS_PER_REV]
    
    steps_per_deg = - motor_steps_per_rev * config[CONF_GEAR_RATIO] / 360.0

    # Offset - convert from specified unit to steps (based on servoxxd)
    offset_obj = config[CONF_POSITION_OFFSET]
    val = offset_obj["value"]
    unit = offset_obj["unit"]
    
    # Convert offset to steps based on unit
    import math
    if unit == "STEPS":
        off_steps = int(val)
    elif unit == "REVOLUTIONS":
        off_steps = int(val * motor_steps_per_rev * config[CONF_GEAR_RATIO])
    elif unit == "DEGREES":
        off_steps = int(val * steps_per_deg)
    elif unit == "RADIANS":
        # 1 revolution = 2π radians
        off_steps = int((val / (2 * math.pi)) * motor_steps_per_rev * config[CONF_GEAR_RATIO])
    elif unit == "ARCMINUTES":
        # 21600 arcminutes = 360 degrees
        off_steps = int((val / 21600.0) * 360.0 * steps_per_deg)
    elif unit == "ARCSECONDS":
        # 1296000 arcseconds = 360 degrees
        off_steps = int((val / 1296000.0) * 360.0 * steps_per_deg)
    else:
        raise cv.Invalid(f"Unknown unit type: {unit}")

    cg.add(var.set_pos_closed(int(angles['closed'] * steps_per_deg) + off_steps))
    cg.add(var.set_pos_open(int(angles['open'] * steps_per_deg) + off_steps))
    cg.add(var.set_pos_block(int(angles['blocked'] * steps_per_deg) + off_steps))
    cg.add(var.set_pos_all_open(int(180 * steps_per_deg) + off_steps))

# Action schemas
VALVE_ACTION_SCHEMA = cv.Schema({
    cv.Required(CONF_ID): cv.use_id(ThreeWayValve),
})

@auto.register_action("valve.block", ThreeWayValveBlockAction, VALVE_ACTION_SCHEMA)
async def valve_block_action_to_code(config, action_id, template_arg, args):
    valve_var = await cg.get_variable(config[CONF_ID])
    return cg.new_Pvariable(action_id, valve_var)

@auto.register_action("valve.open_all", ThreeWayValveOpenAllAction, VALVE_ACTION_SCHEMA)
async def valve_open_all_action_to_code(config, action_id, template_arg, args):
    valve_var = await cg.get_variable(config[CONF_ID])
    return cg.new_Pvariable(action_id, valve_var)
