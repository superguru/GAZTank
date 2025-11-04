# General Development

## Update README
Update the README to reflect the changes since the last time it was updated

## Python script error correction
pylance gives errors for this file

## Convert useful scripts to full Python modules
Move this script into its own dir in .\utils, make it a module like normalise but also stay 
callable as it currently is as a script, and update all scripts, md files, and other references accordingly. 
add a documentation file for this as well that will describe the module in brief.

## Rename module file
Rename this file to XXXXX.py, and update associated shell scripts from .\scripts and also all relevant documentation in the README.md for the module, or in .\docs or .\utils

## Update pipeline module documentation generation
Update or create a group in `.\config\generate.toml` with:
- name = "pipeline_docs"
- enabled=true
- input_type=markdown
- output_dir="pipeline-docs"
Scan the .\utils dir and subdirs, just one level deep, and add all the README.md files, sorted alphabetically by module name. 
The .\utils\README.md, if it exists, should be at the top.
If this is an update, remove orphaned files from the group in the toml file, and report on it.

---
netstat -a -n -o | findstr :219
---

# Files

## Rename
Rename this to XXXXX and update references to it across the project

---

# Website Development

## AI driven linting
How can this site be improved for SEO, speed, responsiveness, and best practices? 
Update recommendations.txt to reflect what has been done and what needs to be done.

---


---

# Temporary Prompt Workspace

## Task: Create new Python module
Create a new python module in .\utils named `gzhost`
The module should use gzlogging and output to both log file and console.
The module should use the pipeline.toml config file, which should be extended to include a new attr named ftpd_port, which works the same as httpd_port, and with defaults of 2190, 2191, 2192 for the dev, staging, and prod environments.
The function of gzhost is to be a simple FTP server, using pyftpdlib. In general it should work the same as the utils.gzserve module, but just for FTP
gzhost exists to simulate a remote host where a package of the website is deployed using FTP.
Add another toml file to .\config\ named ftp_users.toml
This file should have sections per environment, just like tools.toml has
Add the same linting rules for ftp_users.toml to utils.gzlint that are already checked for the tools.toml file to make sure sections align, with pipeline.toml being the source of truth
The ftp_users.toml file should be fully supported for reading by gzconfig
For now, only support one ftp user definition per environment to ftp_users.toml
Each user should have username, password, and permissions attrs.
Passwords can just be in plain text, as this is for local development.
The permissions attr corresponds to the perm argument for the authorizer.add_user() function from pyftpdlib
The home dir for the users should be the environment dir, and presented as / 
Add gzhost to the module maturity tracker under the tools section

---


