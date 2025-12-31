# Three-Way Valve Tests

Comprehensive multi-level test suite for the ESPHome Three-Way Valve component.

## Test Architecture

The test suite consists of three levels:

1. **Python Tests** - Configuration validation and reference implementations
2. **C++ Unit Tests** - Direct testing of C++ component code
3. **ESPHome Compile Tests** - Integration testing with ESPHome framework

## Test Structure

```
tests/
├── __init__.py
├── test_config_validation.py     # Python: Configuration validation
├── test_curve_interpolation.py   # Python: Curve interpolation
├── test_valve_control.py         # Python: Valve control logic
├── cpp/                          # C++ unit tests
│   ├── CMakeLists.txt
│   ├── test_curve_functions.cpp
│   ├── test_valve_control.cpp
│   └── README.md
└── esphome/                      # ESPHome compile tests
    ├── test_basic.yaml
    ├── test_all_features.yaml
    ├── test_port_configs.yaml
    ├── test_offsets.yaml
    ├── test_actions.yaml
    ├── run_compile_tests.sh
    └── README.md
```

## Quick Start

### Run All Test Levels

```bash
# Python tests
pytest

# C++ tests
cd tests/cpp && mkdir build && cd build
cmake .. && cmake --build .
ctest --verbose

# ESPHome compile tests
cd tests/esphome
./run_compile_tests.sh
```

## Level 1: Python Tests

### Install Test Dependencies

```bash
pip install -r requirements-test.txt
```

### Run Python Tests

```bash
# All Python tests
pytest

# Specific test file
pytest tests/test_config_validation.py
pytest tests/test_curve_interpolation.py
pytest tests/test_valve_control.py
```

### Run Python Tests

```bash
# All Python tests
pytest

# Specific test file
pytest tests/test_config_validation.py
pytest tests/test_curve_interpolation.py
pytest tests/test_valve_control.py

# With coverage
pytest --cov=components/three_way_valve --cov-report=html
```

Open `htmlcov/index.html` for coverage report.

### Python Test Categories

- **Configuration Validation** (`test_config_validation.py`)
  - Port configuration validation
  - Offset validation (steps, degrees)
  - Angle mapping logic
  - Error handling

- **Curve Interpolation** (`test_curve_interpolation.py`)
  - `get_flow()` function (position → flow)
  - `get_pos()` function (flow → position)
  - Inverse function consistency
  - Non-linear curve characteristics

- **Valve Control** (`test_valve_control.py`)
  - `control_valve()` method
  - `get_valve_state()` method
  - `park_valve()` and `open_all_valve()` methods
  - Round-trip consistency tests

## Level 2: C++ Unit Tests

C++ unit tests using Google Test framework for direct testing of component code.

### Build C++ Tests

```bash
cd tests/cpp
mkdir build && cd build
cmake ..
cmake --build .
```

### Run C++ Tests

```bash
# Run all tests
ctest --verbose

# Or run individual executables
./test_curve_functions
./test_valve_control
```

### C++ Test Coverage

```bash
# Build with coverage (Debug mode)
cmake -DCMAKE_BUILD_TYPE=Debug ..
cmake --build .
ctest

# Generate coverage report
lcov --capture --directory . --output-file coverage.info
genhtml coverage.info --output-directory coverage_report
```

Open `coverage_report/index.html` for coverage report.

### C++ Test Files

- **`test_curve_functions.cpp`** - Tests for curve interpolation template functions
- **`test_valve_control.cpp`** - Tests for ThreeWayValve class methods

See [tests/cpp/README.md](cpp/README.md) for details.

## Level 3: ESPHome Compile Tests

Integration tests that verify the component compiles correctly with ESPHome.

### Prerequisites

```bash
pip install esphome
```

### Run ESPHome Tests

```bash
cd tests/esphome

# Validate single configuration
esphome config test_basic.yaml

# Compile single configuration
esphome compile test_basic.yaml

# Run all compile tests
./run_compile_tests.sh
```

### ESPHome Test Configurations

