#!/usr/bin/env python3
"""
Test script for CSV import functionality
"""

import os
import sys
from pathlib import Path

# Add the server directory to the Python path
sys.path.insert(0, str(Path(__file__).parent))

from csv_importer import AppStoreReviewImporter

def test_csv_import():
    """Test the CSV import with the sample file."""
    
    # Path to the sample CSV file
    sample_csv = Path(__file__).parent.parent / "sample_app_store_reviews.csv"
    
    if not sample_csv.exists():
        print(f"Error: Sample CSV file not found at {sample_csv}")
        return False
    
    print(f"Testing CSV import with file: {sample_csv}")
    print("-" * 50)
    
    try:
        # Create importer instance
        importer = AppStoreReviewImporter()
        
        # Import the CSV
        stats = importer.import_csv(str(sample_csv), batch_size=5)
        
        print("\n" + "=" * 50)
        print("IMPORT COMPLETED SUCCESSFULLY!")
        print("=" * 50)
        print(f"Total processed: {stats['total_processed']}")
        print(f"Successfully imported: {stats['imported']}")
        print(f"Skipped (duplicates/invalid): {stats['skipped']}")
        print(f"Errors: {stats['errors']}")
        
        if stats['imported'] > 0:
            print(f"\n✅ Successfully imported {stats['imported']} App Store reviews!")
            print("You can now view them in the FEED dashboard.")
        else:
            print("\n⚠️  No new reviews were imported (they may already exist in the database)")
        
        return True
        
    except Exception as e:
        print(f"\n❌ Import failed: {e}")
        return False

if __name__ == "__main__":
    print("FEED CSV Import Test")
    print("=" * 50)
    
    # Check if environment variables are set
    if not os.getenv("SUPABASE_URL") or not os.getenv("SUPABASE_SERVICE_ROLE"):
        print("❌ Error: Missing environment variables!")
        print("Please ensure SUPABASE_URL and SUPABASE_SERVICE_ROLE are set in your .env file")
        sys.exit(1)
    
    success = test_csv_import()
    
    if success:
        print("\n🎉 Test completed successfully!")
        print("\nNext steps:")
        print("1. Start your FastAPI server: uvicorn main:app --reload")
        print("2. Start your Next.js frontend: npm run dev")
        print("3. Visit http://localhost:3000/feed to see the imported reviews")
        print("4. Try uploading your own CSV file using the upload interface")
    else:
        print("\n💥 Test failed!")
        sys.exit(1)
