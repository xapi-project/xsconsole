[![`pre-commit`](https://img.shields.io/badge/pre--commit-enabled-brightgreen?logo=pre-commit)](https://github.com/pre-commit/pre-commit)

# XSConsole: Local Management Console for XenServer and XCP-ng

XSConsole is a robust local management UI designed for XenServer and XCP-ng.
It offers administrators a user-friendly interface for efficiently managing their virtualized environments.

It covers various aspects of virtual infrastructure management, including network configuration, authentication, virtual machines, storage repositories, pools, host operations, backups, and more.

## Accessing XSConsole

XSConsole can be accessed in two ways:

1. **Locally:** Press `Alt + F1` to access the first virtual console screen.
2. **Remotely:** If a Linux shell is available on Dom0, execute the command `xsconsole` from the shell.

## Key Features of XSConsole

### Network Management Interface Configuration
- Easily configure the management interface for your XenServer or XCP-ng host using available NICs.
- Manage NTP servers and set the host's timezone for accurate timekeeping.
- Test network connectivity using `ping` to different addresses.
- Perform an emergency network reset to restore functionality in case of misconfiguration or issues.
- Configure Open vSwitch (OVS) for advanced network management.

### Authentication Configuration
- Conveniently log in and out of XSConsole using secure credentials.
- Change the root password to enhance security and protect your virtual infrastructure.
- Reset the auto-logout time to maintain a secure session and prevent unauthorized access.

### Virtual Machine Management
- Get a comprehensive overview of running virtual machines on the host.
- Forcefully reboot or shut down running VMs to address issues or perform maintenance tasks.
- Start halted VMs to re-enable their execution and resource utilization.
- Monitor host performance metrics for efficiency and identification of potential bottlenecks.

### Storage Repository Management
- List all existing storage repositories associated with the host.
- Create new storage repositories or attach existing ones to expand storage capacity.
- Specify the preferred storage repository for suspend operations and crash dumps.

### Pool Management
- Assign a new master host when part of a pool to maintain cluster integrity.
- Add or remove hosts from a resource pool to optimize resource allocation and workload distribution.

### System Status Reporting
- Generate system status reports for insights into the host's health, performance, and resource utilization.
- Upload and save system status reports to external storage devices for future reference or analysis.

### Host Operations
- Enter or exit maintenance mode on the host for scheduled maintenance tasks without affecting other hosts.
- Reboot or shut down the host to restart its operating system or perform system updates.

### Backup, Restore, and Update
- Schedule or manually perform VM metadata backups to safeguard configurations and data.
- Restore VM metadata backups to recover from accidental changes or system failures.
- Keep your XenServer or XCP-ng installation up-to-date with the latest updates and patches.

## Contributing to XSConsole
Join the XSConsole community by creating issues in the repository to report bugs or suggest enhancements.
- You can propose changes or provide feedback by opening an issue.
- You can contribute changes by creating an Account on GitHub, clicking the Fork button, making your changes, and submitting a pull request.

## Additional Documentation
- Refer to the [`INSTALL`](INSTALL) file for detailed instructions on installing XSConsole for XenServer and XCP-ng.

## Development Status
### Python migration
- The project is currently undergoing upgrades to support running on Python 3.6 to Python 3.11.
- As per the [current developer agreement](https://github.com/xapi-project/xsconsole/pull/18#issuecomment-1791844449), support for Python 3.6+ needs to be fully approved and manually tested before support for Python 2.7 could eventually be dropped. Quotes from it:
  - -- _“However, **master needs to remain atomically py2 or py3 compatible**, and **not a mix of fixes which leaves it broken in both**.”_
  - -- _“**The final commit on the py3 branch** (should bump the major version number of `xsconsole` seeing as it is a big step change).”_
- **As per this agreement**, until that point, changes supporting **only Python3.6+** must go to a **py3 feature branch**.
- The list of `TODOs` remaining for the Python3 upgrade checks (`pylint --py3k`) to be fulfilled is at [line 40 of `.github/workflows/main.yml`](https://github.com/xenserver-next/xsconsole/blob/master/.github/workflows/main.yml#L40).
  Currently, the list of `pylint --py3k` `TODOs` is:
  - `unicode-builtin` (a PR using a function for Py2 and Py3 is working and is coming next)
  - `comprehension-escape`
  - `dict-keys-not-iterating`
  - `old-division`
