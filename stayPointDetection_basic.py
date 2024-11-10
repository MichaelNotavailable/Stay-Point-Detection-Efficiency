from math import radians, cos, sin, asin, sqrt


# structure of point
class Point:
    def __init__(self, latitude, longitude, dateTime, arriveTime, leaveTime):
        self.latitude = latitude
        self.longitude = longitude
        self.dateTime = dateTime
        self.arriveTime = arriveTime
        self.leaveTime = leaveTime


class StayPointDetection_basic:

    # calculate distance between two points from their coordinate
    def getDistanceOfPoints(self, pi, pj):
        lat1, lon1, lat2, lon2 = list(map(radians, [float(pi.latitude), float(pi.longitude),
                                                    float(pj.latitude), float(pj.longitude)]))
        dlon = lon2 - lon1
        dlat = lat2 - lat1
        a = sin(dlat / 2) ** 2 + cos(lat1) * cos(lat2) * sin(dlon / 2) ** 2
        c = 2 * asin(sqrt(a))
        m = 6371000 * c
        return m

    # calculate time interval between two points
    def getTimeIntervalOfPoints(self, pi, pj):
        t_i = pi.dateTime
        t_j = pj.dateTime
        return t_j - t_i

    # compute mean coordinates of a group of points
    def computMeanCoord(self, gpsPoints):
        lat = 0.0
        lon = 0.0
        for point in gpsPoints:
            lat += float(point.latitude)
            lon += float(point.longitude)
        return (lat / len(gpsPoints), lon / len(gpsPoints))

    # extract stay points from a GPS log file
    # input:
    #        file: the name of a GPS log file
    #        distThres: distance threshold
    #        timeThres: time span threshold
    # default values of distThres and timeThres are 200 m and 30 min respectively, according to [1]
    def stayPointExtraction(self, data, distThres=200, timeThres=30 * 60):
        points = self.parseGeoTxt(data)
        stayPointList = []
        stayPointCenterList = []
        pointNum = len(points)
        i = 0
        while i < pointNum:
            j = i + 1
            while j < pointNum:
                if self.getDistanceOfPoints(points[i], points[j]) > distThres:
                    # points[j] has gone out of bound thus it should not be counted in the stay points.
                    if self.getTimeIntervalOfPoints(points[i], points[j - 1]) > timeThres:
                        latitude, longitude = self.computMeanCoord(points[i:j])
                        arriveTime = points[i].dateTime
                        leaveTime = points[j - 1].dateTime
                        stayPointCenterList.append([latitude, longitude, arriveTime, leaveTime])
                        stayPointList.extend(points[i:j])
                    break
                j += 1
            i = j
        return stayPointCenterList, stayPointList

    # parse lines into points
    def parseGeoTxt(self, lines):
        points = []
        latitudelist = list(lines['lat'])
        longitudelist = list(lines['lng'])
        daylist = list(lines['datetime'])
        pointNum = len(lines)

        i = 0
        while i < pointNum:
            latitude = latitudelist[i]
            longitude = longitudelist[i]
            dateTime = daylist[i]
            points.append(Point(latitude, longitude, dateTime, 0, 0))
            i += 1
        return points
