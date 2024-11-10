import csv
import datetime
import glob
import pandas as pd

import skmob
from sklearn.cluster import DBSCAN

from CBSMoT import CBSMoT
from CBSmot2 import CBSmot2
from stayPointDetection_basic import StayPointDetection_basic
from stayPointDetection_density import StayPointDetection_density
from stdbscan3 import ST_DBSCAN3


def read_geolife(data_path):
    gps_log = []
    with open(data_path, mode='r') as file:
        reader = csv.reader(file)
        line_num = 1
        i = 0
        for row in reader:
            if line_num > 6:  # die Daten beginnen ab der 7. Zeile
                gps_log.append([])
                gps_log[i].append(float(row[0]))
                gps_log[i].append(float(row[1]))
                date = datetime.datetime.strptime(row[5] + ' ' + row[6], '%Y-%m-%d %H:%M:%S')
                gps_log[i].append(date)
                i += 1
            line_num += 1

    return gps_log


def staypointdetection_basic(directories):
    print('Hier ist die Anzahl der Daten:')
    print(len(directories))
    stay_point_detection = StayPointDetection_basic()
    stayPointCenterAll = []
    numOfFiles = 0
    i = 0
    while i < len(directories):
        gps_log_list = read_geolife(directories[i])
        tdf = skmob.TrajDataFrame(gps_log_list, latitude=0, longitude=1, datetime=2)
        print(f'Arbeitet an Datei: {directories[i]}')
        stayPointCenter, stayPoint = stay_point_detection.stayPointExtraction(tdf, 200,
                                                                              datetime.timedelta(minutes=30))
        stayPointCenterAll += stayPointCenter
        print(f'Anzahl der Stay Points: {len(stayPointCenterAll)}')
        numOfFiles += 1
        print(f'Abgeschlossen: {numOfFiles}')
        i += 1

    print("Anzahl aller Stay Points: ")
    print(len(stayPointCenterAll))


def staypointdetection_density(directories):
    print('Hier ist die Anzahl der Daten:')
    print(len(directories))
    stay_point_detection = StayPointDetection_density()
    stayPointCenterAll = []
    numOfFiles = 0
    i = 0
    while i < len(directories):
        gps_log_list = read_geolife(directories[i])
        tdf = skmob.TrajDataFrame(gps_log_list, latitude=0, longitude=1, datetime=2)
        print(f'Arbeitet an Datei: {directories[i]}')
        stayPointCenter, stayPoint = stay_point_detection.stayPointExtraction(tdf, 200,
                                                                              datetime.timedelta(minutes=30))
        stayPointCenterAll += stayPointCenter
        print(f'Anzahl der Stay Points: {len(stayPointCenterAll)}')
        numOfFiles += 1
        print(f'Abgeschlossen: {numOfFiles}')
        i += 1

    print("Anzahl aller Stay Points: ")
    print(len(stayPointCenterAll))


def cbsmot(directories):
    print('Hier ist die Anzahl der Daten:')
    print(len(directories))
    cbsmot = CBSmot2()
    stayPointCenterAll = []
    numOfFiles = 0
    i = 0
    while i < len(directories):
        gps_log_list = read_geolife(directories[i])
        tdf = skmob.TrajDataFrame(gps_log_list, latitude=0, longitude=1, datetime=2)
        print(f'Arbeitet an Datei: {directories[i]}')
        cbsmot_result = cbsmot.find_stops(tdf, 50, 5, 5, 50)
        stayPointCenterAll += cbsmot_result
        print(f'Anzahl der Stay Points: {len(stayPointCenterAll)}')
        numOfFiles += 1
        print(f'Abgeschlossen: {numOfFiles}')
        i += 1

    print("Anzahl aller Stay Points: ")
    print(len(stayPointCenterAll))


def dbscan(directories):
    print('Hier ist die Anzahl der Daten:')
    print(len(directories))
    numOfFiles = 0
    stayPointCenterAll = 0
    db = DBSCAN(eps=80, min_samples=100)
    i = 0
    while i < len(directories):
        gps_log_list = read_geolife(directories[i])
        latlong = []
        j = 0
        while j < len(gps_log_list):
            latlong.append([])
            latlong[j].append(gps_log_list[j][0])
            latlong[j].append(gps_log_list[j][1])
            j += 1
        print(f'Arbeitet an Datei: {directories[i]}')
        db.fit(latlong)
        labels = db.labels_
        n_clusters = len(set(labels)) - (1 if -1 in labels else 0)
        stayPointCenterAll += n_clusters
        print(f'Anzahl der Cluster: {stayPointCenterAll}')
        numOfFiles += 1
        print(f'Abgeschlossen: {numOfFiles}')
        i += 1

    print("Anzahl aller Cluster:")
    print(stayPointCenterAll)

"""
ST_DBSCAN benötigt ein Array, wo das erste Element die Zeit als float ist.
Das zweite Element ist latitude, das dritte Element longitude.
"""
def data_for_stdbscan(data):
    newdata = []
    i = 0
    while i < len(data):
        newdata.append([])
        # Wandelt das Date-Objekt in ein float um.
        newdata[i].append(data[i][2].timestamp())

        newdata[i].append(data[i][0])
        newdata[i].append(data[i][1])
        i += 1
    return newdata

def stdbscan3(directories):
    print('Hier ist die Anzahl der Daten:')
    print(len(directories))
    numOfFiles = 0
    stayPointCenterAll = 0
    st_dbscan = ST_DBSCAN3(50, 970, 70)
    i = 0
    while i < len(directories):
        gps_log_list = read_geolife(directories[i])
        data = data_for_stdbscan(gps_log_list)
        df = pd.DataFrame(data, columns=['datetime', 'lat', 'lng'])
        print(f'Arbeitet an Datei: {directories[i]}')
        labels = st_dbscan.fit(df).labels

        n_clusters = len(set(labels)) - (1 if -1 in labels else 0)
        stayPointCenterAll += n_clusters
        print(f'Anzahl der Cluster: {stayPointCenterAll}')
        numOfFiles += 1
        print(f'Abgeschlossen: {numOfFiles}')
        i += 1

    print("Anzahl aller Cluster:")
    print(stayPointCenterAll)


# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    #directories = glob.glob('/home/michael/PycharmProjects/staypointDetectionWithGPX/GeoLifeTest/*')
    directories = glob.glob('/home/michael/PycharmProjects/staypointDetectionWithGPX/Geolife Trajectories '
                            '1.3/Data/*/Trajectory/*')

    #staypointdetection_basic(directories)
    #staypointdetection_density(directories)
    #dbscan(directories)
    cbsmot(directories)
    #stdbscan(directories)
    #stdbscan3(directories)
