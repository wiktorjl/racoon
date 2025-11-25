#!/usr/bin/env python3
import os
import subprocess
import sys
import argparse
import re

# Color support detection
USE_COLOR = False

def check_color_support():
    """Check if the terminal supports color output."""
    if not sys.stdout.isatty():
        return False

    # Check TERM environment variable
    term = os.environ.get('TERM', '')
    if term == 'dumb':
        return False

    # Try to use curses to detect color support
    try:
        import curses
        curses.setupterm()
        return curses.tigetnum('colors') >= 8
    except:
        # Fallback: assume color support if TERM is set
        return bool(term)

# Color codes
class Colors:
    DARK_GREEN = '\033[32m' if USE_COLOR else ''
    BRIGHT_GREEN = '\033[92m' if USE_COLOR else ''
    DARK_YELLOW = '\033[33m' if USE_COLOR else ''
    RESET = '\033[0m' if USE_COLOR else ''

def get_metadata(item_path, key):
    """Generic function to get a metadata value from a script file."""
    try:
        with open(item_path, 'r') as f:
            for line in f:
                if line.strip().startswith(f'# {key}:'):
                    return line.replace(f'# {key}:', '').strip()
    except (IOError, UnicodeDecodeError):
        pass
    return None

def get_label(item_path):
    """Gets the label of a script, falling back to the filename."""
    label = get_metadata(item_path, 'LABEL')
    return label if label else os.path.basename(item_path)

def get_script_args(item_path):
    """Parses '# ARG:' comments in a script to get argument definitions."""
    args = []
    arg_pattern = re.compile(r'# ARG:\s*(\S+)\s+"([^"]*)"\s+"([^"]*)"')
    try:
        with open(item_path, 'r') as f:
            for line in f:
                match = arg_pattern.match(line.strip())
                if match:
                    name, prompt, default = match.groups()
                    args.append((name, prompt, default))
    except (IOError, UnicodeDecodeError):
        pass
    return args

def needs_sudo(item_path):
    """Checks if a script requires sudo."""
    return get_metadata(item_path, 'SUDO') == 'true'

def run_script(selected_item_path):
    """
    Handles the execution of a selected script.
    Collects arguments upfront before execution.
    """
    # Collect arguments before running the script
    script_args = get_script_args(selected_item_path)
    collected_args = []

    if script_args:
        for _, prompt, default in script_args:
            user_input = input(f"  {Colors.DARK_GREEN}{prompt}{Colors.RESET} [{Colors.BRIGHT_GREEN}{default}{Colors.RESET}]: {Colors.DARK_YELLOW}")
            print(Colors.RESET, end='')  # Reset color after input
            collected_args.append(user_input or default)

    # Build command with arguments
    command = []
    if needs_sudo(selected_item_path):
        command.extend(["sudo", "-E"])
    command.append(selected_item_path)
    command.extend(collected_args)

    # Run the script
    try:
        subprocess.run(command)
    except KeyboardInterrupt:
        print(f"\n  {Colors.BRIGHT_GREEN}*{Colors.RESET} Script interrupted")


def handle_choice(choice, menu_items, menu_path):
    """Handles the user's menu choice."""
    if 1 <= choice <= len(menu_items):
        selected_item_name = menu_items[choice - 1]
        selected_item_path = os.path.join(menu_path, selected_item_name)

        if os.path.isdir(selected_item_path):
            menu_loop(selected_item_path)
        else:
            run_script(selected_item_path)
            input(f"\n  {Colors.DARK_GREEN}Press Enter to continue...{Colors.RESET}{Colors.DARK_YELLOW}")
            print(Colors.RESET, end='')  # Reset color after input
    else:
        print(f"  {Colors.BRIGHT_GREEN}*{Colors.RESET} Invalid choice")

def get_menu_items(menu_path):
    """Returns a sorted list of valid menu item names in a given path."""
    items = sorted(os.listdir(menu_path))
    menu_items = []
    for item in items:
        item_path = os.path.join(menu_path, item)
        if os.access(item_path, os.X_OK) or os.path.isdir(item_path):
            menu_items.append(item)
    return menu_items

