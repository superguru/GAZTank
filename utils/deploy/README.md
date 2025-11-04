# Deploy Module

Automated deployment of packaged websites to FTP/FTPS servers with timestamped subdirectories and progress tracking.

**Version:** 1.0  
**Last Updated:** October 23, 2025

## Table of Contents

- [Purpose](#purpose)
- [Build Pipeline](#build-pipeline)
- [Logging](#logging)
- [Usage](#usage)
  - [Command Line](#command-line)
  - [Direct Module Execution](#direct-module-execution)
- [Command Line Arguments](#command-line-arguments)
- [Module Structure](#module-structure)
- [Features](#features)
- [Configuration](#configuration)
  - [Deploy Configuration File](#deploy-configuration-file)
  - [Configuration Options](#configuration-options)
  - [Subdirectory Format](#subdirectory-format)
  - [FTP vs FTPS](#ftp-vs-ftps)
- [Invocation Points](#invocation-points)
- [Development](#development)
  - [Key Functions](#key-functions)
  - [Integration](#integration)
- [Security](#security)
  - [Credentials Protection](#credentials-protection)
  - [Recommended Practices](#recommended-practices)
  - [CI/CD Integration](#cicd-integration)
- [Troubleshooting](#troubleshooting)
- [Best Practices](#best-practices)
- [Performance](#performance)
- [Future Enhancements](#future-enhancements)
- [Related Documentation](#related-documentation)
- [License](#license)

## Purpose

The Deploy module handles automated deployment of packaged websites to remote FTP/FTPS servers. It provides a complete deployment workflow with:

- **Configuration Management** - Reads FTP credentials and settings from `config/deploy.toml` via `gzconfig`
- **Package Discovery** - Automatically finds the latest package for the specified environment
- **Timestamped Subdirectories** - Creates unique upload directories with timestamps and random postfixes
- **Secure Uploads** - Supports both FTP and FTPS (FTP over TLS) protocols
- **Progress Tracking** - Real-time upload progress display
- **Error Handling** - Comprehensive network and FTP error management
- **Deployment Control** - Requires `--deploy` or `--force` flag to enable deployment (prevents accidental uploads)
- **Dry-Run Mode** - Preview deployment without actually uploading

### Environment-Aware Deployment

The deploy module requires a mandatory `-e` argument to specify which environment's package to deploy:
- **dev** - Deploys `publish/packages/package_dev_*.zip`
- **staging** - Deploys `publish/packages/package_staging_*.zip`
- **prod** - Deploys `publish/packages/package_prod_*.zip`

## Build Pipeline

The deploy module is the final step in the GAZTank content delivery pipeline:

```
Deployment Pipeline:
  1. Package module creates package_{env}_{timestamp}.zip in publish/packages/
  2. Deploy module:
     a. Receives environment parameter (-e dev/staging/prod)
     b. Checks for --deploy or --force flag (required to enable deployment)
     c. Reads deploy.toml configuration via gzconfig
     d. Finds latest package for specified environment
     e. Displays package details and FTP settings
     f. Connects to FTP/FTPS server
     g. Changes to target directory
     h. Creates timestamped subdirectory (.YYYYMMDD_HHMMSS_DDD_xxxxx)
     i. Uploads package file
     j. Verifies and reports completion
  3. Package is live on remote server
```

**Purpose:** Automated deployment to FTP/FTPS servers with organization and safety features

**Location:** Called via `scripts/deploy.cmd -e <env>` or `scripts/deploy.sh -e <env>`

### Workflow:
```
-e environment → deploy.toml → find latest package → confirm → FTP upload → remote server
```

### Benefits:
- Environment-specific package selection
- Timestamped subdirectories prevent file overwrites
- Secure FTPS support with TLS encryption
- User confirmation prevents accidental deployments
- Dry-run mode for testing
- Comprehensive logging of all operations

## Logging

The deploy module uses the **gzlogging** infrastructure for environment-aware operational logging.

### Log Configuration

- **Environment:** Specified via `-e` argument (dev/staging/prod)
- **Tool Name:** `deploy`
- **Log Files:** `logs/{environment}/deploy_{YYYYMMDD}.log`

### What Gets Logged

**Log File** (`log.inf()`, `log.wrn()`, `log.err()`):
- Deploy started with environment
- Configuration loaded
- Package found with filename
- FTP connection details
- Directory operations
- Upload progress and completion
- Errors and warnings
- Deployment completion status

**Console Output** (`print()`):
- Deployment headers with emojis
- Package details (📦)
- Upload directory (📁)
- FTP server details (🌐 👤 🔒)
- Confirmation prompts
- Upload status (🚀)
- Success/error messages (✅ ❌)

### Log Examples

#### Successful Deployment:
```
[2025-10-23 23:23:26] [dev] [INF] Deploy starting for environment: dev
[2025-10-23 23:23:26] [dev] [INF] Looking for latest package for dev
[2025-10-23 23:23:26] [dev] [INF] Found package: package_dev_20251023_203933.zip
[2025-10-23 23:23:26] [dev] [INF] Upload subdirectory: .20251023_232326_296_lghex
[2025-10-23 23:23:26] [dev] [INF] Connecting to FTP server localhost:2179
[2025-10-23 23:23:26] [dev] [INF] Logging in as devup
[2025-10-23 23:23:26] [dev] [INF] Connected to FTP server
[2025-10-23 23:23:26] [dev] [INF] Changing to directory: /
[2025-10-23 23:23:26] [dev] [INF] Creating subdirectory: .20251023_232326_296_lghex
[2025-10-23 23:23:26] [dev] [INF] Created directory: .20251023_232326_296_lghex
[2025-10-23 23:23:26] [dev] [INF] Changed to directory: .20251023_232326_296_lghex
[2025-10-23 23:23:26] [dev] [INF] Uploading package_dev_20251023_203933.zip (2.45 MB)
[2025-10-23 23:23:28] [dev] [INF] Upload complete: package_dev_20251023_203933.zip
[2025-10-23 23:23:28] [dev] [INF] Updated deployment history: package_dev_20251023_203933.deploy_history.txt
[2025-10-23 23:23:28] [dev] [INF] Deployment complete: package_dev_20251023_203933.zip → //.20251023_232326_296_lghex
[2025-10-23 23:23:28] [dev] [INF] Closed FTP connection
```

#### Dry-Run Mode:
```
[2025-10-23 23:23:26] [dev] [INF] Deploy starting for environment: dev
[2025-10-23 23:23:26] [dev] [INF] Looking for latest package for dev
[2025-10-23 23:23:26] [dev] [INF] Found package: package_dev_20251023_203933.zip
[2025-10-23 23:23:26] [dev] [INF] Upload subdirectory: .20251023_232326_296_lghex
[2025-10-23 23:23:26] [dev] [INF] [DRY RUN] Would deploy package
```

#### User Cancellation:
```
[2025-10-23 23:25:00] [dev] [INF] Deploy starting for environment: dev
[2025-10-23 23:25:00] [dev] [INF] Looking for latest package for dev
[2025-10-23 23:25:00] [dev] [INF] Found package: package_dev_20251023_203933.zip
[2025-10-23 23:25:02] [dev] [INF] Deployment cancelled by user
```

## Usage

### Command Line

#### Windows:
```bash
# Deploy dev environment
.\scripts\deploy.cmd -e dev --deploy

# Dry-run mode (no actual upload)
.\scripts\deploy.cmd -e dev --dry-run

# Force mode (automatic deployment)
.\scripts\deploy.cmd -e dev --force

# Dry-run with force
.\scripts\deploy.cmd -e dev --dry-run --force
```

#### Linux/Mac:
```bash
# Deploy staging environment
./scripts/deploy.sh -e staging --deploy

# Dry-run mode
./scripts/deploy.sh -e staging --dry-run

# Force mode
./scripts/deploy.sh -e staging --force
```

### Direct Module Execution

```bash
# From project root (with deploy flag)
python -m utils.deploy -e prod --deploy

# With help
python -m utils.deploy --help

# Dry-run
python -m utils.deploy -e dev --dry-run

# Without --deploy or --force (will skip deployment)
python -m utils.deploy -e prod
```

## Command Line Arguments

### Required Arguments

- **`-e, --environment`** (required)
  - Target environment: `dev`, `staging`, or `prod`
  - Determines which package to deploy
  - Example: `-e dev`

### Optional Arguments

- **`--dry-run`**
  - Preview deployment without uploading
  - Shows what would be deployed
  - Useful for testing configuration
  - Example: `--dry-run`

- **`--deploy`**
  - Enable deployment (required unless `--force` is used)
  - Safety flag to prevent accidental deployments
  - Example: `--deploy`

- **`--force`**
  - Enable deployment and bypass all checks
  - Useful for automated deployments
  - Use with caution
  - Example: `--force`

- **`--help`**
  - Show help message and exit
  - Lists all available arguments

### Examples

```bash
# Deploy with explicit flag
python -m utils.deploy -e dev --deploy

# Automated deployment (force mode)
python -m utils.deploy -e prod --force

# Test deployment configuration
python -m utils.deploy -e staging --dry-run

# Without --deploy or --force (deployment will be skipped)
python -m utils.deploy -e dev

# Help
python -m utils.deploy --help
```

## Module Structure

```
deploy/
├── __init__.py      # Public API exports (main)
├── __main__.py      # Entry point for python -m utils.deploy
├── deployer.py      # Core deployment logic
└── README.md        # This file
```

### Module Components

- **`__init__.py`** - Exports `main()` function
- **`__main__.py`** - Enables `python -m utils.deploy` execution
- **`deployer.py`** - Contains all deployment logic:
  - Configuration loading via `gzconfig`
  - Package discovery
  - FTP/FTPS connection management
  - File upload with error handling
  - Logging and user interaction

## Features

✅ **Environment-Aware** - Deploys correct package for specified environment  
✅ **Configuration Management** - Uses `gzconfig` to read `deploy.toml`  
✅ **Automatic Package Discovery** - Finds latest package by timestamp  
✅ **Timestamped Subdirectories** - Prevents overwrites with unique upload dirs  
✅ **Deployment History Tracking** - Maintains deployment log per package  
✅ **FTPS Support** - Secure FTP over TLS encryption  
✅ **Progress Tracking** - Real-time upload progress  
✅ **Interactive Prompts** - Confirms deployment before upload  
✅ **Dry-Run Mode** - Test without uploading  
✅ **Force Mode** - Skip prompts for automation  
✅ **Error Handling** - Network, FTP, and file system errors  
✅ **Comprehensive Logging** - All operations logged via `gzlogging`  
✅ **Exit Codes** - Proper exit codes for automation  
✅ **UTF-8 Support** - Emoji output in console  
✅ **Type Safety** - Full type hints with Pylance compliance  

## Deployment History Tracking

The deploy module automatically maintains a deployment history file for each package, creating an audit trail of all deployments.

### History File Location

For each package file, a corresponding history file is created in the same directory:

```
publish/packages/
├── package_dev_20251023_203933.zip
├── package_dev_20251023_203933.deploy_history.txt    ← History file
├── package_staging_20251023_204512.zip
└── package_staging_20251023_204512.deploy_history.txt
```

### History File Format

**Filename:** `<package_name_without_.zip>.deploy_history.txt`

#### Entry Format:
```
Deployed <package_name>.zip to "<environment>" at <timestamp> to dir <remote_path>
```

#### Example Content:
```
Deployed package_dev_20251023_203933.zip to "dev" at 2025-10-24 00:15:32 to dir /.20251024_001530_297_a3f9k
Deployed package_dev_20251023_203933.zip to "dev" at 2025-10-24 01:22:45 to dir /.20251024_012245_297_x7b2m
Deployed package_dev_20251023_203933.zip to "staging" at 2025-10-24 02:30:18 to dir /.20251024_023018_298_p5n8t
```

### Features

- **Automatic Creation** - History file created on first deployment
- **Append Mode** - New deployments append to existing file
- **One Line Per Deployment** - Simple, parseable format
- **Human Readable** - Clear timestamps and environment names
- **Non-Fatal** - Deployment continues even if history file can't be written
- **UTF-8 Encoding** - Full Unicode support
- **Audit Trail** - Track when and where packages were deployed

### Use Cases

1. **Audit & Compliance** - Track all package deployments for security audits
2. **Troubleshooting** - Identify when and where a specific package was deployed
3. **Rollback Planning** - Know which subdirectory contains each deployment
4. **Deployment Verification** - Confirm package was deployed to correct environment
5. **Timeline Analysis** - Understand deployment frequency and patterns

### Example Usage

After deploying a package multiple times:

```bash
# Deploy to dev
python -m utils.deploy -e dev --deploy

# Deploy to staging
python -m utils.deploy -e staging --deploy

# View deployment history
cat publish/packages/package_dev_20251023_203933.deploy_history.txt
```

#### Output:
```
Deployed package_dev_20251023_203933.zip to "dev" at 2025-10-24 00:15:32 to dir /.20251024_001530_297_a3f9k
Deployed package_dev_20251023_203933.zip to "staging" at 2025-10-24 01:22:45 to dir /.20251024_012245_297_x7b2m
```

### Parsing History Files

The simple format makes it easy to parse programmatically:

```python
from pathlib import Path
import re

history_file = Path('publish/packages/package_dev_20251023_203933.deploy_history.txt')

# Read all deployments
with open(history_file, 'r', encoding='utf-8') as f:
    for line in f:
        # Parse deployment entry
        match = re.match(r'Deployed (.+) to "(.+)" at (.+) to dir (.+)', line)
        if match:
            package, env, timestamp, remote_dir = match.groups()
            print(f"{timestamp}: {package} → {env} ({remote_dir})")
```

**Note:** History files are stored alongside packages in `publish/packages/` and are not automatically cleaned up. Manage these files as part of your package retention policy.

## Configuration

### Deploy Configuration File

**Location:** `config/deploy.toml`

**Note:** This file contains sensitive credentials and is in `.gitignore`.

#### Setup:
1. Copy `config/deploy.example.toml` to `config/deploy.toml`
2. Fill in your FTP server details
3. Never commit this file to version control

#### Example:
```toml
[ftp]
server = "ftp.yourserver.com"
username = "your-username"
password = "your-password"
target_dir = "/public_html"

# Optional settings (with defaults shown)
port = 21
use_ftps = true
upload_subdir_fmt = "%Y%m%d_%H%M%S_%j"
upload_subdir_postfix_len = 5
```

### Configuration Options

| Option | Type | Default | Required | Description |
|--------|------|---------|----------|-------------|
| `server` | string | - | ✅ | FTP/FTPS server hostname or IP |
| `username` | string | - | ✅ | FTP username |
| `password` | string | - | ✅ | FTP password |
| `target_dir` | string | - | ✅ | Remote directory path |
| `port` | integer | `21` | ❌ | FTP server port |
| `use_ftps` | boolean | `true` | ❌ | Use FTPS (encrypted) |
| `upload_subdir_fmt` | string | `"%Y%m%d_%H%M%S_%j"` | ❌ | Subdirectory timestamp format |
| `upload_subdir_postfix_len` | integer | `5` | ❌ | Random postfix length (1-10) |

### Subdirectory Format

The `upload_subdir_fmt` uses Python's `strftime` format codes:

| Code | Meaning | Example |
|------|---------|---------|
| `%Y` | Year (4 digits) | `2025` |
| `%m` | Month (01-12) | `10` |
| `%d` | Day of month (01-31) | `23` |
| `%H` | Hour (00-23) | `21` |
| `%M` | Minute (00-59) | `45` |
| `%S` | Second (00-59) | `30` |
| `%j` | Day of year (001-366) | `296` |

#### Example subdirectory names:
- Format: `%Y%m%d_%H%M%S_%j` → `.20251023_214530_296_a7k2q`
- Format: `%Y-%m-%d` → `.2025-10-23_x9m3p`
- Format: `deploy_%Y%m%d` → `.deploy_20251023_b4t8w`
- Empty string `""` → No subdirectory (upload directly to `target_dir`)

**Note:** All subdirectories are prefixed with `.` (dot) and include a random alphanumeric postfix to prevent collisions.

### FTP vs FTPS

#### FTPS (Recommended - Default)

```toml
[ftp]
use_ftps = true  # or omit (defaults to true)
```

##### Advantages:
- ✅ Encrypted connection (TLS/SSL)
- ✅ Credentials protected
- ✅ Data transfer encrypted
- ✅ Industry standard security

##### Requirements:
- Server must support FTPS (FTP over TLS)
- Usually uses same port as FTP (21)

#### FTP (Legacy - Not Recommended)

```toml
[ftp]
use_ftps = false
```

##### Disadvantages:
- ❌ Unencrypted connection
- ❌ Credentials sent in plain text
- ❌ Data transfer in plain text
- ❌ Vulnerable to interception

##### Use only when:
- Server doesn't support FTPS
- Testing on local network
- Legacy system requirements

## Invocation Points

### Shell Scripts

- **Windows:** `scripts\deploy.cmd -e <environment> [options]`
- **Linux/Mac:** `scripts/deploy.sh -e <environment> [options]`

### Direct Python

- **Module:** `python -m utils.deploy -e <environment> [options]`
- **From Code:** `from utils.deploy import main; main()`

### Build Pipeline Integration

```bash
# Manual deployment workflow
.\scripts\package.cmd -e prod
.\scripts\deploy.cmd -e prod --deploy

# Automated CI/CD deployment
python -m utils.package -e prod --force
python -m utils.deploy -e prod --force
```

## Development

### Key Functions

#### High-Level

- **`main()`**
  - Entry point for module execution
  - Parses command line arguments
  - Initializes logging
  - Calls `deploy_package()`
  - Returns exit code

- **`deploy_package(environment, dry_run, force)`**
  - Main deployment workflow function
  - Loads configuration via `gzconfig`
  - Finds latest package
  - Uploads to FTP server (if enabled via --deploy or --force)
  - Returns exit code (0=success, 1=error)

#### Configuration & Discovery

- **`get_project_root()`**
  - Returns Path to project root directory
  - Used for finding packages directory

- **`get_latest_package(environment)`**
  - Finds most recent `package_{env}_*.zip` file
  - Returns Path object or None
  - Sorted by modification time (newest first)

#### Upload Utilities

- **`create_upload_subdir_name(deploy_config)`**
  - Creates timestamped subdirectory name
  - Adds random alphanumeric postfix
  - Returns subdirectory name with dot prefix

- **`generate_random_string(length)`**
  - Generates random alphanumeric string
  - Used for subdirectory postfix
  - Returns lowercase letters + digits

- **`connect_ftp(deploy_config)`**
  - Connects to FTP or FTPS server
  - Handles authentication
  - Returns connected FTP object
  - Raises ConnectionError on failure

- **`upload_file(ftp, local_path, remote_name)`**
  - Uploads file to FTP server
  - Displays progress and filename
  - Raises OSError on failure

- **`write_deployment_history(package_path, environment, remote_path)`**
  - Writes deployment record to history file
  - Creates history file if it doesn't exist
  - Appends entry with timestamp and deployment details
  - Non-fatal: logs warning but doesn't fail deployment if write fails
  - History filename: `<package_name_without_.zip>.deploy_history.txt`

### Integration

#### Uses:
- `utils.gzconfig` - Configuration management
  - `get_pipeline_config(environment)` - Environment directory info
  - `get_deploy_config()` - FTP credentials and settings
- `utils.gzlogging` - Logging infrastructure
  - `get_logging_context(environment, 'deploy')` - Log context

#### Used By:
- `scripts/deploy.cmd` - Windows launcher
- `scripts/deploy.sh` - Linux/Mac launcher
- CI/CD pipelines - Automated deployments

## Security

### Credentials Protection

⚠️ **CRITICAL:** The `config/deploy.toml` file contains sensitive credentials that must be protected.

#### Security Measures:

1. **Git Ignore** ✅
   - `deploy.toml` is in `.gitignore`
   - Will never be committed to repository
   - Always use `deploy.example.toml` for templates

2. **File Permissions** ✅
   - Restrict access to your user only
   - See platform-specific commands below

3. **FTPS Encryption** ✅
   - Use `use_ftps = true` (default)
   - Encrypts credentials and data in transit
   - Prevents network sniffing

4. **No Hardcoding** ✅
   - Never hardcode credentials in scripts
   - Always read from config file
   - Use environment variables for CI/CD

5. **Password Masking** ✅
   - Passwords masked in logs and output
   - `repr()` shows `password='***'`

### Recommended Practices

#### Linux/Mac:
```bash
# Restrict file permissions (owner read/write only)
chmod 600 config/deploy.toml

# Verify permissions
ls -l config/deploy.toml
# Should show: -rw------- 1 user group ...
```

#### Windows:
```cmd
# Restrict NTFS permissions
icacls config\deploy.toml /inheritance:r /grant:r "%USERNAME%:F"

# Verify permissions
icacls config\deploy.toml
```

### CI/CD Integration

For automated deployments, use environment variables instead of config file:

```python
# Example: Dynamic configuration for CI/CD
import os
from utils.gzconfig.deploy import DeployConfig

# Override with environment variables
deploy_config = DeployConfig(
    server=os.getenv('FTP_SERVER', 'ftp.example.com'),
    username=os.getenv('FTP_USERNAME'),
    password=os.getenv('FTP_PASSWORD'),
    target_dir=os.getenv('FTP_TARGET_DIR', '/public_html'),
    port=int(os.getenv('FTP_PORT', '21')),
    use_ftps=os.getenv('FTP_USE_FTPS', 'true').lower() == 'true'
)
```

#### GitHub Actions Example:
```yaml
env:
  FTP_SERVER: ${{ secrets.FTP_SERVER }}
  FTP_USERNAME: ${{ secrets.FTP_USERNAME }}
  FTP_PASSWORD: ${{ secrets.FTP_PASSWORD }}
  FTP_TARGET_DIR: ${{ secrets.FTP_TARGET_DIR }}
```

## Troubleshooting

### "Configuration file not found"

**Problem:** Cannot find `config/deploy.toml`

#### Solution:
1. Copy `config/deploy.example.toml` to `config/deploy.toml`
2. Fill in your FTP credentials
3. Ensure file is in correct location relative to project root
4. Check file permissions (must be readable)

### "No package found for environment"

**Problem:** No packages in `publish/packages/` for the specified environment

#### Solution:
1. Run package module first: `python -m utils.package -e <environment>`
2. Verify `publish/packages/` directory exists
3. Check package file naming: `package_{environment}_*.zip`
4. Ensure package creation completed successfully

### "Connection refused" or "Login failed"

**Problem:** Cannot connect to FTP server

#### Solution:
1. Verify server hostname is correct
2. Check username and password in `deploy.toml`
3. Ensure firewall allows FTP/FTPS (port 21 or custom)
4. Test with `use_ftps = false` to isolate FTPS issues
5. Confirm server supports FTPS if using encrypted connection
6. Check if server is online and accessible

### "Cannot access target directory"

**Problem:** FTP permission error accessing `target_dir`

#### Solution:
1. Verify `target_dir` path is correct (e.g., `/public_html`)
2. Check FTP user has write permissions to directory
3. Ensure directory exists on server
4. Test by manually connecting with FTP client
5. Check disk space on server

### "Upload failed" or timeout

**Problem:** Upload stops mid-transfer or times out

#### Solution:
1. Check network connection stability
2. Try smaller package sizes (split content)
3. Increase FTP timeout settings (if possible)
4. Check firewall/NAT settings for passive mode
5. Try different network connection
6. Verify server has sufficient disk space

### Dry-run shows wrong server

**Problem:** Dry-run displays unexpected FTP settings

#### Solution:
1. Check `config/deploy.toml` for correct values
2. Ensure no typos in server hostname
3. Verify file was saved after editing
4. Check for multiple `[ftp]` sections (only one allowed)
5. Review gzconfig error messages in logs

## Best Practices

### Before Deploying

1. **Test with Dry-Run**
   ```bash
   python -m utils.deploy -e dev --dry-run
   ```
   - Verify package is correct
   - Check FTP settings
   - Confirm upload directory

2. **Verify Package**
   - Ensure package was recently created
   - Check package size is reasonable
   - Confirm package contains expected files

3. **Check Credentials**
   - Verify `deploy.toml` has correct settings
   - Test FTP connection manually if unsure
   - Ensure FTPS is enabled for production

### During Deployment

1. **Monitor Progress**
   - Watch console output for errors
   - Check upload progress
   - Wait for completion confirmation

2. **Check Logs**
   - Review log file after deployment
   - Look for warnings or errors
   - Verify all steps completed

### After Deployment

1. **Verify Upload**
   - Check FTP server manually
   - Verify file was uploaded completely
   - Confirm file size matches local package

2. **Test Website**
   - Browse to deployed site
   - Check key pages load correctly
   - Verify no broken links or missing resources

3. **Document Deployment**
   - Note deployment time and environment
   - Record any issues encountered
   - Keep deployment logs for audit

### Production Deployments

1. **Use Staging First**
   ```bash
   # Deploy to staging
   python -m utils.deploy -e staging
   
   # Test thoroughly on staging
   
   # Deploy to production
   python -m utils.deploy -e prod
   ```

2. **Backup Before Deploy**
   - Keep previous package versions
   - Document rollback procedure
   - Have recovery plan ready

3. **Deploy During Low Traffic**
   - Schedule deployments for off-peak hours
   - Notify users of maintenance if needed
   - Monitor server after deployment

## Performance

### Upload Speed

Upload time depends on:
- Network bandwidth
- Server location and performance
- Package file size
- FTP vs FTPS overhead
- Network latency

#### Typical Upload Times:

| Package Size | Connection Speed | Estimated Time |
|--------------|------------------|----------------|
| 1 MB | 1 Mbps | ~8 seconds |
| 5 MB | 1 Mbps | ~40 seconds |
| 10 MB | 1 Mbps | ~80 seconds |
| 1 MB | 10 Mbps | <1 second |
| 10 MB | 10 Mbps | ~8 seconds |
| 50 MB | 10 Mbps | ~40 seconds |

**Note:** FTPS adds ~5-10% overhead due to TLS encryption, but this is negligible compared to network latency.

### Optimization Tips

1. **Minimize Package Size**
   - Remove unnecessary files
   - Compress images before packaging
   - Clean up temporary files

2. **Use FTPS Wisely**
   - Use FTPS for production (security first)
   - Use FTP for local testing (faster)

3. **Network Considerations**
   - Deploy from stable network connection
   - Avoid WiFi for large deployments
   - Use wired connection when possible

## Future Enhancements

Planned improvements:

- [x] **Dry-run mode** - Preview deployment without uploading
- [x] **Timestamped subdirectories** - Organize uploads with unique dirs
- [x] **FTPS support** - Secure encrypted uploads
- [x] **Progress tracking** - Real-time upload feedback
- [ ] **SFTP support** - SSH File Transfer Protocol
- [ ] **Resume interrupted uploads** - Continue partial uploads
- [ ] **Incremental deployments** - Upload only changed files
- [ ] **Multi-server deployment** - Deploy to multiple servers in parallel
- [ ] **Deployment rollback** - Revert to previous deployment
- [ ] **Post-deployment verification** - Automated health checks
- [ ] **Webhook notifications** - Notify on completion/failure
- [ ] **Deployment history tracking** - Database of all deployments
- [ ] **AWS S3 support** - Deploy to S3 buckets
- [ ] **Azure Blob Storage support** - Deploy to Azure
- [ ] **CloudFlare Pages support** - Deploy to CloudFlare

## Related Documentation

- **[gzconfig Module](../gzconfig/README.md)** - Configuration management
- **[gzlogging Module](../gzlogging/README.md)** - Logging infrastructure
- **[package Module](../package/README.md)** - Package creation
- **[FTP Protocol](https://en.wikipedia.org/wiki/File_Transfer_Protocol)** - FTP specification
- **[FTPS](https://en.wikipedia.org/wiki/FTPS)** - FTP over TLS
- **[Python ftplib](https://docs.python.org/3/library/ftplib.html)** - Python FTP library
- **[strftime](https://docs.python.org/3/library/datetime.html#strftime-strptime-behavior)** - Date format codes

## License

GPL-3.0-or-later

## Authors

superguru, gazorper

---

*Last updated: October 23, 2025*  
*Deploy version: 1.0*
