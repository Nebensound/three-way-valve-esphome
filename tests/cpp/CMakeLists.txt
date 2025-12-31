cmake_minimum_required(VERSION 3.14)
project(ThreeWayValveTests CXX)

# C++ Standard
set(CMAKE_CXX_STANDARD 17)
set(CMAKE_CXX_STANDARD_REQUIRED ON)

# Enable testing
enable_testing()

# Google Test
include(FetchContent)
FetchContent_Declare(
  googletest
  GIT_REPOSITORY https://github.com/google/googletest.git
  GIT_TAG        v1.14.0
)
# For Windows: Prevent overriding the parent project's compiler/linker settings
set(gtest_force_shared_crt ON CACHE BOOL "" FORCE)
FetchContent_MakeAvailable(googletest)

# Include directories
include_directories(
    ${CMAKE_CURRENT_SOURCE_DIR}
    ${CMAKE_CURRENT_SOURCE_DIR}/..
    ${CMAKE_CURRENT_SOURCE_DIR}/../..
)

# Test executables
add_executable(test_curve_functions
    test_curve_functions.cpp
)

add_executable(test_valve_control
    test_valve_control.cpp
)

# Link against gtest
target_link_libraries(test_curve_functions
    gtest
    gtest_main
)

target_link_libraries(test_valve_control
    gtest
    gtest_main
)

# Add tests to CTest
add_test(NAME CurveFunctions COMMAND test_curve_functions)
add_test(NAME ValveControl COMMAND test_valve_control)

# Compiler warnings
if(MSVC)
    target_compile_options(test_curve_functions PRIVATE /W4)
    target_compile_options(test_valve_control PRIVATE /W4)
else()
    target_compile_options(test_curve_functions PRIVATE -Wall -Wextra -Wpedantic)
    target_compile_options(test_valve_control PRIVATE -Wall -Wextra -Wpedantic)
endif()

# Optional: Add coverage flags for debug builds
if(CMAKE_BUILD_TYPE STREQUAL "Debug")
    if(CMAKE_COMPILER_IS_GNUCXX OR CMAKE_CXX_COMPILER_ID MATCHES "Clang")
        target_compile_options(test_curve_functions PRIVATE --coverage)
        target_link_options(test_curve_functions PRIVATE --coverage)
        target_compile_options(test_valve_control PRIVATE --coverage)
        target_link_options(test_valve_control PRIVATE --coverage)
    endif()
endif()

# Print test configuration
message(STATUS "C++ Tests Configuration:")
message(STATUS "  C++ Standard: ${CMAKE_CXX_STANDARD}")
message(STATUS "  Build Type: ${CMAKE_BUILD_TYPE}")
message(STATUS "  Tests: test_curve_functions, test_valve_control")
