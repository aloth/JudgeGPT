#!/usr/bin/env python3
"""
Data Export Script for JudgeGPT Research

This script exports MongoDB collections (participants, results, fragments) 
to both CSV and JSON formats with timestamped filenames.

Usage:
    python export_data.py

Output files are saved in the data_dumps/ subdirectory with format:
    YYYYMMDDHHMMSS-collectionname.csv
    YYYYMMDDHHMMSS-collectionname.json

Author: Alexander Loth
"""

import os
import sys
import json
import csv
import zipfile
from datetime import datetime
from typing import List, Dict, Any
import pandas as pd
from pymongo import MongoClient
from pymongo.server_api import ServerApi

# Add parent directory to path to import from app.py if needed
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def get_mongodb_connection():
    """
    Get MongoDB connection using Streamlit secrets from parent directory.
    
    Returns:
        MongoClient: Connected MongoDB client
    """
    try:
        # Set up path to use parent directory's .streamlit/secrets.toml
        parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        streamlit_dir = os.path.join(parent_dir, '.streamlit')
        
        # Add parent directory to Python path for streamlit import
        if parent_dir not in sys.path:
            sys.path.insert(0, parent_dir)
        
        # Change to parent directory temporarily to access secrets
        original_cwd = os.getcwd()
        os.chdir(parent_dir)
        
        try:
            import streamlit as st
            connection_string = st.secrets["mongo"].connection
        finally:
            # Change back to original directory
            os.chdir(original_cwd)
            
    except (ImportError, KeyError, Exception) as e:
        # Fallback: Check environment variable
        connection_string = os.getenv('MONGODB_CONNECTION_STRING')
        if not connection_string:
            raise ValueError(
                f"MongoDB connection string not found. Error: {str(e)}\n"
                "Please set MONGODB_CONNECTION_STRING environment variable "
                "or ensure Streamlit secrets are configured in parent directory."
            )
    
    return MongoClient(connection_string, server_api=ServerApi('1'))

def generate_timestamp() -> str:
    """
    Generate timestamp string in YYYYMMDDHHMMSS format.
    
    Returns:
        str: Formatted timestamp string
    """
    return datetime.now().strftime("%Y%m%d%H%M%S")

def export_collection_to_csv(collection_data: List[Dict[str, Any]], 
                           filename: str) -> None:
    """
    Export collection data to CSV file.
    
    Args:
        collection_data (List[Dict]): Data from MongoDB collection
        filename (str): Output filename
    """
    if not collection_data:
        print(f"Warning: No data found for {filename}")
        return
    
    # Convert to DataFrame for easy CSV export
    df = pd.DataFrame(collection_data)
    
    # Ensure data_dumps directory exists
    os.makedirs('data_dumps', exist_ok=True)
    
    filepath = os.path.join('data_dumps', filename)
    df.to_csv(filepath, index=False, encoding='utf-8')
    print(f"✓ Exported {len(collection_data)} records to {filepath}")

def export_collection_to_json(collection_data: List[Dict[str, Any]], 
                            filename: str) -> None:
    """
    Export collection data to JSON file.
    
    Args:
        collection_data (List[Dict]): Data from MongoDB collection
        filename (str): Output filename
    """
    if not collection_data:
        print(f"Warning: No data found for {filename}")
        return
    
    # Ensure data_dumps directory exists
    os.makedirs('data_dumps', exist_ok=True)
    
    filepath = os.path.join('data_dumps', filename)
    with open(filepath, 'w', encoding='utf-8') as f:
        json.dump(collection_data, f, indent=2, ensure_ascii=False, default=str)
    
    print(f"✓ Exported {len(collection_data)} records to {filepath}")

def fetch_collection_data(db, collection_name: str) -> List[Dict[str, Any]]:
    """
    Fetch all data from a MongoDB collection.
    
    Args:
        db: MongoDB database object
        collection_name (str): Name of the collection to fetch
    
    Returns:
        List[Dict]: All documents in the collection
    """
    collection = db[collection_name]
    
    # Fetch all documents and convert ObjectId to string
    documents = []
    for doc in collection.find():
        # Convert ObjectId to string for JSON serialization
        if '_id' in doc:
            doc['_id'] = str(doc['_id'])
        documents.append(doc)
    
    return documents

