#!/usr/bin/env bash
# Type Checking Script - Run Pyright on all Python files
# ======================================================
# This script runs pyright type checker on all Python files in the utils/ directory

set -e

# Default values
TARGET_PATH="utils"
VERBOSE=0
SHOW_HELP=0

# Color codes
RED='\033[0;31m'
GREEN='\033[0;32m'
CYAN='\033[0;36m'
YELLOW='\033[1;33m'
GRAY='\033[0;90m'
NC='\033[0m' # No Color

# Parse arguments
while [[ $# -gt 0 ]]; do
    case $1 in
        -p|--path)
            TARGET_PATH="$2"
            shift 2
            ;;
        -v|--verbose)
            VERBOSE=1
            shift
            ;;
        -h|--help)
            SHOW_HELP=1
            shift
            ;;
        *)
            echo -e "${RED}Unknown option: $1${NC}"
            SHOW_HELP=1
            shift
            ;;
    esac
done

if [ $SHOW_HELP -eq 1 ]; then
    cat << 'EOF'
Type Checking Script - Run Pyright on Python files

USAGE:
    ./dev/check_types.sh [OPTIONS]

OPTIONS:
    -p, --path <path>     Directory to check (default: utils)
    -v, --verbose         Show detailed output
    -h, --help            Show this help message

EXAMPLES:
    ./dev/check_types.sh                      # Check all files in utils/
    ./dev/check_types.sh -p utils/server      # Check specific directory
    ./dev/check_types.sh --verbose            # Verbose output

REQUIREMENTS:
    npm install -g pyright

EOF
    exit 0
fi

# Helper functions
print_success() {
    echo -e "${GREEN}$1${NC}"
}

print_error() {
    echo -e "${RED}$1${NC}"
}

print_info() {
    echo -e "${CYAN}$1${NC}"
}

print_warning() {
    echo -e "${YELLOW}$1${NC}"
}

print_gray() {
    echo -e "${GRAY}$1${NC}"
}

# Check if pyright is installed
print_info "Checking for pyright installation..."
if ! command -v pyright &> /dev/null; then
    print_error "✗ Pyright is not installed"
    echo ""
    print_info "To install pyright:"
    print_info "  npm install -g pyright"
    echo ""
    exit 1
fi

PYRIGHT_VERSION=$(pyright --version 2>&1)
print_success "✓ Pyright found: $PYRIGHT_VERSION"

# Get project root
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"

# Resolve target path
FULL_TARGET_PATH="$PROJECT_ROOT/$TARGET_PATH"
if [ ! -d "$FULL_TARGET_PATH" ]; then
    print_error "✗ Path not found: $FULL_TARGET_PATH"
    exit 1
fi

# Find all Python files
echo ""
print_info "Searching for Python files in: $TARGET_PATH"

# Use find to get all .py files, excluding common directories
mapfile -t PYTHON_FILES < <(find "$FULL_TARGET_PATH" -type f -name "*.py" \
    ! -path "*/__pycache__/*" \
    ! -path "*/.venv/*" \
    ! -path "*/venv/*" \
    ! -path "*/.git/*" \
    2>/dev/null)

if [ ${#PYTHON_FILES[@]} -eq 0 ]; then
    print_warning "⚠ No Python files found in $TARGET_PATH"
    exit 0
fi

print_success "✓ Found ${#PYTHON_FILES[@]} Python file(s)"
echo ""

# Display files to be checked
if [ $VERBOSE -eq 1 ]; then
    print_info "Files to check:"
    for file in "${PYTHON_FILES[@]}"; do
        RELATIVE_PATH="${file#$PROJECT_ROOT/}"
        print_gray "  - $RELATIVE_PATH"
    done
    echo ""
fi

# Run pyright
print_info "============================================================"
print_info "Running Pyright Type Checker"
print_info "============================================================"
echo ""

# Change to project root for proper module resolution
cd "$PROJECT_ROOT"

TOTAL_ERRORS=0
TOTAL_WARNINGS=0
FILES_WITH_ERRORS=()

# Run pyright on each file individually for readable output
for file in "${PYTHON_FILES[@]}"; do
    RELATIVE_PATH="${file#$PROJECT_ROOT/}"
    
    # Run pyright on single file
    PYRIGHT_ARGS=("$RELATIVE_PATH")
    if [ $VERBOSE -eq 1 ]; then
        PYRIGHT_ARGS+=("--verbose")
    fi
    
    OUTPUT=$(pyright "${PYRIGHT_ARGS[@]}" 2>&1)
    FILE_EXIT_CODE=$?
    
    # Only display output if there are errors or verbose mode
    if [ $FILE_EXIT_CODE -ne 0 ] || [ $VERBOSE -eq 1 ]; then
        echo ""
        print_info "File: $RELATIVE_PATH"
        print_gray "------------------------------------------------------------"
        echo "$OUTPUT"
        
        if [ $FILE_EXIT_CODE -ne 0 ]; then
            FILES_WITH_ERRORS+=("$RELATIVE_PATH")
            
            # Try to parse error count from output
            if [[ $OUTPUT =~ ([0-9]+)\ error ]]; then
                TOTAL_ERRORS=$((TOTAL_ERRORS + ${BASH_REMATCH[1]}))
            fi
            if [[ $OUTPUT =~ ([0-9]+)\ warning ]]; then
                TOTAL_WARNINGS=$((TOTAL_WARNINGS + ${BASH_REMATCH[1]}))
            fi
        fi
    fi
done

# Summary
echo ""
print_info "============================================================"
if [ ${#FILES_WITH_ERRORS[@]} -eq 0 ]; then
    print_success "✓ Type checking passed - No errors found"
    print_success "  Files checked: ${#PYTHON_FILES[@]}"
else
    print_error "✗ Type checking failed"
    print_error "  Files with errors: ${#FILES_WITH_ERRORS[@]} / ${#PYTHON_FILES[@]}"
    if [ $TOTAL_ERRORS -gt 0 ]; then
        print_error "  Total errors: $TOTAL_ERRORS"
    fi
    if [ $TOTAL_WARNINGS -gt 0 ]; then
        print_warning "  Total warnings: $TOTAL_WARNINGS"
    fi
    echo ""
    print_info "Files with errors:"
    for f in "${FILES_WITH_ERRORS[@]}"; do
        print_error "  - $f"
    done
fi
print_info "============================================================"

# Exit with error if any files had errors
if [ ${#FILES_WITH_ERRORS[@]} -gt 0 ]; then
    exit 1
else
    exit 0
fi
