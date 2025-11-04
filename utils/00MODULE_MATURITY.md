# Module Maturity Tracker for Python modules

- Checklists for conformity and adequate maturity of the Python modules in the project.
- Expected file path, relative to the project root: `.\utils\00MODULE_MATURITY.md`

## Status Indicators

Done: ✅
WIP : 👉

## Special prompts to maintain this tracking document

### File Organisation
Analyse this file. It has checklist sections for every Python module in .\utils. 
Organise the sections so they are all in the same order as the `sitemap` module. 
Add any missing checklist conditions, and keep but report on any extra ones that is not already in the sitemap checklist. 
Do not add or remove any checkmarks, and do not verify the current state of any of the checklist conditions.
Ensure the different sections are ordered alphabetically in relation to each other, ignoring prefix status characters like those listed in the ## Status Indicators section listed above.
Do not sort the checklist conditions themselves as their order is important to preserve.
Update the TOC to reflect the module sections ordering, including only ## headings below the current TOC.

### Add a new module to track
Add a new module with a ## heading, and mark it as WIP as per ## Status Indicators.
Update the TOC as per the rules in ### File Organisation.

### Update the TOC
Update the TOC by including any ## Status Indicators and heading levels ## and ### in the information below the TOC. 
Adhere to the sort order as described in ### File Organisation.
Of all of the checklist conditions have been ticked off, then mark the module as Done.

# Table of Contents

