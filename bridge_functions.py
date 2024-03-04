import csv
from copy import deepcopy
from math import sin, cos, asin, radians, sqrt, inf
from typing import TextIO

from constants import (
    ID_INDEX, NAME_INDEX, HIGHWAY_INDEX, LAT_INDEX,
    LON_INDEX, YEAR_INDEX, LAST_MAJOR_INDEX,
    LAST_MINOR_INDEX, NUM_SPANS_INDEX,
    SPAN_DETAILS_INDEX, LENGTH_INDEX,
    LAST_INSPECTED_INDEX, BCIS_INDEX, FROM_SEP, TO_SEP,
    HIGH_PRIORITY_BCI, MEDIUM_PRIORITY_BCI,
    LOW_PRIORITY_BCI, HIGH_PRIORITY_RADIUS,
    MEDIUM_PRIORITY_RADIUS, LOW_PRIORITY_RADIUS,
    EARTH_RADIUS)
EPSILON = 0.01


def read_data(csv_file: TextIO) -> list[list[str]]:
    """

    lines = csv.reader(csv_file)
    return list(lines)[2:]



def calculate_distance(lat1: float, lon1: float,
                       lat2: float, lon2: float) -> float:
    """Return the distance in kilometers between the two locations defined by
    (lat1, lon1) and (lat2, lon2), rounded to the nearest meter.

    >>> abs(calculate_distance(43.659777, -79.397383, 43.657129, -79.399439)
    ...     - 0.338) < EPSILON
    True
    >>> abs(calculate_distance(43.42, -79.24, 53.32, -113.30)
    ...     - 2713.226) < EPSILON
    True
    """

    lat1, lon1, lat2, lon2 = (radians(lat1), radians(lon1),
                              radians(lat2), radians(lon2))

    haversine = (sin((lat2 - lat1) / 2) ** 2
                 + cos(lat1) * cos(lat2) * sin((lon2 - lon1) / 2) ** 2)

    return round(2 * EARTH_RADIUS * asin(sqrt(haversine)), 3)



THREE_BRIDGES_UNCLEANED = [
    ['1 -  32/', 'Highway 24 Underpass at Highway 403', '403', '43.167233',
     '-80.275567', '1965', '2014', '2009', '4',
     'Total=64  (1)=12;(2)=19;(3)=21;(4)=12;', '65', '04/13/2012', '72.3', '',
     '72.3', '', '69.5', '', '70', '', '70.3', '', '70.5', '', '70.7', '72.9',
     ''],
    ['1 -  43/', 'WEST STREET UNDERPASS', '403', '43.164531', '-80.251582',
     '1963', '2014', '2007', '4',
     'Total=60.4  (1)=12.2;(2)=18;(3)=18;(4)=12.2;', '61', '04/13/2012',
     '71.5', '', '71.5', '', '68.1', '', '69', '', '69.4', '', '69.4', '',
     '70.3', '73.3', ''],
    ['2 -   4/', 'STOKES RIVER BRIDGE', '6', '45.036739', '-81.33579', '1958',
     '2013', '', '1', 'Total=16  (1)=16;', '18.4', '08/28/2013', '85.1',
     '85.1', '', '67.8', '', '67.4', '', '69.2', '70', '70.5', '', '75.1', '',
     '90.1', '']
]

THREE_BRIDGES = [
    [1, 'Highway 24 Underpass at Highway 403', '403', 43.167233, -80.275567,
     '1965', '2014', '2009', 4, [12.0, 19.0, 21.0, 12.0], 65.0, '04/13/2012',
     [72.3, 69.5, 70.0, 70.3, 70.5, 70.7, 72.9]],
    [2, 'WEST STREET UNDERPASS', '403', 43.164531, -80.251582,
     '1963', '2014', '2007', 4, [12.2, 18.0, 18.0, 12.2], 61.0, '04/13/2012',
     [71.5, 68.1, 69.0, 69.4, 69.4, 70.3, 73.3]],
    [3, 'STOKES RIVER BRIDGE', '6', 45.036739, -81.33579,
     '1958', '2013', '', 1, [16.0], 18.4, '08/28/2013',
     [85.1, 67.8, 67.4, 69.2, 70.0, 70.5, 75.1, 90.1]]
]

def get_bridge(bridge_data: list[list], bridge_id: int) -> list:
    """Return the data for the bridge with id bridge_id from bridge data
    bridge_data. If there is no bridge with id bridge_id, return [].

    >>> result = get_bridge(THREE_BRIDGES, 1)
    >>> result == [
    ...    1, 'Highway 24 Underpass at Highway 403', '403', 43.167233,
    ...    -80.275567, '1965', '2014', '2009', 4,
    ...    [12.0, 19.0, 21.0, 12.0], 65.0, '04/13/2012',
    ...    [72.3, 69.5, 70.0, 70.3, 70.5, 70.7, 72.9]]
    True
    >>> get_bridge(THREE_BRIDGES, 42)
    []
    >>> get_bridge([], 1)
    []
    """

    data = []
    for bridge in bridge_data:
        if bridge[ID_INDEX] == bridge_id:
            data.extend(bridge)
    return data


def get_average_bci(bridge_data: list[list], bridge_id: int) -> float:
    """Return the average BCI for the bridge with id bridge_id from bridge data
    bridge_data. If there are no BCIs for the bridge with id bridge_id,
    return 0, or if there is no bridge with id bridge_id return 0.

    >>> get_average_bci(THREE_BRIDGES, 1)
    70.88571428571429
    >>> get_average_bci(THREE_BRIDGES, 8)
    0
    >>> get_average_bci(THREE_BRIDGES_UNCLEANED, 0)
    0
    >>> get_average_bci([], 1)
    0
    """

    for bridge in bridge_data:
        if bridge[ID_INDEX] == bridge_id:
            return sum(bridge[BCIS_INDEX]) / len(bridge[BCIS_INDEX])
    return 0


def get_total_length_on_hwy(bridge_data: list[list], highway: str) -> float:
    """Return the total length of bridges in bridge_data on highway highway.
    Return 0 if there are no bridges on the highway.

    >>> get_total_length_on_hwy(THREE_BRIDGES, '403')
    126.0

    >>> get_total_length_on_hwy(THREE_BRIDGES, '69')
    0.0
    """

    total_length = 0.0
    for bridge in bridge_data:
        if bridge[HIGHWAY_INDEX] == highway:
            total_length += bridge[LENGTH_INDEX]
    return total_length


def get_distance_between(bridge1: list, bridge2: list) -> float:
    """Return the distance in kilometres, rounded to the nearest metre,
    between a bridge bridge1 and another bridge bridge2.

    >>> get_distance_between([1, 'Highway 24 Underpass at Highway 403',
    ...                     '403', 43.167233, -80.275567,'1965', '2014',
    ...                     '2009', 4,
    ...                     [12.0, 19.0, 21.0, 12.0], 65.0, '04/13/2012',
    ...                     [72.3, 69.5, 70.0, 70.3, 70.5, 70.7, 72.9]],
    ...                     [2, 'WEST STREET UNDERPASS', '403', 43.164531,
    ...                     -80.251582,
    ...                     '1963', '2014', '2007', 4, [12.2, 18.0, 18.0, 12.2],
    ...                     61.0, '04/13/2012',
    ...                     [71.5, 68.1, 69.0, 69.4, 69.4, 70.3, 73.3]])
    1.968

    >>> get_distance_between([1, 'Highway 24 Underpass at Highway 403',
    ...                     '403', 43.167233, -80.275567,
    ...                     '1965', '2014', '2009', 4, [12.0, 19.0, 21.0, 12.0],
    ...                     65.0, '04/13/2012',
    ...                     [72.3, 69.5, 70.0, 70.3, 70.5, 70.7, 72.9]],
    ...                     [3, 'STOKES RIVER BRIDGE', '6', 45.036739, -81.33579
    ...                     ,'1958', '2013', '', 1, [16.0], 18.4, '08/28/2013',
    ...                     [85.1, 67.8, 67.4, 69.2, 70.0, 70.5, 75.1, 90.1]])
    224.451
    """

    return calculate_distance(bridge1[LAT_INDEX], bridge1[LON_INDEX],
                              bridge2[LAT_INDEX], bridge2[LON_INDEX])


def get_closest_bridge(bridge_data: list[list], bridge_id: int) -> int:
    """Return the id of a bridge in bridge_data that has the shortest distance
    to the bridge with the given id bridge_id.

    Precondition: the bridge with the given id is present in the bridge data,
    and that there are at least two bridge in the bridge data.

    >>> get_closest_bridge(THREE_BRIDGES, 2)
    1
    >>> get_closest_bridge(THREE_BRIDGES, 1)
    2
    >>> get_bridge([], 1)
    []
    >>> get_bridge(THREE_BRIDGES, 99)
    []
    """

    d = float("inf")
    index = 0
    for i in range(len(bridge_data) - 1):
        if bridge_data[i][ID_INDEX] != bridge_id:
            if d > get_distance_between(bridge_data[i], bridge_data[bridge_id]):
                d = get_distance_between(bridge_data[i], bridge_data[bridge_id])
                index = bridge_data[i][ID_INDEX]
    return index


def get_bridges_in_radius(bridge_data: list[list], latitude: float,
                          longtitude: float, radius: float) -> int:
    """Return all id of the bridges in brdige_data within a given distance
    radius of the given location (latitude and longtitude).

    >>> get_bridges_in_radius(THREE_BRIDGES, 43.10, -80.15, 50)
    [1, 2]
    >>> get_bridges_in_radius(THREE_BRIDGES, 20.15, -55.15, 50)
    []
    >>> get_bridges_in_radius([], 43.10, -80.15, 50)
    []
    >>> get_bridges_in_radius(THREE_BRIDGES, 43.10, -80.15, -50)
    []
    >>> get_bridges_in_radius(THREE_BRIDGES, 43.10, -80.15, 0)
    []
    """

    bridges_in_radius = []
    for bridge in bridge_data:
        if calculate_distance(bridge[LAT_INDEX], bridge[LON_INDEX], latitude,
                              longtitude) <= radius:
            bridges_in_radius.append(bridge[ID_INDEX])
    return bridges_in_radius


def get_bridges_with_bci_below(bridge_data: list[list], id_list: list[int],
                               bci: float) -> list[int]:
    """ Return a list of ids of all bridges in bridge_data whose ids are
    in the given list of ids id_list and whose BCI is less than or equal
    to the given BCI bci.

    >>> get_bridges_with_bci_below(THREE_BRIDGES, [1, 2], 72)
    [2]
    >>> get_bridges_with_bci_below(THREE_BRIDGES, [1, 3], 0)
    []
    >>> get_bridges_with_bci_below([], [1, 2], 72)
    []
    >>> get_bridges_with_bci_below(THREE_BRIDGES, [1, 2], -72)
    []
    """

    bridge_list = []

    for bridge in bridge_data:
        if bridge[ID_INDEX] in id_list:
            if bridge[BCIS_INDEX][0] <= bci:
                bridge_list.append(bridge[ID_INDEX])
    return bridge_list


def get_bridges_containing(bridge_data: list[list], search: str) -> list[int]:
    """ Return a list of ids of all bridges in bridge_data whose names contain
    the search string search.

    >>> get_bridges_containing(THREE_BRIDGES, 'underpass')
    [1, 2]
    >>> get_bridges_containing(THREE_BRIDGES, 'pass')
    [1, 2]
    >>> get_bridges_containing([], 'underpass')
    []
    >>> get_bridges_containing(THREE_BRIDGES, '')
    [1, 2, 3]
    >>> get_bridges_containing(THREE_BRIDGES, 'hotdog')
    []
    """

    bridges_list = []
    for bridge in bridge_data:
        if search.lower() in bridge[NAME_INDEX].lower():
            bridges_list.append(bridge[ID_INDEX])
    return bridges_list

    >>> assign_inspectors(THREE_BRIDGES, [[43.10, -80.15], [42.10, -81.15]], 0)
    [[], []]
    >>> assign_inspectors(THREE_BRIDGES, [[43.10, -80.15]], 1)
    [[1]]
    >>> assign_inspectors(THREE_BRIDGES, [[43.10, -80.15]], 2)
    [[1, 2]]
    >>> assign_inspectors(THREE_BRIDGES, [[43.10, -80.15]], 3)
    [[1, 2]]
    >>> assign_inspectors(THREE_BRIDGES, [[43.20, -80.35], [43.10, -80.15]], 1)
    [[1], [2]]
    >>> assign_inspectors(THREE_BRIDGES, [[43.20, -80.35], [43.10, -80.15]], 2)
    [[1, 2], []]
    >>> assign_inspectors(THREE_BRIDGES, [[43.20, -80.35], [45.0368, -81.34]],
    ...                   2)
    [[1, 2], [3]]
    >>> assign_inspectors(THREE_BRIDGES, [[38.691, -80.85], [43.20, -80.35]],
    ...                   2)
    [[], [1, 2]]

    """

    bridge_ids = [bridge[ID_INDEX] for bridge in bridge_data]
    inspector_assignments = []

    for inspector in inspectors:
        bridges_in_hp_radius = get_bridges_in_radius(bridge_data,
                                                     inspector[0],
                                                     inspector[1],
                                                     HIGH_PRIORITY_RADIUS)
        bridges_in_mp_radius = get_bridges_in_radius(bridge_data,
                                                     inspector[0],
                                                     inspector[1],
                                                     MEDIUM_PRIORITY_RADIUS)
        bridges_in_lp_radius = get_bridges_in_radius(bridge_data,
                                                     inspector[0],
                                                     inspector[1],
                                                     LOW_PRIORITY_RADIUS)

        hp_bridges = [bridge for bridge in bridge_data
                      if (bridge[ID_INDEX] in bridge_ids
                          and bridge[ID_INDEX] not in inspector_assignments
                          and bridge[ID_INDEX] in bridges_in_hp_radius
                          and bridge[BCIS_INDEX][0] <= HIGH_PRIORITY_BCI)]
        mp_bridges = [bridge for bridge in bridge_data
                      if (bridge[ID_INDEX] in bridge_ids
                          and bridge[ID_INDEX] not in inspector_assignments
                          and bridge[ID_INDEX] in bridges_in_mp_radius
                          and HIGH_PRIORITY_BCI < bridge[BCIS_INDEX][0]
                          <= MEDIUM_PRIORITY_BCI)]
        lp_bridges = [bridge for bridge in bridge_data
                      if (bridge[ID_INDEX] in bridge_ids
                          and bridge[ID_INDEX] not in inspector_assignments
                          and bridge[ID_INDEX] in bridges_in_lp_radius
                          and bridge[BCIS_INDEX][0] > MEDIUM_PRIORITY_BCI)]

        bridges_to_assign = hp_bridges + mp_bridges + lp_bridges
        assigned_bridges = bridges_to_assign[:max_bridges]
        inspector_assignments.append([bridge[ID_INDEX] for
                                      bridge in assigned_bridges])
        bridge_ids = [bridge_id for bridge_id in bridge_ids
                      if (bridge_id not in
                          [bridge[ID_INDEX] for bridge in assigned_bridges])]

    return inspector_assignments

