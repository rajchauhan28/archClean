# ArchClean

A robust CLI tool for safely cleaning Arch Linux systems. ArchClean helps you maintain a tidy system by automating cache cleaning, removing orphans, and analyzing disk usage, all with safety checks and user confirmation.


## Requirements

*   Python 3.13+ (for now as it actually doesn't require exactly 3.13+)
*   Arch Linux (or derivative)
*   `pacman`
*   `ncdu` (optional, for analysis)


## Features

*   **System Cleaning**:
    *   Clean Pacman cache (`pacman -Sc`).
    *   Clean AUR helper caches (`yay`, `paru`).
    *   Remove orphan packages (`pacman -Qtdq`).
    *   Vacuum systemd journals.
*   **Home Directory**:
    *   Clean thumbnail cache.
    *   Empty Trash.
*   **Language Ecosystems**:
    *   Detects and cleans caches for Python (`pip`), Node.js (`npm`, `yarn`), and Go.
*   **Disk Analysis**:
    *   Integrates with `ncdu` to visualize and clean disk space.
*   **Safety First**:
    *   Interactive prompts for every action (unless `--force` is used).
    *   Checks for binary existence before running commands.

## Installation

### From Source (Poetry)

1.  Clone the repository.
2.  Install dependencies:
    ```bash
    poetry install
    ```
3.  Run the tool:
    ```bash
    poetry run archclean --help
    ```

## Usage

ArchClean uses a command-based interface. The default command `full` runs the entire cleaning wizard.

```bash
# Run the full interactive wizard
archclean full

# Run only system maintenance
archclean system-clean

# Run only home directory cleaning
archclean home-clean

# Run only language cache cleaning
archclean lang-clean

# Run disk analysis (ncdu)
archclean analyze
```

### Options

*   `--force`: Skip confirmation prompts. Note that `sudo` will still ask for a password if required.
    ```bash
    archclean full --force
    ```



## Disclaimer

This tool deletes files. While it aims to be safe by targeting known cache directories and asking for confirmation, **always have backups**. The authors are not responsible for any data loss.
