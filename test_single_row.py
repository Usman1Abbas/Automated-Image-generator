#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Test script to process a single row from the spreadsheet
"""

import os
import sys
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

from main import ImageGenerationSystem
from sheets_client import GoogleSheetsClient
from utils import setup_logging

# Set up logger
logger = setup_logging()

def process_single_row(row_number, force=False):
    """
    Process a single row from the spreadsheet.
    
    Args:
        row_number: The row number to process
        force: If True, process the row even if it already has content in column E
    """
    # Get spreadsheet details from environment variables
    spreadsheet_id = os.environ.get("SPREADSHEET_ID")
    credentials_file = os.environ.get("GOOGLE_CREDENTIALS", "service-account.json")
    
    if not spreadsheet_id:
        print("Error: SPREADSHEET_ID not set in environment or .env file")
        sys.exit(1)
    
    if not os.path.exists(credentials_file):
        print(f"Error: Credentials file '{credentials_file}' not found")
        sys.exit(1)
    
    # If force=True, clear the existing content in column E first
    if force:
        sheets_client = GoogleSheetsClient(credentials_file)
        cell_range = f"Sheet1!E{row_number}"
        print(f"Clearing cell {cell_range} (force mode)")
        sheets_client.update_cell(spreadsheet_id, cell_range, "")
    
    # Create a range for just the one row
    sheet_range = f"Sheet1!A{row_number}:E{row_number}"
    
    print(f"Processing row {row_number} from spreadsheet {spreadsheet_id}")
    print(f"Using credentials from {credentials_file}")
    print(f"Range: {sheet_range}")
    print(f"Force mode: {force}")
    
    try:
        # Create the system with a specific range for just one row
        system = ImageGenerationSystem(
            spreadsheet_id=spreadsheet_id,
            sheet_range=sheet_range,
            credentials_file=credentials_file
        )
        
        # Process the sheet (will only process one row)
        stats = system.process_sheet(batch_size=1)
        
        print("\nProcessing complete!")
        print(f"  - Success: {stats['success']}")
        print(f"  - Errors: {stats['error']}")
        print(f"  - Skipped: {stats['skipped']}")
        
    except Exception as e:
        print(f"Error: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    # Parse command line arguments
    import argparse
    parser = argparse.ArgumentParser(description="Process a single row from the spreadsheet")
    parser.add_argument("row_number", type=int, help="Row number to process (2 or greater)")
    parser.add_argument("--force", "-f", action="store_true", help="Force processing even if the row already has content")
    
    args = parser.parse_args()
    
    if args.row_number < 2:
        print("Error: Row number must be 2 or greater (1 is header row)")
        sys.exit(1)
    
    process_single_row(args.row_number, args.force) 