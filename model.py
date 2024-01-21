from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline
from sklearn.impute import SimpleImputer
from sklearn.preprocessing import OneHotEncoder
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score
from xgboost import XGBClassifier
from scipy.stats import mode
from sklearn import preprocessing
from sklearn.preprocessing import PolynomialFeatures
import optuna
from category_encoders import TargetEncoder
import re
from sklearn.feature_selection import SelectFromModel
from sklearn.metrics import mean_squared_error
from sklearn.metrics import accuracy_score
from sklearn.preprocessing import LabelEncoder
import pandas as pd
import numpy as np 
import sqlite3

while True:
    df = pd.read_csv("train_folds_washing.csv")

    bins = [0, 30, 45, 60, 75,90]
    labels = [0, 1, 2, 3,4]

    df['WashingTime'] = pd.cut(df['WashingTime'], bins=bins, labels=labels, include_lowest=True)

    useful_features = [c for c in df.columns if c not in ("kfold","WashingTime")]

    poly = PolynomialFeatures(degree=3, interaction_only=True, include_bias=False)

    df_train=df[useful_features]

    train_poly = poly.fit_transform(df_train)

    df_poly = pd.DataFrame(train_poly, columns=[f"poly_{i}" for i in range(train_poly.shape[1])])

    df = pd.concat([df, df_poly], axis=1)

    label_encoder = LabelEncoder()
    df["WashingTimeClassEncoded"] = label_encoder.fit_transform(df["WashingTime"])

    train_features = df.drop(columns=["kfold", "WashingTime", "WashingTimeClassEncoded"])
    train_targets = df["WashingTimeClassEncoded"]

    # Instantiate RandomForestClassifier for multiclass classification
    clf = RandomForestClassifier(n_estimators=50, max_features='sqrt', random_state=42)

    # Fit the classifier
    clf.fit(train_features, train_targets)

    # Create a DataFrame to visualize feature importances
    features_importance = pd.DataFrame()
    features_importance['feature'] = train_features.columns
    features_importance['importance'] = clf.feature_importances_
    features_importance.sort_values(by=['importance'], ascending=False, inplace=True)

    # Visualize feature importances
    features_importance.plot(kind='barh', figsize=(12, 8), legend=False, title='Feature Importances')

    # Choose the top k most important features
    k = 14
    selected_features = features_importance.head(k)['feature'].tolist()

    print(selected_features)

    final_predictions = []

