import pandas as pd
import itertools
import os
from datetime import datetime, timedelta

def process_2ns(mm, target_station, nearby):
    target_station_data = pd.read_csv('../data/0-RawData/' + mm + '/Station_' + str(target_station) + '.csv',
                                      usecols=['datetime', 'pickup', 'dropoff', 'bike', 'dock'])
    target_station_data.datetime = pd.to_datetime(target_station_data['datetime'], format="%Y/%m/%d %H:%M:%S")
    target_station_data.set_index('datetime')
    nearby_station_1 = pd.read_csv('../data/0-RawData/' + mm + '/Station_' + str(nearby[0]) + '.csv',
                                   usecols=['datetime', 'bike', 'dock'])
    nearby_station_1.columns = ['datetime', 'bike1', 'dock1']
    nearby_station_2 = pd.read_csv('../data/0-RawData/' + mm + '/Station_' + str(nearby[1]) + '.csv',
                                   usecols=['datetime', 'bike', 'dock'])
    nearby_station_2.columns = ['datetime', 'bike2', 'dock2']
    nearby_station_1.datetime = pd.to_datetime(target_station_data['datetime'], format="%Y/%m/%d %H:%M:%S")
    nearby_station_1.set_index('datetime')
    nearby_station_2.datetime = pd.to_datetime(target_station_data['datetime'], format="%Y/%m/%d %H:%M:%S")
    nearby_station_2.set_index('datetime')
    result = pd.merge(target_station_data, nearby_station_1, how='left', on='datetime')
    result = pd.merge(result, nearby_station_2, how='left', on='datetime')

    status_empty_indicator = {}
    status_full_indicator = {}
    status = list(itertools.product([0, 1], repeat=len(nearby) + 1))
    for row in status:
        status_empty_indicator[row] = 0
        status_full_indicator[row] = 0
    nearby_station_id_1 = nearby[0]
    nearby_station_id_2 = nearby[1]
    aggregate_table = pd.DataFrame(
        columns=['target_station_id', 'nearby_station_id_1', 'nearby_station_id_2', 'date','hour','period', 'pickup', 'dropoff'] + [
            'is_empty_' + str(rows) for rows in status] + ['is_full_' + str(rows) for rows in status])

    # in case empty input
    if len(target_station_data) == 0:
        directory = 'Station' + str(target_station)
        if directory not in os.listdir('../data/1-DemandData'):
            os.mkdir('../data/1-DemandData/' + directory)
        aggregate_table.to_csv(
            '../data/1-DemandData/Station' + str(target_station) + '/AggregatedStation_' + mm + '_' + str(
                target_station) + '.csv', index=False)
        return

    jj = 0
    i = 0
    pickup_demand = 0
    dropoff_demand = 0
    target_empty = 0
    target_full = 0
    this_record = result.iloc[0]
    last_time = this_record.datetime

    for i in range(len(result) - 1):
        this_record = result.iloc[i]
        this_time = this_record.datetime
        next_record = result.iloc[i + 1]
        next_time = next_record.datetime

        if next_time.hour == this_time.hour:
            if next_time.minute<=30 and this_time.minute<=30:
                time_duration = int((next_time - this_time).seconds / 60)
            elif next_time.minute>30 and this_time.minute<=30:
                time_duration = 30 - this_time.minute
            elif next_time.minute>30 and this_time.minute>30:
                time_duration = int((next_time - this_time).seconds / 60)
        else:
            time_duration = 60 - this_time.minute

        thispick = this_record.pickup
        thisdrop = this_record.dropoff
        if this_record.bike == 0 and thispick == 0:
            target_station_empty_status = 1  # it is empty
            nearby_station_1_empty_status = 0
            nearby_station_2_empty_status = 0
        else:
            target_station_empty_status = 0
        if this_record.dock == 0 and thisdrop == 0:
            target_station_full_status = 1
            nearby_station_1_full_status = 0
            nearby_station_2_full_status = 0
        else:
            target_station_full_status = 0

        if target_station_empty_status == 0:
            if this_record.bike1 == 0 or pd.isnull(this_record.bike1):
                nearby_station_1_empty_status = 1
            else:
                nearby_station_1_empty_status = 0
        if target_station_full_status == 0:
            if this_record.dock1 == 0 or pd.isnull(this_record.dock1):
                nearby_station_1_full_status = 1
            else:
                nearby_station_1_full_status = 0

        if target_station_empty_status == 0:
            if this_record.bike2 == 0 or pd.isnull(this_record.bike2):
                nearby_station_2_empty_status = 1
            else:
                nearby_station_2_empty_status = 0
        if target_station_full_status == 0:
            if this_record.dock2 == 0 or pd.isnull(this_record.dock2):
                nearby_station_2_full_status = 1
            else:
                nearby_station_2_full_status = 0

        if this_time.hour == last_time.hour and ((this_time.minute<=30 and last_time.minute<=30) or (this_time.minute>30 and last_time.minute>30)):
                pickup_demand += thispick
                dropoff_demand += thisdrop
                status_empty_indicator[
                    target_station_empty_status, nearby_station_1_empty_status, nearby_station_2_empty_status] += time_duration
                status_full_indicator[
                    target_station_full_status, nearby_station_1_full_status, nearby_station_2_full_status] += time_duration

        else:
            if last_time.minute<=30:
                last_period=1
            else:
                last_period=2
            aggregate_table.loc[jj] = [target_station, nearby_station_id_1, nearby_station_id_2, last_time.date(), last_time.hour,last_period,
                                       pickup_demand, dropoff_demand] + [status_empty_indicator[rows] for rows in
                                                                         status] + [status_full_indicator[rows] for rows
                                                                                    in status]
            if this_time.hour == last_time.hour:
                time_duration = this_time.minute-30
            else:
                time_duration = this_time.minute

            for row in status:
                status_empty_indicator[row] = 0
                status_full_indicator[row] = 0
            status_empty_indicator[
                target_station_empty_status, nearby_station_1_empty_status, nearby_station_2_empty_status] += time_duration
            status_full_indicator[
                target_station_full_status, nearby_station_1_full_status, nearby_station_2_full_status] += time_duration

            if next_time.hour == this_time.hour:
                if next_time.minute <= 30 and this_time.minute <= 30:
                    time_duration = int((next_time - this_time).seconds / 60)
                elif next_time.minute > 30 and this_time.minute <= 30:
                    time_duration = 30 - this_time.minute
                elif next_time.minute > 30 and this_time.minute > 30:
                    time_duration = int((next_time - this_time).seconds / 60)
            else:
                time_duration = 60 - this_time.minute

            jj += 1
            pickup_demand = 0
            dropoff_demand = 0
            pickup_demand += thispick
            dropoff_demand += thisdrop

            status_empty_indicator[
                target_station_empty_status, nearby_station_1_empty_status, nearby_station_2_empty_status] += time_duration
            status_full_indicator[
                target_station_full_status, nearby_station_1_full_status, nearby_station_2_full_status] += time_duration

            last_time = this_time
    directory = 'Station' + str(target_station)
    if directory not in os.listdir('../data/1-DemandData/'):
        os.mkdir('../data/1-DemandData/' + directory)
    aggregate_table.to_csv(
        '../data/1-DemandData/Station' + str(target_station) + '/AggregatedStation_' + mm + '_' + str(
            target_station) + '.csv', index=False)


