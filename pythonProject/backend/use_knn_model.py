import pickle

def predict_crop(pckl_file, N, P, K, temperature, humidity, ph, rainfall):
    # Load the trained model and label encoder from pickle file
    with open(pckl_file, 'rb') as f:
        knn, label_encoder = pickle.load(f)

    # Make predictions
    input_data = [[N, P, K, temperature, humidity, ph, rainfall]]
    predicted_class = knn.predict(input_data)

    # Decode the predicted class
    predicted_class = label_encoder.inverse_transform(predicted_class)

    return predicted_class[0]

"""
# Example usage:
N = 180
P = 46
K = 19
temperature = 29.93964907
humidity = 54.61813464
ph = 4.726212446
rainfall = 45.43669946

pickle_file_path = "knn_crop_classifier.pkl"
predicted_label = predict_crop(pickle_file_path, N, P, K, temperature, humidity, ph, rainfall)
print("Predicted label:", predicted_label)
"""