# def run(trial):
    accuracy_scores=[]

    for fold in range(5):

        # learning_rate = trial.suggest_float("learning_rate", 1e-2, 0.25, log=True)
        # reg_lambda = trial.suggest_loguniform("reg_lambda", 1e-8, 100.0)
        # reg_alpha = trial.suggest_loguniform("reg_alpha", 1e-8, 100.0)
        # subsample = trial.suggest_float("subsample", 0.1, 1.0)
        # colsample_bytree = trial.suggest_float("colsample_bytree", 0.1, 1.0)
        # max_depth = trial.suggest_int("max_depth", 1, 7)
        # n_estimators = trial.suggest_int("n_estimators", 50, 1000)

        xtrain = df[df.kfold != fold].reset_index(drop=True)
        xvalid = df[df.kfold == fold].reset_index(drop=True)

        ytrain = xtrain.WashingTime
        yvalid = xvalid.WashingTime

        xtrain = xtrain[selected_features]
        xvalid = xvalid[selected_features]
        

        # Select categorical columns
    #     categorical_cols = [cname for cname in xtrain.columns if
    #                         xtrain[cname].nunique() < 10 and 
    #                         xtrain[cname].dtype == "object"]

    #     # Select numerical columns
    #     numerical_cols = [cname for cname in xtrain.columns if 
    #                       xtrain[cname].dtype in ['int64', 'float64']]

    #     # Keep selected columns only
    #     my_cols = categorical_cols + numerical_cols

    #     # Normalization((x-mu)/sigma)

    #     scaler = preprocessing.StandardScaler()
    #     xtrain[numerical_cols_1] = scaler.fit_transform(xtrain[numerical_cols_1])
    #     xvalid[numerical_cols_1] = scaler.transform(xvalid[numerical_cols_1])
    #     xtest[numerical_cols_1] = scaler.transform(xtest[numerical_cols_1])

        # Define model
        model = XGBClassifier(objective='multi:softmax', num_class=5, n_estimators=100, learning_rate=0.019391533676654422, max_depth=4,reg_alpha=0.8511059335413129,subsample=0.4378621338516323, n_jobs=5)

        model.fit(xtrain, ytrain)

        preds_valid = model.predict(xvalid)
        print(fold, accuracy_score(yvalid, preds_valid))
            
        accuracy_scores.append(accuracy_score(yvalid, preds_valid))

    connection = sqlite3.connect("user_database.db")
    cursor = connection.cursor()

    # Define the table names
    table_name = "Queue"
    table_name_1 = "WashingData1"
    column_name = "Email"

    # Fetch data from the existing table
    select_query = f"SELECT {column_name} FROM {table_name}"
    df_email=pd.read_sql_query(select_query, connection)

    fetch_data_query = f"SELECT {', '.join(useful_features)} FROM {table_name}"
    df_from_db = pd.read_sql_query(fetch_data_query, connection)

    # Copy the dataframe for later use
    df_db_copy = df_from_db.copy()

    # Perform polynomial feature transformation
    train_db_poly = poly.fit_transform(df_db_copy[useful_features])
    df_db_poly = pd.DataFrame(train_db_poly, columns=[f"poly_{i}" for i in range(train_db_poly.shape[1])])

    # Concatenate the polynomial features to the original dataframe
    df_from_db = pd.concat([df_from_db, df_db_poly], axis=1)

    # Use selected features
    df_from_db = df_from_db[selected_features]

    # Make predictions using the model
    datab_pred = model.predict(df_from_db)

    # Map predictions to actual values
    value_mapping = {0: 30, 1: 45, 2: 60, 3: 75, 4: 90}
    datab_pred = [value_mapping[val] for val in datab_pred]

    cumulative_sum_list = np.cumsum([0] + datab_pred)

    # print(df_email['Email'][2])

    # Create a new table if not exists
    create_table_query = f"""
    CREATE TABLE IF NOT EXISTS {table_name_1} 
    (
        Email TEXT,
        Time INT,
        Jackets INT,
        Shirts INT,
        Pants INT,
        Undergarments INT,
        WaitingTime INT
    )
    """

    cursor.execute(create_table_query)

    # Insert data into the new table
    for i in range(len(df_db_copy)):

        email_value = f"'{df_email['Email'][i]}'"

        cursor.execute(f"INSERT INTO {table_name_1} (Email,Time, Jackets, Shirts,Pants ,Undergarments,  WaitingTime) VALUES ({email_value},{datab_pred[i]} ,{df_db_copy['Jackets'][i]}, {df_db_copy['Shirts'][i]}, {df_db_copy['Pants'][i]}, {df_db_copy['Undergarments'][i]},{cumulative_sum_list[i]})")
        

    # Commit changes and close the connection
    connection.commit()
    connection.close()

    # Reconnect to fetch and print the data from the new table
    connection = sqlite3.connect("user_database.db")
    cursor = connection.cursor()

    # Fetch and print data from the new table
    cursor.execute(f'SELECT * FROM {table_name_1}')
    rows = cursor.fetchall()
    print(rows)

    drop_table_query = f"DROP TABLE IF EXISTS {table_name}"
    cursor.execute(drop_table_query)

    rename_table_query = f"ALTER TABLE {table_name_1} RENAME TO {table_name}"
    cursor.execute(rename_table_query)

    # Close the connection
    connection.close()

