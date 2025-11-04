#!/usr/bin/env pwsh
# Type Checking Script - Run Pyright on all Python files
# ======================================================
# This script runs pyright type checker on all Python files in the utils/ directory

param(
    [string]$Path = "utils",
    [switch]$Verbose,
    [switch]$Help
)

if ($Help) {
    $helpText = @"
Type Checking Script - Run Pyright on Python files

USAGE:
    .\dev\check_types.ps1 [OPTIONS]

OPTIONS:
    -Path <path>      Directory to check (default: utils)
    -Verbose          Show detailed output
    -Help             Show this help message

EXAMPLES:
    .\dev\check_types.ps1                    # Check all files in utils/
    .\dev\check_types.ps1 -Path utils/server # Check specific directory
    .\dev\check_types.ps1 -Verbose           # Verbose output

REQUIREMENTS:
    npm install -g pyright
"@
    Write-Host $helpText
    exit 0
}

# Color output helpers
function Write-Success($message) {
    Write-Host $message -ForegroundColor Green
}

function Write-ErrorMsg($message) {
    Write-Host $message -ForegroundColor Red
}

function Write-Info($message) {
    Write-Host $message -ForegroundColor Cyan
}

function Write-Warning($message) {
    Write-Host $message -ForegroundColor Yellow
}

# Check if pyright is installed
Write-Info "Checking for pyright installation..."
$pyrightVersion = $null
try {
    $pyrightVersion = pyright --version 2>&1 | Out-String
    if ($LASTEXITCODE -eq 0) {
        Write-Success "✓ Pyright found: $($pyrightVersion.Trim())"
    } else {
        throw "Pyright not found"
    }
} catch {
    Write-ErrorMsg "✗ Pyright is not installed"
    Write-Info ""
    Write-Info "To install pyright:"
    Write-Info "  npm install -g pyright"
    Write-Info ""
    exit 1
}

# Get project root
$scriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$projectRoot = Split-Path -Parent $scriptDir

# Resolve target path
$targetPath = Join-Path $projectRoot $Path
if (-not (Test-Path $targetPath)) {
    Write-ErrorMsg "✗ Path not found: $targetPath"
    exit 1
}

# Find all Python files
Write-Info ""
Write-Info "Searching for Python files in: $Path"
$pythonFiles = Get-ChildItem -Path $targetPath -Filter "*.py" -Recurse | Where-Object { 
    $_.FullName -notmatch '\\__pycache__\\' -and 
    $_.FullName -notmatch '\\.venv\\' -and
    $_.FullName -notmatch '\\venv\\' -and
    $_.FullName -notmatch '\\.git\\'
}

if ($pythonFiles.Count -eq 0) {
    Write-Warning "⚠ No Python files found in $Path"
    exit 0
}

Write-Success "✓ Found $($pythonFiles.Count) Python file(s)"
Write-Info ""

# Display files to be checked
if ($Verbose) {
    Write-Info "Files to check:"
    foreach ($file in $pythonFiles) {
        $relativePath = $file.FullName.Replace($projectRoot + [IO.Path]::DirectorySeparatorChar, "")
        Write-Host "  - $relativePath" -ForegroundColor Gray
    }
    Write-Info ""
}

# Run pyright
Write-Info ""
$separator = "=" * 60
Write-Info $separator
Write-Info "Running Pyright Type Checker"
Write-Info $separator
Write-Info ""

# Change to project root for proper module resolution
Push-Location $projectRoot

try {
    $totalErrors = 0
    $totalWarnings = 0
    $filesWithErrors = @()
    
    # Run pyright on each file individually for readable output
    foreach ($file in $pythonFiles) {
        $relativePath = $file.FullName.Replace($projectRoot + [IO.Path]::DirectorySeparatorChar, "").Replace([IO.Path]::DirectorySeparatorChar, "/")
        
        # Run pyright on single file
        $pyrightArgs = @($relativePath)
        if ($Verbose) {
            $pyrightArgs += "--verbose"
        }
        
        $output = & pyright @pyrightArgs 2>&1 | Out-String
        $fileExitCode = $LASTEXITCODE
        
        # Only display output if there are errors or verbose mode
        if ($fileExitCode -ne 0 -or $Verbose) {
            Write-Host ""
            Write-Host "File: $relativePath" -ForegroundColor Cyan
            Write-Host ("-" * 60) -ForegroundColor Gray
            Write-Host $output
            
            if ($fileExitCode -ne 0) {
                $filesWithErrors += $relativePath
                
                # Try to parse error count from output
                if ($output -match '(\d+) error') {
                    $totalErrors += [int]$Matches[1]
                }
                if ($output -match '(\d+) warning') {
                    $totalWarnings += [int]$Matches[1]
                }
            }
        }
    }
    
    # Summary
    Write-Info ""
    Write-Info $separator
    if ($filesWithErrors.Count -eq 0) {
        Write-Success "✓ Type checking passed - No errors found"
        Write-Success "  Files checked: $($pythonFiles.Count)"
    } else {
        Write-ErrorMsg "✗ Type checking failed"
        Write-ErrorMsg "  Files with errors: $($filesWithErrors.Count) / $($pythonFiles.Count)"
        if ($totalErrors -gt 0) {
            Write-ErrorMsg "  Total errors: $totalErrors"
        }
        if ($totalWarnings -gt 0) {
            Write-Warning "  Total warnings: $totalWarnings"
        }
        Write-Info ""
        Write-Info "Files with errors:"
        foreach ($f in $filesWithErrors) {
            Write-Host "  - $f" -ForegroundColor Red
        }
    }
    Write-Info $separator
    
    # Exit with error if any files had errors
    if ($filesWithErrors.Count -gt 0) {
        exit 1
    } else {
        exit 0
    }
    
} finally {
    Pop-Location
}
