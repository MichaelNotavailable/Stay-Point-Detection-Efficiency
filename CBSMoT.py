import math
from math import radians, cos, sin, asin, sqrt


class Stop(object):
    def __init__(self):
        self.trajectories = []
        self.init_time = None
        self.delta_time = 0.0
        self.last_time = None
        self.dist = 0.0

    def add(self, trajectory, dist):
        self.dist += dist
        if self.init_time is None:
            self.init_time = trajectory[2]
        else:
            self.delta_time += (trajectory[2] - self.last_time).total_seconds()
        self.trajectories.append(trajectory)
        self.last_time = trajectory[2]


class CBSMoT:

    def haversine(self, lon1, lat1, lon2, lat2):
        lon1, lat1, lon2, lat2 = map(radians, [lon1, lat1, lon2, lat2])

        dlon = lon2 - lon1
        dlat = lat2 - lat1
        a = sin(dlat / 2) ** 2 + cos(lat1) * cos(lat2) * sin(dlon / 2) ** 2
        c = 2 * asin(sqrt(a))
        r = 6371
        return c * r

    def distance_absolute(self, lat1, lon1, lat2, lon2):
        return self.haversine(lon1, lat1, lon2, lat2) * 1000

    def average_speed(self, dist, delta_time):
        return dist / delta_time

    def delta_time(self, a, b):
        return (a - b).total_seconds()

    def cbsmot(self, trajectories, min_time, max_average_speed):
        stops = []
        trajectories = list(trajectories.values)
        previous = trajectories[0]
        stop = None
        for trajectory in trajectories[1:]:
            dt = self.delta_time(trajectory[2], previous[2])
            if dt > 0:
                dist = self.distance_absolute(trajectory[0], trajectory[1], previous[0], previous[1])
                average_s = self.average_speed(dist, dt)
                if dt < 20.0 and average_s < max_average_speed:
                    if stop is None:
                        stop = Stop()
                        stop.add(previous, 0)
                    stop.add(trajectory, dist)
                else:
                    if stop and stop.delta_time > min_time.total_seconds():
                        stops.append(stop)
                    stop = None
                previous = trajectory
        return stops
