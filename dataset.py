# import random
# import pandas as pd
# import numpy as np

# # Function to generate dataset
# def generate_washing_dataset(num_samples):
#     data = {'Shirts': [], 'Pants': [], 'Undergarments': [], 'Jackets': [], 'WashingTime': []}

#     for _ in range(num_samples):
#         num_shirts = random.randint(0, 10)
#         num_pants = random.randint(0, 10)
#         num_jackets = random.randint(0, 5)
#         num_undergarments = random.randint(0, 7)

#         weight_shirts = random.uniform(1, 2.5)
#         weight_pants = random.uniform(2, 3.5)
#         weight_jackets = random.uniform(4, 5.5)
#         weight_undergarments = random.uniform(0, 1.5)

#         washing_time = 10 + weight_shirts * num_shirts + weight_pants * num_pants + weight_undergarments * num_undergarments + weight_jackets * num_jackets

#         data['Shirts'].append(num_shirts)
#         data['Pants'].append(num_pants)
#         data['Jackets'].append(num_jackets)
#         data['Undergarments'].append(num_undergarments)
#         data['WashingTime'].append(int(washing_time))

#     df = pd.DataFrame(data)
#     return df

# # Generate a dataset with 1000 samples
# dataset = generate_washing_dataset(500)

# # Save the dataset to a CSV file
# csv_filename = 'washing_test_dataset.csv'
# dataset.to_csv(csv_filename, index=False)

# print(f'Dataset saved to {csv_filename}')

# df = pd.read_csv("washing_test_dataset.csv")

# df = df.drop(columns=['WashingTime'])

# # print(df)
# csv_filename_dropped = "washing_test_dropped.csv"
# df.to_csv(csv_filename_dropped, index=False)
