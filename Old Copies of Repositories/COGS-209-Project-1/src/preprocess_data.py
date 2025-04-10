import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.impute import SimpleImputer, KNNImputer
from sklearn.experimental import enable_iterative_imputer
from sklearn.impute import IterativeImputer

def load_data(train_file_path, test_file_path):
    """
    Load train and test data from CSV files.

    Parameters:
    - train_file_path (str): File path to the train CSV file.
    - test_file_path (str): File path to the test CSV file.

    Returns:
    - train_data (DataFrame): DataFrame containing train data.
    - test_data (DataFrame): DataFrame containing test data.
    """
    # Load train data
    train_data = pd.read_csv(train_file_path)

    # Load test data
    test_data = pd.read_csv(test_file_path)

    return train_data, test_data

def combine_datasets(train_data, test_data):
    """
    Combine train and test datasets into a single DataFrame.

    Parameters:
    - train_data (DataFrame): DataFrame containing train data.
    - test_data (DataFrame): DataFrame containing test data.

    Returns:
    - combined_data (DataFrame): DataFrame containing combined data.
    """
    # Add a 'Dataset' column to indicate train/test set
    train_data['Dataset'] = 'Train'
    test_data['Dataset'] = 'Test'

    # Concatenate train and test DataFrames
    combined_data = pd.concat([train_data, test_data], ignore_index=True)

    # Drop the column named "Dataset"
    combined_data = combined_data.drop(columns=["Dataset"])

    # Drop the column named "Id"
    combined_data = combined_data.drop(columns=["Id"])

    return combined_data

def impute_missing_values(combined_data):
    """
    Impute missing values using advanced imputation techniques.

    Parameters:
    - combined_data (DataFrame): DataFrame containing combined data.

    Returns:
    - combined_data (DataFrame): DataFrame with imputed missing values.
    """
    # Separate numerical and categorical columns
    numerical_cols = combined_data.select_dtypes(include=['float64', 'int64']).columns
    categorical_cols = combined_data.select_dtypes(include=['object']).columns

    # Impute numerical columns using Iterative Imputer
    iter_imputer = IterativeImputer()
    combined_data[numerical_cols] = iter_imputer.fit_transform(combined_data[numerical_cols])

    # Impute categorical columns using most frequent (mode) imputation
    mode_imputer = SimpleImputer(strategy='most_frequent')
    combined_data[categorical_cols] = mode_imputer.fit_transform(combined_data[categorical_cols])

    return combined_data

if __name__ == "__main__":
    # File paths
    train_file_path = "data/train.csv"
    test_file_path = "data/test.csv"

    # Load data
    train_data, test_data = load_data(train_file_path, test_file_path)

    # Combine datasets
    combined_data = combine_datasets(train_data, test_data)

    # Count the number of rows
    num_initial_rows = combined_data.shape[0]

    # Calculate the percentage of missing values in each column
    missing_percentage = (combined_data.isnull().sum() / len(combined_data)) * 100

    # Set a threshold for the percentage of missing values to drop columns
    threshold = 10  # Drop columns where more than 10% of the rows have missing values

    # Drop columns where the percentage of missing values exceeds the threshold
    columns_to_drop = missing_percentage[missing_percentage > threshold].index
    if 'SalePrice' in columns_to_drop:
        columns_to_drop = columns_to_drop.drop('SalePrice') # Don't drop SalePrice
    combined_data = combined_data.drop(columns_to_drop, axis=1)

    # Impute missing values instead of dropping rows
    combined_data = impute_missing_values(combined_data)

    # Perform train-test split
    train_data, test_data = train_test_split(combined_data, test_size=0.2, random_state=42)

    # Save processed train and test data to CSV files
    train_data.to_csv("data/processed_train.csv", index=False)
    test_data.to_csv("data/processed_test.csv", index=False)

    # Count the number of rows
    num_final_rows = combined_data.shape[0]

    print(f"Finished preprocessing data with {train_data.shape[0]} rows and {train_data.shape[1]} columns remaining.")
    # print("Removed columns: ", columns_to_drop)
    # print("Number of rows removed: ", (num_initial_rows - num_final_rows))
