# Three Way Valve

The `three_way_valve` valve platform allows you to easily use a geared stepper on a three-way mixing valve.

## Installation

Add this external component to your ESPHome configuration:

```yaml
external_components:
  - source: github://Nebensound/three_way_valve-esphome
    components: [ three_way_valve ]
```

> [!TIP]
> To use a specific branch or tag, add it after `@`: `github://Nebensound/three_way_valve-esphome@main` or `github://Nebensound/three_way_valve-esphome@v1.0.0`

## Configuration

```yaml
valve:
  - platform: three_way_valve
    name: "Three Way Valve"
    stepper: my_stepper
    gear_ratio: 4.888888889  # 44/9
    motor_steps_per_rev: 200
    ports:
      supply: 1
      buffer: 2
      return: 3
    position_offset: "0steps"
    # mixer_curve defaults to "evenes easyflow"
```

### With Linear Mixer Curve

```yaml
valve:
  - platform: three_way_valve
    name: "Three Way Valve"
    stepper: my_stepper
    gear_ratio: 4.888888889
    motor_steps_per_rev: 200
    ports:
      supply: 1
      buffer: 2
      return: 3
    mixer_curve: linear  # Use linear mapping
```

### With Custom Mixer Curve

```yaml
valve:
  - platform: three_way_valve
    name: "Three Way Valve"
    stepper: my_stepper
    gear_ratio: 4.888888889
    motor_steps_per_rev: 200
    ports:
      supply: 1
      buffer: 2
      return: 3
    mixer_curve:  # Custom curve with list notation
      - [0.0, 0.0]
      - [0.5, 0.5]
      - [1.0, 1.0]
```

### Alternative Custom Curve Notations

```yaml
# Using x/y notation
mixer_curve:
  - x: 0.0
    y: 0.0
  - x: 0.5
    y: 0.3
  - x: 1.0
    y: 1.0

# Using flow/position notation
mixer_curve:
  - flow: 0.0
    position: 0.0
  - flow: 0.5
    position: 0.3
  - flow: 1.0
    position: 1.0
```

## Base Configuration

- **id** (*Optional*, [ID](https://esphome.io/guides/configuration-types.html#config-id)): Specify the ID of the valve so that you can control it. At least one of `id` or `name` must be specified.
- **name** (*Optional*, [string](https://esphome.io/guides/configuration-types.html#config-string)): The name of the valve. At least one of `id` or `name` must be specified.
- **stepper** (**Required**, [ID](https://esphome.io/guides/configuration-types.html#config-id)): The ID of the stepper motor to use for valve actuation. Must reference a `stepper` component.
- **gear_ratio** (*Optional*, [float](https://esphome.io/guides/configuration-types.html#config-float)): The gear ratio of the valve mechanism. This is the ratio of motor revolutions to valve revolutions. Defaults to 1.0 (direct drive).
- **motor_steps_per_rev** (**Required**, [int](https://esphome.io/guides/configuration-types.html#config-int)): Number of motor steps per full revolution of the motor.
- **ports** (**Required**, object): Port configuration for the valve with explicit mapping of port numbers from hardware manual to their functions:
  - **supply** (**Required**, [int](https://esphome.io/guides/configuration-types.html#config-int)): The port number for the supply line (labeled in hardware manual).
  - **buffer** (**Required**, [int](https://esphome.io/guides/configuration-types.html#config-int)): The port number for the buffer line (labeled in hardware manual).
  - **return** (**Required**, [int](https://esphome.io/guides/configuration-types.html#config-int)): The port number for the return line (labeled in hardware manual).
- **position_offset** (*Optional*, [string](https://esphome.io/guides/configuration-types.html#config-string)): Offset to apply to valve position. Accepts values with units like `"10steps"`, `"-7.5deg"`. Default: `"0steps"`.
- **mixer_curve** (*Optional*, string or list): Defines how flow values (0.0-1.0) map to valve positions (0.0-1.0). Can be either:
  
  **Predefined types** (string):
  - `"evenes easyflow"`: Non-linear curve optimized for Evenes EasyFlow valve hardware (default)
  - `"linear"`: Linear 1:1 mapping between flow and position
  
  **Custom curve** (list): Define your own curve as a list of points. Each point maps a flow value (0.0-1.0) to a valve position (0.0-1.0). Supports multiple notations:
  - List notation: `[[0.0, 0.0], [0.5, 0.3], [1.0, 1.0]]`
  - Dict with x/y: `[{x: 0.0, y: 0.0}, {x: 0.5, y: 0.3}, {x: 1.0, y: 1.0}]`
  - Dict with flow/position: `[{flow: 0.0, position: 0.0}, ...]`

## Actions

### `valve.block`

Move valve to the blocked position where the supply to the heating surface is closed, stopping circulation.

```yaml
on_...:
  - valve.block:
      id: my_valve
```

**Configuration:**
- **id** (**Required**, [ID](https://esphome.io/guides/configuration-types.html#config-id)): The ID of the valve.

### `valve.open_all`

Move valve to the position where all ports are open.

```yaml
on_...:
  - valve.open_all:
      id: my_valve
```

**Configuration:**
- **id** (**Required**, [ID](https://esphome.io/guides/configuration-types.html#config-id)): The ID of the valve.

## Hardware Setup

For information about the hardware valve and port configuration, refer to the [hardware documentation](docs/hardware/).

## See Also

- [ESPHome Valve Component](https://esphome.io/components/valve/)
- [ESPHome Stepper Component](https://esphome.io/components/stepper/)
