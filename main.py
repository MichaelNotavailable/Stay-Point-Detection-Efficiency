
import json
import skmob
import gpxpy
import datetime
from sklearn.cluster import DBSCAN

from CBSmot2 import CBSmot2
from CBSMoT import CBSMoT
from stayPointDetection_density import StayPointDetection_density
from stayPointDetection_basic import StayPointDetection_basic
import pandas as pd

from stdbscan3 import ST_DBSCAN3

# Press Umschalt+F10 to execute it or replace it with your code.
# Press Double Shift to search everywhere for classes, files, tool windows, actions, and settings.


lat = []
longg = []


def read_gpx(data_path):
    gpx_file = open(data_path, 'r')
    gpx = gpxpy.parse(gpx_file)
    data = []
    for track in gpx.tracks:
        for segment in track.segments:
            for point in segment.points:
                data.append([point.latitude, point.longitude, point.time, point.elevation])
    return data


def read_google_timeline(data_path):
    with open(data_path, 'r') as file:
        data = json.load(file)

    new_list = []
    i = 0
    while i < len(data['rawSignals']):
        if 'position' in data['rawSignals'][i]:
            latlong = data['rawSignals'][i]['position']['LatLng'].split("°,")
            latitude = float(latlong[0])
            longitude = float(latlong[1].replace('°', ''))
            time = datetime.datetime.strptime(data['rawSignals'][i]['position']['timestamp'], '%Y-%m-%dT%H:%M:%S.%f%z')
            new_list.append([latitude, longitude, time])
        i += 1
    return new_list



def dbscan(gps_log):
    X = []
    i = 0
    while i < len(gps_log):
        X.append([])
        X[i].append(gps_log[i][0])
        X[i].append(gps_log[i][1])
        i += 1

    db = DBSCAN(eps=0.001, min_samples=90).fit(X)
    labels = db.labels_
    return labels


def stdbscan(gps_log):
    """
    Für ST-DBSCAN wird das Date-Objekt in ein float umgewandelt.
    Es soll in der Liste an erster Stelle stehen.
    Anschließend wird die Liste in ein pandas Dataframe umgewandelt.
    """
    X = []
    i = 0
    while i < len(gps_log):
        X.append([])

        X[i].append(gps_log[i][2].timestamp())

        X[i].append(gps_log[i][0])
        X[i].append(gps_log[i][1])
        i += 1
    df = pd.DataFrame(X, columns=['datetime', 'lat', 'lng'])
    st_dbscan3 = ST_DBSCAN3(0.0003, 400, 80)
    labels = st_dbscan3.fit(df).labels
    return labels


def add_arrival_departure_time(gps_log_list, labels):
    """
    Erstellt einen neuen Log, der Ankunftszeit und Abfahrtszeit zu jedem Cluster hinzufügt
    :param gps_log_list: Eine Liste mit Längengrade, Breitengrade und Zeit
    :param labels: Labels die ein Cluster-Algorithmus erstellt hat
    :return: Gibt eine neue Liste zurück mit Längengrade, Breitengrade, Ankunftszeit, Abfahrtzeit, Label und Zeit der
    Aufnahme
    """
    new_log = []
    n_clusters = len(set(labels)) - (1 if -1 in labels else 0)
    cluster_index = 0
    while cluster_index < n_clusters:
        cluster_list = []
        i = 0
        for row in gps_log_list:
            if labels[i] == cluster_index:
                cluster_list.append([row[0], row[1], row[2], labels[i]])
            i += 1

        arrival_time = cluster_list[0][2]
        depature_time = cluster_list[len(cluster_list) - 1][2]

        for row in cluster_list:
            new_log.append([row[0], row[1], arrival_time, depature_time, row[2], row[3]])
        cluster_index += 1

    # Punkte die keinem Cluster zugewiesen werden (-1) sollen auch hinzugefügt werden,
    # damit sie auch auf der Karte dargestellt werden
    i = 0
    for row in gps_log_list:
        if labels[i] == -1:
            new_log.append([row[0], row[1], row[2], row[2], row[2], labels[i]])
        i += 1

    return new_log


