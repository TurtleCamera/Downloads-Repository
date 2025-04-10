import pandas as pd
import numpy as np
from sklearn.linear_model import ElasticNet
from sklearn.model_selection import GridSearchCV
import warnings
import pickle
from tqdm import tqdm
import matplotlib.pyplot as plt
import warnings

warnings.filterwarnings("ignore")

# Load the preprocessed data
train_data = pd.read_csv('data/processed_train.csv')
test_data = pd.read_csv('data/processed_test.csv')

# Extract the target variable
y_train = train_data['woba'].values  # Adjust the target variable column name to lowercase

# Initialize an empty set of selected features
selected_features = []

# Initialize empty lists to store model evaluation data
means_list = []
features_list = []
parameter_list = []

# Define the forward selection loop
pbar = tqdm(total=len(train_data.columns) - 1)  # Initialize tqdm progress bar
while True:
    # Store information about the best model in this iteration
    best_feature = None
    best_score = float('inf')
    best_means = None
    best_parameters = None
    
    # Iterate through each feature not yet selected
    for feature in tqdm(train_data.columns, desc="Feature Loop", leave=True):  # Second tqdm progress bar
        if feature != 'woba' and feature != 'xwoba' and feature not in selected_features:  # Adjust the target variable column name to lowercase
            # Train a model using the selected features plus the current feature
            features_to_use = selected_features + [feature]
            
            X_train_selected = train_data[features_to_use].values
            X_test_selected = test_data[features_to_use].values
            
            # Define the hyperparameters grid
            param_grid = {
                'alpha': [1e-7, 1e-6, 1e-5, 1e-4, 1e-3, 1e-2, 1e-1, 1],
                'l1_ratio': [1e-7, 1e-6, 1e-5, 1e-4, 1e-3, 1e-2, 1e-1, 1]
            }
            
            grid_search = GridSearchCV(estimator=ElasticNet(random_state=42),
                                       param_grid=param_grid,
                                       cv=5,
                                       scoring='neg_mean_squared_error')
            grid_search.fit(X_train_selected, y_train)
            
            # Get the mean cross-validated MSE
            mean_cv_score = -np.mean(grid_search.cv_results_['mean_test_score'])
            means = -grid_search.cv_results_['mean_test_score']
            parameters = grid_search.best_params_
            
            # Select the feature that results in the greatest improvement in performance
            if mean_cv_score < best_score:
                best_score = mean_cv_score
                best_feature = feature
                best_means = means
                best_parameters = parameters
    
    # Check if further addition of features does not significantly improve performance or starts to degrade it
    if best_feature is None:
        break

    # Add the best feature to the selected features
    means_list.append(means)  # Store the mean test score
    selected_features.append(best_feature)
    features_list.append(selected_features.copy())
    parameter_list.append(best_parameters)

    # Increment tqdm progress bar
    pbar.update(1)

# Store all lists into a dictionary
data_dict = {
    'means_list': means_list,
    'features_list': features_list,
    'parameter_list': parameter_list
}

# Save the dictionary to a pickle file
with open('model_information/model_evaluation_data.pkl', 'wb') as f:  # Adjust the file path to save the model evaluation data
    pickle.dump(data_dict, f)

# Create a boxplot for each set of MSE values in best_means
plt.figure(figsize=(10, 6))
plt.boxplot(means_list)
plt.title('Box and Whisker Plots of MSE Values for Each Model')
plt.xlabel('Model Iteration')
plt.ylabel('Mean Squared Error')
plt.show()
