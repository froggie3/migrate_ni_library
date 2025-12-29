## What it does

This CLI tool scans the `ContentDir` registered in the Native Instruments product registry and conditionally rewrites only those paths that match a specified path.

Its primary purpose is to organize and migrate library locations.

* Enumerates subkeys under `HKEY_LOCAL_MACHINE\SOFTWARE\Native Instruments`
* Only includes entries with `ContentDir`
* Temporarily normalizes `ContentDir` before comparison
* Removes trailing backslashes
  * Rewrites only if it **exactly matches** the specified path set
* The new `ContentDir` will be in the following format

```
<original path> Library\
```

---

## Requirements

* Windows
* Python version not guaranteed (but tested with 3.13.7!)
* Administrator privileges
  * Required to rewrite `HKEY_LOCAL_MACHINE`
* Uses only standard libraries (no external dependencies)

---

## Usage

```
script.py [--dry-run] <paths>...
```

### Arguments

#### `paths` (required)

* One or more can be specified
* Base path to compare against
* Trailing `\` is ignored

Example:

```bash
python script.py "C:/mnt2/#Composing/libraries/NI_Contents/Noire" "C:/mnt2/#Composing/libraries/NI_Contents/Analog Dreams"
```

#### `--dry-run`

* Does not actually rewrite anything.
* Displays only the affected items and changes.

---

## Execution example

### dry-run (check only)

```bash
python script.py --dry-run "C:/mnt2/#Composing/libraries/NI_Contents/Noire"
```

Example output:

```
[DRY-RUN] Kontakt ContentDir: 'C:\mnt2\#Composing\libraries\NI_Contents\Noire' -> 'C:\mnt2\#Composing\libraries\NI_Contents\Noire Library'
```

### To actually rewrite

```bash
python script.py "C:/mnt2/#Composing/libraries/NI_Contents/Noire"
```

Example output:

```
[WRITE] Kontakt ContentDir: 'C:\mnt2\#Composing\libraries\NI_Contents\Noire' -> 'C:\mnt2\#Composing\libraries\NI_Contents\Noire Library'
```

---

## Notes

* It is recommended to check the results by adding `--dry-run` before execution.
