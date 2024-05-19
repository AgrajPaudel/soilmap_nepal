import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder
from sklearn.neighbors import KNeighborsClassifier
import pickle

def train_knn_model(csv_file, pckl_file):
    # Load the dataset
    data = pd.read_csv(csv_file)

    # Set feature names
    data.columns = ['N', 'P', 'K', 'temperature', 'humidity', 'ph', 'rainfall', 'label']

    # Split features and labels
    X = data.drop('label', axis=1)
    y = data['label']

    # Encode categorical labels
    label_encoder = LabelEncoder()
    y = label_encoder.fit_transform(y)

    # Split data into training and testing sets
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

    # Initialize KNN classifier
    knn = KNeighborsClassifier(n_neighbors=3)

    # Train the classifier
    knn.fit(X_train, y_train)

    # Save the trained model and label encoder to a pickle file
    with open(pckl_file, 'wb') as f:
        pickle.dump((knn, label_encoder), f)

    print("KNN model trained and saved successfully!")

# Example usage:
csv_file_path = "Crop_recommendation.csv"
pickle_file_path = "knn_crop_classifier.pkl"
train_knn_model(csv_file_path, pickle_file_path)
