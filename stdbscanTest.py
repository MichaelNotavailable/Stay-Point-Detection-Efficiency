import csv

import gpxpy
import pandas as pd
import skmob
import datetime
import numpy as np
import itertools

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


def read_gpx(file):
    gpx_file = open(file, 'r')
    gpx = gpxpy.parse(gpx_file)
    data = []
    for track in gpx.tracks:
        for segment in track.segments:
            for point in segment.points:
                data.append([point.latitude, point.longitude, point.time, point.elevation])
    return data





def data_for_stdbscan(data):
    """
    ST_DBSCAN benötigt ein Array, wo das erste Element die Zeit als float ist.
    Das zweite Element ist latitude, das dritte Element longitude.
    """
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


# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    gps_log_list = read_gpx('04.11.2024_16_08.gpx')
    #gps_log_list = read_gpx()
    data_for_stdbscan = data_for_stdbscan(gps_log_list)
    df = pd.DataFrame(data_for_stdbscan, columns=['lat', 'lng', 'datetime'])

    epsilon = np.linspace(0.0001, 0.0009, 9)
    time_samples = np.arange(50, 901)
    min_samples = np.arange(30, 100)
    combinations = list(itertools.product(epsilon, time_samples, min_samples))

    for i, (eps, time_samples, min_samples) in enumerate(combinations):
        st_dbscan3 = ST_DBSCAN3(eps, 50, min_samples)
        labels = st_dbscan3.fit(df).labels
        n_clusters = len(set(labels)) - (1 if -1 in labels else 0)
        if 4 >= n_clusters >= 3:
            print(f"{i}. eps: {eps}, Zeit: {time_samples}, min_samples: {min_samples}. Die Anzahl der Cluster beträgt: {n_clusters}")
