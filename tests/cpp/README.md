# C++ Unit Tests

C++ unit tests for the Three-Way Valve component using Google Test framework.

## Prerequisites

- CMake 3.14 or higher
- C++17 compatible compiler (GCC, Clang, or MSVC)
- Internet connection (for downloading Google Test)

## Building Tests

```bash
cd tests/cpp
mkdir build
cd build
cmake ..
cmake --build .
```

## Running Tests

### Run all tests
```bash
ctest --verbose
```

Or run individual test executables:
```bash
./test_curve_functions
./test_valve_control
```

## Test Coverage

### With GCC/Clang (Debug build)
```bash
cmake -DCMAKE_BUILD_TYPE=Debug ..
cmake --build .
ctest
lcov --capture --directory . --output-file coverage.info
genhtml coverage.info --output-directory coverage_report
```

Then open `coverage_report/index.html` in a browser.

## Test Files

- **`test_curve_functions.cpp`** - Tests for `get_flow()` and `get_pos()` template functions
- **`test_valve_control.cpp`** - Tests for `ThreeWayValve` class methods

## Architecture

The C++ tests use minimal mocks for ESPHome dependencies (Valve, Stepper, Component) to allow standalone compilation without the full ESPHome framework.
