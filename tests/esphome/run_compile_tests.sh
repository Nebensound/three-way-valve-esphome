#!/bin/bash
# ESPHome Compile Tests Runner
# Tests compilation of all YAML configurations

set -e  # Exit on error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

# Check if esphome is installed
if ! command -v esphome &> /dev/null; then
    echo -e "${RED}Error: esphome command not found${NC}"
    echo "Install with: pip install esphome"
    exit 1
fi

echo "==================================="
echo "ESPHome Compile Tests"
echo "==================================="
echo ""

# Array of test files
TEST_FILES=(
    "test_basic.yaml"
    "test_all_features.yaml"
    "test_port_configs.yaml"
    "test_offsets.yaml"
    "test_actions.yaml"
)

PASSED=0
FAILED=0
FAILED_TESTS=()

# Function to run test
run_test() {
    local yaml_file="$1"
    echo -e "${YELLOW}Testing: $yaml_file${NC}"
    
    if esphome config "$yaml_file" > /dev/null 2>&1; then
        echo -e "${GREEN}✓ PASSED: $yaml_file${NC}"
        ((PASSED++))
        return 0
    else
        echo -e "${RED}✗ FAILED: $yaml_file${NC}"
        ((FAILED++))
        FAILED_TESTS+=("$yaml_file")
        return 1
    fi
    echo ""
}

# Run all tests
for test_file in "${TEST_FILES[@]}"; do
    if [ -f "$test_file" ]; then
        run_test "$test_file"
    else
        echo -e "${RED}✗ NOT FOUND: $test_file${NC}"
        ((FAILED++))
        FAILED_TESTS+=("$test_file (not found)")
    fi
done

# Summary
echo ""
echo "==================================="
echo "Test Summary"
echo "==================================="
echo -e "Total:  $((PASSED + FAILED))"
echo -e "${GREEN}Passed: $PASSED${NC}"
echo -e "${RED}Failed: $FAILED${NC}"

if [ $FAILED -gt 0 ]; then
    echo ""
    echo "Failed tests:"
    for failed_test in "${FAILED_TESTS[@]}"; do
        echo -e "  ${RED}✗${NC} $failed_test"
    done
    exit 1
else
    echo ""
    echo -e "${GREEN}All tests passed!${NC}"
    exit 0
fi
