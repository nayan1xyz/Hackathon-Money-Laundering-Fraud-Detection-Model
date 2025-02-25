import pandas as pd
import joblib
import numpy as np
import tensorflow as tf
from tensorflow import keras
from tensorflow.keras import layers
import keras_tuner as kt
from sklearn.model_selection import train_test_split

df = pd.read_csv("preprocessed_transactions.csv")
X = df.drop(columns=["fraud"]).values
y = df["fraud"].values

X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

def build_model(hp):
    model = keras.Sequential()
    model.add(
        layers.Dense(
            units=hp.Int('units_input', min_value=16, max_value=128, step=16),
            activation='relu',
            input_shape=(X_train.shape[1],)
        )
    )
    
    for i in range(hp.Int('num_layers', 1, 3)):
        model.add(
            layers.Dense(
                units=hp.Int(f'units_{i}', min_value=16, max_value=128, step=16),
                activation='relu'
            )
        )
    
    model.add(layers.Dense(1, activation='sigmoid'))
    
    model.compile(
        optimizer=keras.optimizers.Adam(
            learning_rate=hp.Choice('learning_rate', values=[1e-2, 1e-3, 1e-4])
        ),
        loss='binary_crossentropy',
        metrics=['accuracy']
    )
    
    return model

tuner = kt.Hyperband(
    build_model,
    objective='val_accuracy',
    max_epochs=10,
    factor=3,
    directory='my_dir',
    project_name='iso20022_deep_fraud'
)

stop_early = keras.callbacks.EarlyStopping(monitor='val_loss', patience=3)
tuner.search(X_train, y_train, epochs=10, validation_split=0.2, callbacks=[stop_early])

best_hps = tuner.get_best_hyperparameters(num_trials=1)[0]
print(f"Optimal units in the first layer: {best_hps.get('units_input')}")
print(f"Optimal number of hidden layers: {best_hps.get('num_layers')}")
print(f"Optimal learning rate: {best_hps.get('learning_rate')}")

model = tuner.hypermodel.build(best_hps)
history = model.fit(X_train, y_train, epochs=10, validation_split=0.2)

test_loss, test_acc = model.evaluate(X_test, y_test)
print(f"Test Accuracy: {test_acc:.2f}")

model.save("deep_fraud_model.h5")
print("✅ Deep learning model saved as 'deep_fraud_model.h5'")
