import pandas as pd
import numpy as np
import pickle
import warnings

from sklearn.tree import DecisionTreeRegressor
from sklearn.metrics import mean_squared_error, mean_absolute_error
from sklearn.preprocessing import OneHotEncoder
from sklearn.tree import plot_tree
import matplotlib.pyplot as plt

# Ignore warnings
warnings.filterwarnings("ignore", category=FutureWarning)

def load_model_evaluation_data(file_path):
    # Load the data from the pickle file
    with open(file_path, 'rb') as f:
        data_dict = pickle.load(f)
    
    # Extract the lists from the dictionary
    means_list = data_dict['means_list']
    features_list = data_dict['features_list']
    parameter_list = data_dict['parameter_list']
    
    return means_list, features_list, parameter_list

def visualize_model_performance(means_list, save_path):
    # Create a boxplot for each set of MSE values in best_means
    plt.figure(figsize=(30, 6))
    plt.boxplot(means_list)
    plt.title('Box and Whisker Plots of MSE Values for Each Model', fontsize=26)
    plt.xlabel('Model Iteration', fontsize=26)
    plt.ylabel('Mean Squared Error', fontsize=26)
    plt.xticks(range(1, len(means_list) + 1), [f'{i}' for i in range(1, len(means_list) + 1)], fontsize=16)
    plt.yticks(fontsize=16)
    plt.savefig(f"figures/{save_path}")

# def visualize_model_performance(means_list, save_path):
#     # Slice means_list to include only iterations 12 to 20
#     means_to_plot = means_list[11:20]  # Index 11 corresponds to iteration 12

#     # Create a boxplot for each set of MSE values in best_means
#     plt.figure(figsize=(10, 6))
#     plt.boxplot(means_to_plot)
#     plt.title('Box and Whisker Plots of MSE Values (Partial)', fontsize=26)
#     plt.xlabel('Model Iteration', fontsize=26)
#     plt.ylabel('Mean Squared Error', fontsize=26)
#     plt.xticks(range(1, len(means_to_plot) + 1), [f'{i}' for i in range(12, 21)], fontsize=16)
#     plt.yticks(fontsize=16)
#     plt.savefig(f"figures/{save_path}")
#     plt.show()

def plot_hyperparameters(parameter_list, save_path):
    # Extract hyperparameters
    hyperparameters = {
        'max_depth': [],
        'min_samples_split': [],
        'min_samples_leaf': [],
        'min_impurity_decrease': []
    }

    for parameters in parameter_list:
        for key, value in parameters.items():
            if key != 'max_features':
                if value == None:
                    value = 0
                hyperparameters[key].append(value)

    # Define ticks and ranges for each hyperparameter
    ticks_ranges = {
        'max_depth': [0, 5, 10, 15, 20, 25, 30],
        'min_samples_split': [2, 3, 4, 5, 6, 7],
        'min_samples_leaf': [1, 2, 3, 4, 5, 6],
        'min_impurity_decrease': [0, 0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7]
    }

    # Plot box and whisker plot for each hyperparameter separately
    plt.figure(figsize=(4, 10))

    for i, (param, values) in enumerate(hyperparameters.items(), start=1):
        plt.subplot(4, 1, i)
        plt.boxplot(values, vert=False)
        plt.title(f"{param} Values")
        plt.xlabel('Value')
        plt.ylabel(param)
        plt.xticks(ticks_ranges[param])

    plt.suptitle('Hyperparameters Visualization By Grid Search')
    plt.tight_layout()
    plt.savefig(f"figures/{save_path}")

def get_user_input_integer(max_index):
    while True:
        try:
            user_input = int(input(f"Please enter an integer between 1 and {max_index}: "))
            if 0 < user_input <= max_index:
                return user_input
            else:
                print(f"Index must be between 1 and {max_index}. Please try again.")
        except ValueError:
            print("Invalid input. Please enter an integer.")

def get_feature_and_parameters(index, features_list, parameter_list):
    # Extract the feature and parameters at the specified index
    feature = features_list[index]
    parameters = parameter_list[index]
    return feature, parameters

