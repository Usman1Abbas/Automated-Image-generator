#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Script to clear an error from a specific row and retry image generation
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

def clear_and_retry_row(row_number):
    """Clear error from a row and retry image generation."""
    # Get spreadsheet details from environment variables
    spreadsheet_id = os.environ.get("SPREADSHEET_ID")
    credentials_file = os.environ.get("GOOGLE_CREDENTIALS", "service-account.json")
    
    if not spreadsheet_id:
        print("Error: SPREADSHEET_ID not set in environment or .env file")
        sys.exit(1)
    
    if not os.path.exists(credentials_file):
        print(f"Error: Credentials file '{credentials_file}' not found")
        sys.exit(1)
    
    # Create the sheet client
    sheets_client = GoogleSheetsClient(credentials_file)
    
    # Define the range for the specific cell (column E, row number)
    cell_range = f"Sheet1!E{row_number}"
    
    print(f"Clearing error from row {row_number}, column E (Image Generation)")
    print(f"Spreadsheet ID: {spreadsheet_id}")
    
    try:
        # Clear the error message by setting the cell to an empty string
        sheets_client.update_cell(spreadsheet_id, cell_range, "")
        print(f"Successfully cleared cell {cell_range}")
        
        # Now retry processing this row
        sheet_range = f"Sheet1!A{row_number}:E{row_number}"
        print(f"\nRetrying image generation for row {row_number}")
        print(f"Range: {sheet_range}")
        
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
    # Check if a row number was provided
    if len(sys.argv) > 1:
        try:
            row_number = int(sys.argv[1])
            if row_number < 2:
                print("Error: Row number must be 2 or greater (1 is header row)")
                sys.exit(1)
            clear_and_retry_row(row_number)
        except ValueError:
            print("Error: Row number must be an integer")
            sys.exit(1)
    else:
        print("Usage: python clear_and_retry.py ROW_NUMBER")
        print("Example: python clear_and_retry.py 2")
        sys.exit(1) 