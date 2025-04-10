import pandas as pd
import numpy as np
from sklearn.tree import DecisionTreeRegressor
from sklearn.model_selection import GridSearchCV
from sklearn.preprocessing import OneHotEncoder
import warnings
import pickle
from tqdm import tqdm
import matplotlib.pyplot as plt

# Ignore warnings
warnings.filterwarnings("ignore", category=FutureWarning)

# Load the preprocessed data
train_data = pd.read_csv('data/processed_train.csv')
test_data = pd.read_csv('data/processed_test.csv')

# Extract the target variable
y_train = train_data['SalePrice'].values

# Initialize an empty set of selected features
selected_features = []

# Initialize an empty list to store the mean test scores of the best-performing models
means_list = []

# Initialize an empty list to store the hyperparameters of the best-performing models
parameter_list = []

# Initialize an empty list to store the list of selected feature for that specific iteration
features_list = []

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
        if feature != 'SalePrice' and feature not in selected_features:
            # Train a model using the selected features plus the current feature
            features_to_use = selected_features + [feature]
            
            # Separate categorical and numerical features
            categorical_cols = train_data[features_to_use].select_dtypes(include=['object']).columns
            numerical_cols = train_data[features_to_use].select_dtypes(include=['number']).columns
            
            # One-hot encode categorical columns
            encoder = OneHotEncoder(sparse=False, handle_unknown='ignore')
            X_train_cat = encoder.fit_transform(train_data[features_to_use][categorical_cols])
            X_test_cat = encoder.transform(test_data[features_to_use][categorical_cols])
            
            # Concatenate encoded categorical and numerical columns
            X_train_selected = np.concatenate([X_train_cat, train_data[features_to_use][numerical_cols].values], axis=1)
            X_test_selected = np.concatenate([X_test_cat, test_data[features_to_use][numerical_cols].values], axis=1)
            
            # Define the hyperparameters grid
            # param_grid = {
            #     'max_depth': [10],
            #     'min_samples_split': [2],
            #     'min_samples_leaf': [2],
            #     'max_features': ['sqrt'],
            #     'min_impurity_decrease': [0.2]
            # }
            param_grid = {
                'max_depth': [5, 10, 15],
                'min_samples_split': [2, 3, 4],
                'min_samples_leaf': [1, 2, 3],
                'max_features': ['auto', 'sqrt', 'log2'],
                'min_impurity_decrease': [0.2, 0.3, 0.4, 0.5, 0.6]
            }
            
            grid_search = GridSearchCV(estimator=DecisionTreeRegressor(random_state=42),
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
with open('model_information/model_evaluation_data.pkl', 'wb') as f:
    pickle.dump(data_dict, f)

# Create a boxplot for each set of MSE values in best_means
plt.figure(figsize=(10, 6))
plt.boxplot(means_list)
plt.title('Box and Whisker Plots of MSE Values for Each Model')
plt.xlabel('Model Iteration')
plt.ylabel('Mean Squared Error')
plt.xticks(range(1, len(means_list) + 1), [f'{i}' for i in range(1, len(means_list) + 1)])
plt.show()