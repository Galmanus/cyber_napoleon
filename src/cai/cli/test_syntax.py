"""
Simple syntax test for refactored CLI modules

Tests that all modules have valid Python syntax without importing dependencies.
"""

import os
import sys
import ast

def test_module_syntax():
    """Test that all refactored modules have valid Python syntax."""
    print("Testing module syntax...")

    modules_to_test = [
        "session_manager.py",
        "command_processor.py",
        "agent_runner.py",
        "parallel_executor.py",
        "ui_manager.py",
        "error_handler.py",
        "state_manager.py",
        "warning_suppressor.py",
        "main.py",
        "__init__.py"
    ]

    cli_dir = os.path.dirname(__file__)
    passed = 0
    total = len(modules_to_test)

    for module_name in modules_to_test:
        module_path = os.path.join(cli_dir, module_name)

        if not os.path.exists(module_path):
            print(f"✗ Module {module_name} not found")
            continue

        try:
            with open(module_path, 'r', encoding='utf-8') as f:
                source_code = f.read()

            # Parse the AST to check syntax
            ast.parse(source_code, filename=module_name)
            print(f"✓ {module_name} syntax is valid")
            passed += 1

        except SyntaxError as e:
            print(f"✗ {module_name} has syntax error: {e}")
        except Exception as e:
            print(f"✗ {module_name} error: {e}")

    return passed, total

def test_module_structure():
    """Test that modules have expected structure."""
    print("\nTesting module structure...")

    cli_dir = os.path.dirname(__file__)

    # Check that all expected files exist
    expected_files = [
        "__init__.py",
        "session_manager.py",
        "command_processor.py",
        "agent_runner.py",
        "parallel_executor.py",
        "ui_manager.py",
        "error_handler.py",
        "state_manager.py",
        "warning_suppressor.py",
        "main.py"
    ]

    passed = 0
    total = len(expected_files)

    for filename in expected_files:
        filepath = os.path.join(cli_dir, filename)
        if os.path.exists(filepath):
            print(f"✓ {filename} exists")
            passed += 1
        else:
            print(f"✗ {filename} missing")

    return passed, total

def test_import_structure():
    """Test that __init__.py has proper imports."""
    print("\nTesting import structure...")

    init_file = os.path.join(os.path.dirname(__file__), "__init__.py")

    try:
        with open(init_file, 'r', encoding='utf-8') as f:
            content = f.read()

        # Check for expected imports
        expected_imports = [
            "SessionManager",
            "CLISession",
            "TimingStats",
            "CommandProcessor",
            "AgentRunner",
            "ParallelExecutor",
            "UIManager",
            "ErrorHandler",
            "StateManager",
            "CLIState",
            "WarningSuppressor",
            "setup_warning_suppression"
        ]

        passed = 0
        for import_name in expected_imports:
            if import_name in content:
                passed += 1
            else:
                print(f"✗ Missing import: {import_name}")

        if passed == len(expected_imports):
            print("✓ All expected imports found in __init__.py")

        return passed, len(expected_imports)

    except Exception as e:
        print(f"✗ Error reading __init__.py: {e}")
        return 0, 12  # Return expected count

def run_tests():
    """Run all syntax and structure tests."""
    print("Running CAI CLI Refactoring Syntax Tests")
    print("=" * 50)

    tests = [
        test_module_syntax,
        test_module_structure,
        test_import_structure,
    ]

    total_passed = 0
    total_tests = 0

    for test in tests:
        try:
            passed, total = test()
            total_passed += passed
            total_tests += total
        except Exception as e:
            print(f"✗ Test {test.__name__} failed with exception: {e}")

    print("\n" + "=" * 50)
    print(f"Tests completed: {total_passed}/{total_tests} passed")

    if total_passed == total_tests:
        print("🎉 All syntax and structure tests passed!")
        print("The refactored CLI modules appear to be structurally sound.")
        return True
    else:
        print("❌ Some tests failed. Please review the refactoring.")
        return False

if __name__ == "__main__":
    success = run_tests()
    sys.exit(0 if success else 1)