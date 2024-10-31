import os
import json
from pymongo import MongoClient
from tqdm import tqdm
from dotenv import load_dotenv

def load_sec_filings_to_mongo(folder_path: str, mongodb_uri: str, db_name: str = "sec_data", collection_name: str = "filings"):
    """
    Load JSON files from a specified folder into a MongoDB collection.
    
    Args:
        folder_path (str): Path to the folder containing JSON files.
        mongodb_uri (str): URI for MongoDB connection.
        db_name (str): Name of the MongoDB database.
        collection_name (str): Name of the MongoDB collection to insert the data.
    """
    client = MongoClient(mongodb_uri)
    db = client[db_name]
    collection = db[collection_name]
    
    collection.create_index("filename", unique=True)
    
    # Count total JSON files for progress tracking
    total_files = sum(1 for _, _, files in os.walk(folder_path) for file in files if file.endswith('.json'))
    
    # Iterate over JSON files in the folder
    current_file_index = 0  # Initialize current file index

    for root, _, files in os.walk(folder_path):
        for file in tqdm(files, desc="Loading SEC filings"):
            if file.endswith('.json'):
                current_file_index += 1  # Increment current file index
                file_path = os.path.join(root, file)
                with open(file_path, 'r') as json_file:
                    try:
                        data = json.load(json_file)
                        # Add filename as an identifier in case it's needed for reference
                        data["filename"] = file
                        print(f"Inserting data for company: {data.get('company', 'Unknown')} ({current_file_index}/{total_files})")  

                        # Insert into MongoDB with upsert to prevent duplicates
                        collection.update_one(
                            {"filename": file},  # Match on filename to avoid re-inserting
                            {"$set": data},       # Update document if exists
                            upsert=True           # Insert if not exists
                        )
                    except json.JSONDecodeError:
                        print(f"Error reading {file_path}: Not a valid JSON file")
                    except Exception as e:
                        print(f"Error inserting {file}: {str(e)}")

    print(f"Data loaded into MongoDB collection '{collection_name}' in database '{db_name}'.")

if __name__ == "__main__":
    # Load environment variables
    load_dotenv()
    mongodb_uri = os.getenv("MONGODB_URI")
    
    # Define path to JSON files
    data_folder_path = '/data/10-K'
    print("data folder path:", data_folder_path)
    
    # Check if the folder exists
    if os.path.exists(data_folder_path):
        # List all files in the directory
        files = os.listdir(data_folder_path)

        # Print the list of files
        # print("Files in data/10-K folder:")
        # for file in files:
        #     print(file)

        # Run the loader function
        load_sec_filings_to_mongo(data_folder_path, mongodb_uri)
    else:
        print(f"The specified folder does not exist: {data_folder_path}")

    if not mongodb_uri:
        raise ValueError("MONGODB_URI not found in environment variables")
    else:
        print(f"MONGODB_URI: {mongodb_uri}")
