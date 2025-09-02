#!/usr/bin/env python3
"""
CAI Framework - Simple Startup Script
Starts CAI without the problematic ML dependencies
"""

import sys
import os

# Add src directory to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

def main():
    print("🚀 Starting CAI Framework...")
    print("=" * 50)
    
    try:
        # Try to import and run CAI
        from cai.cli import main as cai_main
        cai_main()
    except Exception as e:
        print(f"❌ Error starting CAI: {e}")
        print("\n💡 Available alternatives:")
        print("1. Run the monitoring script: python3 monitor.py --mode health")
        print("2. Check basic import: python3 -c 'import cai; print(\"CAI imported successfully\")'")
        return 1
    
    return 0

if __name__ == "__main__":
    sys.exit(main())
