# -*- coding: utf-8 -*-

import pandas as pd
import numpy as np

from sklearn.neural_network import MLPRegressor


def main():
    # Configurations
    HOUR = 9
    PERIOD = 2
    WEEKDAY = True
    HISTORICAL_WINDOW = 5
    TEST_HORIZON = 10

    df_data_focal = pd.read_csv('../data/2-DataWeather/Station_Station72_whole_life.csv')
    df_data_nearby = pd.read_csv('../data/2-DataWeather/Station_Station480_whole_life.csv')

    if WEEKDAY:
        df_data_focal_sub = df_data_focal[(df_data_focal['hour'] == HOUR) & (df_data_focal['period'] == PERIOD) & (df_data_focal['weekday'] <= 4)].reset_index().drop(['index'], axis=1)
        df_data_nearby_sub = df_data_nearby[(df_data_nearby['hour'] == HOUR) & (df_data_nearby['period'] == PERIOD) & (df_data_nearby['weekday'] <= 4)].reset_index().drop(['index'], axis=1)


    else:
        df_data_focal_sub = df_data_focal[(df_data_focal['hour'] == HOUR) & (df_data_focal['period'] == PERIOD) & (df_data_focal['weekday'] > 4)].reset_index().drop(['index'], axis=1)
        df_data_nearby_sub = df_data_nearby[(df_data_nearby['hour'] == HOUR) & (df_data_nearby['period'] == PERIOD) & (df_data_nearby['weekday'] > 4)].reset_index().drop(['index'], axis=1)

    # Adding lag features
    for i in range(1, HISTORICAL_WINDOW+1):
        df_data_focal_sub[f'pickup_lag_{i}'] = df_data_focal_sub['pickup'].shift(i)
        df_data_focal_sub[f'nearby_pickup_lag_{i}'] = df_data_nearby_sub['pickup'].shift(i)

    # Delete the first historical_window rows of data
    df_data_focal_sub = df_data_focal_sub.iloc[HISTORICAL_WINDOW:]

    # Split the training and test dataset
    feas_cols = ['is_empty_(0, 0)', 'is_empty_(0, 1)', 'is_empty_(1, 0)', 'is_empty_(1, 1)', 'temperature', 'humidity',
                 'visibility', 'windspeed', 'condition'] \
                + [f'pickup_lag_{i}' for i in range(1, HISTORICAL_WINDOW+1)] \
                + [f'nearby_pickup_lag_{i}' for i in range(1, HISTORICAL_WINDOW+1)]

    df_train_X = df_data_focal_sub[feas_cols][:-TEST_HORIZON]
    df_train_y = df_data_focal_sub['pickup'][:-TEST_HORIZON]

    df_test_X = df_data_focal_sub[feas_cols][-TEST_HORIZON:]
    df_test_y = df_data_focal_sub['pickup'][-TEST_HORIZON:]

    # Iterated retraining & predicting for the test dataset
    test_predictions = []
    for i in range(len(df_test_X)):

        nn_regressor = MLPRegressor(hidden_layer_sizes=8, random_state=42)
        nn_regressor.fit(df_train_X, df_train_y)

        test_predictions.append(nn_regressor.predict(df_test_X.iloc[5].values.reshape(1, -1))[0])

        df_train_X = df_train_X.append(df_test_X.iloc[i])
        df_train_y = df_train_y.append(pd.Series(df_test_y.iloc[i]))

    # Final prediction results are stored in test_predictions
    print(test_predictions)


if __name__ == '__main__':
    main()