def inspect_bridges(bridge_data: list[list], bridge_ids: list[int], date: str,
                    bci: float) -> None:
    """Update the bridges in bridge_data with id in bridge_ids with the new
    date date and BCI score for a new inspection.

    >>> bridges = deepcopy(THREE_BRIDGES)
    >>> inspect_bridges(bridges, [1], '09/15/2018', 71.9)
    >>> bridges == [
    ...   [1, 'Highway 24 Underpass at Highway 403', '403',
    ...    43.167233, -80.275567, '1965', '2014', '2009', 4,
    ...    [12.0, 19.0, 21.0, 12.0], 65, '09/15/2018',
    ...    [71.9, 72.3, 69.5, 70.0, 70.3, 70.5, 70.7, 72.9]],
    ...   [2, 'WEST STREET UNDERPASS', '403', 43.164531, -80.251582,
    ...    '1963', '2014', '2007', 4, [12.2, 18.0, 18.0, 12.2],
    ...    61, '04/13/2012', [71.5, 68.1, 69.0, 69.4, 69.4, 70.3, 73.3]],
    ...   [3, 'STOKES RIVER BRIDGE', '6', 45.036739, -81.33579,
    ...    '1958', '2013', '', 1, [16.0], 18.4, '08/28/2013',
    ...    [85.1, 67.8, 67.4, 69.2, 70.0, 70.5, 75.1, 90.1]]]
    True

    """

    for bridge in bridge_data:
        if bridge[ID_INDEX] in bridge_ids:
            bridge[LAST_INSPECTED_INDEX] = date
            bridge[BCIS_INDEX].insert(0, bci)