def process_1ns(mm, target_station, nearby):
    target_station_data = pd.read_csv('../data/0-RawData/' + mm + '/Station_' + str(target_station) + '.csv',
                                      usecols=['datetime', 'pickup', 'dropoff', 'bike', 'dock'])
    target_station_data.datetime = pd.to_datetime(target_station_data['datetime'], format="%Y/%m/%d %H:%M:%S")
    target_station_data.set_index('datetime')
    nearby_station_1 = pd.read_csv('../data/0-RawData/' + mm + '/Station_' + str(nearby[0]) + '.csv',
                                   usecols=['datetime', 'bike', 'dock'])
    nearby_station_1.columns = ['datetime', 'bike1', 'dock1']
    nearby_station_1.datetime = pd.to_datetime(target_station_data['datetime'], format="%Y/%m/%d %H:%M:%S")
    nearby_station_1.set_index('datetime')
    result = pd.merge(target_station_data, nearby_station_1, how='left', on='datetime')

    nearby_station_id_1 = nearby[0]
    status_empty_indicator = {}
    status_full_indicator = {}
    status = list(itertools.product([0, 1], repeat=len(nearby) + 1))
    for row in status:
        status_empty_indicator[row] = 0
        status_full_indicator[row] = 0

    aggregate_table = pd.DataFrame(
        columns=['target_station_id', 'nearby_station_id_1', 'date','hour','period', 'pickup', 'dropoff'] + ['is_empty_' + str(rows)
                                                                                                 for rows in status] + [
                    'is_full_' + str(rows) for rows in status])

    # in case empty input
    if len(target_station_data) == 0:
        directory = 'Station' + str(target_station)
        if directory not in os.listdir('../data/1-DemandData'):
            os.mkdir('../data/1-DemandData/' + directory)
        aggregate_table.to_csv('../data/1-DemandData/Station'+str(target_station)+'/AggregatedStation_'+mm+'_' + str(target_station) + '.csv', index=False)


    jj = 0
    i = 0
    pickup_demand = 0
    dropoff_demand = 0
    this_record = result.iloc[0]
    last_time = this_record.datetime

    for i in range(len(result) - 1):
        this_record = result.iloc[i]
        this_time = this_record.datetime

        next_record = result.iloc[i + 1]
        next_time = next_record.datetime

        if next_time.hour == this_time.hour:
            if next_time.minute <= 30 and this_time.minute <= 30:
                time_duration = int((next_time - this_time).seconds / 60)
            elif next_time.minute > 30 and this_time.minute <= 30:
                time_duration = 30 - this_time.minute
            elif next_time.minute > 30 and this_time.minute > 30:
                time_duration = int((next_time - this_time).seconds / 60)
        else:
            time_duration = 60 - this_time.minute

        thispick = this_record.pickup
        thisdrop = this_record.dropoff
        if this_record.bike == 0 and thispick == 0:
            target_station_empty_status = 1  # it is empty
            nearby_station_1_empty_status = 0
        else:
            target_station_empty_status = 0
        if this_record.dock == 0 and thisdrop == 0:
            target_station_full_status = 1
            nearby_station_1_full_status = 0
        else:
            target_station_full_status = 0

        if target_station_empty_status == 0:
            if this_record.bike1 == 0 or pd.isnull(this_record.bike1):
                nearby_station_1_empty_status = 1
            else:
                nearby_station_1_empty_status = 0
        if target_station_full_status == 0:
            if this_record.dock1 == 0 or pd.isnull(this_record.dock1):
                nearby_station_1_full_status = 1
            else:
                nearby_station_1_full_status = 0

        if this_time.hour == last_time.hour and ((this_time.minute<=30 and last_time.minute<=30) or (this_time.minute>30 and last_time.minute>30)):
            pickup_demand += thispick
            dropoff_demand += thisdrop

            status_empty_indicator[target_station_empty_status, nearby_station_1_empty_status] += time_duration
            status_full_indicator[target_station_full_status, nearby_station_1_full_status] += time_duration

        else:
            if last_time.minute<=30:
                last_period=1
            else:
                last_period=2
            aggregate_table.loc[jj] = [target_station, nearby_station_id_1, last_time.date(), last_time.hour,last_period, pickup_demand,
                                       dropoff_demand] + [status_empty_indicator[rows] for rows in status] + [
                                          status_full_indicator[rows] for rows in status]
            if this_time.hour == last_time.hour:
                time_duration = this_time.minute - 30
            else:
                time_duration = this_time.minute

            for row in status:
                status_empty_indicator[row] = 0
                status_full_indicator[row] = 0
            status_empty_indicator[target_station_empty_status, nearby_station_1_empty_status] += time_duration
            status_full_indicator[target_station_full_status, nearby_station_1_full_status] += time_duration

            if next_time.hour == this_time.hour:
                if next_time.minute <= 30 and this_time.minute <= 30:
                    time_duration = int((next_time - this_time).seconds / 60)
                elif next_time.minute > 30 and this_time.minute <= 30:
                    time_duration = 30 - this_time.minute
                elif next_time.minute > 30 and this_time.minute > 30:
                    time_duration = int((next_time - this_time).seconds / 60)
            else:
                time_duration = 60 - this_time.minute

            jj += 1
            pickup_demand = 0
            dropoff_demand = 0
            pickup_demand += thispick
            dropoff_demand += thisdrop
            if this_record.bike == 0 and thispick == 0:
                target_station_empty_status = 1  # it is empty
                nearby_station_1_empty_status = 0
            else:
                target_station_empty_status = 0
            if this_record.dock == 0 and thisdrop == 0:
                target_station_full_status = 1
                nearby_station_1_full_status = 0
            else:
                target_station_full_status = 0

            if target_station_empty_status == 0:
                if this_record.bike1 == 0 or pd.isnull(this_record.bike1):
                    nearby_station_1_empty_status = 1
                else:
                    nearby_station_1_empty_status = 0
            if target_station_full_status == 0:
                if this_record.dock1 == 0 or pd.isnull(this_record.dock1):
                    nearby_station_1_full_status = 1
                else:
                    nearby_station_1_full_status = 0

            status_empty_indicator[target_station_empty_status, nearby_station_1_empty_status] += time_duration
            status_full_indicator[target_station_full_status, nearby_station_1_full_status] += time_duration

            last_time = this_time
    directory = 'Station' + str(target_station)
    if directory not in os.listdir('../data/1-DemandData'):
        os.mkdir('../data/1-DemandData/' + directory)
    aggregate_table.to_csv(
        '../data/1-DemandData/Station' + str(target_station) + '/AggregatedStation_' + mm + '_' + str(
            target_station) + '.csv', index=False)