# Press the green button in the gutter to run the script.
if __name__ == '__main__':


    # Die Standortpunkte können aus einer GPX Datei gelesen werden,
    # oder aus der json Datei die von Google Timeline exportiert werden kann

    #gpx = read_google_timeline('Zeitachse.json')

    gpx = read_gpx('09.11.2024_14_15.gpx')

    #DBSCAN wird aufgerufen,
    # das Ergebnis wird in eine Karte auf einer HTML Datei gespeichert
    labels = dbscan(gpx)
    new_gpx = add_arrival_departure_time(gpx, labels)
    tdf = skmob.TrajDataFrame(new_gpx, latitude=0, longitude=1, datetime=2)
    tdf.rename(columns={3: 'leaving_datetime'}, inplace=True)
    tdf.rename(columns={5: 'cluster'}, inplace=True)
    map_f = tdf.plot_stops()
    map_f.save("DBSCAN Algorithmus" + ".html")

    # ST-DBSCAN wird aufgerufen,
    # das Ergebnis wird in eine Karte auf einer HTML Datei gespeichert
    labels = stdbscan(gpx)
    new_gpx = add_arrival_departure_time(gpx, labels)
    tdf = skmob.TrajDataFrame(new_gpx, latitude=0, longitude=1, datetime=2)
    tdf.rename(columns={3: 'leaving_datetime'}, inplace=True)
    tdf.rename(columns={5: 'cluster'}, inplace=True)
    map_f = tdf.plot_stops()
    map_f.save("ST-DBSCAN Algorithmus" + ".html")

    # Der Stay Point Detection Algorithmus von Li et al.  wird aufgerufen,
    # das Ergebnis wird in eine Karte auf einer HTML Datei gespeichert
    stay_point_detection_basic = StayPointDetection_basic()
    tdf = skmob.TrajDataFrame(gpx, latitude=0, longitude=1, datetime=2)
    stayPointCenter, stayPoint = stay_point_detection_basic.stayPointExtraction(tdf, 200,
                                                                                datetime.timedelta(minutes=15))
    tdf = skmob.TrajDataFrame(stayPointCenter, latitude=0, longitude=1, datetime=2)
    tdf.rename(columns={3: 'leaving_datetime'}, inplace=True)
    map_f = tdf.plot_stops()
    map_f.save("Stay Point Detection Basic Algorithmus" + ".html")

    # Die Verbesserung des Stay Point Algorithmus von Yuan et al. wird aufgerufen,
    # das Ergebnis wird in eine Karte auf einer HTML Datei gespeichert
    stay_point_detection_density = StayPointDetection_density()
    tdf = skmob.TrajDataFrame(gpx, latitude=0, longitude=1, datetime=2)
    stayPointCenter, stayPoint = stay_point_detection_density.stayPointExtraction(tdf, 200,
                                                                                  datetime.timedelta(minutes=15))
    tdf = skmob.TrajDataFrame(stayPointCenter, latitude=0, longitude=1, datetime=2)
    tdf.rename(columns={3: 'leaving_datetime'}, inplace=True)
    map_f = tdf.plot_stops()
    map_f.save("Stay Point Detection Density Algorithmus" + ".html")

    cbsmot = CBSMoT()
    tdf = skmob.TrajDataFrame(gpx, latitude=0, longitude=1, datetime=2)
    cbsmot_result = cbsmot.cbsmot(tdf, datetime.timedelta(minutes=15), max_average_speed=2.0)
    stops = []
    for stop in cbsmot_result:
        stops.append(stop.trajectories[0])
        if len(stops) > 0:
            tdf = skmob.TrajDataFrame(stops, latitude=0, longitude=1, datetime=2)
            map_f = tdf.plot_stops()
            map_f.save('CB-SMoT Algorithmus' + ".html")
