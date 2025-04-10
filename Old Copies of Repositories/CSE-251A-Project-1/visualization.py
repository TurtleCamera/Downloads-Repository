import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd

# Load the results from the CSV file
results_df = pd.read_csv("results/prototype_selection_results.csv")

# Visualize Accuracy vs. Number of Prototypes (M)
plt.figure(figsize=(10, 6))
for method in results_df['Method'].unique():
    method_data = results_df[results_df['Method'] == method]
    plt.plot(method_data["M"], method_data["Mean Accuracy"], marker="o", label=method)
    plt.fill_between(method_data["M"], 
                     method_data["Mean Accuracy"] - method_data["Std Accuracy"], 
                     method_data["Mean Accuracy"] + method_data["Std Accuracy"], 
                     alpha=0.2)
plt.title("Accuracy vs. Number of Prototypes")
plt.xlabel("Number of Prototypes (M)")
plt.ylabel("Mean Accuracy")
plt.grid(True)
plt.legend()
plt.savefig("accuracy_vs_prototypes.png")  # Save the figure
plt.show()

# Visualize Training Time vs. Number of Prototypes (M)
plt.figure(figsize=(10, 6))
for method in results_df['Method'].unique():
    method_data = results_df[results_df['Method'] == method]
    plt.plot(method_data["M"], method_data["Mean Training Time (s)"], marker="o", label=method)
    plt.fill_between(method_data["M"], 
                     method_data["Mean Training Time (s)"] - method_data["Std Training Time (s)"], 
                     method_data["Mean Training Time (s)"] + method_data["Std Training Time (s)"], 
                     alpha=0.2)
plt.title("Training Time vs. Number of Prototypes")
plt.xlabel("Number of Prototypes (M)")
plt.ylabel("Mean Training Time (s)")
plt.grid(True)
plt.legend()
plt.savefig("training_time_vs_prototypes.png")  # Save the figure
plt.show()

# Visualize Test Time vs. Number of Prototypes (M)
plt.figure(figsize=(10, 6))
for method in results_df['Method'].unique():
    method_data = results_df[results_df['Method'] == method]
    plt.plot(method_data["M"], method_data["Mean Test Time (s)"], marker="o", label=method)
    plt.fill_between(method_data["M"], 
                     method_data["Mean Test Time (s)"] - method_data["Std Test Time (s)"], 
                     method_data["Mean Test Time (s)"] + method_data["Std Test Time (s)"], 
                     alpha=0.2)
plt.title("Test Time vs. Number of Prototypes")
plt.xlabel("Number of Prototypes (M)")
plt.ylabel("Mean Test Time (s)")
plt.grid(True)
plt.legend()
plt.savefig("test_time_vs_prototypes.png")  # Save the figure
plt.show()

# Table of Mean Accuracy and Mean Training Time for each Method and M
summary_table = results_df.pivot_table(index="M", columns="Method", values=["Mean Accuracy", "Mean Training Time (s)", "Mean Test Time (s)"])
summary_table.to_csv("summary_table.csv")
print("Summary Table:")
print(summary_table)