import pandas as pd
import numpy as np
import pickle
import warnings

from sklearn.linear_model import ElasticNet
from sklearn.metrics import mean_squared_error, mean_absolute_error
import matplotlib.pyplot as plt
from matplotlib.ticker import FuncFormatter
from sklearn.linear_model import LinearRegression
from scipy.stats import pearsonr

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
    plt.figure(figsize=(10, 4))
    plt.boxplot(means_list)
    plt.title('Box and Whisker Plots of MSE Values for Each Model')
    plt.xlabel('Model Iteration')
    plt.ylabel('Mean Squared Error')
    plt.xticks(range(1, len(means_list) + 1), [f'{i}' for i in range(1, len(means_list) + 1)])
    plt.savefig(f"figures/{save_path}")

def plot_hyperparameters(parameter_list, save_path):
    # Extract hyperparameters
    hyperparameters = {
        'alpha': [],
        'l1_ratio': []
    }

    for parameters in parameter_list:
        for key, value in parameters.items():
            if key in hyperparameters:
                hyperparameters[key].append(value)

    # Define ticks and ranges for each hyperparameter
    ticks_ranges = {
        'alpha': [1e-7, 1e-6, 1e-5, 1e-4, 1e-3, 1e-2, 1e-1],
        'l1_ratio': [1e-7, 1e-6, 1e-5, 1e-4, 1e-3, 1e-2, 1e-1]
    }

    # Plot box and whisker plot for each hyperparameter separately
    plt.figure(figsize=(6, 5))

    num_hyperparameters = len(hyperparameters)
    for i, (param, values) in enumerate(hyperparameters.items(), start=1):
        plt.subplot(num_hyperparameters, 1, i)
        plt.boxplot(values, vert=False)
        plt.title(f"{param} Values")
        plt.xlabel('Value')
        plt.ylabel(param)
        ax = plt.gca()

        # Remove y-axis ticks
        ax.yaxis.set_ticks([])

        # Get min and max values for the current parameter
        min_value = min(ticks_ranges[param])
        max_value = max(ticks_ranges[param])

        # Use logarithmic scale
        ax.set_xscale('log')

        # Set x-ticks to the range of values
        ax.set_xticks(ticks_ranges[param])

        # Customize tick formatter to display "e" for exponents
        formatter = FuncFormatter(lambda x, _: f"{x:.0e}".replace("e", "e") if x != 0 else "0")
        ax.xaxis.set_major_formatter(formatter)

        # Add margin to x-axis limits for spacing
        log_min = np.log10(min_value)
        log_max = np.log10(max_value)
        margin = (log_max - log_min) * 0.05  # 5% margin
        ax.set_xlim(10**(log_min - margin), 10**(log_max + margin))

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

def train_elastic_net(features, hyperparameters, train_data, test_data):
    # Extract the target variable
    y_train = train_data['woba'].values
    y_test = test_data['woba'].values
    
    # Extract numerical features
    numerical_cols = train_data[features].select_dtypes(include=['number']).columns
    
    # Prepare the input data
    X_train = train_data[features][numerical_cols].values
    X_test = test_data[features][numerical_cols].values
    
    # Train the ElasticNet model with specified hyperparameters
    model = ElasticNet(**hyperparameters)
    model.fit(X_train, y_train)

    # Make predictions on the test data
    y_pred = model.predict(X_test)

    return model, y_pred, y_test

def plot_scatter(y_pred, y_test, save_path):
    plt.figure(figsize=(8, 6))
    plt.scatter(y_test, y_pred, color='blue', alpha=0.5)
    plt.title('Scatter Plot of Predicted vs. Actual Values')
    plt.xlabel('Actual Values')
    plt.ylabel('Predicted Values')
    plt.savefig(f"figures/{save_path}")

