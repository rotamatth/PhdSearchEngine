import pandas as pd
import os

def preprocess_data():
    # Paths to the data files
    data_files = [
        './data/raw/academic_positions.csv',
        './data/raw/nature_positions_detailed_with_pagination.csv',
        './data/raw/eth_positions_with_description.csv'
    ]
    
    # List to hold DataFrames
    dataframes = []
    
    # Load data from all files
    for file_path in data_files:
        if os.path.exists(file_path):
            try:
                df = pd.read_csv(file_path)
                dataframes.append(df)
                print(f"Loaded data from {file_path}")
            except Exception as e:
                print(f"Error reading {file_path}: {e}")
        else:
            print(f"File {file_path} does not exist.")
    
    # Exit if no data was loaded
    if not dataframes:
        print("No data to process.")
        return
    
    # Combine all data
    combined_df = pd.concat(dataframes, ignore_index=True)
    
    # Drop 'Salary', 'Closing In', and 'Closing Date' columns if they exist
    columns_to_drop = ['Salary', 'Closing In', 'Closing Date']
    combined_df.drop(columns=[col for col in columns_to_drop if col in combined_df.columns], inplace=True)
    
    # Normalize text columns
    for col in ['Title', 'Employer', 'Location', 'Description']:
        if col in combined_df.columns:
            combined_df[col] = combined_df[col].astype(str).str.lower().str.strip()
            combined_df[col] = combined_df[col].str.replace(r'\s+', ' ', regex=True)
    
    # Remove duplicate rows
    combined_df.drop_duplicates(inplace=True)

    # Save the combined and cleaned data
    output_path = './data/cleaned/positions_cleaned.csv'
    os.makedirs('./data/cleaned', exist_ok=True)
    combined_df.to_csv(output_path, index=False)
    print(f"Cleaned data saved to {output_path}")

if __name__ == '__main__':
    preprocess_data()
