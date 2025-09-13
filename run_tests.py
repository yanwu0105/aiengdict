#!/usr/bin/env python3
"""
Test runner script for aiengdict project
"""

import subprocess
import sys
import os


def run_command(command, description):
    """Run a command and handle errors"""
    print(f"\n{'='*60}")
    print(f"🔄 {description}")
    print(f"{'='*60}")

    try:
        result = subprocess.run(
            command, shell=True, check=True, capture_output=True, text=True
        )
        print(result.stdout)
        if result.stderr:
            print("STDERR:", result.stderr)
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Error running: {command}")
        print(f"Exit code: {e.returncode}")
        print(f"STDOUT: {e.stdout}")
        print(f"STDERR: {e.stderr}")
        return False


def main():
    """Main test runner"""
    print("🧪 AI English-Chinese Dictionary Test Suite")
    print("=" * 60)

    # Change to project directory
    os.chdir(os.path.dirname(os.path.abspath(__file__)))

    # Test commands
    test_commands = [
        ("uv run pytest tests/ -v", "Running all tests with verbose output"),
        (
            "uv run pytest tests/ --cov=. --cov-report=term-missing",
            "Running tests with coverage report",
        ),
        ("uv run pytest tests/test_prompts.py -v", "Testing prompts module"),
        ("uv run pytest tests/test_main.py -v", "Testing main Flask application"),
    ]

    success_count = 0
    total_count = len(test_commands)

    for command, description in test_commands:
        if run_command(command, description):
            success_count += 1
        else:
            print(f"❌ Failed: {description}")

    # Summary
    print(f"\n{'='*60}")
    print("📊 Test Summary")
    print(f"{'='*60}")
    print(f"✅ Passed: {success_count}/{total_count}")
    print(f"❌ Failed: {total_count - success_count}/{total_count}")

    if success_count == total_count:
        print("🎉 All tests passed!")
        return 0
    else:
        print("💥 Some tests failed!")
        return 1


if __name__ == "__main__":
    sys.exit(main())