- **`test_basic.yaml`** - Minimal configuration
- **`test_all_features.yaml`** - Full configuration with all options
- **`test_port_configs.yaml`** - All four valid port configurations
- **`test_offsets.yaml`** - Various position offset formats
- **`test_actions.yaml`** - Custom actions (block, open_all)

See [tests/esphome/README.md](esphome/README.md) for details.

## Continuous Integration

The project uses GitHub Actions for automated testing. See `.github/workflows/tests.yml`.

### CI Pipeline

1. **Python Tests** - Run on Python 3.9, 3.10, 3.11, 3.12
2. **C++ Tests** - Build and run on Ubuntu and macOS (Debug & Release)
3. **ESPHome Compile Tests** - Test against multiple ESPHome versions
4. **Code Quality** - black, flake8, pylint checks

### Run Locally Like CI

```bash
# Python tests (all versions if you have them)
pytest tests/ -v --ignore=tests/cpp --ignore=tests/esphome

# C++ tests
cd tests/cpp && mkdir build && cd build
cmake -DCMAKE_BUILD_TYPE=Debug .. && cmake --build .
ctest --output-on-failure

# ESPHome compile tests
cd tests/esphome
./run_compile_tests.sh

# Code quality
black --check components/three_way_valve/ tests/*.py
flake8 components/three_way_valve/ tests/*.py --max-line-length=100
```

## Test Coverage Summary

### Python Tests (Reference Implementation)
- ✅ Configuration validation (validate_offset, validate_ports)
- ✅ Port configuration logic
- ✅ Angle mapping calculations
- ✅ Curve interpolation (get_flow, get_pos)
- ✅ Valve control logic
- ✅ Edge cases and error handling

### C++ Unit Tests
- ✅ Template function correctness (get_flow, get_pos)
- ✅ ThreeWayValve class methods
- ✅ Position calculations
- ✅ State reading
- ✅ Special commands (park, open_all)
- ✅ Tolerance calculations

### ESPHome Compile Tests
- ✅ Component loads correctly
- ✅ Configuration schema validation
- ✅ All port combinations compile
- ✅ Offset calculations work
- ✅ Custom actions register properly
- ✅ Integration with ESPHome framework

## Writing New Tests

When adding new features:

1. **Python Tests** - Add tests to appropriate `test_*.py` file
2. **C++ Tests** - Add tests to `tests/cpp/test_*.cpp`
3. **ESPHome Tests** - Add or update YAML configurations in `tests/esphome/`

### Test Guidelines

- Write tests before implementing features (TDD)
- Cover happy path, edge cases, and error conditions
- Use descriptive test names: `test_<what>_<condition>_<expected>`
- Keep tests independent and isolated
- Mock external dependencies appropriately

## Troubleshooting

### Python Import Errors

If you get ESPHome import errors, the tests use reference implementations that don't require ESPHome installed for Python tests.

### C++ Compilation Errors

Ensure you have:
- CMake 3.14+
- C++17 compatible compiler
- Internet connection (for Google Test download)

### ESPHome Errors

```bash
# Install/upgrade ESPHome
pip install --upgrade esphome

# Check version
esphome version
```

## Contributing

Before submitting PRs:

1. Run all test levels locally
2. Ensure coverage doesn't decrease
3. Update tests for new features
4. Check CI passes on GitHub

## Contributing

Before submitting PRs:

1. Run all test levels locally
2. Ensure coverage doesn't decrease
3. Update tests for new features
4. Check CI passes on GitHub

## Additional Resources

