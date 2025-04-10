import pandas as pd
from sklearn.model_selection import train_test_split

def load_data(file_path):
    """
    Load data from a CSV file.

    Parameters:
    - file_path (str): File path to the CSV file.

    Returns:
    - data (DataFrame): DataFrame containing the data.
    """
    # Load data
    data = pd.read_csv(file_path)

    return data

if __name__ == "__main__":
    # File path
    file_path = "data/stats.csv"  # Adjust the file path accordingly

    # Load data
    data = load_data(file_path)

    # Drop specified columns
    columns_to_drop = ["last_name, first_name", "player_id", "year"]
    data = data.drop(columns=columns_to_drop)

    # Perform train-test split
    train_data, test_data = train_test_split(data, test_size=0.2, random_state=42)

    # Save processed train and test data to CSV files
    train_data.to_csv("data/processed_train.csv", index=False)
    test_data.to_csv("data/processed_test.csv", index=False)

    print(f"Finished preprocessing data. The train data has {train_data.shape[0]} rows and {train_data.shape[1]} columns while the test data has {test_data.shape[0]} rows and {test_data.shape[1]} columns.")