def plot_residuals(y_pred_model, y_pred_xwoba, y_test, save_path):
    # Calculate residuals for the model's predictions
    residuals_model = y_test - y_pred_model
    
    # Calculate residuals for the xwOBA predictions
    residuals_xwoba = y_test - y_pred_xwoba
    
    # Create a residual plot
    plt.figure(figsize=(8, 6))
    plt.scatter(y_test, residuals_model, color='blue', alpha=0.5, label='Model Predictions')
    plt.scatter(y_test, residuals_xwoba, color='red', alpha=0.5, label='xwOBA Predictions')
    plt.title('Residual Plot')
    plt.xlabel('True Values')
    plt.ylabel('Residuals')
    plt.axhline(y=0, color='black', linestyle='-')  # Add a horizontal line at y=0
    plt.legend()
    plt.savefig(f"figures/{save_path}")

def simple_xwoba_linear_regression(train_data, test_data):
    # Extract the target variable
    y_train = train_data['woba'].values
    y_test = test_data['woba'].values
    
    # Extract xwoba as the only predictor
    X_train = train_data[['xwoba']].values
    X_test = test_data[['xwoba']].values
    
    # Train the linear regression model
    model = LinearRegression()
    model.fit(X_train, y_train)

    # Make predictions on the test data
    y_pred = model.predict(X_test)

    return model, y_pred

# Visualize models
if __name__ == "__main__":
    # Load the preprocessed data
    train_data = pd.read_csv('data/processed_train.csv')
    test_data = pd.read_csv('data/processed_test.csv')

    # Extract xwoba column from the test dataset
    xwoba = test_data['xwoba'].values

    # Load the stats from model selection
    file_path = 'model_information/model_evaluation_data.pkl'
    means_list, features_list, parameter_list = load_model_evaluation_data(file_path)

    # Visualize models during forward selection
    visualize_model_performance(means_list, "forward_selection_visualization.png")

    # Visualize the hyperparameters chosen
    plot_hyperparameters(parameter_list, "parameters_visualization.png")

    # Prompt user to input an index within the range of the number of entries in features_list
    max_index = len(features_list)
    # user_input = get_user_input_integer(max_index)
    user_input = 7
    user_input -= 1 # Because index by 0 in the code

    # Extract feature and parameters corresponding to the user-input index
    features, parameters = get_feature_and_parameters(user_input, features_list, parameter_list)

    # Print out the hyperparameters used
    print("\nHyperparameters Used")
    print("alpha: ", parameters["alpha"])
    print("l1_ratio: ", parameters["l1_ratio"])

    # Retrain the ElasticNet model again on the best-performing hyperparameters and features
    model, y_pred, y_test = train_elastic_net(features, parameters, train_data, test_data)

    # Also train a simple linear regression model on only xwoba
    xwoba_model, xwoba_y_pred = simple_xwoba_linear_regression(train_data, test_data)
    
    # Create a scatterplot for the predicted and test values
    plot_scatter(y_pred, y_test, "prediction_vs_test.png")

    # Sort feature names and coefficients by coefficient magnitude
    sorted_features_coef = sorted(zip(features, model.coef_), key=lambda x: abs(x[1]), reverse=True)

    # Print out the sorted feature names and coefficients
    print("\nFeature Coefficients of Elastic Net Model (Sorted by Magnitude):")
    for feature_name, coef in sorted_features_coef:
        print(f"{feature_name}: {coef}")

    # Compute Pearson correlation coefficient
    pearson_corr, _ = pearsonr(y_pred, y_test)
    print("\nPearson Correlation Coefficient:", pearson_corr)

    # Compute MSE for model's predictions and MSE for comparing xwOBA values
    model_mse = mean_squared_error(y_test, y_pred)
    xwoba_mse = mean_squared_error(y_test, xwoba_y_pred)
    print("\nElastic Net's MSE: ", model_mse)
    print("xwOBA's MSE: ", xwoba_mse)

    # Print the coefficient of the simple linear regression model (xwOBA only)
    print("\nFeature Coefficients of Simple Linear Regression (xwOBA only):")
    print("xwoba :", xwoba_model.coef_[0])

    # Create a residual plot for the predicted and test values
    plot_residuals(y_pred, xwoba, y_test, "residual_plot.png")