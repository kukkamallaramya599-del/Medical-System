import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder
from sklearn.neural_network import MLPClassifier
import joblib

# Load dataset
data = pd.read_csv("cleaned_dataset.csv")

# Split input & output
X = data.drop("Disease", axis=1)
y = data["Disease"]

# Encode labels
encoder = LabelEncoder()
y_encoded = encoder.fit_transform(y)

# Split data
X_train, X_test, y_train, y_test = train_test_split(X, y_encoded, test_size=0.2)

# ANN Model (MLP)
model = MLPClassifier(hidden_layer_sizes=(32,16), max_iter=500)

# Train model
model.fit(X_train, y_train)

# Accuracy
acc = model.score(X_test, y_test)
print("Accuracy:", acc)

# Save model
joblib.dump(model, "model.pkl")
joblib.dump(encoder, "encoder.pkl")