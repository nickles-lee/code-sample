import time
import math
import geopy
import ujson as json
from geographiclib.geodesic import Geodesic
from geopy.distance import vincenty
import requests
from datetime import datetime


__author__ = 'nick'

RAIL_POLYMAP_CACHE = {}
RAIL_VECTOR_CACHE = {}

def bearing(latitude_1, longitude_1, latitude_2, longitude_2):
        """
       Calculation of direction between two geographical points
       """
        rlat1 = math.radians(latitude_1)
        rlat2 = math.radians(latitude_2)
        rlon1 = math.radians(longitude_1)
        rlon2 = math.radians(longitude_2)
        drlon = rlon2-rlon1

        b = math.atan2(math.sin(drlon)*math.cos(rlat2),math.cos(rlat1)*math.sin(rlat2)-math.sin(rlat1)*math.cos(rlat2)*math.cos(drlon))
        return (math.degrees(b) + 360) % 360

def calculate_distance_km(lat_a, lon_a, lat_b, lon_b):
    latlon_a = (lat_a, lon_a)
    latlon_b = (lat_b, lon_b)
    return vincenty(latlon_a, latlon_b).km

def convert_string_pair(latlon_string):
    return geopy.point.Point(00.00,00.00)

# We should include the TripStops in this algorithm if we want to make things more fault-tolerant
def get_routemap_info(trip_uid, date=time.strftime('%Y-%m-%d')):
    resp = requests.get('http://journeyplanner.silverrailtech.com/journeyplannerservice/v2/REST/DataSets/UKRailPolylines/Trip?ApiKey=1333ecbd-2a86-08a5-7168-d325c905a731&format=json&tripDate={}&tripUid=UKRailPolylines:{}'.format(date, trip_uid))
    out = json.loads(resp.content.decode())
    ret = {}
    try:
        polyline = out['Summary']['Polyline'].split(';')
        polyline = list(map(geopy.point.Point, polyline))
        ret['points'] = polyline
        ret['start_time'] = datetime.strptime(out['Summary']['TripStartTime'], "%Y-%m-%dT%H:%M").timestamp()

        ret['end_time'] = datetime.strptime(out['TripStops'][-1]['ArrivalTime'], "%Y-%m-%dT%H:%M").timestamp()
    except:
        pass
    return ret

# 1. Take the sum of the polygonal point sequence
# 2. Get the time delta of the start/end times
# 3. Distance / Elapsed time to get velocity
# 4. Take most recent checkpoint (rel. to rx timestamp)
# 5. Integrate averaged velocity against small time delta

# 6. We now have the point on the linear scale.
# 7. Apply delta since last checkpoint in direction of bearing


def convert_sequence(gp_seq, unix_start_time, unix_end_time, estimated_arrival_time, trip_uid):
    if unix_start_time > unix_end_time:
        unix_end_time = unix_start_time
        print("Overriding negative end time")
    if unix_end_time >= estimated_arrival_time:
        return {'lat' : gp_seq[len(gp_seq) - 1].latitude, 'lon' : gp_seq[len(gp_seq) - 1].longitude}

    cumulative_dist = 0

    if True or RAIL_VECTOR_CACHE.get((trip_uid, datetime.utcfromtimestamp(estimated_arrival_time).strftime("%Y-%m-%d"))) is None:
        vector_list = []
        for i in range(1, len(gp_seq) - 1):
            delta = calculate_distance_km(gp_seq[i-1].latitude, gp_seq[i-1].longitude,
                                          gp_seq[i].latitude, gp_seq[i].longitude)
            cumulative_dist += delta
            vector_list.append(
                {
                    'lat' : gp_seq[i].latitude,
                    'lon' : gp_seq[i].longitude,
                    'next_bearing' : bearing(gp_seq[i-1].latitude, gp_seq[i-1].longitude,
                                             gp_seq[i].latitude, gp_seq[i].longitude),
                    'dist' : delta,
                    'cumulative_dist' : cumulative_dist
                }
            )
            # RAIL_VECTOR_CACHE[(trip_uid, datetime.utcfromtimestamp(estimated_arrival_time).strftime("%Y-%m-%d"))] = vector_list

    else:
        vector_list = RAIL_VECTOR_CACHE[(trip_uid, datetime.utcfromtimestamp(estimated_arrival_time).strftime("%Y-%m-%d"))]

    time_delta = (unix_end_time - unix_start_time) / 3600.0


    try:
        avg_velocity = cumulative_dist / ((estimated_arrival_time - unix_start_time)/3600.0)
    except:
        avg_velocity = 0.0

    estimated_dist_travelled = time_delta * avg_velocity

    furthest_vertex = vector_list[0]
    for v in vector_list:
        if v['cumulative_dist'] > estimated_dist_travelled:
            break
        else:
            furthest_vertex = v


    distance_remaining = estimated_dist_travelled - furthest_vertex['cumulative_dist']

    pt = geopy.point.Point(furthest_vertex['lat'], furthest_vertex['lon'])
    dist = geopy.distance.VincentyDistance(kilometers=furthest_vertex['dist'])

    final_destination = dist.destination(point=pt, bearing=furthest_vertex['next_bearing'])

    return {'location':  {'lat': final_destination.latitude, 'lon': final_destination.longitude}}

def get_train_coordinates(trip_uid, unix_time_seconds):
    if RAIL_POLYMAP_CACHE.get((trip_uid, datetime.utcfromtimestamp(unix_time_seconds).strftime("%Y-%m-%d"))) is None:
        train_info = get_routemap_info(trip_uid, datetime.utcfromtimestamp(unix_time_seconds).strftime("%Y-%m-%d"))
        RAIL_POLYMAP_CACHE[(trip_uid, datetime.utcfromtimestamp(unix_time_seconds).strftime("%Y-%m-%d"))] = train_info
    else:
        train_info = RAIL_POLYMAP_CACHE[(trip_uid, datetime.utcfromtimestamp(unix_time_seconds).strftime("%Y-%m-%d"))]
    out = convert_sequence(train_info['points'], train_info['start_time'], unix_time_seconds, train_info['end_time'], trip_uid)
    return out

#get_routemap_info('Y58505_001', '2015-11-22')
#get_routemap_info('Y58301', '2015-11-20')
#get_routemap_info('Y58311_001', '2015-11-21')
#
#get_train_coordinates('Y58505_001', time.time()+3600*9.5)
#
#for t in range(1448182500, 1448186100, 60):
#    print(get_train_coordinates('Y58505_001', t))
#
#pass
#
