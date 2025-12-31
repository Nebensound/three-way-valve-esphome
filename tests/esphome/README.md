# ESPHome Compile Tests

YAML configuration files to test ESPHome compilation of the Three-Way Valve component.

## Test Configurations

Each YAML file tests a different aspect of the component:

- **`test_basic.yaml`** - Basic minimal configuration
- **`test_all_features.yaml`** - Full configuration with all options
- **`test_port_configs.yaml`** - Different port configurations
- **`test_actions.yaml`** - Custom actions (block, open_all)
- **`test_offsets.yaml`** - Various position offsets

## Running Tests

### Validate Configuration (No Build)
```bash
esphome config test_basic.yaml
```

### Compile Test (No Upload)
```bash
esphome compile test_basic.yaml
```

### Run All Tests
```bash
./run_compile_tests.sh
```

## Expected Behavior

All configurations should compile without errors. These tests verify:
- ✅ Component loads correctly
- ✅ Configuration schema validation
- ✅ All port combinations compile
- ✅ Offset calculations work
- ✅ Actions are properly registered
