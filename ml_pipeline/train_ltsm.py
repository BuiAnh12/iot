import numpy as np
import pandas as pd
import os
from keras.models import Sequential, load_model
from keras.layers import LSTM, Dense, Dropout
from sklearn.model_selection import train_test_split

# Đọc dữ liệu
body_falling = pd.read_csv("./data/data_falling_merged.csv")
body_sitting = pd.read_csv("./data/data_sitting_merged.csv")
body_standing = pd.read_csv("./data/data_standing_merged.csv")

X = []
y = []
no_of_timesteps = 10

# Gán nhãn và tạo tập dữ liệu
def process_data(df, label):
    dataset = df.iloc[:, 1:].values
    n_sample = len(dataset)
    for i in range(no_of_timesteps, n_sample):
        X.append(dataset[i-no_of_timesteps:i, :])
        y.append(label)

process_data(body_falling, 0)  # Falling
process_data(body_sitting, 1)  # Sitting
process_data(body_standing, 2)  # Standing

X, y = np.array(X), np.array(y)
print(X.shape, y.shape)

X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2)

# Load existing model if available, otherwise create a new one
if os.path.exists("../model/model.h5"):
    model = load_model("model.h5")
    print("Loaded existing model.")
else:
    model  = Sequential()
    model.add(LSTM(units=50, return_sequences=True, input_shape=(X.shape[1], X.shape[2])))
    model.add(Dropout(0.2))
    model.add(LSTM(units=50, return_sequences=True))
    model.add(Dropout(0.2))
    model.add(LSTM(units=50, return_sequences=True))
    model.add(Dropout(0.2))
    model.add(LSTM(units=50))
    model.add(Dropout(0.2))
    model.add(Dense(units=3, activation="softmax"))  # Adjusted for 3 classes
    model.compile(optimizer="adam", metrics=['accuracy'], loss="sparse_categorical_crossentropy")
    print("Created new model.")

# Continue training
model.fit(X_train, y_train, epochs=16, batch_size=32, validation_data=(X_test, y_test))
model.save("model.h5")
