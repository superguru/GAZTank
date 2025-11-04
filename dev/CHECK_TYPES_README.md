# Type Checking Scripts

Automated type checking for Python files using Pyright.

## Files

- `check_types.ps1` - PowerShell script (Windows/Linux/Mac)
- `check_types.cmd` - Windows batch wrapper
- `check_types.sh` - Bash script (Linux/Mac)

## Installation

Requires `pyright` to be installed:

```bash
npm install -g pyright
```

## Usage

### Windows

```cmd
.\dev\check_types.cmd                    # Check all files in utils/
.\dev\check_types.cmd -Path utils/server # Check specific directory
.\dev\check_types.cmd -Verbose           # Verbose output
.\dev\check_types.cmd -Help              # Show help
```

### Linux/Mac

```bash
./dev/check_types.sh                      # Check all files in utils/
./dev/check_types.sh -p utils/server      # Check specific directory
./dev/check_types.sh --verbose            # Verbose output
./dev/check_types.sh --help               # Show help
```

### Direct PowerShell

```powershell
pwsh -File .\dev\check_types.ps1 -Path utils -Verbose
```

## Features

- ✅ Automatically detects all Python files recursively
- ✅ Excludes `__pycache__`, `.venv`, `venv`, `.git` directories
- ✅ Colored output for better readability
- ✅ Proper exit codes (0 = success, 1 = errors)
- ✅ Cross-platform compatible
- ✅ Verbose mode for detailed output

## Exit Codes

- `0` - No type errors found
- `1` - Type errors found or pyright not installed

## Integration

Can be integrated into:
- CI/CD pipelines
- Pre-commit hooks
- VS Code tasks
- Build scripts

## Example Output

```
Checking for pyright installation...
✓ Pyright found: pyright 1.1.406

Searching for Python files in: utils
✓ Found 33 Python file(s)

============================================================
Running Pyright Type Checker
============================================================

0 errors, 0 warnings, 0 informations

============================================================
✓ Type checking passed - No errors found
============================================================
```