def print_menu(menu_items, menu_path):
    """Prints the formatted menu to the console."""
    print("")
    for i, item_name in enumerate(menu_items):
        item_path = os.path.join(menu_path, item_name)
        if os.path.isdir(item_path):
            print(f"  {Colors.BRIGHT_GREEN}[{i + 1}]{Colors.RESET}  {Colors.DARK_GREEN}{item_name}/{Colors.RESET}")
        else:
            label = get_label(item_path)
            print(f"  {Colors.BRIGHT_GREEN}[{i + 1}]{Colors.RESET}  {Colors.BRIGHT_GREEN}{label}{Colors.RESET}")
    print()
    print(f"  {Colors.BRIGHT_GREEN}[0]{Colors.RESET}  {Colors.BRIGHT_GREEN}Exit{Colors.RESET}")

def print_banner():
    """Prints the ASCII art banner."""
    banner = r"""  ____
 |  _ \ __ _  ___ ___   ___  _ __
 | |_) / _` |/ __/ _ \ / _ \| '_ \
 |  _ < (_| | (_| (_) | (_) | | | |
 |_| \_\__,_|\___\___/ \___/|_| |_|
"""
    print(f"{Colors.BRIGHT_GREEN}{banner}{Colors.RESET}")

def menu_loop(menu_path, is_top_level=False):
    """Displays the menu and handles user interaction."""
    if is_top_level:
        print_banner()

    while True:
        try:
            menu_items = get_menu_items(menu_path)
            print_menu(menu_items, menu_path)
            choice_str = input(f"  {Colors.DARK_GREEN}>{Colors.RESET} {Colors.DARK_YELLOW}").strip()
            print(Colors.RESET, end='')  # Reset color after input

            if not choice_str:
                if is_top_level:
                    print(f"  {Colors.DARK_GREEN}Goodbye.{Colors.RESET}")
                    sys.exit(0)
                else:
                    break

            if not choice_str.isdigit():
                print(f"  {Colors.BRIGHT_GREEN}*{Colors.RESET} Please enter a number")
                continue

            choice = int(choice_str)
            if choice == 0:
                if is_top_level:
                    print(f"  {Colors.DARK_GREEN}Goodbye.{Colors.RESET}")
                    sys.exit(0)
                else:
                    break

            handle_choice(choice, menu_items, menu_path)

        except ValueError:
            print(f"  {Colors.BRIGHT_GREEN}*{Colors.RESET} Please enter a number")
        except KeyboardInterrupt:
            print(f"\n  {Colors.DARK_GREEN}Goodbye.{Colors.RESET}")
            sys.exit(0)

def main():
    """Main function to parse arguments and start the menu."""
    global USE_COLOR

    if not sys.stdout.isatty():
        script_path = os.path.abspath(__file__)
        args = [sys.executable, script_path] + sys.argv[1:]
        subprocess.run(['konsole', '--hold', '-e'] + args)
        sys.exit(0)

    # Initialize color support
    USE_COLOR = check_color_support()

    # Reinitialize Colors class with the detected support
    Colors.DARK_GREEN = '\033[32m' if USE_COLOR else ''
    Colors.BRIGHT_GREEN = '\033[92m' if USE_COLOR else ''
    Colors.DARK_YELLOW = '\033[33m' if USE_COLOR else ''
    Colors.RESET = '\033[0m' if USE_COLOR else ''

    parser = argparse.ArgumentParser(description="A simple, file-based terminal menu system.")
    parser.add_argument(
        "path",
        nargs="?",
        default="menu",
        help="The path to the directory to use as the menu. Defaults to 'menu'."
    )
    args = parser.parse_args()

    start_path = args.path
    if not os.path.isdir(start_path):
        print(f"Error: Directory '{start_path}' not found.")
        sys.exit(1)

    menu_loop(start_path, is_top_level=True)

if __name__ == "__main__":
    main()
