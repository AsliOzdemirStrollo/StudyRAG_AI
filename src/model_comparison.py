import numpy as np
import pandas as pd

from sklearn.model_selection import train_test_split
from sklearn.linear_model import LinearRegression
from sklearn.ensemble import RandomForestRegressor, GradientBoostingRegressor
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score


# Features:
# previous_score, days_left, study_hours,
# quiz_score, completion_percent, document_pages, document_chunks

X = np.array([
    [55, 2, 3, 40, 50, 120, 180],
    [60, 5, 6, 55, 60, 90, 140],
    [72, 7, 10, 70, 75, 70, 100],
    [80, 10, 14, 85, 90, 50, 80],
    [90, 14, 20, 95, 100, 40, 60],

    [50, 1, 2, 35, 40, 150, 220],
    [65, 4, 5, 60, 55, 100, 150],
    [75, 8, 12, 78, 80, 60, 90],
    [85, 12, 16, 90, 95, 45, 70],
    [92, 15, 22, 98, 100, 30, 50],

    [45, 3, 4, 45, 50, 130, 200],
    [70, 6, 8, 68, 70, 85, 130],
    [82, 9, 13, 82, 90, 55, 85],
    [58, 2, 5, 50, 45, 110, 170],
    [88, 13, 18, 92, 100, 35, 55],
])

y = np.array([
    50, 58, 72, 84, 94,
    45, 63, 77, 88, 96,
    52, 69, 84, 55, 93
])


X_train, X_test, y_train, y_test = train_test_split(
    X,
    y,
    test_size=0.3,
    random_state=42
)


models = {
    "Linear Regression": LinearRegression(),
    "Random Forest": RandomForestRegressor(
        n_estimators=100,
        random_state=42
    ),
    "Gradient Boosting": GradientBoostingRegressor(
        random_state=42
    )
}


results = []

for model_name, model in models.items():
    model.fit(X_train, y_train)

    predictions = model.predict(X_test)

    mae = mean_absolute_error(y_test, predictions)
    rmse = np.sqrt(mean_squared_error(y_test, predictions))
    r2 = r2_score(y_test, predictions)

    results.append({
        "Model": model_name,
        "MAE": round(mae, 2),
        "RMSE": round(rmse, 2),
        "R2 Score": round(r2, 2)
    })


results_df = pd.DataFrame(results)

results_df = results_df.sort_values(
    by="MAE",
    ascending=True
)

print("\nModel Comparison Results:")
print(results_df.to_string(index=False))

best_model = results_df.iloc[0]["Model"]

print(f"\nBest model based on lowest MAE: {best_model}")