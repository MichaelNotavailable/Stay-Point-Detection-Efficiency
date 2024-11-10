# Press the green button in the gutter to run the script.
import csv
import datetime
import numpy as np
import itertools
import skmob

from CBSMoT import CBSMoT


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
                gps_log[i].append(row[5] + ' ' + row[6])
                i += 1
            line_num += 1

    return gps_log


if __name__ == '__main__':
    cbsmot = CBSMoT()
    gpx = read_geolife('GeoLifeTest/20090403011657.plt')
    tdf = skmob.TrajDataFrame(gpx, latitude=0, longitude=1, datetime=2)

    minutes = np.arange(10, 30)
    max_average_speed = np.arange(1, 50)

    combinations = list(itertools.product(minutes, max_average_speed))

    for i, (min, speed) in enumerate(combinations):
        cbsmot_result = cbsmot.cbsmot(tdf, datetime.timedelta(minutes=float(min)), max_average_speed=speed)
        n_stops = len(cbsmot_result)
        if 4 >= n_stops >= 2:
            print(f"{i}. Minuten: {min}, max_average_speed: {speed}. Die Anzahl der Stopps beträgt: {n_stops}")


