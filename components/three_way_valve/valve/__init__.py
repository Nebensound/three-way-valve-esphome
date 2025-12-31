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

def validate_offset(value):
    """Validate position offset (e.g. '10steps', '-7.5deg')."""
    value = cv.string(value).replace(" ", "")
    allowed_types = {
        "steps": "steps",
        "deg": "deg",
        "degree": "deg",
        "degrees": "deg",
    }
    matched = None
    for key in allowed_types:
        if value.endswith(key):
            try:
                num = float(value[:-len(key)])
            except ValueError:
                raise cv.Invalid(f"Invalid number for offset: {value}")
            matched = allowed_types[key]
            break
    if matched is None:
        raise cv.Invalid(
            "Position offset must end with one of: steps, deg, degree(s). Example: 10steps or -7.5deg"
        )
    return {"type": matched, "value": num}

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

CONFIG_SCHEMA = valve.valve_schema(ThreeWayValve).extend({
    cv.GenerateID(): cv.declare_id(ThreeWayValve),
    cv.Required(CONF_STEPPER): cv.use_id(stepper.Stepper),
    cv.Required(CONF_GEAR_RATIO): cv.float_,
    cv.Required(CONF_MOTOR_STEPS_PER_REV): cv.int_,
    cv.Required(CONF_PORTS): cv.All(ensure_dict, validate_ports),
    cv.Optional(CONF_POSITION_OFFSET, default='0steps'): validate_offset,
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

    steps_per_deg = - config[CONF_MOTOR_STEPS_PER_REV] * config[CONF_GEAR_RATIO] / 360.0

    # Offset (validated and robust)
    offset_obj = config[CONF_POSITION_OFFSET]
    val = offset_obj["value"]
    unit = offset_obj["type"]
    off_steps = int(val * steps_per_deg) if unit == "deg" else int(val)

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