def add_rehab(bridge_data: list[list], bridge_id: int, rehab_year: str,
              rehab: bool) -> None:
    """Update the bridge in bridge_data with the given ID bridge_id with the
    new rehab year record rehab_year: year of major rehab, if the
    last argument rehab is True, and year of minor rehab if the last argument
    rehab is False.

    >>> bridges = deepcopy(THREE_BRIDGES)
    >>> add_rehab(bridges, 1, '09/15/2023', False)
    >>> bridges == [
    ...         [1, 'Highway 24 Underpass at Highway 403', '403', 43.167233,
    ...            -80.275567, '1965', '2014', '2023', 4,
    ...            [12.0, 19.0, 21.0, 12.0], 65, '04/13/2012',
    ...            [72.3, 69.5, 70.0, 70.3, 70.5, 70.7, 72.9]],
    ...        [2, 'WEST STREET UNDERPASS', '403', 43.164531, -80.251582,
    ...         '1963', '2014', '2007', 4, [12.2, 18.0, 18.0, 12.2], 61.0,
    ...            '04/13/2012',
    ...         [71.5, 68.1, 69.0, 69.4, 69.4, 70.3, 73.3]],
    ...        [3, 'STOKES RIVER BRIDGE', '6', 45.036739, -81.33579,
    ...         '1958', '2013', '', 1, [16.0], 18.4, '08/28/2013',
    ...         [85.1, 67.8, 67.4, 69.2, 70.0, 70.5, 75.1, 90.1]]]
    True
    >>> add_rehab(THREE_BRIDGES, 5, '09/15/2023', False)

    """
    rehab_year_slice = rehab_year[6:10]
    for bridge in bridge_data:
        if bridge[ID_INDEX] == bridge_id:
            if rehab is True:
                bridge[LAST_MAJOR_INDEX] = rehab_year_slice
            else:
                bridge[LAST_MINOR_INDEX] = rehab_year_slice

