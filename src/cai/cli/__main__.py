#!/usr/bin/env python3
"""
CAI CLI Main Module

Entry point for running the CAI CLI as a module.
"""

try:
    # Try to import the main function from the module
    from . import main
    if callable(main):
        # If main is a function, call it directly
        main_function = main
    else:
        # If main is a module, get the main function from it
        main_function = getattr(main, 'main', None)
except ImportError:
    # Fallback if import fails
    def main_function():
        print("Error: Could not load CAI CLI")
        return 1

if __name__ == "__main__":
    if main_function and callable(main_function):
        main_function()
    else:
        print("Error: Main function not found or not callable")
