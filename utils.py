#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Utilities Module

This module provides helper functions and utilities for the image generation system.
"""

import os
import logging
import sys
from datetime import datetime

def setup_logging(log_level=logging.INFO, log_file=None):
    """
    Set up logging configuration.
    
    Args:
        log_level: Logging level (default: INFO)
        log_file: Path to log file (default: None, which logs to console only)
        
    Returns:
        Logger instance
    """
    # Create logs directory if it doesn't exist and log_file is specified
    if log_file:
        os.makedirs(os.path.dirname(log_file), exist_ok=True)
    
    # If no log file is specified, create one with timestamp
    if not log_file:
        os.makedirs('logs', exist_ok=True)
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        log_file = f"logs/image_generation_{timestamp}.log"
    
    # Configure logger
    logger = logging.getLogger()
    logger.setLevel(log_level)
    
    # Clear any existing handlers
    logger.handlers = []
    
    # Create console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(log_level)
    console_format = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
    console_handler.setFormatter(console_format)
    logger.addHandler(console_handler)
    
    # Create file handler if log_file is specified
    if log_file:
        file_handler = logging.FileHandler(log_file)
        file_handler.setLevel(log_level)
        file_format = logging.Formatter('%(asctime)s - %(levelname)s - %(name)s - %(message)s')
        file_handler.setFormatter(file_format)
        logger.addHandler(file_handler)
    
    return logger

def validate_spreadsheet_id(spreadsheet_id):
    """
    Validate that the spreadsheet ID is in the correct format.
    
    Args:
        spreadsheet_id: The spreadsheet ID to validate
        
    Returns:
        bool: True if valid, False otherwise
    """
    if not spreadsheet_id or not isinstance(spreadsheet_id, str):
        return False
    
    # Google Sheets IDs are typically around 44 characters
    if len(spreadsheet_id) < 20:
        return False
    
    return True

def parse_range(range_str):
    """
    Parse a range string in A1 notation (e.g., 'Sheet1!A1:E10').
    
    Args:
        range_str: Range string in A1 notation
        
    Returns:
        tuple: (sheet_name, start_col, start_row, end_col, end_row)
    """
    if '!' not in range_str:
        raise ValueError(f"Invalid range format: {range_str}")
    
    sheet_name, cell_range = range_str.split('!')
    
    if ':' not in cell_range:
        # Single cell
        col, row = split_col_row(cell_range)
        return sheet_name, col, row, col, row
    
    start, end = cell_range.split(':')
    start_col, start_row = split_col_row(start)
    end_col, end_row = split_col_row(end)
    
    return sheet_name, start_col, start_row, end_col, end_row

def split_col_row(cell_ref):
    """
    Split a cell reference (e.g., 'A1') into column and row.
    
    Args:
        cell_ref: Cell reference string
        
    Returns:
        tuple: (column, row)
    """
    for i, c in enumerate(cell_ref):
        if c.isdigit():
            return cell_ref[:i], int(cell_ref[i:])
    
    return cell_ref, None  # No row number found

def get_column_letter(col_idx):
    """
    Convert a column index to a column letter (e.g., 1 -> A, 27 -> AA).
    
    Args:
        col_idx: 1-based column index
        
    Returns:
        str: Column letter(s)
    """
    result = ""
    while col_idx > 0:
        col_idx, remainder = divmod(col_idx - 1, 26)
        result = chr(65 + remainder) + result
    return result 