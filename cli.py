#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Command Line Interface for Google Sheets Image Generation System

This script provides a command-line interface to run the image generation system.
"""

import os
import sys
import argparse
import json
from typing import Dict, Any
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

from main import ImageGenerationSystem
from utils import setup_logging, validate_spreadsheet_id

# Set up logger
logger = setup_logging()

def parse_args():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(
        description="Google Sheets Image Generation System",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter
    )
    
    parser.add_argument(
        "--spreadsheet-id",
        dest="spreadsheet_id",
        type=str,
        help="Google Sheets spreadsheet ID",
        required=False,
        default=os.environ.get("SPREADSHEET_ID")
    )
    
    parser.add_argument(
        "--sheet-range",
        dest="sheet_range",
        type=str,
        help="Sheet range in A1 notation (e.g., 'Sheet1!A2:E100')",
        required=False,
        default=os.environ.get("SHEET_RANGE", "Sheet1!A2:E100")
    )
    
    parser.add_argument(
        "--credentials",
        dest="credentials_file",
        type=str,
        help="Path to Google API credentials JSON file",
        required=False,
        default=os.environ.get("GOOGLE_CREDENTIALS", "credentials.json")
    )
    
    parser.add_argument(
        "--batch-size",
        dest="batch_size",
        type=int,
        help="Number of rows to process in one batch",
        default=10
    )
    
    parser.add_argument(
        "--max-retries",
        dest="max_retries",
        type=int,
        help="Maximum number of retries for API calls",
        default=3
    )
    
    parser.add_argument(
        "--retry-delay",
        dest="retry_delay",
        type=int,
        help="Delay in seconds between retries",
        default=5
    )
    
    parser.add_argument(
        "--config",
        dest="config_file",
        type=str,
        help="Path to JSON configuration file",
        default=None
    )
    
    return parser.parse_args()

def load_config(config_file: str) -> Dict[str, Any]:
    """
    Load configuration from a JSON file.
    
    Args:
        config_file: Path to the JSON configuration file
        
    Returns:
        Dictionary with configuration values
    """
    if not os.path.exists(config_file):
        logger.error(f"Config file not found: {config_file}")
        return {}
        
    try:
        with open(config_file, 'r') as f:
            config = json.load(f)
        return config
    except Exception as e:
        logger.error(f"Error loading config file: {str(e)}")
        return {}

def main():
    """Main entry point for the CLI."""
    args = parse_args()
    
    # Load config file if provided
    config = {}
    if args.config_file:
        config = load_config(args.config_file)
    
    # Override config with command line arguments
    spreadsheet_id = args.spreadsheet_id or config.get("spreadsheet_id")
    sheet_range = args.sheet_range or config.get("sheet_range", "Sheet1!A2:E100")
    credentials_file = args.credentials_file or config.get("credentials_file", "credentials.json")
    batch_size = args.batch_size or config.get("batch_size", 10)
    max_retries = args.max_retries or config.get("max_retries", 3)
    retry_delay = args.retry_delay or config.get("retry_delay", 5)
    
    # Validate spreadsheet ID
    if not spreadsheet_id:
        logger.error("Spreadsheet ID is required. Provide it via --spreadsheet-id argument, "
                     "SPREADSHEET_ID environment variable, or config file.")
        sys.exit(1)
        
    if not validate_spreadsheet_id(spreadsheet_id):
        logger.error(f"Invalid spreadsheet ID: {spreadsheet_id}")
        sys.exit(1)
    
    # Check if credentials file exists
    if not os.path.exists(credentials_file):
        logger.error(f"Credentials file not found: {credentials_file}")
        sys.exit(1)
    
    # Create and run the system
    try:
        system = ImageGenerationSystem(
            spreadsheet_id=spreadsheet_id,
            sheet_range=sheet_range,
            credentials_file=credentials_file
        )
        
        stats = system.process_sheet(
            batch_size=batch_size,
            max_retries=max_retries,
            retry_delay=retry_delay
        )
        
        logger.info(f"Processing complete: {stats}")
        print(f"Processing complete: {stats['success']} successful, {stats['error']} errors, {stats['skipped']} skipped")
        
    except Exception as e:
        logger.error(f"Error running image generation system: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main() 