#!/usr/bin/env python3
"""
Main Execution Script for RBF System

This script provides the main entry point for the RBF system.
"""

import sys
import os

def show_menu():
    """Display the main menu"""
    print("=" * 50)
    print("BITCOIN RBF SYSTEM")
    print("=" * 50)
    print("1. Run Interactive RBF System")
    print("2. Run Demo with Predefined Inputs")
    print("3. Exit")
    print()

def run_interactive():
    """Run the interactive RBF system"""
    try:
        # Import and run the main RBF system
        from rbf_main import main
        main()
    except ImportError as e:
        print(f"Error importing RBF system: {e}")
        print("Make sure all files are in the correct location.")

def run_demo():
    """Run the demo version"""
    try:
        # Import and run the demo
        from run_rbf_demo import run_demo
        run_demo()
    except ImportError as e:
        print(f"Error importing demo: {e}")
        print("Make sure all files are in the correct location.")

def main():
    """Main execution function"""
    while True:
        show_menu()
        try:
            choice = input("Enter your choice (1-3): ").strip()
            
            if choice == "1":
                print("\nStarting Interactive RBF System...")
                run_interactive()
            elif choice == "2":
                print("\nRunning Demo...")
                run_demo()
            elif choice == "3":
                print("\nGoodbye!")
                break
            else:
                print("Invalid choice. Please enter 1, 2, or 3.\n")
                
            input("\nPress Enter to continue...")
            print()
            
        except KeyboardInterrupt:
            print("\n\nGoodbye!")
            break
        except Exception as e:
            print(f"An error occurred: {e}")
            input("\nPress Enter to continue...")

if __name__ == "__main__":
    # Make sure we can import modules from the current directory
    sys.path.append(os.path.dirname(os.path.abspath(__file__)))
    main()