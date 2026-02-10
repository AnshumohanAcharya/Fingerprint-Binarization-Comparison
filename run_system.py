#!/usr/bin/env python3
"""
Quick Start Script for Fingerprint Authentication System
Provides an interactive menu to run different components
"""

import os
import sys
import subprocess


def print_banner():
    """Print a nice banner."""
    print("\n" + "="*80)
    print(" 🔐 FINGERPRINT AUTHENTICATION SYSTEM")
    print(" Equal Error Rate (EER) Analysis & Optimal Threshold Determination")
    print("="*80 + "\n")


def check_database():
    """Check if the fingerprints database exists."""
    db_path = "outputs/fingerprints.db"
    return os.path.exists(db_path)


def run_command(command, description):
    """Run a shell command and handle errors."""
    print(f"\n▶️  {description}")
    print(f"Command: {command}")
    print("-" * 80)

    result = subprocess.run(command, shell=True)

    if result.returncode == 0:
        print(f"✅ {description} completed successfully!")
    else:
        print(f"❌ {description} failed with error code {result.returncode}")
        return False
    return True


def main():
    """Main menu."""
    print_banner()

    while True:
        print("\n📋 MENU:")
        print("-" * 80)
        print("1. Process Fingerprints & Extract Minutiae (Step 1)")
        print("2. Evaluate Authentication System & Calculate EER (Step 2)")
        print("3. Run Complete Pipeline (Steps 1 & 2)")
        print("4. View Authentication Evaluation Report")
        print("5. View Fingerprint Processing Results")
        print("6. Check System Status")
        print("0. Exit")
        print("-" * 80)

        choice = input("\nEnter your choice (0-6): ").strip()

        if choice == "1":
            print("\n🔄 Processing fingerprints...")
            print("This will:")
            print("  - Apply binarization techniques")
            print("  - Extract minutiae features")
            print("  - Store templates in database")
            print("\n⚠️  This may take several minutes depending on dataset size...")

            confirm = input("\nProceed? (y/n): ").strip().lower()
            if confirm == 'y':
                run_command("python3 main.py", "Fingerprint Processing")

        elif choice == "2":
            if not check_database():
                print("\n❌ Error: Database not found!")
                print("Please run option 1 first to process fingerprints.")
                continue

            print("\n📊 Evaluating authentication system...")
            print("This will:")
            print("  - Perform genuine and impostor matching")
            print("  - Calculate FAR, FRR at various thresholds")
            print("  - Determine Equal Error Rate (EER)")
            print("  - Generate comprehensive visualizations")
            print("\n⚠️  This may take a few minutes...")

            confirm = input("\nProceed? (y/n): ").strip().lower()
            if confirm == 'y':
                success = run_command("python3 evaluate_authentication.py",
                                    "Authentication System Evaluation")
                if success:
                    print("\n" + "="*80)
                    print("📁 Results saved to: outputs/authentication_evaluation/")
                    print("🌐 Open: outputs/authentication_evaluation/authentication_evaluation_report.html")
                    print("="*80)

        elif choice == "3":
            print("\n🚀 Running complete pipeline...")
            confirm = input("This will take several minutes. Proceed? (y/n): ").strip().lower()
            if confirm == 'y':
                if run_command("python3 main.py", "Fingerprint Processing"):
                    run_command("python3 evaluate_authentication.py",
                              "Authentication System Evaluation")

        elif choice == "4":
            report_path = "outputs/authentication_evaluation/authentication_evaluation_report.html"
            if os.path.exists(report_path):
                print(f"\n🌐 Opening report: {report_path}")
                run_command(f"open {report_path}", "Opening Report")
            else:
                print("\n❌ Report not found. Please run option 2 first.")

        elif choice == "5":
            index_path = "outputs/index.html"
            if os.path.exists(index_path):
                print(f"\n🌐 Opening results: {index_path}")
                run_command(f"open {index_path}", "Opening Results")
            else:
                print("\n❌ Results not found. Please run option 1 first.")

        elif choice == "6":
            print("\n📊 SYSTEM STATUS:")
            print("-" * 80)

            db_exists = check_database()
            print(f"Database: {'✅ Found' if db_exists else '❌ Not Found'}")

            if db_exists:
                import sqlite3
                conn = sqlite3.connect("outputs/fingerprints.db")
                cursor = conn.cursor()
                cursor.execute("SELECT COUNT(*) FROM fingerprints")
                count = cursor.fetchone()[0]
                conn.close()
                print(f"Templates in database: {count}")

            eval_exists = os.path.exists("outputs/authentication_evaluation/authentication_evaluation_report.html")
            print(f"Evaluation Report: {'✅ Generated' if eval_exists else '❌ Not Generated'}")

            proc_exists = os.path.exists("outputs/index.html")
            print(f"Processing Report: {'✅ Generated' if proc_exists else '❌ Not Generated'}")

            print("-" * 80)

            if not db_exists:
                print("\n💡 Next step: Run option 1 to process fingerprints")
            elif not eval_exists:
                print("\n💡 Next step: Run option 2 to evaluate authentication system")
            else:
                print("\n✅ System fully configured! Use options 4 and 5 to view reports.")

        elif choice == "0":
            print("\n👋 Goodbye!")
            break

        else:
            print("\n❌ Invalid choice. Please try again.")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n👋 Interrupted by user. Goodbye!")
        sys.exit(0)
