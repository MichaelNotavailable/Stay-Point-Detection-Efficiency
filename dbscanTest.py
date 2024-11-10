import csv

import gpxpy
from sklearn.cluster import DBSCAN
import numpy as np
import itertools


def read_gpx(data_path):
    gpx_file = open(data_path, 'r')
    gpx = gpxpy.parse(gpx_file)
    data = []
    for track in gpx.tracks:
        for segment in track.segments:
            for point in segment.points:
                data.append([point.latitude, point.longitude])
    return data


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

                i += 1
            line_num += 1

    return gps_log


def dbscan(gps_log):
    db = DBSCAN(eps=50, min_samples=100).fit(gps_log)
    labels = db.labels_
    n_clusters_ = len(set(labels)) - (1 if -1 in labels else 0)
    n_noise_ = list(labels).count(-1)
    return labels


# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    gps_log = read_gpx('04.11.2024_16_08.gpx')

    epsilon = np.linspace(0.001, 0.01, 100)
    min_samples = np.arange(1, 1000)

    combinations = list(itertools.product(epsilon, min_samples))

    for i, (eps, min_samples) in enumerate(combinations):
        db = DBSCAN(eps=eps, min_samples=min_samples).fit(gps_log)
        labels = db.labels_
        n_clusters = len(set(labels)) - (1 if -1 in labels else 0)
        if 4 >= n_clusters >= 3:
            print(f"{i}. eps: {eps}, min_samples: {min_samples}. Die Anzahl der Cluster beträgt: {n_clusters}")