- [Python Testing Documentation](https://docs.pytest.org/)
- [Google Test Documentation](https://google.github.io/googletest/)
- [ESPHome Documentation](https://esphome.io/)
- [GitHub Actions Documentation](https://docs.github.com/actions)

## Test Categories

### 1. Configuration Validation Tests (`test_config_validation.py`)

Tests for the Python configuration schema validation:

- **`TestValidateOffset`**: Tests for position offset validation
  - Valid formats: `"10steps"`, `"-7.5deg"`, `"180degrees"`
  - Invalid inputs and error handling
  - Edge cases (zero, negative, large values)

- **`TestValidatePorts`**: Tests for port configuration validation
  - All valid port assignments (1-2-3, 1-3-2, etc.)
  - Case-insensitive port names
  - Duplicate port detection
  - Invalid port numbers

- **`TestAngleMapping`**: Tests for the angle mapping logic
  - Verifies 90° separation between open/closed positions
  - Tests all four valid port configurations
  - Checks blocked position assignments

### 2. Curve Interpolation Tests (`test_curve_interpolation.py`)

Tests for the non-linear mixer curve functions:

- **`TestGetFlow`**: Tests for position → flow mapping
  - Exact curve points
  - Interpolation between points
  - Boundary conditions (below min, above max)
  - Monotonic increase verification

- **`TestGetPos`**: Tests for flow → position mapping (inverse function)
  - Exact curve points
  - Interpolation accuracy
  - Boundary conditions
  - Monotonic increase verification

- **`TestInverseFunctions`**: Round-trip consistency tests
  - pos → flow → pos
  - flow → pos → flow
  - Verifies functions are proper inverses

- **`TestCurveCharacteristics`**: Validates curve properties
  - Non-linearity
  - Extreme value emphasis
  - Midpoint balance
  - Symmetry characteristics

### 3. Valve Control Tests (`test_valve_control.py`)

Tests for the valve control logic:

- **`TestControlValve`**: Tests for `control_valve()` method
  - Zero and full flow positions
  - Intermediate flow values
  - Flow clamping (negative, > 1.0)
  - Non-linear flow mapping

- **`TestGetValveState`**: Tests for `get_valve_state()` method
  - State at closed/open positions
  - Tolerance handling
  - Position clamping
  - Intermediate positions

- **`TestParkValve`**: Tests for `park_valve()` method
  - Moves to blocked position
  - Different block positions

- **`TestOpenAllValve`**: Tests for `open_all_valve()` method
  - Moves to all-open position
  - Different all-open positions

- **`TestPositionCalculations`**: Edge case tests
  - Reversed position ranges
  - Large and small step ranges
  - Negative positions

- **`TestRoundTripConsistency`**: Integration tests
  - Set flow → read back state consistency
  - Verifies control and state functions work together

## Test Coverage

The tests aim to cover:

- ✅ All configuration validation functions
- ✅ All curve interpolation edge cases
- ✅ All valve control methods
- ✅ Boundary conditions and error cases
- ✅ Integration between components

## Writing New Tests

When adding new features, ensure corresponding tests cover:

1. **Happy path**: Normal, expected usage
2. **Edge cases**: Boundary values (0, 1, min, max)
3. **Error cases**: Invalid inputs, out-of-range values
4. **Integration**: How components work together

## Continuous Integration

These tests can be integrated into CI/CD pipelines:

```yaml
# Example GitHub Actions workflow
- name: Run Tests
  run: |
    pip install -r requirements-test.txt
    pytest --cov --cov-report=xml
```

## Notes

- **Python Reference Implementation**: Since C++ code can't be directly tested from Python, the tests use reference implementations that match the C++ logic exactly.
- **Mock Objects**: Stepper motor and other ESPHome components are mocked to allow unit testing without full ESPHome environment.
- **Tolerance**: Some tests use small tolerances (e.g., `< 1e-6`) to account for floating-point precision.

## Contributing

When contributing new code:

1. Write tests first (TDD approach)
2. Ensure all tests pass: `pytest`
3. Check coverage: `pytest --cov`
4. Run tests before committing

## Troubleshooting

### Import Errors

If you get import errors for ESPHome modules, ensure you're using the mock implementations provided in the tests, or install ESPHome:

```bash
pip install esphome
```

### Test Discovery Issues

If pytest doesn't find tests:

```bash
# Explicitly specify test directory
pytest tests/

# Or run from project root
cd /path/to/Three-Way-Valve
pytest
```
