#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Quickstart script for Google Sheets Image Generation System

This script provides a simplified way to start using the image generation system.
It guides the user through basic setup and runs a sample process.
"""

import os
import sys
import json
import shutil
from pathlib import Path

# Check if Python version is compatible
if sys.version_info < (3, 8):
    print("Error: Python 3.8 or higher is required.")
    sys.exit(1)

# Try to import required packages
try:
    from dotenv import load_dotenv
except ImportError:
    print("Installing required packages...")
    import subprocess
    subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"])
    from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Import the system after ensuring dependencies are installed
from main import ImageGenerationSystem
from utils import setup_logging, validate_spreadsheet_id

# Set up logger
logger = setup_logging()

def check_credentials():
    """Check if credentials file exists, and guide the user to create one if not."""
    creds_file = os.environ.get("GOOGLE_CREDENTIALS", "credentials.json")
    
    if not os.path.exists(creds_file):
        print("Google API credentials file not found!")
        print("\nTo set up Google Sheets API credentials:")
        print("1. Go to https://console.cloud.google.com/")
        print("2. Create a new project")
        print("3. Enable the Google Sheets API")
        print("4. Create service account credentials")
        print("5. Download the JSON key file")
        print(f"6. Save it as '{creds_file}' in this directory")
        print("\nAfter you've done this, run this script again.")
        return False
    
    print(f"Credentials file found: {creds_file}")
    return True

def check_spreadsheet_id():
    """Check if spreadsheet ID is set, and guide the user to set one if not."""
    spreadsheet_id = os.environ.get("SPREADSHEET_ID")
    
    if not spreadsheet_id:
        print("Spreadsheet ID not found!")
        
        # Ask user for spreadsheet ID
        spreadsheet_id = input("\nEnter your Google Sheets ID: ").strip()
        
        if not validate_spreadsheet_id(spreadsheet_id):
            print("Invalid spreadsheet ID format.")
            return False
        
        # Save to .env file
        with open(".env", "a+") as f:
            f.write(f"\nSPREADSHEET_ID={spreadsheet_id}")
        
        print("Spreadsheet ID saved to .env file.")
        
        # Remind user to share the spreadsheet
        creds_file = os.environ.get("GOOGLE_CREDENTIALS", "credentials.json")
        if os.path.exists(creds_file):
            try:
                with open(creds_file, "r") as f:
                    creds_data = json.load(f)
                    client_email = creds_data.get("client_email")
                    if client_email:
                        print(f"\nIMPORTANT: You need to share your Google Sheet with:")
                        print(f"  {client_email}")
            except Exception as e:
                print(f"Couldn't read credentials file: {str(e)}")
    
    else:
        print(f"Spreadsheet ID found: {spreadsheet_id}")
    
    return True

def setup_env_file():
    """Set up the .env file if it doesn't exist."""
    if not os.path.exists(".env"):
        if os.path.exists("env.example"):
            shutil.copy("env.example", ".env")
            print("Created .env file from template.")
        else:
            with open(".env", "w") as f:
                f.write("# Google Sheets Configuration\n")
                f.write("SPREADSHEET_ID=\n")
                f.write("SHEET_RANGE=Sheet1!A2:E100\n")
                f.write("GOOGLE_CREDENTIALS=credentials.json\n")
            print("Created basic .env file.")

def main():
    """Main function to guide the user through setup and run a sample process."""
    print("=" * 60)
    print("Google Sheets Image Generation System - Quickstart")
    print("=" * 60)
    
    # Set up environment file
    setup_env_file()
    
    # Reload environment variables
    load_dotenv(override=True)
    
    # Check credentials and spreadsheet ID
    if not check_credentials() or not check_spreadsheet_id():
        return
    
    # Confirm sheet range
    sheet_range = os.environ.get("SHEET_RANGE", "Sheet1!A2:E100")
    print(f"\nCurrent sheet range: {sheet_range}")
    change_range = input("Do you want to change the sheet range? (y/N): ").strip().lower()
    
    if change_range == "y":
        new_range = input("Enter new sheet range (e.g., 'Sheet1!A2:E100'): ").strip()
        if new_range:
            sheet_range = new_range
            # Update .env file
            with open(".env", "r") as f:
                lines = f.readlines()
            
            with open(".env", "w") as f:
                for line in lines:
                    if line.startswith("SHEET_RANGE="):
                        f.write(f"SHEET_RANGE={sheet_range}\n")
                    else:
                        f.write(line)
    
    # Confirm running
    print("\nReady to process spreadsheet with the following settings:")
    print(f"  - Spreadsheet ID: {os.environ.get('SPREADSHEET_ID')}")
    print(f"  - Sheet Range: {sheet_range}")
    print(f"  - Credentials: {os.environ.get('GOOGLE_CREDENTIALS', 'credentials.json')}")
    
    confirm = input("\nStart processing? (Y/n): ").strip().lower()
    if confirm == "n":
        print("Exiting without processing. Run 'python cli.py' when you're ready.")
        return
    
    try:
        # Create and run the system
        system = ImageGenerationSystem(
            spreadsheet_id=os.environ.get("SPREADSHEET_ID"),
            sheet_range=sheet_range,
            credentials_file=os.environ.get("GOOGLE_CREDENTIALS", "credentials.json")
        )
        
        batch_size = int(os.environ.get("BATCH_SIZE", "10"))
        
        print("\nProcessing spreadsheet...")
        stats = system.process_sheet(batch_size=batch_size)
        
        print("\nProcessing complete!")
        print(f"  - Success: {stats['success']}")
        print(f"  - Errors: {stats['error']}")
        print(f"  - Skipped: {stats['skipped']}")
        
        print("\nTip: You can use 'python cli.py' with additional options for more control.")
        print("     See README.md for full documentation.")
        
    except Exception as e:
        print(f"\nError processing spreadsheet: {str(e)}")
        print("Please check your configuration and try again.")

if __name__ == "__main__":
    main() 