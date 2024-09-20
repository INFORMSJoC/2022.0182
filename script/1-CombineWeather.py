import pandas as pd
import os

file_list=os.listdir('../data/0-RawData/Weather_Report/Refined_NYC')
iris_list=[]
for this_file in file_list:
    iris=pd.read_csv('../data/0-RawData/Weather_Report/Refined_NYC/'+this_file)
    iris['datetime']=[pd.to_datetime(this_file.split('.')[0]+":"+str(i),format='%Y_%m_%d:%H') for i in range(24)]
    iris_list.append(iris)

result1 = pd.concat(iris_list)
result1['date']=result1['datetime'].dt.date
result1['hour']=result1['datetime'].dt.hour
result1['date']= pd.to_datetime(result1['date'])

folder_list=os.listdir('../data/1-DemandData')
for this_folder in folder_list:
    if '.DS' not in this_folder:
        station_id=this_folder
        iris_list=[]
        file_list=os.listdir('../data/1-DemandData/'+this_folder)
        for this_file in file_list:
            iris=pd.read_csv('../data/1-DemandData/'+this_folder+'/'+this_file)
            iris_list.append(iris)

        result = pd.concat(iris_list)
        result['date']= pd.to_datetime(result['date'])

        result2 = pd.merge(result, result1, how='left', on=['date', 'hour'])
        result2['weekday'] = result2['datetime'].dt.dayofweek
        result2 = result2.drop(columns=['datetime'], axis=1)
        result2.to_csv('../data/2-DataWeather/Station_' + str(station_id) + '_whole_life.csv', index=None)