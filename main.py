import os
import logging
import time
import re
from typing import List, Dict, Any, Tuple, Optional
from googleapiclient.errors import HttpError
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

from sheets_client import GoogleSheetsClient
from image_generator import SanaSprintGenerator
from utils import setup_logging

# Configure logging
logger = setup_logging()

class ImageGenerationSystem:
    """Main class to handle the image generation workflow."""
    
    def __init__(self, spreadsheet_id: str, sheet_range: str, credentials_file: str = "credentials.json"):
        """
        Initialize the image generation system.
        
        Args:
            spreadsheet_id: The ID of the Google Sheet to process
            sheet_range: The range of cells to read/write (e.g., 'Sheet1!A2:E100')
            credentials_file: Path to the Google API credentials file
        """
        self.spreadsheet_id = spreadsheet_id
        self.sheet_range = sheet_range
        self.credentials_file = credentials_file
        
        # Initialize clients
        self.sheets_client = GoogleSheetsClient(credentials_file)
        self.image_generator = SanaSprintGenerator()
        
        # Column indices (0-based)
        self.col_content_title = 0
        self.col_image_style = 1
        self.col_background_color = 2
        self.col_theme_description = 3
        self.col_image_generation = 4
        
        # Extract the starting row number from the range
        self.start_row = self._extract_start_row(sheet_range)
        
    def _extract_start_row(self, sheet_range: str) -> int:
        """
        Extract the starting row number from a sheet range.
        
        Args:
            sheet_range: The range in A1 notation (e.g., 'Sheet1!A2:E100')
            
        Returns:
            The starting row number (e.g., 2 for 'Sheet1!A2:E100')
        """
        # Use regex to extract the row number after the first column letter
        match = re.search(r'![A-Z]+(\d+):', sheet_range)
        if match:
            return int(match.group(1))
        return 2  # Default to 2 (assuming header is row 1)
    
    def _create_prompt(self, row: List[str], last_values: Dict[str, str]) -> str:
        """
        Create an image generation prompt from row data.
        
        Args:
            row: A row of data from the spreadsheet
            last_values: Dictionary with the most recent non-blank values
            
        Returns:
            Formatted prompt string
        """
        # Get current values or fall back to last non-blank values
        content_title = ""
        if len(row) > self.col_content_title and row[self.col_content_title].strip():
            content_title = row[self.col_content_title]
            last_values["content_title"] = content_title
        else:
            content_title = last_values.get("content_title", "")
        
        image_style = ""
        if len(row) > self.col_image_style and row[self.col_image_style].strip():
            image_style = row[self.col_image_style]
            last_values["image_style"] = image_style
        else:
            image_style = last_values.get("image_style", "")
        
        background_color = ""
        if len(row) > self.col_background_color and row[self.col_background_color].strip():
            background_color = row[self.col_background_color]
            last_values["background_color"] = background_color
        else:
            background_color = last_values.get("background_color", "")
        
        theme_description = ""
        if len(row) > self.col_theme_description and row[self.col_theme_description].strip():
            theme_description = row[self.col_theme_description]
            last_values["theme_description"] = theme_description
        else:
            theme_description = last_values.get("theme_description", "")
        
        # Enhanced prompt template with more detailed guidance
        prompt = f"""Create a {image_style} depiction of '{content_title}', set against a {background_color} background.
The overall mood and narrative should convey {theme_description}.
Enhance with:
• Lighting: soft natural lighting with clarity
• Composition: balanced composition with clear focal point
• Technical finish: high resolution with clean details
• Camera & style notes: professional quality with vibrant colors"""
        
        return prompt
    
    def process_sheet(self, batch_size: int = 10, max_retries: int = 3, retry_delay: int = 5) -> Dict[str, int]:
        """
        Process the entire spreadsheet and generate images.
        
        Args:
            batch_size: Number of rows to process in one batch
            max_retries: Maximum number of retries for API calls
            retry_delay: Delay in seconds between retries
            
        Returns:
            Statistics about the processing results
        """
        logger.info(f"Starting to process spreadsheet {self.spreadsheet_id}")
        
        # Get spreadsheet data
        try:
            rows = self.sheets_client.read_range(self.spreadsheet_id, self.sheet_range)
        except Exception as e:
            logger.error(f"Failed to read spreadsheet: {str(e)}")
            return {"error": 1, "success": 0, "skipped": 0}
            
        if not rows:
            logger.warning("No data found in the specified range.")
            return {"error": 0, "success": 0, "skipped": 0}
            
        # Track statistics
        stats = {"success": 0, "error": 0, "skipped": 0}
        updates = []
        
        # Dictionary to store the most recent non-blank values
        last_values = {
            "content_title": "",
            "image_style": "",
            "background_color": "",
            "theme_description": ""
        }
        
        # Process rows in batches
        for i, row in enumerate(rows):
            # Calculate the actual row number in the spreadsheet
            actual_row_number = self.start_row + i
            
            # Skip rows that already have an image
            if len(row) > self.col_image_generation and row[self.col_image_generation]:
                logger.info(f"Row {actual_row_number} already has an image, skipping.")
                
                # Still update last_values for future rows
                if len(row) > self.col_content_title and row[self.col_content_title].strip():
                    last_values["content_title"] = row[self.col_content_title]
                if len(row) > self.col_image_style and row[self.col_image_style].strip():
                    last_values["image_style"] = row[self.col_image_style]
                if len(row) > self.col_background_color and row[self.col_background_color].strip():
                    last_values["background_color"] = row[self.col_background_color]
                if len(row) > self.col_theme_description and row[self.col_theme_description].strip():
                    last_values["theme_description"] = row[self.col_theme_description]
                
                stats["skipped"] += 1
                continue
                
            # Create prompt, inheriting values from previous rows if needed
            prompt = self._create_prompt(row, last_values)
            logger.info(f"Processing row {actual_row_number} with prompt: {prompt}")
            
            # Print the prompt clearly for verification
            print(f"\n{'='*60}")
            print(f"ROW {actual_row_number} PROMPT:")
            print(f"{'='*60}")
            print(f"{prompt}")
            print(f"{'='*60}\n")
            
            # Skip if we have no meaningful prompt content after inheriting values
            if prompt.strip() == "illustration of '' on a  background, ":
                logger.warning(f"Row {actual_row_number} has no meaningful content even after inheriting values, skipping.")
                stats["skipped"] += 1
                continue
            
            # Generate image with retries
            image_url = None
            retry_count = 0
            
            while retry_count < max_retries and not image_url:
                try:
                    image_url = self.image_generator.generate_image(prompt)
                    logger.info(f"Generated image for row {actual_row_number}")
                    stats["success"] += 1
                except Exception as e:
                    retry_count += 1
                    logger.error(f"Error generating image (attempt {retry_count}/{max_retries}): {str(e)}")
                    if retry_count < max_retries:
                        logger.info(f"Retrying in {retry_delay} seconds...")
                        time.sleep(retry_delay)
                    else:
                        logger.error(f"Failed to generate image after {max_retries} attempts")
                        image_url = "ERROR: Image generation failed"
                        stats["error"] += 1
            
            # Prepare update - Use actual_row_number instead of i+2
            row_idx = actual_row_number
            col_idx = self.col_image_generation + 1  # +1 for 1-indexing
            updates.append({
                "range": f"{self.sheet_range.split('!')[0]}!{chr(64+col_idx)}{row_idx}",
                "values": [[image_url]]
            })
            
            # Update in batches
            if len(updates) >= batch_size or i == len(rows) - 1:
                try:
                    self.sheets_client.batch_update(self.spreadsheet_id, updates)
                    logger.info(f"Updated {len(updates)} rows in the spreadsheet")
                    updates = []
                except HttpError as e:
                    logger.error(f"Error updating spreadsheet: {str(e)}")
                    stats["error"] += len(updates)
                    updates = []
        
        logger.info(f"Processing complete. Stats: {stats}")
        return stats

def main():
    """Main entry point of the application."""
    # Set these values from environment variables or config file in a real application
    SPREADSHEET_ID = os.environ.get("SPREADSHEET_ID", "your_spreadsheet_id_here")
    SHEET_RANGE = os.environ.get("SHEET_RANGE", "Sheet1!A2:E100")
    CREDENTIALS_FILE = os.environ.get("GOOGLE_CREDENTIALS", "credentials.json")
    
    # Create and run the system
    system = ImageGenerationSystem(
        spreadsheet_id=SPREADSHEET_ID,
        sheet_range=SHEET_RANGE,
        credentials_file=CREDENTIALS_FILE
    )
    
    stats = system.process_sheet(batch_size=10)
    print(f"Processing complete: {stats['success']} successful, {stats['error']} errors, {stats['skipped']} skipped")

if __name__ == "__main__":
    main() 