def format_data(data: list[list[str]]) -> None:
    """Modify the uncleaned bridge data data, so that it contains proper
    bridge data, i.e., follows the format outlined in the 'Data
    formatting' section of the assignment handout.

    >>> d = THREE_BRIDGES_UNCLEANED
    >>> format_data(d)
    >>> d == THREE_BRIDGES
    True
    >>> format_data([])
    """

    for i in range(len(data)):
        data[i][ID_INDEX] = i + 1
        format_location(data[i])
        format_spans(data[i])
        format_length(data[i])
        format_bcis(data[i])

def format_location(bridge_record: list) -> None:
    """Format latitude and longitude data in the bridge record bridge_record.

    >>> record = ['1 -  32/', 'Highway 24 Underpass at Highway 403', '403',
    ...           '43.167233', '-80.275567', '1965', '2014', '2009', '4',
    ...           'Total=64  (1)=12;(2)=19;(3)=21;(4)=12;', '65', '04/13/2012',
    ...           '72.3', '', '72.3', '', '69.5', '', '70', '', '70.3', '',
    ...           '70.5', '', '70.7', '72.9', '']
    >>> format_location(record)
    >>> record == ['1 -  32/', 'Highway 24 Underpass at Highway 403', '403',
    ...           43.167233, -80.275567, '1965', '2014', '2009', '4',
    ...           'Total=64  (1)=12;(2)=19;(3)=21;(4)=12;', '65', '04/13/2012',
    ...           '72.3', '', '72.3', '', '69.5', '', '70', '', '70.3', '',
    ...           '70.5', '', '70.7', '72.9', '']
    True
    """
    bridge_record[LAT_INDEX] = float(bridge_record[LAT_INDEX])
    bridge_record[LON_INDEX] = float(bridge_record[LON_INDEX])

