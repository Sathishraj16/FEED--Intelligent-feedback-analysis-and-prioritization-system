# CSV Import Guide for FEED

This guide explains how to import App Store Reviews (or any feedback data) into your FEED system using CSV files.

## Overview

The FEED system now supports importing feedback data from CSV files, with automatic column detection and intelligent data processing. Each imported review is analyzed for sentiment, urgency, impact, and priority using the same NLP pipeline as manual feedback entries.

## Features

- **Auto-detection of CSV columns** - No need to rename your columns
- **Duplicate prevention** - Automatically skips duplicate reviews based on content hash
- **Batch processing** - Handles large CSV files efficiently
- **Rich metadata support** - Preserves ratings, dates, app versions, and reviewer info
- **Real-time progress tracking** - See import statistics and status
- **Web interface** - Upload CSV files directly through the dashboard
- **Command-line support** - Import CSV files via Python script

## Supported CSV Formats

The system automatically detects columns based on common naming patterns:

### Required Columns
- **Review Text**: `review`, `content`, `text`, `comment`, `feedback`, `body`, `message`

### Optional Columns
- **Rating**: `rating`, `score`, `stars`, `star`
- **Title**: `title`, `subject`, `headline`, `summary`
- **Date**: `date`, `created`, `submitted`, `time`, `timestamp`
- **App Version**: `version`, `app_version`, `build`
- **Reviewer**: `reviewer`, `user`, `author`, `name`

### Example CSV Structure

```csv
title,review,rating,date,app_version,reviewer
"Great app!","I love this app! It works perfectly.",5,2024-01-15,2.1.0,user123
"Needs improvement","The app crashes frequently.",2,2024-01-14,2.1.0,reviewer456
```

## Import Methods

### 1. Web Interface (Recommended)

1. Navigate to `/feed` in your FEED dashboard
2. Find the "Import App Store Reviews" section at the top
3. Click "Upload a CSV file" or drag and drop your CSV
4. Monitor the upload progress and view import statistics
5. Check the "Refresh Status" to see updated import counts

### 2. Command Line

```bash
# Navigate to the server directory
cd server

# Install dependencies (if not already installed)
pip install -r requirements.txt

# Import a CSV file
python csv_importer.py path/to/your/reviews.csv

# Import with custom batch size
python csv_importer.py path/to/your/reviews.csv --batch-size 50
```

### 3. Test with Sample Data

```bash
# Test the import functionality with sample data
cd server
python test_csv_import.py
```

## API Endpoints

### Upload CSV File
```
POST /upload-csv
Content-Type: multipart/form-data

Form data:
- file: CSV file to upload
```

**Response:**
```json
{
  "success": true,
  "message": "Successfully imported 10 reviews",
  "stats": {
    "imported": 10,
    "skipped": 2,
    "errors": 0,
    "total_processed": 12
  },
  "filename": "app_store_reviews.csv"
}
```

### Get Import Status
```
GET /import-status
```

**Response:**
```json
{
  "total_feedback": 150,
  "app_store_reviews": 100,
  "recent_imports_24h": 25,
  "other_sources": 50
}
```

## Data Processing

Each imported review goes through the following processing pipeline:

1. **Text Normalization** - Cleans and standardizes the text
2. **Sentiment Analysis** - Calculates sentiment score (-1 to 1)
3. **Urgency Scoring** - Determines how urgent the feedback is (0 to 1)
4. **Impact Assessment** - Evaluates potential business impact (0 to 1)
5. **Priority Calculation** - Combines all factors for overall priority (0 to 1)
6. **Tag Extraction** - Automatically generates relevant tags
7. **Duplicate Detection** - Prevents importing the same review twice

## Metadata Preservation

The system preserves additional metadata from your CSV:

- **Rating** - Stored as `metadata.rating`
- **Review Date** - Stored as `metadata.review_date`
- **App Version** - Stored as `metadata.app_version`
- **Reviewer** - Stored as `metadata.reviewer`

This metadata is available for filtering and analysis in the dashboard.

## Best Practices

### CSV Preparation
- Ensure your CSV has a header row with column names
- Use UTF-8 encoding to support international characters
- Keep review text in a single column (don't split across multiple columns)
- Remove any completely empty rows

### File Size Considerations
- The system processes files in batches (default: 100 rows per batch)
- Large files (>10MB) may take several minutes to process
- Consider splitting very large files (>100k rows) into smaller chunks

### Data Quality
- Remove test data or spam reviews before importing
- Ensure review text is meaningful (avoid empty or "N/A" entries)
- Verify date formats are consistent

## Troubleshooting

### Common Issues

**"Could not detect review text column"**
- Ensure your CSV has a column containing review text
- Check that the column name matches one of the supported patterns
- Verify the CSV has a proper header row

**"Upload failed with status 413"**
- File is too large for upload
- Split the file into smaller chunks
- Use command-line import for very large files

**"Duplicate reviews skipped"**
- Reviews with identical text content are automatically skipped
- This is normal behavior to prevent duplicates
- Check the import statistics for details

**"Import status shows 0 recent imports"**
- Check that the server is running and accessible
- Verify the database connection is working
- Look at server logs for error messages

### Getting Help

1. Check the server logs for detailed error messages
2. Verify your `.env` file has correct database credentials
3. Test with the sample CSV file first
4. Use the command-line import for debugging

## Sample Data

A sample CSV file is included at `sample_app_store_reviews.csv` with 10 example reviews. Use this to test the import functionality before importing your own data.

## Integration with FEED Dashboard

Once imported, App Store reviews appear in the FEED dashboard alongside other feedback:

- **Priority List** - Shows highest priority reviews first
- **Sentiment Analysis** - Tracks sentiment trends over time
- **Impact/Urgency Chart** - Visualizes review distribution
- **KPI Dashboard** - Includes imported reviews in metrics
- **Action Analysis** - Generates next steps and team assignments

Reviews imported from CSV are marked with source `app_store_csv` for easy filtering and reporting.

## Security Considerations

- CSV files are processed server-side and temporarily stored
- Temporary files are automatically cleaned up after processing
- No sensitive data is logged during import
- All imported data follows the same security model as manual entries

## Performance

- Typical import speed: 100-500 reviews per second
- Memory usage scales with batch size
- Database performance depends on existing data volume
- Large imports may temporarily increase server load

For optimal performance with large datasets, consider importing during off-peak hours.