def process_0ns(mm, target_station, nearby):
    target_station_data = pd.read_csv('../data/0-RawData/' + mm + '/Station_' + str(target_station) + '.csv',
                                      usecols=['datetime', 'pickup', 'dropoff', 'bike', 'dock'])
    target_station_data.datetime = pd.to_datetime(target_station_data['datetime'], format="%Y/%m/%d %H:%M:%S")
    result = target_station_data

    status_empty_indicator = {}
    status_full_indicator = {}
    status = [0, 1]
    for row in status:
        status_empty_indicator[row] = 0
        status_full_indicator[row] = 0

    aggregate_table = pd.DataFrame(
        columns=['target_station_id', 'date','hour','period', 'pickup', 'dropoff'] + ['is_empty_' + str(rows) for rows in
                                                                          status] + ['is_full_' + str(rows) for rows in
                                                                                     status])

    # in case empty input
    if len(target_station_data) == 0:
        directory = 'Station' + str(target_station)
        if directory not in os.listdir('../data/1-DemandData'):
            os.mkdir('../data/1-DemandData/' + directory)
        aggregate_table.to_csv(
            '../data/1-DemandData/Station' + str(target_station) + '/AggregatedStation_' + mm + '_' + str(
                target_station) + '.csv', index=False)
        return

    jj = 0
    i = 0
    pickup_demand = 0
    dropoff_demand = 0
    this_record = result.iloc[0]
    last_time = this_record.datetime
    last_time = datetime(last_time.year, last_time.month, last_time.day, last_time.hour)

    for i in range(len(result) - 1):
        this_record = result.iloc[i]
        this_time = this_record.datetime

        next_record = result.iloc[i + 1]
        next_time = next_record.datetime

        if next_time.hour == this_time.hour:
            if next_time.minute <= 30 and this_time.minute <= 30:
                time_duration = int((next_time - this_time).seconds / 60)
            elif next_time.minute > 30 and this_time.minute <= 30:
                time_duration = 30 - this_time.minute
            elif next_time.minute > 30 and this_time.minute > 30:
                time_duration = int((next_time - this_time).seconds / 60)
        else:
            time_duration = 60 - this_time.minute

        thispick = this_record.pickup
        thisdrop = this_record.dropoff
        if this_record.bike == 0 and thispick == 0:
            target_station_empty_status = 1  # it is empty
        else:
            target_station_empty_status = 0
        if this_record.dock == 0 and thisdrop == 0:
            target_station_full_status = 1
        else:
            target_station_full_status = 0

        if this_time.hour == last_time.hour and ((this_time.minute<=30 and last_time.minute<=30) or (this_time.minute>30 and last_time.minute>30)):
            pickup_demand += thispick
            dropoff_demand += thisdrop


            status_empty_indicator[target_station_empty_status] += time_duration
            status_full_indicator[target_station_full_status] += time_duration

        else:
            if last_time.minute<=30:
                last_period=1
            else:
                last_period=2
            aggregate_table.loc[jj] = [target_station, last_time.date(), last_time.hour,last_period, pickup_demand, dropoff_demand] + [
                status_empty_indicator[rows] for rows in status] + [status_full_indicator[rows] for rows in status]
            if this_time.hour == last_time.hour:
                time_duration = this_time.minute - 30
            else:
                time_duration = this_time.minute
            for row in status:
                status_empty_indicator[row] = 0
                status_full_indicator[row] = 0
            status_empty_indicator[target_station_empty_status] += time_duration
            status_full_indicator[target_station_full_status] += time_duration

            if next_time.hour == this_time.hour:
                if next_time.minute <= 30 and this_time.minute <= 30:
                    time_duration = int((next_time - this_time).seconds / 60)
                elif next_time.minute > 30 and this_time.minute <= 30:
                    time_duration = 30 - this_time.minute
                elif next_time.minute > 30 and this_time.minute > 30:
                    time_duration = int((next_time - this_time).seconds / 60)
            else:
                time_duration = 60 - this_time.minute

            jj += 1
            pickup_demand = 0
            dropoff_demand = 0
            pickup_demand += thispick
            dropoff_demand += thisdrop
            if this_record.bike == 0 and thispick == 0:
                target_station_empty_status = 1  # it is empty
            else:
                target_station_empty_status = 0
            if this_record.dock == 0 and thisdrop == 0:
                target_station_full_status = 1
            else:
                target_station_full_status = 0

            status_empty_indicator[target_station_empty_status] += time_duration
            status_full_indicator[target_station_full_status] += time_duration

            last_time = this_time
    directory = 'Station' + str(target_station)
    if directory not in os.listdir('../data/1-DemandData'):
        os.mkdir('../data/1-DemandData/' + directory)
    aggregate_table.to_csv(
        '../data/1-DemandData/Station' + str(target_station) + '/AggregatedStation_' + mm + '_' + str(
            target_station) + '.csv', index=False)


