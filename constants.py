"""Assignment 2: Bridges

The data used for this assignment is a subset of the data found in:
https://data.ontario.ca/dataset/bridge-conditions

This code is provided solely for the personal and private use of
students taking the CSCA08 course at the University of Toronto
Scarborough. Copying for purposes other than this use is expressly
prohibited. All forms of distribution of this code, whether as given
or with any changes, are expressly prohibited.

All of the files in this directory and all subdirectories are:
Copyright (c) 2023 Anya Tafliovich, Mario Badr, Tom Fairgrieve, Sadia
Sharmin, and Jacqueline Smith

"""

ID_INDEX = 0
NAME_INDEX = 1
HIGHWAY_INDEX = 2
LAT_INDEX = 3
LON_INDEX = 4
YEAR_INDEX = 5
LAST_MAJOR_INDEX = 6
LAST_MINOR_INDEX = 7
NUM_SPANS_INDEX = 8
SPAN_DETAILS_INDEX = 9
LENGTH_INDEX = 10
LAST_INSPECTED_INDEX = 11
BCIS_INDEX = 12
FROM_SEP = '='
TO_SEP = ';'

HIGH_PRIORITY_BCI = 60
MEDIUM_PRIORITY_BCI = 70
LOW_PRIORITY_BCI = 100

HIGH_PRIORITY_RADIUS = 500
MEDIUM_PRIORITY_RADIUS = 250
LOW_PRIORITY_RADIUS = 100

EARTH_RADIUS = 6371
