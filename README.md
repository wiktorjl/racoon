# Racoon Menu

A simple, file-based terminal menu system.

## Usage

To run the menu, execute the `menu.py` script:

```bash
./menu.py
```

You can also specify a starting directory:

```bash
./menu.py /path/to/your/menu
```

## How it Works

The menu is generated from the file system. Each executable file and directory within the `menu` directory (or the directory you specify) becomes a menu item.

-   **Directories:** Entering a directory will navigate into a sub-menu.
-   **Executable Files:** Selecting an executable file will run it.

## Creating Menu Items

To add a new menu item, simply create a new file or directory inside the `menu` directory.

### Labels

The text displayed in the menu for each item is determined by a special comment in the script file. To set a label for your script, add a comment like this near the top of the file:

```bash
# LABEL: My Awesome Script
```

If a script does not have a `# LABEL:` comment, its filename will be used as the label.