# Static: list of investigating months
mm_list = ["2017-0" + str(i) for i in range(1, 4)]
# mm_list = ["2016-0" + str(i) for i in range(6, 10)] + ["2016-" + str(i) for i in range(10, 13)]
# mm_list = mm_list + ["2017-0" + str(i) for i in range(1, 8)]

# Static: read nearby table
nearby_table = pd.read_csv('../data/0-RawData/nearby_stations.csv', index_col=0)

kkk=0
for target_station in list(nearby_table.index):
    print(target_station)
    if target_station>=3085:
        begin_time = datetime.now()
        row = nearby_table.loc[target_station]
        if row[0] == 0:
            nearby = []
        elif row[0] == 1:
            nearby = [int(row[1])]
        elif row[0] == 2:
            nearby = [int(row[1]), int(row[2])]
        for mm in mm_list:
            nearby_mm = nearby
            for item in nearby_mm:
                path = '../' + mm + '/Station_' + str(item) + '.csv'
                # if os.stat(path).st_size == 58: #That is no available record
                #     nearby_mm.remove(item) #temporarily removed from the nearby-station list
            if len(nearby_mm) == 0:
                process_0ns(mm, target_station, nearby_mm)
            elif len(nearby_mm) == 1:
                process_1ns(mm, target_station, nearby_mm)
            elif len(nearby_mm) == 2:
                process_2ns(mm, target_station, nearby_mm)
        end_time = datetime.now()
