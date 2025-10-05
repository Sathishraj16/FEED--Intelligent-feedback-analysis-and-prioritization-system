"""
CSV Importer for App Store Reviews
Imports CSV files containing App Store reviews into the FEED system.
"""

import pandas as pd
import os
from pathlib import Path
from typing import Dict, List, Any, Optional
from supabase import create_client, Client
from dotenv import load_dotenv
from datetime import datetime
import json

# Import NLP utilities
from nlp import (
    normalize_text,
    sha256_hex,
    sentiment_compound,
    score_urgency,
    score_impact,
    score_priority,
    simple_tags,
)

# Load environment variables
BASE_DIR = Path(__file__).resolve().parent
ENV_PATH = BASE_DIR / ".env"
load_dotenv(dotenv_path=ENV_PATH, override=True)

# Initialize Supabase client
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_SERVICE_ROLE = os.getenv("SUPABASE_SERVICE_ROLE")

if not SUPABASE_URL or not SUPABASE_SERVICE_ROLE:
    raise ValueError("Missing SUPABASE_URL or SUPABASE_SERVICE_ROLE in environment variables")

supabase: Client = create_client(SUPABASE_URL, SUPABASE_SERVICE_ROLE)

def _compute_signals_for_text(text: str) -> Dict[str, Any]:
    """Compute NLP signals for a given text (same as main.py)."""
    normalized = normalize_text(text)
    text_hash = sha256_hex(normalized)
    sentiment = sentiment_compound(normalized)
    urgency = score_urgency(normalized)
    impact = score_impact(normalized)
    priority = score_priority(normalized, sentiment, urgency, impact)
    tags = simple_tags(normalized)
    
    return {
        "normalized_text": normalized,
        "text_hash": text_hash,
        "sentiment": sentiment,
        "urgency": urgency,
        "impact": impact,
        "priority": priority,
        "tags": tags,
    }

