# knn_barangay_training_script.py

import pandas as pd
import numpy as np
import pickle
from sklearn.neighbors import KNeighborsClassifier
from sklearn.preprocessing import LabelEncoder
import math
import os

# Define haversine distance locally
def haversine_distance(coord1, coord2):
    lat1, lon1 = coord1
    lat2, lon2 = coord2
    R = 6371
    lat1, lon1, lat2, lon2 = map(math.radians, [lat1, lon1, lat2, lon2])
    dlat = lat2 - lat1
    dlon = lon2 - lon1
    a = math.sin(dlat/2)**2 + math.cos(lat1)*math.cos(lat2)*math.sin(dlon/2)**2
    return R * 2 * math.atan2(math.sqrt(a), math.sqrt(1-a))

# Load data
# Load data
df = pd.read_csv("barangay_locations.csv")

# Drop rows with missing coordinates
df = df.dropna(subset=["latitude", "longitude"])

# Prepare training data
X = df[['latitude', 'longitude']].values
y = df['barangay'].values
label_encoder = LabelEncoder()
y_encoded = label_encoder.fit_transform(y)

# Train model
knn = KNeighborsClassifier(n_neighbors=3, metric=haversine_distance)
knn.fit(X, y_encoded)


# Save model and label encoder
with open("knn_model.pkl", "wb") as f:
    pickle.dump(knn, f)
with open("label_encoder.pkl", "wb") as f:
    pickle.dump(label_encoder, f)

missing_coords = df[df[['latitude', 'longitude']].isna().any(axis=1)]
print("Barangays with missing coordinates:")
print(missing_coords)