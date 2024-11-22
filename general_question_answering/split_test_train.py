import os
import json
import random
from pathlib import Path
from shutil import copy2

def split_dataset(input_folder, train_folder, test_folder, test_ratio=0.2):
    """
    Splits the dataset into train and test sets such that all data for a company is either in train or test.
    
    Args:
        input_folder (str): Path to the folder containing the JSON files.
        train_folder (str): Path to the folder where training data will be stored.
        test_folder (str): Path to the folder where testing data will be stored.
        test_ratio (float): Proportion of companies to include in the test set.
    """
    # Create folders for train and test if they don't exist
    Path(train_folder).mkdir(parents=True, exist_ok=True)
    Path(test_folder).mkdir(parents=True, exist_ok=True)
    
    # Group files by company ticker
    company_files = {}
    for file in os.listdir(input_folder):
        if file.endswith('.json'):
            file_path = os.path.join(input_folder, file)
            with open(file_path, 'r') as f:
                data = json.load(f)
                stock_ticker = data.get('stock_ticker')
                if stock_ticker:
                    company_files.setdefault(stock_ticker, []).append(file_path)
    
    # Shuffle companies and split into train and test
    companies = list(company_files.keys())
    random.shuffle(companies)
    test_size = int(len(companies) * test_ratio)
    test_companies = set(companies[:test_size])
    train_companies = set(companies[test_size:])
    
    # Move files to train or test folders
    for company, files in company_files.items():
        target_folder = test_folder if company in test_companies else train_folder
        for file_path in files:
            copy2(file_path, target_folder)
    
    print(f"Dataset split completed: {len(train_companies)} companies in train, {len(test_companies)} companies in test.")

if __name__ == "__main__":
    # Define paths
    input_folder = "./data/10-K"  # Folder containing the JSON files
    train_folder = "./data/train"        # Folder for training data
    test_folder = "./data/test"          # Folder for testing data
    
    # Split the dataset
    split_dataset(input_folder, train_folder, test_folder)