def format_spans(bridge_record: list) -> None:
    """Format the bridge spans data in the bridge record bridge_record.

    >>> record = ['1 -  32/', 'Highway 24 Underpass at Highway 403', '403',
    ...           '43.167233', '-80.275567', '1965', '2014', '2009', '4',
    ...           'Total=64  (1)=12;(2)=19;(3)=21;(4)=12;', '65', '04/13/2012',
    ...           '72.3', '', '72.3', '', '69.5', '', '70', '', '70.3', '',
    ...           '70.5', '', '70.7', '72.9', '']
    >>> format_spans(record)
    >>> record == ['1 -  32/', 'Highway 24 Underpass at Highway 403', '403',
    ...           '43.167233', '-80.275567', '1965', '2014', '2009', 4,
    ...           [12.0, 19.0, 21.0, 12.0], '65', '04/13/2012',
    ...           '72.3', '', '72.3', '', '69.5', '', '70', '', '70.3', '',
    ...           '70.5', '', '70.7', '72.9', '']
    True

    """

    bridge_record[NUM_SPANS_INDEX] = int(bridge_record[NUM_SPANS_INDEX])

    s = list(bridge_record[SPAN_DETAILS_INDEX].split(' '))
    del s[0]
    del s[0]

    r = ''.join(s).split(';')
    del r[-1]

    spans_list = []
    for char in r:
        index = char.find('=')
        new = char[index + 1:]
        new = float(new)
        spans_list.append(new)

    bridge_record[SPAN_DETAILS_INDEX] = spans_list

