import datetime
import json

# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    with open('Zeitachse.json', 'r') as file:
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
    print(new_list)