class AppStoreReviewImporter:
    """Handles importing App Store reviews from CSV files."""
    
    def __init__(self):
        self.supabase = supabase
        self.imported_count = 0
        self.skipped_count = 0
        self.error_count = 0
    
    def detect_csv_format(self, df: pd.DataFrame) -> Dict[str, str]:
        """
        Auto-detect the CSV format and map columns to our expected fields.
        Returns a mapping of our fields to CSV column names.
        """
        columns = [col.lower().strip() for col in df.columns]
        mapping = {}
        
        # Common patterns for review text
        review_patterns = ['review', 'content', 'text', 'comment', 'feedback', 'body', 'message']
        for pattern in review_patterns:
            matches = [col for col in columns if pattern in col]
            if matches:
                mapping['review_text'] = matches[0]
                break
        
        # Common patterns for rating
        rating_patterns = ['rating', 'score', 'stars', 'star']
        for pattern in rating_patterns:
            matches = [col for col in columns if pattern in col]
            if matches:
                mapping['rating'] = matches[0]
                break
        
        # Common patterns for title
        title_patterns = ['title', 'subject', 'headline', 'summary']
        for pattern in title_patterns:
            matches = [col for col in columns if pattern in col]
            if matches:
                mapping['title'] = matches[0]
                break
        
        # Common patterns for date
        date_patterns = ['date', 'created', 'submitted', 'time', 'timestamp']
        for pattern in date_patterns:
            matches = [col for col in columns if pattern in col]
            if matches:
                mapping['date'] = matches[0]
                break
        
        # Common patterns for app version
        version_patterns = ['version', 'app_version', 'build']
        for pattern in version_patterns:
            matches = [col for col in columns if pattern in col]
            if matches:
                mapping['app_version'] = matches[0]
                break
        
        # Common patterns for reviewer info
        reviewer_patterns = ['reviewer', 'user', 'author', 'name']
        for pattern in reviewer_patterns:
            matches = [col for col in columns if pattern in col]
            if matches:
                mapping['reviewer'] = matches[0]
                break
        
        return mapping
    
    def process_review(self, row: pd.Series, column_mapping: Dict[str, str]) -> Optional[Dict[str, Any]]:
        """Process a single review row and return the data for insertion."""
        try:
            # Extract review text (required)
            review_text = ""
            if 'review_text' in column_mapping:
                review_text = str(row[column_mapping['review_text']]).strip()
            
            # If no review text found, try title
            if not review_text and 'title' in column_mapping:
                review_text = str(row[column_mapping['title']]).strip()
            
            # Skip if no meaningful text
            if not review_text or review_text.lower() in ['nan', 'none', '']:
                return None
            
            # Combine title and review if both exist
            title = ""
            if 'title' in column_mapping:
                title = str(row[column_mapping['title']]).strip()
                if title and title.lower() not in ['nan', 'none', ''] and title != review_text:
                    review_text = f"{title}. {review_text}"
            
            # Extract additional metadata
            metadata = {}
            
            if 'rating' in column_mapping:
                try:
                    rating = float(row[column_mapping['rating']])
                    metadata['rating'] = rating
                except (ValueError, TypeError):
                    pass
            
            if 'date' in column_mapping:
                try:
                    date_str = str(row[column_mapping['date']])
                    if date_str and date_str.lower() not in ['nan', 'none']:
                        metadata['review_date'] = date_str
                except:
                    pass
            
            if 'app_version' in column_mapping:
                try:
                    version = str(row[column_mapping['app_version']])
                    if version and version.lower() not in ['nan', 'none']:
                        metadata['app_version'] = version
                except:
                    pass
            
            if 'reviewer' in column_mapping:
                try:
                    reviewer = str(row[column_mapping['reviewer']])
                    if reviewer and reviewer.lower() not in ['nan', 'none']:
                        metadata['reviewer'] = reviewer
                except:
                    pass
            
            # Compute NLP signals
            signals = _compute_signals_for_text(review_text)
            
            # Prepare the row for insertion
            row_data = {
                "raw_text": review_text,
                "source": "app_store_csv",
                "metadata": json.dumps(metadata) if metadata else None,
                "created_at": datetime.utcnow().isoformat(),
                **signals,
            }
            
            return row_data
            
        except Exception as e:
            print(f"Error processing row: {e}")
            return None
    
    def import_csv(self, csv_path: str, batch_size: int = 100) -> Dict[str, int]:
        """
        Import App Store reviews from a CSV file.
        
        Args:
            csv_path: Path to the CSV file
            batch_size: Number of rows to process in each batch
            
        Returns:
            Dictionary with import statistics
        """
        print(f"Starting import from: {csv_path}")
        
        try:
            # Read CSV file
            df = pd.read_csv(csv_path)
            print(f"Loaded CSV with {len(df)} rows and columns: {list(df.columns)}")
            
            # Auto-detect column mapping
            column_mapping = self.detect_csv_format(df)
            print(f"Detected column mapping: {column_mapping}")
            
            if 'review_text' not in column_mapping:
                raise ValueError("Could not detect review text column. Please ensure your CSV has a column containing review text.")
            
            # Process rows in batches
            total_rows = len(df)
            processed_rows = []
            
            for index, row in df.iterrows():
                processed_row = self.process_review(row, column_mapping)
                if processed_row:
                    processed_rows.append(processed_row)
                else:
                    self.skipped_count += 1
                
                # Insert batch when it reaches batch_size
                if len(processed_rows) >= batch_size:
                    self._insert_batch(processed_rows)
                    processed_rows = []
                
                # Progress update
                if (index + 1) % 100 == 0:
                    print(f"Processed {index + 1}/{total_rows} rows...")
            
            # Insert remaining rows
            if processed_rows:
                self._insert_batch(processed_rows)
            
            print(f"Import completed!")
            print(f"Imported: {self.imported_count}")
            print(f"Skipped: {self.skipped_count}")
            print(f"Errors: {self.error_count}")
            
            return {
                "imported": self.imported_count,
                "skipped": self.skipped_count,
                "errors": self.error_count,
                "total_processed": total_rows
            }
            
        except Exception as e:
            print(f"Error during import: {e}")
            raise
    
    def _insert_batch(self, rows: List[Dict[str, Any]]):
        """Insert a batch of rows into the database."""
        try:
            # Check for duplicates based on text_hash
            hashes = [row['text_hash'] for row in rows]
            existing_resp = self.supabase.table("feedback").select("text_hash").in_("text_hash", hashes).execute()
            existing_hashes = {item['text_hash'] for item in existing_resp.data}
            
            # Filter out duplicates
            new_rows = [row for row in rows if row['text_hash'] not in existing_hashes]
            
            if new_rows:
                resp = self.supabase.table("feedback").insert(new_rows).execute()
                self.imported_count += len(new_rows)
                print(f"Inserted {len(new_rows)} new rows (skipped {len(rows) - len(new_rows)} duplicates)")
            else:
                self.skipped_count += len(rows)
                print(f"Skipped {len(rows)} duplicate rows")
                
        except Exception as e:
            print(f"Error inserting batch: {e}")
            self.error_count += len(rows)

def main():
    """Command line interface for CSV import."""
    import argparse
    
    parser = argparse.ArgumentParser(description="Import App Store reviews from CSV")
    parser.add_argument("csv_file", help="Path to the CSV file")
    parser.add_argument("--batch-size", type=int, default=100, help="Batch size for processing (default: 100)")
    
    args = parser.parse_args()
    
    if not os.path.exists(args.csv_file):
        print(f"Error: CSV file not found: {args.csv_file}")
        return
    
    importer = AppStoreReviewImporter()
    try:
        stats = importer.import_csv(args.csv_file, args.batch_size)
        print(f"\nImport Summary:")
        print(f"Total processed: {stats['total_processed']}")
        print(f"Successfully imported: {stats['imported']}")
        print(f"Skipped (duplicates/invalid): {stats['skipped']}")
        print(f"Errors: {stats['errors']}")
    except Exception as e:
        print(f"Import failed: {e}")

if __name__ == "__main__":
    main()
