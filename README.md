# Google Sheets Image Generation System

A Python application that automates AI image generation based on Google Sheets data using the SanaSprint API.

## Features

- Connect to Google Sheets to read prompt data
- Generate AI images based on spreadsheet content
- Update the spreadsheet with generated image URLs
- Error handling and retry mechanisms
- Batch processing
- Detailed logging

## Prerequisites

- Python 3.8 or higher
- Google Sheets API credentials
- Access to the SanaSprint AI image generation API

## Installation

1. Clone this repository or download the source code.

2. Install the required Python packages:

```bash
pip install -r requirements.txt
```

3. Set up Google Sheets API credentials:

   a. Go to the [Google Cloud Console](https://console.cloud.google.com/)
   b. Create a new project
   c. Enable the Google Sheets API
   d. Create service account credentials and download the JSON file
   e. Save the credentials file as `credentials.json` in the project directory
   f. Share your target Google Sheet with the service account email address

## Configuration

You can configure the application using one of the following methods:

### Environment Variables

Set the following environment variables:

- `SPREADSHEET_ID`: The ID of your Google Sheet
- `SHEET_RANGE`: The range of cells to process (e.g., 'Sheet1!A2:E100')
- `GOOGLE_CREDENTIALS`: Path to your Google API credentials JSON file

### Command Line Arguments

Use command line arguments to override environment variables:

```bash
python cli.py --spreadsheet-id YOUR_SPREADSHEET_ID --sheet-range 'Sheet1!A2:E100' --credentials credentials.json
```

### Configuration File

Create a JSON configuration file:

```json
{
  "spreadsheet_id": "YOUR_SPREADSHEET_ID",
  "sheet_range": "Sheet1!A2:E100",
  "credentials_file": "credentials.json",
  "batch_size": 10,
  "max_retries": 3,
  "retry_delay": 5
}
```

And run the application with:

```bash
python cli.py --config config.json
```

## Input Data Structure

Your Google Sheet should have the following columns:

1. **Content Title** - The title of the content
2. **Image Style** - The desired visual style for the image
3. **Background Color** - The background color for the image
4. **Theme Description** - Additional descriptive elements for the image
5. **Image Generation** - Output column where generated images will be placed

## Usage

### Basic Usage

```bash
python cli.py --spreadsheet-id YOUR_SPREADSHEET_ID
```

### Advanced Usage

```bash
python cli.py --spreadsheet-id YOUR_SPREADSHEET_ID --sheet-range 'Sheet1!A2:E100' --batch-size 20 --max-retries 5 --retry-delay 10
```

## Error Handling

- The system will retry failed API calls up to the specified number of times
- Detailed logs are saved to the `logs` directory
- Failed rows are marked in the spreadsheet for easy identification

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Acknowledgments

- [Google Sheets API](https://developers.google.com/sheets/api)
- [SanaSprint AI](https://github.com/Efficient-Large-Model/SanaSprint) for the image generation API
- [Gradio Client](https://github.com/gradio-app/gradio-client) for the API client implementation