def format_length(bridge_record: list) -> None:
    """Format the bridge length data in the bridge record bridge_record.

    >>> record = ['1 -  32/', 'Highway 24 Underpass at Highway 403', '403',
    ...           '43.167233', '-80.275567', '1965', '2014', '2009', '4',
    ...           'Total=64  (1)=12;(2)=19;(3)=21;(4)=12;', '65', '04/13/2012',
    ...           '72.3', '', '72.3', '', '69.5', '', '70', '', '70.3', '',
    ...           '70.5', '', '70.7', '72.9', '']
    >>> format_length(record)
    >>> record == ['1 -  32/', 'Highway 24 Underpass at Highway 403', '403',
    ...            '43.167233', '-80.275567', '1965', '2014', '2009', '4',
    ...            'Total=64  (1)=12;(2)=19;(3)=21;(4)=12;', 65, '04/13/2012',
    ...            '72.3', '', '72.3', '', '69.5', '', '70', '', '70.3', '',
    ...            '70.5', '', '70.7', '72.9', '']
    True

    """

    if bridge_record != '':
        bridge_record[LENGTH_INDEX] = float(bridge_record[LENGTH_INDEX])
    else:
        bridge_record[LENGTH_INDEX] = 0.0

def format_bcis(bridge_record: list) -> None:
    """Format the bridge BCI data in the bridge record bridge_record.

    >>> record = ['1 -  32/', 'Highway 24 Underpass at Highway 403', '403',
    ...           '43.167233', '-80.275567', '1965', '2014', '2009', '4',
    ...           'Total=64  (1)=12;(2)=19;(3)=21;(4)=12;', '65', '04/13/2012',
    ...           '72.3', '', '72.3', '', '69.5', '', '70', '', '70.3', '',
    ...           '70.5', '', '70.7', '72.9', '']
    >>> format_bcis(record)
    >>> record == ['1 -  32/', 'Highway 24 Underpass at Highway 403', '403',
    ...           '43.167233', '-80.275567', '1965', '2014', '2009', '4',
    ...           'Total=64  (1)=12;(2)=19;(3)=21;(4)=12;', '65', '04/13/2012',
    ...           [72.3, 69.5, 70.0, 70.3, 70.5, 70.7, 72.9]]
    True

    """

    bcis_list = []

    for i in range(len(bridge_record) - 1, BCIS_INDEX, -1):
        if bridge_record[i] != '':
            bcis_list.append(float(bridge_record[i]))
        del bridge_record[i]

    bcis_list.reverse()
    bridge_record[BCIS_INDEX] = bcis_list


if __name__ == '__main__':
    import doctest
    doctest.testmod()

    
