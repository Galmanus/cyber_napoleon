#!/usr/bin/env python3
"""
CAI CLI Main Module

Entry point for running the CAI CLI as a module.
"""

try:
    # Try to import the main function directly
    from . import main as main_module
    
    # Look for available main functions
    if hasattr(main_module, "main_refactored"):
        main_function = main_module.main_refactored
    elif hasattr(main_module, "main"):
        main_function = main_module.main
    elif callable(main_module):
        main_function = main_module
    else:
        def main_function():
            print("Error: No suitable main function found")
            return 1
            
except ImportError as e:
    print(f"Import error: {e}")
    def main_function():
        print("Error: Could not load CAI CLI")
        return 1

if __name__ == "__main__":
    if main_function and callable(main_function):
        main_function()
    else:
        print("Error: Main function not found or not callable")