def save_export_summary(timestamp: str, export_summary: Dict[str, int]) -> str:
    """
    Save export summary to a text file.
    
    Args:
        timestamp (str): Export timestamp
        export_summary (Dict[str, int]): Dictionary with collection names and counts
    
    Returns:
        str: Path to the created summary file
    """
    # Ensure data_dumps directory exists
    os.makedirs('data_dumps', exist_ok=True)
    
    summary_filename = f"{timestamp}-export_summary.txt"
    filepath = os.path.join('data_dumps', summary_filename)
    
    total_documents = sum(export_summary.values())
    files_created = len([c for c in export_summary.values() if c > 0]) * 2
    
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(f"JudgeGPT Data Export Summary\n")
        f.write(f"Export Timestamp: {timestamp}\n")
        f.write(f"Export Date: {datetime.strptime(timestamp, '%Y%m%d%H%M%S').strftime('%Y-%m-%d %H:%M:%S')}\n")
        f.write("=" * 50 + "\n")
        f.write("\nDocument Counts by Collection:\n")
        for collection, count in export_summary.items():
            f.write(f"  {collection:<12}: {count:>8} documents\n")
        f.write("=" * 50 + "\n")
        f.write(f"  {'TOTAL':<12}: {total_documents:>8} documents\n")
        f.write(f"  {'Files created':<12}: {files_created:>8} files\n")
        f.write(f"\nFiles generated:\n")
        for collection, count in export_summary.items():
            if count > 0:
                f.write(f"  - {timestamp}-{collection}.csv\n")
                f.write(f"  - {timestamp}-{collection}.json\n")
        f.write(f"  - {summary_filename}\n")
    
    print(f"✓ Export summary saved to {filepath}")
    return filepath

def create_zip_archive(timestamp: str, export_summary: Dict[str, int], summary_file: str) -> None:
    """
    Create a ZIP archive containing all exported files.
    
    Args:
        timestamp (str): Export timestamp
        export_summary (Dict[str, int]): Dictionary with collection names and counts
        summary_file (str): Path to the summary file
    """
    # Ensure data_dumps directory exists
    os.makedirs('data_dumps', exist_ok=True)
    
    zip_filename = f"{timestamp}-judgegpt_export.zip"
    zip_filepath = os.path.join('data_dumps', zip_filename)
    
    files_to_zip = []
    
    # Add CSV and JSON files for each collection
    for collection, count in export_summary.items():
        if count > 0:
            csv_file = f"{timestamp}-{collection}.csv"
            json_file = f"{timestamp}-{collection}.json"
            files_to_zip.append(os.path.join('data_dumps', csv_file))
            files_to_zip.append(os.path.join('data_dumps', json_file))
    
    # Add summary file
    files_to_zip.append(summary_file)
    
    # Create ZIP archive
    with zipfile.ZipFile(zip_filepath, 'w', zipfile.ZIP_DEFLATED) as zipf:
        for file_path in files_to_zip:
            if os.path.exists(file_path):
                # Add file to zip with just the filename (not the full path)
                arcname = os.path.basename(file_path)
                zipf.write(file_path, arcname)
    
    print(f"✓ Created ZIP archive: {zip_filepath}")
    print(f"  Archive contains {len(files_to_zip)} files")

def main():
    """
    Main function to export all collections.
    """
    print("🚀 Starting JudgeGPT data export...")
    
    # Generate timestamp for this export session
    timestamp = generate_timestamp()
    print(f"📅 Export timestamp: {timestamp}")
    
    # Collection names to export
    collections = ['participants', 'results', 'fragments']
    export_summary = {}
    
    try:
        # Connect to MongoDB
        print("🔌 Connecting to MongoDB...")
        with get_mongodb_connection() as client:
            db = client.realorfake
            
            print("✓ Connected to database 'realorfake'")
            
            # Export each collection
            for collection_name in collections:
                print(f"\n📊 Processing collection: {collection_name}")
                
                # Fetch data
                try:
                    data = fetch_collection_data(db, collection_name)
                    document_count = len(data)
                    print(f"📈 Found {document_count} documents in {collection_name}")
                    
                    # Store count for summary
                    export_summary[collection_name] = document_count
                    
                    # Generate filenames
                    csv_filename = f"{timestamp}-{collection_name}.csv"
                    json_filename = f"{timestamp}-{collection_name}.json"
                    
                    # Export to both formats
                    export_collection_to_csv(data, csv_filename)
                    export_collection_to_json(data, json_filename)
                    
                except Exception as e:
                    print(f"❌ Error processing {collection_name}: {str(e)}")
                    export_summary[collection_name] = 0
                    continue
            
            # Print export summary
            print(f"\n🎉 Export completed successfully!")
            print(f"📁 Files saved in: {os.path.abspath('data_dumps')}")
            print("\n📊 EXPORT SUMMARY:")
            print("=" * 50)
            total_documents = 0
            for collection, count in export_summary.items():
                print(f"  {collection:<12}: {count:>8} documents")
                total_documents += count
            print("=" * 50)
            print(f"  {'TOTAL':<12}: {total_documents:>8} documents")
            print(f"  {'Files created':<12}: {len([c for c in export_summary.values() if c > 0]) * 2:>8} files")
            
            # Save summary to text file
            print(f"\n📄 Creating summary file...")
            summary_file = save_export_summary(timestamp, export_summary)
            
            # Create ZIP archive with all files
            print(f"\n📦 Creating ZIP archive...")
            create_zip_archive(timestamp, export_summary, summary_file)
            
            print(f"\n✅ All export operations completed successfully!")
            
    except Exception as e:
        print(f"❌ Critical error: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main()