def train_decision_tree(features, hyperparameters, train_data, test_data):
    # Extract the target variable
    y_train = train_data['SalePrice'].values
    y_test = test_data['SalePrice'].values
    
    # Separate categorical and numerical features
    categorical_cols = train_data[features].select_dtypes(include=['object']).columns
    numerical_cols = train_data[features].select_dtypes(include=['number']).columns
    
    # One-hot encode categorical columns
    encoder = OneHotEncoder(sparse=False, handle_unknown='ignore')
    X_train_cat = encoder.fit_transform(train_data[features][categorical_cols])
    X_test_cat = encoder.transform(test_data[features][categorical_cols])
    
    # Concatenate encoded categorical and numerical columns
    X_train_selected = np.concatenate([X_train_cat, train_data[features][numerical_cols].values], axis=1)
    X_test_selected = np.concatenate([X_test_cat, test_data[features][numerical_cols].values], axis=1)
    
    # Train the decision tree model with specified hyperparameters
    tree_regressor = DecisionTreeRegressor(**hyperparameters, random_state=44)
    tree_regressor.fit(X_train_selected, y_train)

    # Make predictions on the test data
    y_pred = tree_regressor.predict(X_test_selected)

    # Evaluate the model
    mse = mean_squared_error(y_test, y_pred)
    mae = mean_absolute_error(y_test, y_pred)
    print("Decision Tree Mean Squared Error:", mse)
    print("Decision Tree Mean Absolute Error:", mae)

    return tree_regressor, y_pred, y_test

def plot_scatter(y_pred, y_test, save_path):
    plt.figure(figsize=(11, 7))
    plt.scatter(y_test, y_pred, color='blue', alpha=0.5)
    plt.title('Scatter Plot of Predicted vs. Actual Values', fontsize=26)
    plt.xlabel('Actual Values', fontsize=26)
    plt.ylabel('Predicted Values', fontsize=26)
    plt.xticks(fontsize=16)
    plt.yticks(fontsize=16)
    plt.savefig(f"figures/{save_path}")

import pandas as pd

def get_feature_importance(tree_regressor, feature_names):
    # Retrieve feature importance
    feature_importance = tree_regressor.feature_importances_
    
    # Create a dictionary to store aggregated importance values for original categorical features
    aggregated_importance = {}
    
    # Aggregate importance values for original categorical features
    for feature_name in feature_names:
        # Check if the feature is one-hot encoded
        if '_' in feature_name:
            # Extract the original feature name
            original_feature = feature_name.split('_')[0]
            # Add the importance value to the aggregated importance of the original feature
            if original_feature in aggregated_importance:
                aggregated_importance[original_feature] += feature_importance[feature_names.index(feature_name)]
            else:
                aggregated_importance[original_feature] = feature_importance[feature_names.index(feature_name)]
        else:
            # If the feature is not one-hot encoded, simply add its importance value
            aggregated_importance[feature_name] = feature_importance[feature_names.index(feature_name)]
    
    # Create a DataFrame to store aggregated feature importance
    aggregated_importance_df = pd.DataFrame({'Feature': aggregated_importance.keys(), 'Importance': aggregated_importance.values()})
    
    # Sort the DataFrame by importance values in descending order
    aggregated_importance_df = aggregated_importance_df.sort_values(by='Importance', ascending=False)
    
    return aggregated_importance_df

# Visualize models
if __name__ == "__main__":
    # Load the preprocessed data
    train_data = pd.read_csv('data/processed_train.csv')
    test_data = pd.read_csv('data/processed_test.csv')

    file_path = 'model_information/model_evaluation_data.pkl'
    means_list, features_list, parameter_list = load_model_evaluation_data(file_path)

    # Visualize models during forward selection
    visualize_model_performance(means_list, "forward_selection_visualization.png")

    # Prompt user to input an index within the range of the number of entries in features_list
    max_index = len(features_list)
    # user_input = get_user_input_integer(max_index)
    user_input = 16
    user_input -= 1 # Because index by 0 in the code

    # Extract feature and parameters corresponding to the user-input index
    features, parameters = get_feature_and_parameters(user_input, features_list, parameter_list)

    # Visualize the hyperparameters chosen
    plot_hyperparameters(parameter_list, "parameters_visualization.png")

    # Retrain the decision tree again on the best-performing hyperparameters and features
    tree_regressor, y_pred, y_test = train_decision_tree(features, parameters, train_data, test_data)
    
    # Create a scatterplot for the predicted and test values
    plot_scatter(y_pred, y_test, "prediction_vs_test.png")

    # Visualize the decision tree
    plt.figure(figsize=(10, 5))
    plot_tree(tree_regressor, filled=True, fontsize=2)
    plt.savefig("figures/decision_tree.png")

    # Print the best hyperparameters and features
    print(parameter_list[user_input])
    print(features_list[user_input])

    # Compute Pearson correlation coefficient
    correlation = np.corrcoef(y_test, y_pred)[0, 1]
    print("Correlation coefficient:", correlation)

    # Print out the feature importances
    print(get_feature_importance(tree_regressor, features_list[user_input]))