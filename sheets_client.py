#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Google Sheets Client Module

This module handles all interactions with the Google Sheets API.
"""

import os
import json
from typing import List, Dict, Any, Optional

from google.oauth2.service_account import Credentials
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

class GoogleSheetsClient:
    """Client for interacting with Google Sheets API."""
    
    # Define the scopes
    SCOPES = ['https://www.googleapis.com/auth/spreadsheets']
    
    def __init__(self, credentials_file: str):
        """
        Initialize the Google Sheets client.
        
        Args:
            credentials_file: Path to the service account credentials JSON file
        """
        self.credentials_file = credentials_file
        self.service = self._create_service()
    
    def _create_service(self):
        """Create and return an authorized Sheets API service instance."""
        try:
            creds = Credentials.from_service_account_file(
                self.credentials_file, scopes=self.SCOPES)
            service = build('sheets', 'v4', credentials=creds)
            return service
        except Exception as e:
            raise Exception(f"Failed to create Google Sheets service: {str(e)}")
    
    def read_range(self, spreadsheet_id: str, range_name: str) -> List[List[str]]:
        """
        Read data from a specified range in a Google Sheet.
        
        Args:
            spreadsheet_id: The ID of the spreadsheet
            range_name: The A1 notation of the range to read
            
        Returns:
            A list of rows, where each row is a list of values
        """
        try:
            result = self.service.spreadsheets().values().get(
                spreadsheetId=spreadsheet_id, range=range_name).execute()
            values = result.get('values', [])
            return values
        except HttpError as error:
            raise Exception(f"An error occurred while reading from the spreadsheet: {error}")
    
    def update_cell(self, spreadsheet_id: str, range_name: str, value: str) -> None:
        """
        Update a single cell in a Google Sheet.
        
        Args:
            spreadsheet_id: The ID of the spreadsheet
            range_name: The A1 notation of the cell to update
            value: The new value for the cell
        """
        try:
            body = {
                'values': [[value]]
            }
            result = self.service.spreadsheets().values().update(
                spreadsheetId=spreadsheet_id, range=range_name,
                valueInputOption='USER_ENTERED', body=body).execute()
            return result
        except HttpError as error:
            raise Exception(f"An error occurred while updating the spreadsheet: {error}")
    
    def batch_update(self, spreadsheet_id: str, data: List[Dict[str, Any]]) -> None:
        """
        Perform a batch update of multiple cells in a Google Sheet.
        
        Args:
            spreadsheet_id: The ID of the spreadsheet
            data: A list of dictionaries, each with 'range' and 'values' keys
        """
        try:
            body = {
                'valueInputOption': 'USER_ENTERED',
                'data': [
                    {
                        'range': item['range'],
                        'values': item['values']
                    } for item in data
                ]
            }
            result = self.service.spreadsheets().values().batchUpdate(
                spreadsheetId=spreadsheet_id, body=body).execute()
            return result
        except HttpError as error:
            raise Exception(f"An error occurred during batch update: {error}") 