- [Foundation](#foundation)
  - [✅ gzconfig](#gzconfig)
  - [✅ gzlogging](#gzlogging)
- [Tools](#tools)
  - [✅ gzhost](#gzhost)
  - [✅ gzserve](#gzserve)
- [Pipeline](#pipeline)
  - [✅ clean](#clean)
  - [✅ compose](#compose)
  - [✅ deploy](#deploy)
  - [✅ generate](#generate)
  - [✅ gzbuild](#gzbuild)
  - [✅ gzlint](#gzlint)
  - [✅ normalise](#normalise)
  - [✅ package](#package)
  - [✅ setup](#setup)
  - [✅ sitemap](#sitemap)
  - [✅ toc](#toc)

---

## Foundation

### ✅gzconfig
[x] Is a proper module that can run with python -m <modulename>
[x] Has -e <env> command line param, or has a specific design decision to default to dev environment
[x] Has --help command line param
[x] Uses gzconfig for all config operations
[x] Uses gzlogging
[x] Uses an appropriate .\config\*.toml file
[x] Has shell invocation scripts for cmd and sh
[x] Has --force command line param, or a specific design choice not to have it
[x] Has --dry-run command line param, or a specific design choice not to have it
[x] Consistenly and correctly log appropriate items to log and to console
[x] Is verified to be UTF-8 compliant
[x] Is generic in design so it can be easily extended in future
[x] Has updated README.md that conforms to .\dev\MODULE_README_STRUCTURE.md

**Design Decision Notes:**
- **Library Module**: gzconfig is a library module (like gzlogging), not a command-line tool. It doesn't have command-line parameters or shell scripts because it's designed to be imported by other modules.
- **Configuration abstraction**: Provides clean API to access configuration files without exposing implementation details (file paths, TOML format, etc.)
- **No command-line interface**: Intentionally has no -e, --help, --force, --dry-run parameters - it's a Python library, not a CLI tool
- **No shell scripts**: Shell invocation not applicable - used via `from gzconfig import get_pipeline_config`
- **No gzlogging**: As a low-level library, it doesn't use gzlogging to avoid circular dependencies and complexity
- **Example file**: Includes example.py to demonstrate usage patterns (similar to gzlogging's approach)

### ✅gzlogging
[x] Is a proper module that can run with python -m <modulename>
[x] Has -e <env> command line param, or has a specific design decision to default to dev environment
[x] Has --help command line param
[x] Uses gzconfig for all config operations
[x] Uses gzlogging
[x] Uses an appropriate .\config\*.toml file
[x] Has shell invocation scripts for cmd and sh
[x] Has --force command line param, or a specific design choice not to have it
[x] Has --dry-run command line param, or a specific design choice not to have it
[x] Consistenly and correctly log appropriate items to log and to console
[x] Is verified to be UTF-8 compliant
[x] Is generic in design so it can be easily extended in future
[x] Has updated README.md that conforms to .\dev\MODULE_README_STRUCTURE.md

**Design Decision Notes:**
- **gzconfig Integration**: Uses gzconfig.tools module for accessing tools.toml configuration
- **Configuration abstraction**: ToolsEnvironment provides clean property-based access (log_directory_path, get_tool_rotation_settings)
- **Removed deprecated code**: Eliminated ~120 lines of direct TOML-handling code (_load_config, _load_rotation_config, manual dict access)
- **Library module**: Like gzconfig, it's a library module - doesn't use gzlogging itself to avoid circular dependency
- **Automatic rotation**: Tool-specific rotation settings accessed via ToolsEnvironment.get_tool_rotation_settings(tool_name)

## Tools

### ✅gzhost
[x] Is a proper module that can run with python -m <modulename>
[x] Has -e <env> command line param, or has a specific design decision to default to dev environment
[x] Has --help command line param
[x] Uses gzconfig for all config operations
[x] Uses gzlogging
[x] Uses an appropriate .\config\*.toml file
[x] Has shell invocation scripts for cmd and sh
[x] Has --force command line param, or a specific design choice not to have it
[x] Has --dry-run command line param, or a specific design choice not to have it
[x] Consistenly and correctly log appropriate items to log and to console
[x] Is verified to be UTF-8 compliant
[x] Is generic in design so it can be easily extended in future
[x] Has updated README.md that conforms to .\dev\MODULE_README_STRUCTURE.md

**Design Decision Notes:**
- **FTP simulation server**: Uses pyftpdlib to simulate remote FTP deployment hosts for local testing
- **Environment-specific authentication**: Each environment has its own FTP credentials from ftp_users.toml
- **Integration with deploy module**: Provides local target for testing FTP deployment workflows
- **Security by design**: Plain text passwords acceptable as this is local development only
- **Permission management**: Configurable FTP permissions per environment via pyftpdlib permission strings
- **No --force or --dry-run**: Server operation doesn't require these flags - not applicable to FTP server

### ✅gzserve
[x] Is a proper module that can run with python -m <modulename>
[x] Has -e <env> command line param, or has a specific design decision to default to dev environment
[x] Has --help command line param
[x] Uses gzconfig for all config operations
[x] Uses gzlogging
[x] Uses an appropriate .\config\*.toml file
[x] Has shell invocation scripts for cmd and sh
[x] Has --force command line param, or a specific design choice not to have it
[x] Has --dry-run command line param, or a specific design choice not to have it
[x] Consistenly and correctly log appropriate items to log and to console
[x] Is verified to be UTF-8 compliant
[x] Is generic in design so it can be easily extended in future
[x] Has updated README.md that conforms to .\dev\MODULE_README_STRUCTURE.md

## Pipeline

### ✅clean
[x] Is a proper module that can run with python -m <modulename>
[x] Has -e <env> command line param, or has a specific design decision to default to dev environment
[x] Has --help command line param
[x] Uses gzconfig for all config operations
[x] Uses gzlogging
[x] Uses an appropriate .\config\*.toml file
[x] Has shell invocation scripts for cmd and sh
[x] Has --force command line param, or a specific design choice not to have it
[x] Has --dry-run command line param, or a specific design choice not to have it
[x] Consistenly and correctly log appropriate items to log and to console
[x] Is verified to be UTF-8 compliant
[x] Is generic in design so it can be easily extended in future
[x] Has updated README.md that conforms to .\dev\MODULE_README_STRUCTURE.md

**Design Decision Notes:**
- **Extracted from package module**: Orphaned file cleanup logic moved to dedicated clean module (October 23, 2025)
- **Pipeline integration**: Runs before package module to ensure environment is clean before syncing/archiving
- **Environment-aware**: Uses gzconfig.pipeline to get environment directory from environments.toml
- **Orphaned file detection**: Compares publish/{env}/ against src/ - src/ is source of truth
- **Separation of concerns**: Clean module handles orphaned files, package module handles sync/minify/archive

### ✅compose
[x] Is a proper module that can run with python -m <modulename>
[x] Has -e <env> command line param, or has a specific design decision to default to dev environment
[x] Has --help command line param
[x] Uses gzconfig for all config operations
[x] Uses gzlogging
[x] Uses an appropriate .\config\*.toml file
[x] Has shell invocation scripts for cmd and sh
[x] Has --force command line param, or a specific design choice not to have it
[x] Has --dry-run command line param, or a specific design choice not to have it
[x] Consistenly and correctly log appropriate items to log and to console
[x] Is verified to be UTF-8 compliant
[x] Is generic in design so it can be easily extended in future
[x] Has updated README.md that conforms to .\dev\MODULE_README_STRUCTURE.md

**Design Decision Notes:**
- **Pipeline Step 0**: Runs before all other pipeline steps to assemble HTML from components ✅ Integrated
- **Configuration files**: Uses compose.toml (composition definitions) and site.toml (feature flags)
- **gzconfig integration**: Uses get_compose_config() and get_site_config() for configuration access
- **Component transformation**: Transforms markdown to navigation HTML, supports future transform types
- **Composition markers**: Processes <!-- COMPOSE:KEY:config_flag --> in base HTML files
- **No --dry-run**: Composition is safe and creates output files - dry-run not applicable

### ✅deploy
[x] Is a proper module that can run with python -m <modulename>
[x] Has -e <env> command line param, or has a specific design decision to default to dev environment
[x] Has --help command line param
[x] Uses gzconfig for all config operations
[x] Uses gzlogging
[x] Uses an appropriate .\config\*.toml file
[x] Has shell invocation scripts for cmd and sh
[x] Has --force command line param, or a specific design choice not to have it
[x] Has --dry-run command line param, or a specific design choice not to have it
[x] Consistenly and correctly log appropriate items to log and to console
[x] Is verified to be UTF-8 compliant
[x] Is generic in design so it can be easily extended in future
[x] Has updated README.md that conforms to .\dev\MODULE_README_STRUCTURE.md

**Design Decision Notes:**
- **FTP/FTPS deployment**: Uploads packaged websites to remote FTP/FTPS servers
- **gzconfig integration**: Uses get_deploy_config() for deploy.toml and get_pipeline_config() for environment info
- **Timestamped subdirectories**: Creates unique upload directories with format .YYYYMMDD_HHMMSS_DDD_xxxxx
- **Secure by default**: FTPS (FTP over TLS) enabled by default for encrypted uploads
- **Interactive confirmation**: Prompts before upload unless --force specified
- **Package discovery**: Automatically finds latest package_{env}_*.zip for specified environment

### ✅generate
[x] Is a proper module that can run with python -m <modulename>
[x] Has -e <env> command line param, or has a specific design decision to default to dev environment
[x] Has --help command line param
[x] Uses gzconfig for all config operations
[x] Uses gzlogging
[x] Uses an appropriate .\config\*.toml file
[x] Has shell invocation scripts for cmd and sh
[x] Has --force command line param, or a specific design choice not to have it
[x] Has --dry-run command line param, or a specific design choice not to have it
[x] Consistenly and correctly log appropriate items to log and to console
[x] Is verified to be UTF-8 compliant
[x] Is generic in design so it can be easily extended in future
[x] Has updated README.md that conforms to .\dev\MODULE_README_STRUCTURE.md

**Design Decision Notes:**
- **Environment-aware output (v2.0)**: Now requires mandatory -e parameter, outputs to publish/{env}/content/ instead of src/content/ (October 23, 2025)
- **gzconfig Integration**: Uses gzconfig.generate module for generate.toml AND gzconfig.pipeline for environment directories
- **Configuration abstraction**: GenerateGroup and GenerateConfig classes provide clean property-based access
- **Output path resolution**: GenerateGroup.output_path dynamically resolves based on environment parameter using pipeline config

### ✅gzbuild
[x] Is a proper module that can run with python -m <modulename>
[x] Has -e <env> command line param, or has a specific design decision to default to dev environment
[x] Has --help command line param
[x] Uses gzconfig for all config operations
[x] Uses gzlogging
[x] Uses an appropriate .\config\*.toml file
[x] Has shell invocation scripts for cmd and sh
[x] Has --force command line param, or a specific design choice not to have it
[x] Has --dry-run command line param, or a specific design choice not to have it
[x] Consistenly and correctly log appropriate items to log and to console
[x] Is verified to be UTF-8 compliant
[x] Is generic in design so it can be easily extended in future
[x] Has updated README.md that conforms to .\dev\MODULE_README_STRUCTURE.md

**Design Decision Notes:**
- **Pipeline orchestrator**: Coordinates execution of all 8 pipeline modules in sequence (October 24, 2025)
- **Simplified argument handling**: Only validates -e and -h, passes all other arguments through to pipeline modules
- **No config file**: Doesn't use its own config file - relies on modules to use their respective configs
- **Timing metrics**: Tracks build time (steps 1-7), deployment time (step 8), and total time separately
- **Stop-on-error**: Halts pipeline if any step fails, preventing invalid deployments
- **Clean-all mode**: Special handling for --clean-all that runs clean and exits without pipeline
- **Setup force mode**: Always passes --force to setup module (step 2) for consistent configuration

### ✅gzlint
[x] Is a proper module that can run with python -m <modulename>
[x] Has -e <env> command line param, or has a specific design decision to default to dev environment
[x] Has --help command line param
[x] Uses gzconfig for all config operations
[x] Uses gzlogging
[x] Uses an appropriate .\config\*.toml file
[x] Has shell invocation scripts for cmd and sh
[x] Has --force command line param, or a specific design choice not to have it
[x] Has --dry-run command line param, or a specific design choice not to have it
[x] Consistenly and correctly log appropriate items to log and to console
[x] Is verified to be UTF-8 compliant
[x] Is generic in design so it can be easily extended in future
[x] Has updated README.md that conforms to .\dev\MODULE_README_STRUCTURE.md

### ✅normalise
[x] Is a proper module that can run with python -m <modulename>
[x] Has -e <env> command line param, or has a specific design decision to default to dev environment
[x] Has --help command line param
[x] Uses gzconfig for all config operations
[x] Uses gzlogging
[x] Uses an appropriate .\config\*.toml file
[x] Has shell invocation scripts for cmd and sh
[x] Has --force command line param, or a specific design choice not to have it
[x] Has --dry-run command line param, or a specific design choice not to have it
[x] Consistenly and correctly log appropriate items to log and to console
[x] Is verified to be UTF-8 compliant
[x] Is generic in design so it can be easily extended in future
[x] Has updated README.md that conforms to .\dev\MODULE_README_STRUCTURE.md

### ✅package
[x] Is a proper module that can run with python -m <modulename>
[x] Has -e <env> command line param, or has a specific design decision to default to dev environment
[x] Has --help command line param
[x] Uses gzconfig for all config operations
[x] Uses gzlogging
[x] Uses an appropriate .\config\*.toml file
[x] Has shell invocation scripts for cmd and sh
[x] Has --force command line param, or a specific design choice not to have it
[x] Has --dry-run command line param, or a specific design choice not to have it
[x] Consistenly and correctly log appropriate items to log and to console
[x] Is verified to be UTF-8 compliant
[x] Is generic in design so it can be easily extended in future
[x] Has updated README.md that conforms to .\dev\MODULE_README_STRUCTURE.md

### ✅setup
[x] Is a proper module that can run with python -m <modulename>
[x] Has -e <env> command line param, or has a specific design decision to default to dev environment
[x] Has --help command line param
[x] Uses gzconfig for all config operations
[x] Uses gzlogging
[x] Uses an appropriate .\config\*.toml file
[x] Has shell invocation scripts for cmd and sh
[x] Has --force command line param, or a specific design choice not to have it
[x] Has --dry-run command line param, or a specific design choice not to have it
[x] Consistenly and correctly log appropriate items to log and to console
[x] Is verified to be UTF-8 compliant
[x] Is generic in design so it can be easily extended in future
[x] Has updated README.md that conforms to .\dev\MODULE_README_STRUCTURE.md

### ✅sitemap
[x] Is a proper module that can run with python -m <modulename>
[x] Has -e <env> command line param, or has a specific design decision to default to dev environment
[x] Has --help command line param
[x] Uses gzconfig for all config operations
[x] Uses gzlogging
[x] Uses an appropriate .\config\*.toml file
[x] Has shell invocation scripts for cmd and sh
[x] Has --force command line param, or a specific design choice not to have it
[x] Has --dry-run command line param, or a specific design choice not to have it
[x] Consistenly and correctly log appropriate items to log and to console
[x] Is verified to be UTF-8 compliant
[x] Is generic in design so it can be easily extended in future
[x] Has updated README.md that conforms to .\dev\MODULE_README_STRUCTURE.md

### ✅toc
[x] Is a proper module that can run with python -m <modulename>
[x] Has -e <env> command line param, or has a specific design decision to default to dev environment
[x] Has --help command line param
[x] Uses gzconfig for all config operations
[x] Uses gzlogging
[x] Uses an appropriate .\config\*.toml file
[x] Has shell invocation scripts for cmd and sh
[x] Has --force command line param, or a specific design choice not to have it
[x] Has --dry-run command line param, or a specific design choice not to have it
[x] Consistenly and correctly log appropriate items to log and to console
[x] Is verified to be UTF-8 compliant
[x] Is generic in design so it can be easily extended in future
[x] Has updated README.md that conforms to .\dev\MODULE_README_STRUCTURE.md
