import os
import numpy as np
import pandas as pd

# Paths
input_dir = "data"
output_dir = "increase_data/sitting"

# Ensure output directory exists
os.makedirs(output_dir, exist_ok=True)

# Load existing data files
existing_files = [f"data_sitting_{i}.csv" for i in range(1, 7)]
existing_data = [pd.read_csv(os.path.join(input_dir, file), header=None).values for file in existing_files]

# Function to interpolate between two datasets
def interpolate_data(data1, data2, alpha=0.5):
    """Interpolates two time-series data maintaining row-to-row relationships."""
    return alpha * data1 + (1 - alpha) * data2

# Generate 100 new files
for i in range(1, 101):
    # Select two random datasets for interpolation
    idx1, idx2 = np.random.choice(len(existing_data), 2, replace=False)
    data1, data2 = existing_data[idx1], existing_data[idx2]

    # Ensure both datasets have the same shape
    min_rows = min(data1.shape[0], data2.shape[0])  # To avoid shape mismatch
    data1, data2 = data1[:min_rows], data2[:min_rows]

    # Random interpolation factor
    alpha = np.random.uniform(0.3, 0.7)  # To introduce more variation
    new_data = interpolate_data(data1, data2, alpha)

    # Save the new data
    output_file = os.path.join(output_dir, f"data_sitting_{i}.csv")
    pd.DataFrame(new_data).to_csv(output_file, header=False, index=False)

    print(f"Generated: {output_file}")

print("Data augmentation complete. 100 files created!")
