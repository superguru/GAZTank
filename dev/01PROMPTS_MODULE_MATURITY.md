# Checklist prompts for Python modules
Prompts to ensure Python modules are mature, professional, and high quality.

## Is a proper module
Verify that this is a proper module that can run with python -m <modulename>
Ensure the module has a --help command line argument

## Must have -e <environment> command line argument
Ensure there is a mandatory command line argument -e <environment>, which corresponds to environment sections in .\config\environments.toml. Examples: "-e dev" or "-e staging".
The output dir should depend on the environment passed in.

## Uses gzconfig
Ensure this module uses gzconfig for all config files

## Does not need -e <environment> command line argument
This module does not need a -e <environment> command line argument. In cases where an environment is needed, such as for logging context or configuration data, assume the dev environment.

## Uses gzlogging
Ensure that this module uses gzlogging to output to both log file and to console. 
The tool-name for logging purposes is "XXX". 
If no -e command line parameter has been implemented for this module, then it doesn't need it, but for logging and any other purposes assume that the environment to use is dev
Add only statements appropriate for a log file to the log statements.
What goes where:
    Console output (print()):
        Headers and decorative lines
        Emojis and visual formatting
        Blank lines for spacing
        Summary boxes
        User-facing messages
    Log file (log.inf(), log.wrn(), log.err()):
        Operational information (files processed, configuration loaded)
        Error messages (without emojis)
        Success/failure status
        Concise summaries

## Shell scripts
Create or update launcher shell scripts (.cmd and .sh) for this module. Follow the design rules in .\docs\DESIGN_RULES.md line 213-245 and lines 193-211 for UTF-8 handling, as well as the setlocal pattern that can be observed in other scripts in the .\scripts dir. 
The UTF-8 patterns are required, whether or not the shell scripts or the Python scripts output emojis.
Ensure that all command line arguments passed to the shell scripts are passed on to the Python module. See the existing shell scripts in .\scripts for `generate` as examples. 

# Must have a --force command line argument
Add an optional command line argument --force. If this is specified, then the output should be generated regardless of whether it is outdated or not. Otherwise, the input files should be checked to see if they are newer or if the output does not exist, and only perform the operations if needed.

## Must have --dry-run command line argument
Ensure thhis module has an optional command line argument --dry-run. If this is present, then no output will be generated, however all the other logic will still apply as if output were generated. Ensure that logging and statistics output accurately refects this.

# Log file and Console out consistency, effectiveness, and style
Ensure the logging and statistics output for this module correctly shows what is going on. 

The examples and example data following this were taken from the `generate` and `sitemapper` modules, which are both already compliant with these requirements.

1. Make sure log statements include information with this sort of style and content, taken from the log file of generate to use as an example, if applicable:
[2025-10-22 13:20:27] [dev] [INF] Static Content Generator started
[2025-10-22 13:20:27] [dev] [INF] DRY RUN MODE enabled
[2025-10-22 13:20:27] [dev] [INF] FORCE MODE enabled
[2025-10-22 13:20:27] [dev] [INF] Project root: D:\Projects\www\GAZTank
[2025-10-22 13:20:27] [dev] [INF] Loaded configuration from D:\Projects\www\GAZTank\config\generate.toml
...
...
...
[2025-10-22 13:16:34] [dev] [INF] Static Content Generator completed successfully

But there must be no blank lines in the log output, and no lines like:
[2025-10-22 13:16:34] [dev] [INF] ============================================================

2. Make the statistics output to both log files and console indicate the settings in use like DRY RUN MODE enabled, etc.

3. Make sure the output doesn't give false information that files were written during dry run mode, then in fact nothing was modified. 
For instance, the log file of sitemapper has this style, which is good:
[2025-10-22 13:16:14] [dev] [INF] Dry-run complete: 6 URLs prepared (not written)

4. Include emojis to make console output look more visually appealing and easier to understand at a glance.

## Is verified to be UTF-8 compliant for module and associated shell scripte
Verify that UTF-8 handling for the scripts in this module, and the shell invocation scripts, is correct as per the the design rules in .\docs\DESIGN_RULES.md line 213-245 and lines 193-211. Make sure the shell invocation scripts follow the setlocal pattern that can be observed in other scripts in the .\scripts dir. Also make sure that all command line arguments passed to the shell scripts for this module are passed on to the python module.
All of these patterns are required, whether or not the shell scripts or the Python scripts output emojis.

## Re-organise / Create module README.md
Using .\dev\MODULE_README_STRUCTURE.md as a template, re-organise this module's README.md to match that structure, and fill in and applicable optional sections, or other applicable and logically relevant topics not explicitly listed. 
Some of the content areas contain examples, and aren't meant to be literally followed. 
Update the README to reflect the changes since the last time it was updated. 
If the readme doesn't exist, look at the generate module's README. 
If items in the Future Enhancements have been done, they can be ticked.

## Track conformity conditions

### Final Step

Tick off checklist conditions in .\utils\00MODULE_MATURITY.md for this module and for the specified tasks only.
Do not check or tick off checklist conditions for other modules or any checklist conditions for this module that have not been explicitely requested in this list if tasks.
If all of the checklist conditions for the module has been ticked, then the module itself can be marked as done in the content and the TOC.
Adhere to the rules in ### File Organisation and ### Update the TOC

