# GAZTank Build Pipeline Orchestrator

Complete build pipeline orchestration system that runs all GAZTank build steps in sequence. Coordinates execution of clean, setup, lint, normalise, generate, sitemap, toc, package, and deploy modules in the correct order with unified argument handling.

**Version:** 1.1  
**Last Updated:** November 4, 2025

## Table of Contents

- [Purpose](#purpose)
- [Build Pipeline](#build-pipeline)
- [Logging](#logging)
- [Usage](#usage)
  - [Command Line](#command-line)
  - [As a Module](#as-a-module)
- [Command Line Arguments](#command-line-arguments)
- [Module Structure](#module-structure)
- [Features](#features)
- [Pipeline Stages](#pipeline-stages)
- [Timing Metrics](#timing-metrics)
- [Invocation Points](#invocation-points)
- [Development](#development)
- [Best Practices](#best-practices)
- [Troubleshooting](#troubleshooting)
- [Future Enhancements](#future-enhancements)
- [Related Documentation](#related-documentation)
- [License](#license)

## Purpose

The GAZTank Build Pipeline Orchestrator provides a single command to execute the complete website build and deployment workflow. It acts as a coordinator that:

- Executes all pipeline modules in the correct sequence
- Passes arguments through to each module consistently
- Tracks execution time for build steps and deployment separately
- Provides unified error handling and reporting
- Manages clean-all mode for environment cleanup
- Offers rich console output with progress indicators
- Generates comprehensive operational logs

### Pipeline Execution Order

The orchestrator runs 10 steps in this sequence:

1. **Clean** - Identify orphaned files in environment (no deletion by default)
2. **Compose** - Generate source content (e.g., humans.txt from template)
3. **Setup** - Apply site configuration (forced)
4. **Lint** - Run HTML, JavaScript, and config validation
5. **Normalise** - Normalize markdown file formatting
6. **Generate** - Convert markdown to HTML content
7. **Sitemap** - Generate sitemap.xml for SEO
8. **TOC** - Add table of contents to HTML files
9. **Package** - Sync, minify, and archive site files
10. **Deploy** - Upload package to remote FTP/FTPS server

### Environment-Aware Operation

The orchestrator requires a mandatory `-e` argument to specify the target environment:
- **dev** - Development environment for local testing
- **staging** - Pre-production environment for validation
- **prod** - Production environment for live deployment

All downstream modules receive this environment parameter automatically.

### Argument Pass-Through

The orchestrator uses a simplified argument handling approach:
- Only validates `-e` (required) and `-h` (help)
- Passes all other arguments through to every pipeline module
- Each module decides which arguments it supports
- Enables flexible workflows without code changes

## Build Pipeline

The orchestrator coordinates the complete GAZTank build workflow:

```
Build Pipeline Flow:
  1. Parse -e environment argument (required)
  2. Initialize logging for gzbuild
  3. Handle --clean-all or --clean-orphaned modes (if specified):
     → Run clean module with all arguments
     → Exit without running pipeline
  4. Execute 10-step pipeline:
     a. Identify orphaned files (no deletion)
     b. Generate source content
     c. Apply site configuration (with --force)
     d. Run lint checks
     e. Normalize markdown formatting
     f. Generate content
     g. Generate sitemap
     h. Generate table of contents
     i. Package site files
     [Build timing captured here]
     j. Deploy to environment
     [Deployment timing captured here]
  5. Report timing metrics (build, deploy, total)
  6. Return exit code for automation
```

**Purpose:** Single-command full website build and deployment

**Location:** Called via `scripts/gzbuild.cmd -e <env>` or `scripts/gzbuild.sh -e <env>`

### Workflow:
```
gzbuild -e env [options] → validates environment → passes args to 10 modules → reports timing → exit
```

### Benefits:
- Single command builds and deploys entire site
- Consistent argument handling across all modules
- Separate timing for build (steps 1-9) and deployment (step 10)
- Stop-on-error behavior prevents invalid deployments
- Rich console output with emojis and progress indicators
- Clean operational logs without formatting
- Safe default: clean step identifies orphaned files without deleting

## Logging

The orchestrator uses the **gzlogging** infrastructure for environment-aware operational logging.

### Log Configuration

- **Environment:** Specified via `-e` argument (dev/staging/prod)
- **Tool Name:** `gzbuild`
- **Log Location:** `logs/{environment}/gzbuild_YYYYMMDD.log`
- **Output Mode:** File-only (console has its own formatting)
- **Encoding:** UTF-8

### What Gets Logged

#### Logged to file (clean operational log):
- GAZTank Build Pipeline started
- Project root path
- Target environment
- Step 1/8 through Step 8/8 with descriptive names
- Step failures with error messages
- Build steps completed with formatted time
- Deployment completed with formatted time
- Build/deployment/total time metrics
- Pipeline execution completed successfully
- Pipeline execution failed (on error)

#### Console output (rich formatting with emojis):
- Pipeline header with separator (🏗️)
- Progress indicators: [1/8] through [8/8]
- Step emojis: 🧹🧰🔍📄🗺️📑📦🚀
- Success banner with checkmarks (✅)
- Timing summary with clock emoji (⏱️)
- Clean-all mode banner (🧹)
- Blank lines for visual spacing

#### Not logged (kept clean):
- No blank lines in log files
- No separator lines (===) in logs
- No emoji or formatting characters in log files
- Individual module output (each module logs separately)

### Log File Example

```log
[2025-11-04 01:15:32] [dev] [INF] GAZTank Build Pipeline started
[2025-11-04 01:15:32] [dev] [INF] Project root: D:\Projects\www\GAZTank
[2025-11-04 01:15:32] [dev] [INF] Target environment: dev
[2025-11-04 01:15:32] [dev] [INF] Step 1/10: Identifying orphaned files
[2025-11-04 01:15:33] [dev] [INF] Step 2/10: Generating source content
[2025-11-04 01:15:34] [dev] [INF] Step 3/10: Applying site configuration
[2025-11-04 01:15:36] [dev] [INF] Step 4/10: Running lint checks
[2025-11-04 01:15:37] [dev] [INF] Step 5/10: Normalizing markdown files
[2025-11-04 01:15:38] [dev] [INF] Step 6/10: Generating content files
[2025-11-04 01:15:39] [dev] [INF] Step 7/10: Generating sitemap
[2025-11-04 01:15:40] [dev] [INF] Step 8/10: Generating table of contents
[2025-11-04 01:15:41] [dev] [INF] Step 9/10: Packaging site files
[2025-11-04 01:15:43] [dev] [INF] Build steps completed in 0m 11s
[2025-11-04 01:15:43] [dev] [INF] Step 10/10: Deploying to target environment
[2025-11-04 01:16:00] [dev] [INF] Deployment completed in 0m 17s
[2025-11-04 01:16:00] [dev] [INF] Build time: 0m 11s, Deployment time: 0m 17s, Total time: 0m 28s
[2025-11-04 01:16:00] [dev] [INF] GAZTank Build Pipeline completed successfully
```

In clean-all or clean-orphaned mode:

```log
[2025-11-04 01:20:15] [dev] [INF] GAZTank Build Pipeline started in CLEAN-ALL mode
[2025-11-04 01:20:15] [dev] [INF] Project root: D:\Projects\www\GAZTank
[2025-11-04 01:20:15] [dev] [INF] Target environment: dev
```

### Viewing Logs

```bash
# View today's log (Linux/Mac)
cat logs/dev/gzbuild_$(date +%Y%m%d).log

# View today's log (PowerShell)
Get-Content "logs\dev\gzbuild_$(Get-Date -Format 'yyyyMMdd').log"

# Tail recent entries
Get-Content -Tail 30 "logs\dev\gzbuild_$(Get-Date -Format 'yyyyMMdd').log"
```

## Usage

### Command Line

```bash
# Using the launcher script (recommended)
scripts\gzbuild.cmd -e dev                    # Windows - build dev environment
scripts\gzbuild.cmd -e staging                # Windows - build staging environment
scripts\gzbuild.cmd -e prod                   # Windows - build production environment
./scripts/gzbuild.sh -e dev                   # Linux/Mac - build dev environment

# With command-line options
scripts\gzbuild.cmd -e dev --force            # Force all operations
scripts\gzbuild.cmd -e dev --dry-run          # Preview without changes
scripts\gzbuild.cmd -e dev --force --dry-run  # Preview forced operations
scripts\gzbuild.cmd -e dev --clean-all        # Clean environment and exit

# Direct invocation
python -m gzbuild -e dev
python -m gzbuild -e staging --force
python -m gzbuild -e prod --dry-run
python -m gzbuild --help
```

#### Launcher Scripts:
- `scripts/gzbuild.cmd` - Windows launcher with UTF-8 encoding
- `scripts/gzbuild.sh` - Linux/Mac launcher with UTF-8 encoding

Both scripts:
- Set `PYTHONIOENCODING=utf-8` for emoji support in console
- Call `python -m gzbuild` module pattern
- Pass all arguments (including `-e environment`) through to the Python module
- Return the module's exit code for build automation

### As a Module

You can import and use the orchestrator functions in your own Python scripts:

```python
from utils.gzbuild.builder import run_pipeline
from utils.gzlogging import get_logging_context

# Initialize logging
log = get_logging_context('dev', 'gzbuild')

# Build pass-through arguments
pass_through_args = ['-e', 'dev', '--force']

# Run the complete pipeline
success, build_time, deploy_time, total_time = run_pipeline(pass_through_args)

if success:
    print(f"Pipeline completed in {total_time}s")
else:
    print("Pipeline failed")
```

For simpler integration:

```python
from utils.gzbuild.builder import main
import sys

# Set up arguments
sys.argv = ['gzbuild', '-e', 'dev', '--force']

# Run the orchestrator
main()  # Will exit with appropriate code
```

## Command Line Arguments

### Required Arguments

- **`-e`, `--environment`** - Target environment for build and deployment (REQUIRED)
  - **Choices:** `dev`, `staging`, `prod`
  - **Purpose:** Specifies which environment to build and deploy
  - **Passed to:** All 8 pipeline modules automatically
  - **Examples:**
    - `-e dev` → builds and deploys to dev environment
    - `-e staging` → builds and deploys to staging environment
    - `-e prod` → builds and deploys to production environment

### Optional Arguments

- **`--force`** - Force operations even if validation fails
  - Passed through to all modules that support it
  - Each module interprets --force according to its needs
  - Example: `scripts\gzbuild.cmd -e dev --force`

- **`--dry-run`** - Preview operations without making changes
  - Passed through to all modules that support it
  - Modules that don't fully implement dry-run may warn
  - Does not prevent pipeline execution
  - Example: `scripts\gzbuild.cmd -e dev --dry-run`

- **`--clean-all`** - Clean all generated files and exit
  - Runs only the clean module with --clean-all flag
  - Exits immediately without running pipeline
  - Requires confirmation prompt (type "yes" to proceed)
  - Useful for complete environment reset
  - Example: `scripts\gzbuild.cmd -e dev --clean-all`

- **`--clean-orphaned`** - Clean orphaned files and exit
  - Runs only the clean module with --clean-orphaned flag
  - Exits immediately without running pipeline
  - Removes files in environment that don't exist in source
  - Requires confirmation prompt (type "yes" to proceed)
  - Example: `scripts\gzbuild.cmd -e dev --clean-orphaned`

- **`-h`, `--help`** - Display usage information
  - Shows all available command-line options
  - Lists all 10 pipeline stages
  - Displays usage examples
  - Example: `python -m gzbuild --help`

### Argument Pass-Through Behavior

The orchestrator uses a **simplified pass-through model**:

1. **Validates only:** `-e` (required) and `-h` (help)
2. **Passes through:** All other arguments to every module
3. **Module responsibility:** Each module decides which arguments it supports
4. **Benefits:** No code changes needed to add new arguments

#### Example:
```bash
scripts\gzbuild.cmd -e dev --force --dry-run --custom-arg
```

What happens:
- `gzbuild` validates `-e dev` is valid
- Passes `['-e', 'dev', '--force', '--dry-run', '--custom-arg']` to all 10 modules
- Modules that support `--force` use it
- Modules that support `--dry-run` use it
- Modules that don't recognize `--custom-arg` ignore it or error

### Console Output Modes

#### Default mode with per-step timing:
```
============================================================
  🏗️  GAZ Tank - Complete Pipeline Execution
============================================================

🧹 [1/10] Identifying orphaned files...

✏️  [2/10] Generating source content...

⚙️  [3/10] Applying site configuration...

🔍 [4/10] Running lint checks...

� [5/10] Normalizing markdown files...

�📄 [6/10] Generating content...

🗺️  [7/10] Generating sitemap...

📑 [8/10] Generating table of contents...

📦 [9/10] Packaging site files...

🚀 [10/10] Deploying to environment...

============================================================
  ✅ Pipeline Complete!
============================================================
  All pipeline stages executed successfully.
  Your site has been:
    - 🧹 Identifying orphaned files    ⏱️  7ms
    - ✏️  Generating source content     ⏱️  45ms
    - ⚙️  Applying site configuration  ⏱️  407ms
    - 🔍 Running lint checks           ⏱️  12ms
    - 📏 Normalizing markdown files    ⏱️  28ms
    - 📄 Generating content            ⏱️  17ms
    - 🗺️  Generating sitemap           ⏱️  8ms
    - 📑 Generating table of contents  ⏱️  99ms
    - 📦 Packaging site files          ⏱️  8ms
    - 🚀 Deploying to environment      ⏱️  3ms

  ⏱️  Total time: 634ms
============================================================
```

#### Clean-all or clean-orphaned mode:
```
============================================================
  🧹 GAZ Tank - Clean Mode
============================================================

🧹 Cleaning files...

============================================================
  ✅ Clean Complete!
============================================================
  Files have been removed (or identified).
============================================================
```

## Module Structure

```
gzbuild/
├── __init__.py      # Package initialization with version
├── __main__.py      # Entry point for python -m gzbuild
├── builder.py       # Main orchestrator (this module)
└── README.md        # This file
```

### Architecture

The module uses an object-oriented design with two main classes:

#### PipelineStep (dataclass)

Encapsulates configuration and execution logic for a single pipeline step.

##### Responsibilities:
- Store step configuration (icon, module, function, description, args)
- Execute the module with proper argument handling
- Track execution timing in milliseconds
- Generate formatted summary lines with aligned timing
- Log step progress and results

##### Benefits:
- Clean separation of step configuration from execution
- Reusable for any pipeline module
- Pre-calculates full_description in __post_init__ for performance
- Type-safe with dataclass field definitions

#### Pipeline

Manages the collection of steps and orchestrates their execution.

##### Responsibilities:
- Maintain ordered list of PipelineStep instances
- Automatically track max_desc_len as steps are added
- Execute all steps sequentially with stop-on-error behavior
- Extract deployment timing from flagged steps
- Display formatted completion summary with aligned per-step timings

##### Benefits:
- Automatic alignment tracking eliminates manual calculation
- Single source of truth for step collection
- Encapsulates execution loop and summary display
- Easy to extend with new methods (e.g., parallel execution, filtering)

#### run_pipeline() Function

High-level coordinator that uses the Pipeline API.

##### Responsibilities:
- Create Pipeline instance
- Configure and add 8 pipeline steps
- Execute pipeline and handle results
- Calculate timing metrics (build, deploy, total)
- Coordinate logging of completion status

##### Benefits:
- Clean, declarative step configuration
- Simple API: pipeline.add(), pipeline.execute_all(), pipeline.print_summary()
- Easy to modify step order or add new steps
- Separation of concerns: configuration vs execution vs summary

### Key Classes

#### PipelineStep (dataclass)

A dataclass representing a single step in the build pipeline.

##### Fields:
- `icon: str` - Emoji icon for visual identification
- `module_name: str` - Name of the module being executed
- `main_func: Callable` - Main function of the module to execute
- `description: str` - Human-readable description of the step
- `extra_args: list` - Additional arguments to pass to module (default: [])
- `display_timing: bool` - Whether to highlight this step's timing (default: False)
- `time_ms: int` - Execution time in milliseconds (computed, not initialized)
- `step_num: int` - Step number in pipeline (computed, not initialized)
- `full_description: str` - Concatenated icon + description (computed in __post_init__)

##### Methods:
- `__post_init__()` - Calculates full_description after initialization
- `get_summary_line(max_desc_len)` - Returns formatted string with aligned timing for summary display
- `execute(step_num, total_steps, pass_through_args)` - Executes the module, tracks timing, logs results; returns True on success

#### Pipeline

A class that manages a collection of pipeline steps and orchestrates their execution.

##### Attributes:
- `steps: list[PipelineStep]` - List of pipeline steps to execute
- `max_desc_len: int` - Maximum description length for aligned display (auto-updated)

##### Methods:
- `add(step)` - Adds a step to the pipeline and automatically updates max_desc_len
- `execute_all(pass_through_args)` - Executes all steps in sequence, returns True if all succeed
- `get_deploy_time()` - Returns deployment time from step marked with display_timing=True
- `print_summary(total_time)` - Prints formatted completion summary with aligned per-step timings

### Key Functions

#### builder.py

- **`main()`** - Entry point with argument parsing and pipeline execution
- **`get_project_root()`** - Returns project root directory Path
- **`format_time(milliseconds)`** - Formats milliseconds into flexible time display format
- **`run_pipeline(pass_through_args)`** - Creates Pipeline, adds 8 steps, executes them, returns (success, build_time_ms, deploy_time_ms, total_time_ms)

### Pipeline Module Imports

```python
from utils.clean.cleaner import main as clean_main
from utils.compose.composer import main as compose_main
from utils.setup.setup import main as setup_main
from utils.gzlint.gzlinter import main as lint_main
from utils.normalise.batch import main as normalise_main
from utils.generate.generator import main as generate_main
from utils.sitemap.sitemapper import main as sitemap_main
from utils.toc.toc import main as toc_main
from utils.package.packager import main as package_main
from utils.deploy.deployer import main as deploy_main
```

## Features

### Core Features

- **Sequential execution**: Runs 10 pipeline modules in correct order
- **Stop-on-error**: Halts pipeline if any step fails
- **Argument pass-through**: Simplifies adding new arguments
- **Clean modes**: Dedicated cleanup without pipeline (--clean-all, --clean-orphaned)
- **Safe defaults**: Clean step identifies orphaned files without deleting
- **Timing metrics**: Separate tracking for build, deployment, and total time
- **Per-step timing display**: Shows execution time for each individual step in summary
- **Aligned output**: Column-aligned timing display for easy reading
- **Rich console output**: Emojis and progress indicators for better UX
- **Clean logging**: Operational logs without formatting or blank lines
- **Exit codes**: Returns proper codes for build automation (0 success, 1 failure)
- **UTF-8 support**: Full Unicode and emoji support in console output
- **Environment-aware**: All modules receive environment parameter
- **Object-oriented design**: Clean separation with PipelineStep and Pipeline classes

### Stop-on-Error Behavior

The orchestrator uses exception handling to detect failures:

```python
try:
    module_main()
except SystemExit as e:
    if e.code != 0:
        log.err("Step X/8 failed: Module Name")
        return False, 0, 0, 0
```

#### What happens on failure:
- Pipeline stops immediately
- Error logged to gzbuild log file
- Console shows which step failed
- Returns exit code 1 for automation
- No subsequent steps execute
- Invalid builds never reach deployment

### Simplified Argument Handling

**Philosophy:** The orchestrator should not need code changes to support new arguments.

#### Implementation:
```python
# Only validate -e and -h
environment = extract_environment_from_argv()

# Pass everything else through
pass_through_args = sys.argv[1:]  # Include -e and all other args

# Each module receives same args
sys.argv = ['module_name'] + pass_through_args
module_main()
```

#### Benefits:
- No explicit `--force`, `--dry-run` argument definitions
- Easy to add new arguments in the future
- Modules control their own argument support
- Consistent argument handling across pipeline

## Pipeline Stages

The orchestrator executes 10 stages in sequence:

### Stage 1: Identify Orphaned Files

**Module:** `utils.clean.cleaner`  
**Purpose:** Identify files in environment that don't exist in source (no deletion)  
**Arguments:** Receives all pass-through args (runs in identify-only mode by default)  
**Console:** 🧹 [1/10] Identifying orphaned files...  
**Note:** Does NOT delete files by default - use `--clean-orphaned` separately if cleanup needed

### Stage 2: Generate Source Content

**Module:** `utils.compose.composer`  
**Purpose:** Generate source content files from templates (e.g., humans.txt)  
**Arguments:** Receives all pass-through args  
**Console:** ✏️  [2/10] Generating source content...

**Module:** `utils.setup.setup`  
**Purpose:** Apply site.toml configuration to environment  
**Arguments:** Receives `--force` plus all pass-through args  
**Console:** ⚙️  [3/10] Applying site configuration...  
**Note:** Always runs in force mode to ensure consistent configuration

### Stage 4: Run Lint Checks

**Module:** `utils.gzlint.gzlinter`  
**Purpose:** Validate HTML, JavaScript, and config files  
**Arguments:** Receives all pass-through args  
**Console:** 🔍 [4/10] Running lint checks...

### Stage 5: Normalize Markdown Formatting

**Module:** `utils.normalise.batch`  
**Purpose:** Normalize markdown file formatting for consistency  
**Arguments:** Receives all pass-through args  
**Console:** 📏 [5/10] Normalizing markdown files...

### Stage 6: Generate Content

**Module:** `utils.generate.generator`  
**Purpose:** Convert markdown to HTML content  
**Arguments:** Receives all pass-through args  
**Console:** 📄 [6/10] Generating content...

### Stage 7: Generate Sitemap

**Module:** `utils.sitemap.sitemapper`  
**Purpose:** Create sitemap.xml for search engines  
**Arguments:** Receives all pass-through args  
**Console:** 🗺️  [7/10] Generating sitemap...

### Stage 8: Generate Table of Contents

**Module:** `utils.toc.toc`  
**Purpose:** Add TOC navigation to HTML files  
**Arguments:** Receives all pass-through args  
**Console:** 📑 [8/10] Generating table of contents...

### Stage 9: Package Site Files

**Module:** `utils.package.packager`  
**Purpose:** Sync, minify, and archive site for deployment  
**Arguments:** Receives all pass-through args  
**Console:** 📦 [9/10] Packaging site files...  
**Timing:** Build time captured after this step

### Stage 10: Deploy to Environment

**Module:** `utils.deploy.deployer`  
**Purpose:** Upload package to remote FTP/FTPS server  
**Arguments:** Receives all pass-through args  
**Console:** 🚀 [10/10] Deploying to environment...  
**Timing:** Deployment time captured for this step only

## Timing Metrics

The orchestrator tracks three timing metrics with millisecond precision:

### Build Time

**Measured:** From pipeline start through step 9 (package)  
**Includes:** Clean, compose, setup, lint, normalise, generate, sitemap, toc, package  
**Excludes:** Deployment (step 10)  
**Purpose:** Track local build operations performance  
**Precision:** Milliseconds  
**Display:** Flexible format based on duration

### Deployment Time

**Measured:** Step 10 (deploy) only  
**Includes:** FTP/FTPS upload to remote server  
**Excludes:** All build steps  
**Purpose:** Track network upload performance separately  
**Precision:** Milliseconds  
**Display:** Flexible format based on duration

### Total Time

**Measured:** From pipeline start to end  
**Includes:** All 10 steps  
**Formula:** Build time + Deployment time  
**Purpose:** Overall pipeline duration  
**Precision:** Milliseconds  
**Display:** Flexible format based on duration

### Timing Display Format

Time is formatted flexibly based on duration:
- **Under 1 second:** "XXXms" (e.g., "450ms", "892ms")
- **1-59 seconds:** "Xs XXXms" (e.g., "5s 234ms", "42s 891ms")
- **60+ seconds:** "Xm Ys XXXms" (e.g., "2m 15s 340ms", "15m 0s 120ms")
- Milliseconds omitted if zero (e.g., "3s", "2m 15s")

### Example Timing Output

```
============================================================
  ✅ Pipeline Complete!
============================================================
  All pipeline stages executed successfully.
  Your site has been:
    - 🧹 Cleaning orphaned files       ⏱️  7ms
    - ⚙️  Applying site configuration  ⏱️  407ms
    - 🔍 Running lint checks           ⏱️  12ms
    - 📄 Generating content            ⏱️  17ms
    - 🗺️  Generating sitemap           ⏱️  8ms
    - 📑 Generating table of contents  ⏱️  99ms
    - 📦 Packaging site files          ⏱️  8ms
    - 🚀 Deploying to environment      ⏱️  3ms

  ⏱️  Total time: 566ms
============================================================
```

## Invocation Points

The orchestrator is the main entry point for full website builds:

### 1. Direct Command-Line Usage

Primary method for running full builds:

```bash
# Windows
scripts\gzbuild.cmd -e dev

# Linux/Mac
./scripts/gzbuild.sh -e dev
```

**Purpose:** Complete build and deployment workflow  
**Location:** `scripts/gzbuild.cmd` and `scripts/gzbuild.sh`

### 2. CI/CD Pipeline

Continuous integration systems call gzbuild for automated deployments:

```yaml
# Example CI/CD step
- name: Build and Deploy
  run: scripts/gzbuild.cmd -e prod --force
```

**Purpose:** Automated production deployments

### 3. Development Workflow

Developers use gzbuild for testing complete workflows:

```bash
# Test full build without deploying
scripts\gzbuild.cmd -e dev --dry-run

# Force complete rebuild
scripts\gzbuild.cmd -e dev --force
```

**Purpose:** Development and testing

### Integration Points

| Component | Path | Description |
|-----------|------|-------------|
| **Launcher Scripts** | `scripts/gzbuild.*` | Command-line interface |
| **Pipeline Modules** | `utils/{module}/` | 10 modules orchestrated |
| **Logging** | `utils/gzlogging/` | Centralized logging |
| **Configuration** | `config/*.toml` | All module configs |
| **Environments** | `publish/{env}/` | Target directories |
| **Packages** | `publish/packages/` | Deployment archives |

## Development

The module follows standard Python packaging conventions with a focus on simplicity and maintainability.

### File Locations

```
GAZTank/
├── config/
│   └── *.toml                       # All module configurations
│
├── logs/
│   └── {environment}/
│       └── gzbuild_YYYYMMDD.log     # Daily orchestrator logs
│       └── {module}_YYYYMMDD.log    # Module-specific logs
│
├── scripts/
│   ├── gzbuild.cmd                  # Windows launcher
│   └── gzbuild.sh                   # Linux/Mac launcher
│
├── publish/
│   ├── dev/                         # Dev environment output
│   ├── staging/                     # Staging environment output
│   ├── prod/                        # Production environment output
│   └── packages/                    # Deployment archives
│
└── utils/
    ├── gzbuild/                     # This module
    │   ├── __init__.py              # Package initialization
    │   ├── __main__.py              # Entry point
    │   ├── builder.py               # Main orchestrator
    │   └── README.md                # This file
    │
    ├── clean/                       # Pipeline module 1
    ├── compose/                     # Pipeline module 2
    ├── setup/                       # Pipeline module 3
    ├── gzlint/                      # Pipeline module 4
    ├── normalise/                   # Pipeline module 5
    ├── generate/                    # Pipeline module 6
    ├── sitemap/                     # Pipeline module 7
    ├── toc/                         # Pipeline module 8
    ├── package/                     # Pipeline module 9
    ├── deploy/                      # Pipeline module 10
    │
    ├── gzlogging/                   # Logging infrastructure
    └── gzconfig/                    # Configuration library
```

### Adding New Pipeline Modules

To add a new module to the pipeline:

1. Create the module following GAZTank standards
2. Import the module's main function in `builder.py`:
   ```python
   from utils.newmodule.newmodule import main as newmodule_main
   ```
3. Add a step to the Pipeline in `run_pipeline()` function:
   ```python
   pipeline.add(PipelineStep(
       "🔧",              # Icon emoji
       "newmodule",       # Module name
       newmodule_main,    # Main function
       "Running new module"  # Description
   ))
   ```
4. Update total step count (currently 10) in console output and documentation
5. The Pipeline class automatically:
   - Tracks max_desc_len for alignment
   - Numbers steps sequentially
   - Displays timing in summary
   - Handles execution and error reporting

### Design Principles

- **Orchestration not implementation**: Delegates all work to modules
- **Stop-on-error**: Fail fast to prevent invalid deployments
- **Argument pass-through**: Minimize orchestrator responsibilities
- **Timing transparency**: Show where time is spent (total and per-step)
- **Clean separation**: Build time vs deployment time
- **Rich console UX**: Visual progress for users
- **Clean logs**: Operational audit trail
- **Exit codes matter**: Proper codes for automation
- **Object-oriented architecture**: PipelineStep dataclass and Pipeline class for maintainability
- **Single responsibility**: Each class has focused purpose (PipelineStep = execution, Pipeline = orchestration)

### Code Style

The module follows GAZTank Python coding standards:
- **UTF-8 encoding** with BOM markers in Python files
- **Type hints** for function signatures (Path, Tuple, Optional, Callable, list[Type])
- **Dataclasses** with @dataclass decorator and field() for clean class definitions
- **Docstrings** for all public functions and classes
- **Clean logging** - no separators or blank lines in log files
- **Rich console** - emojis and formatting for user experience
- **Error handling** - try/except with proper logging
- **Exit codes** - 0 for success, 1 for failure
- **Object-oriented design** - Classes with single responsibility principle

## Best Practices

### When to Run gzbuild

1. **Complete site updates**
   - Changes across multiple content files
   - Configuration updates that affect entire site
   - Full rebuild and deployment needed

2. **Before production deployments**
   - Use `gzbuild -e prod --force` for clean builds
   - Ensures all steps execute freshly
   - Validates entire workflow before going live

3. **Development testing**
   - Use `gzbuild -e dev --dry-run` to test changes
   - Preview full pipeline without modifications
   - Verify configuration changes

4. **Environment resets**
   - Use `gzbuild -e dev --clean-all` to clear environment completely
   - Use `gzbuild -e dev --clean-orphaned` to remove only orphaned files
   - Both require confirmation prompts (add `--force` to skip)
   - Start fresh for troubleshooting

5. **Check for orphaned files**
   - Run normal pipeline: `gzbuild -e dev` (clean step identifies only)
   - Review console output for orphaned files
   - Use `--clean-orphaned` separately if cleanup needed

### Workflow Recommendations

```bash
# 1. Preview full build
scripts\gzbuild.cmd -e dev --dry-run

# 2. If satisfied, run for real (identifies orphaned files, doesn't delete)
scripts\gzbuild.cmd -e dev

# 3. If orphaned files found, clean them separately (requires confirmation)
scripts\gzbuild.cmd -e dev --clean-orphaned

# 4. Force complete rebuild if needed
scripts\gzbuild.cmd -e dev --force

# 5. Clean environment completely for fresh start (requires confirmation)
scripts\gzbuild.cmd -e dev --clean-all

# 6. Deploy to production with force
scripts\gzbuild.cmd -e prod --force
```

### Individual Module vs Full Pipeline

#### Use individual modules when:
- Working on specific content (generate only)
- Testing module changes (sitemap, toc)
- Iterating quickly on single aspect
- Example: `scripts\generate.cmd -e dev`

#### Use gzbuild when:
- Need complete build workflow
- Deploying to staging or production
- Want consistent, repeatable process
- Example: `scripts\gzbuild.cmd -e prod`

### Performance Tips

- **Leverage module timestamp checking**: Most modules skip up-to-date files automatically
- **Use --dry-run first**: Preview operations before committing
- **Force only when necessary**: Full rebuilds take longer
- **Monitor timing metrics**: Identify slow steps for optimization
- **Clean periodically**: Use --clean-all to remove cruft

### Troubleshooting Individual Steps

When pipeline fails at a specific step:

1. Note which step failed from console output
2. Check module-specific log file: `logs/{env}/{module}_YYYYMMDD.log`
3. Run that module individually for detailed debugging
4. Fix the issue
5. Re-run full pipeline

Example:
```bash
# Pipeline failed at step 4 (generate)
# Run generate individually with verbose output
scripts\generate.cmd -e dev

# Fix any issues, then re-run full pipeline
scripts\gzbuild.cmd -e dev
```

## Troubleshooting

### Missing -e Argument

**Problem:** `Error: -e ENVIRONMENT is required`

#### Solution:
- Add `-e` parameter with valid environment
- Valid environments: dev, staging, prod
- Example: `scripts\gzbuild.cmd -e dev`

### Invalid Environment

**Problem:** `Error: Invalid environment 'xyz'. Must be dev, staging, or prod`

#### Solution:
- Check spelling of environment name
- Only dev, staging, prod are valid
- Use lowercase (not Dev, STAGING, etc.)

### Step Failure

**Problem:** Pipeline stops at specific step: `Step X/8 failed: Module Name`

#### Diagnosis:
- Console shows which step failed
- Check gzbuild log for step error
- Check module-specific log for details

#### Solution:
1. Note failing step from console (e.g., "Step 4/8 failed: Content generation")
2. Check module log: `logs/{env}/generate_YYYYMMDD.log`
3. Run failing module individually: `scripts\generate.cmd -e dev`
4. Fix underlying issue
5. Re-run pipeline: `scripts\gzbuild.cmd -e dev`

### Module Doesn't Support Argument

**Problem:** `error: unrecognized arguments: --custom-arg`

**Cause:** Passed an argument that a module doesn't support

#### Solution:
- Check which step failed from console
- Review module's `--help` to see supported arguments
- Either add support to module or remove argument
- Example: Some modules may not support `--dry-run` yet

### Clean-All Mode Confusion

**Problem:** Pipeline exits immediately after clean step

**Cause:** Used `--clean-all` flag, which is intentional behavior

#### Solution:
- `--clean-all` is designed to clean and exit
- Remove `--clean-all` flag for normal pipeline execution
- Use `--clean-all` only when you want to reset environment

### Timing Shows 0m 0s

**Problem:** Timing metrics show unrealistic zero values

**Cause:** Pipeline failed before timing capture

#### Diagnosis:
- Check for error messages in console
- Review gzbuild log for failures
- Look for step failure messages

#### Solution:
- Fix the underlying pipeline failure
- Timing will show correctly on successful run

### Permission Denied

**Problem:** `PermissionError: [Errno 13] Permission denied`

#### Solution:
- Check permissions on logs, publish directories
- Close any programs using output files
- Ensure not running in read-only location
- Run with appropriate permissions (avoid admin unless necessary)

### Logs Not Found

**Problem:** Can't find log file for today

#### Solution:
- Logs are in: `logs/{environment}/gzbuild_YYYYMMDD.log`
- Check you're looking in correct environment folder
- Verify date format: YYYYMMDD (e.g., 20251024)
- Log only created when pipeline runs

### Emojis Not Displaying

**Problem:** Console shows squares or question marks instead of emojis

#### Solution:
- Launcher scripts set `PYTHONIOENCODING=utf-8` automatically
- Ensure terminal supports UTF-8 encoding
- On Windows: Use Windows Terminal or PowerShell 7+
- Check terminal font supports emoji glyphs
- Note: Log files never contain emojis (by design)

## Future Enhancements

### Completed Features

- ✅ **Timing metrics**: Separate tracking for build, deployment, and total time (v1.0)
- ✅ **Simplified argument handling**: Pass-through model eliminates explicit argument definitions (v1.0)
- ✅ **Clean-all mode**: Dedicated environment cleanup without running pipeline (v1.0)
- ✅ **Rich console output**: Emojis and progress indicators for better UX (v1.0)
- ✅ **Clean logging**: Operational logs without formatting or blank lines (v1.0)
- ✅ **PipelineStep dataclass**: Clean configuration with @dataclass decorator and field() (v1.0)
- ✅ **Per-step timing**: Individual step execution times displayed in summary (v1.0)
- ✅ **Aligned timing display**: Column-aligned output for easy reading (v1.0)
- ✅ **Pipeline class**: Automatic step management with add(), execute_all(), print_summary() (v1.0)
- ✅ **Automatic tracking**: max_desc_len updated incrementally during Pipeline.add() (v1.0)

### Planned Features

- **Selective module execution**: Run specific steps only (e.g., `--steps=1,3,5` or `--skip=8`)
- **Parallel execution**: Run independent steps concurrently where possible
- **Resume capability**: Continue from failed step without restarting
- **Configuration validation**: Pre-flight checks before running pipeline
- **Rollback support**: Revert to previous deployment on failure
- **Pipeline profiles**: Named configurations for common workflows (e.g., `--profile=quick-test`)
- **Module timing breakdown**: Show timing for each individual step
- **Summary statistics**: File counts, size totals across all steps
- **Summary statistics**: File counts, size totals across all steps
- **Verbose mode**: `--verbose` flag for detailed operation logging
- **Quiet mode**: `--quiet` flag for minimal console output

### Integration Enhancements

- **Pre/post hooks**: Run custom scripts before/after pipeline or steps
- **Notification system**: Email/Slack notifications on completion/failure
- **Metric export**: Export timing and statistics to monitoring systems
- **Configuration hot-reload**: Detect config changes without restart
- **Module discovery**: Automatically detect and integrate new modules

### Performance Improvements

- **Caching layer**: Cache module results to skip unnecessary work
- **Dependency graph**: Only run modules affected by changes
- **Incremental builds**: Smart detection of what needs rebuilding
- **Progress streaming**: Real-time progress updates for long operations

## Related Documentation

### Internal Documentation
- **[Clean Module](../clean/README.md)** - Orphaned file cleanup (step 1)
- **[Setup Module](../setup/README.md)** - Site configuration (step 2)
- **[GZLint Module](../gzlint/README.md)** - HTML/JS validation (step 3)
- **[Generate Module](../generate/README.md)** - Content generation (step 4)
- **[Sitemap Module](../sitemap/README.md)** - Sitemap generation (step 5)
- **[TOC Module](../toc/README.md)** - Table of contents (step 6)
- **[Package Module](../package/README.md)** - Site packaging (step 7)
- **[Deploy Module](../deploy/README.md)** - FTP/FTPS deployment (step 8)
- **[GZLogging](../gzlogging/README.md)** - Logging infrastructure
- **[GZConfig](../gzconfig/README.md)** - Configuration library
- **[Module README Structure](../../dev/MODULE_README_STRUCTURE.md)** - README template
- **[Pipeline Flow](../FLOW_PIPELINE.md)** - Overall pipeline documentation

### External Resources
- **Python sys.argv**: https://docs.python.org/3/library/sys.html#sys.argv - Command-line argument handling
- **Python SystemExit**: https://docs.python.org/3/library/exceptions.html#SystemExit - Exit code handling
- **Python time module**: https://docs.python.org/3/library/time.html - Timing functions

## License

GPL-3.0-or-later

## Authors

superguru, gazorper

---

### Changelog:
- **v1.1** (November 4, 2025): Updated to 10-step pipeline (added compose, normalise); clean step now identifies only (no deletion by default); added --clean-orphaned mode
- **v1.0** (October 24, 2025): Initial 8-step pipeline with timing metrics, per-step timing display, PipelineStep/Pipeline classes

---

*Last updated: November 4, 2025*  
*gzbuild module version: 1.1*
