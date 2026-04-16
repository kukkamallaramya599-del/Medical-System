import pandas as pd

# Load your dataset
data = pd.read_csv("dataset.csv")

# Collect all unique symptoms
symptoms = set()

for col in data.columns[1:]:
    for val in data[col].dropna():
        symptoms.add(val.strip())

symptoms = list(symptoms)

# Create new dataframe
new_data = []

for i in range(len(data)):
    row = dict.fromkeys(symptoms, 0)

    for col in data.columns[1:]:
        symptom = str(data.iloc[i][col]).strip()
        if symptom != "nan":
            row[symptom] = 1

    row["Disease"] = data.iloc[i][0]
    new_data.append(row)

# Convert to DataFrame
df = pd.DataFrame(new_data)

# Save new dataset
df.to_csv("cleaned_dataset.csv", index=False)

print("✅ Dataset converted successfully!")