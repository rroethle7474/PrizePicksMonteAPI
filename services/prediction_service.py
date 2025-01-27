import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LinearRegression
from sklearn.metrics import mean_squared_error
import os

# CANCEL ROTOWIRE!!!!!
# 1) Get Last Years Data for players
# 2) Get Current Season Data for players
# 3) Get Last 7 days data for players
# pass in player name - get prediction value for likelihood of total bases
# have a function run that will get all of the player data and parse into sql database


def load_test_data_training(csv_file_name):
    current_dir = os.path.dirname(__file__)  # Gets the directory where the script is running
    csv_file_path = os.path.join(current_dir, '..', 'csv_data', csv_file_name)

    data = pd.read_csv(csv_file_path)
    print("Data loaded successfully", data.head())
    # Total Base Probability - Current Season
    # Total Base Probability - Last Year
    # Total Base Probability - Last 7 days
    # Pitcher Factor: Optional
    # Handedness Factor: Optional
    # Additional Factors: Optional
    # example would be TB_Current (1.75), TB_LastYear(1.25), TB_Last7Days(.75)
    # ignore these for nowPF, HF, AF
    return data













def predict_fantasy_baseball_score(csv_file_name):
    # Load the data
    data = load_test_data_training(csv_file_name)
    
    
    
    # Select features and target
    # For example, using 'feature1', 'feature2' as predictors and 'score' as the target
    X = data[['TB_Current', 'TB_Last_Year', 'TB_Last7']].copy()  # Replace 'feature1', 'feature2' with your actual feature columns
    y = data['TB_Predicted']  # Replace 'score' with your actual target column
    print("X",X)
    # Scaling features example (optional based on your earlier question)
    X['TB_Current'] = X['TB_Current'] * 100
    X['TB_Last7'] = X['TB_Last7'] * 5
    X['TB_Last_Year'] = X['TB_Last_Year'] * 200
    print("X",X)
    # Split the data into training and testing sets
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

    # Create a linear regression model
    model = LinearRegression()

    # Train the model
    model.fit(X_train, y_train)

    # Make predictions
    y_pred = model.predict(X_test)

    # Calculate the mean squared error
    mse = mean_squared_error(y_test, y_pred)
    print(f"Mean Squared Error: {mse}")
    print(f"Predicted Fantasy Baseball Score: {y_pred}")

    # Example prediction with new data
    # new_data = [[value1, value2]]  # Replace value1, value2 with actual values for prediction
    # prediction = model.predict(new_data)
    # print(f"Predicted Fantasy Baseball Score: {prediction[0]}")

    return model  # Returning the model if you need to use it later

# Usage
print("RUNNING")
model = predict_fantasy_baseball_score('Test_Data.csv')
