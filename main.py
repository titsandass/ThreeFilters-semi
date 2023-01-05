from satellite import Satellite
from threefilters import ThreeFilters

from datetime import datetime, timedelta
from sgp4.api import Satrec, SatrecArray, jday
import numpy as np
import time

#PARAMETERS
tleFileName = './TLE/tle_all.txt'
timeWindow = (datetime(2023,1,4,12,0,0), datetime(2023,1,5,12,0,0))
timeStep = timedelta(seconds=1)
separationDistance = 10
padding = 10

start = time.time()
#PARSE TLE FILES
TLEs = []
with open(tleFileName, 'r') as f:
    lines = f.readlines()
    TLEs = [(lines[3*i].rstrip(), lines[3*i+1].rstrip(), lines[3*i+2].rstrip()) for i in range(int(len(lines)/3))]
    
TLEs = TLEs[3500:6500]    

tle = time.time()
print('TLE : {}'.format(tle-start))    

#PARSE JD, FR
windowSize = int((timeWindow[1]-timeWindow[0])/timeStep)
currtime = timeWindow[0]

jds, frs = np.empty(windowSize, dtype=np.float32), np.empty(windowSize, dtype=np.float32)
for i in range(windowSize):
    jd, fr = jday(currtime.year, currtime.month, currtime.day, currtime.hour, currtime.minute, currtime.second)

    jds[i], frs[i] = jd, fr
    currtime += timeStep

jdfr = time.time()
print('JDFR : {}'.format(jdfr-tle))   
 
#GENERATE SATREC OBJECT AND PROPAGATE
satrecs = [Satrec.twoline2rv(TLE[1], TLE[2]) for TLE in TLEs]
satrecArray = SatrecArray(satrecs)
errors, positions, velocities = satrecArray.sgp4(jds, frs)            

propagate = time.time()
print('PROPAGATE : {}'.format(propagate-jdfr))   

#GENERATE SATELLITE CLASS OBJECTS
satellites = []
for i, satrec in enumerate(satrecs):
    if np.any(errors[i]):
        print('\tPROPAGATION ERROR IN SAT : {}'.format(i))
        continue
    satellites.append(Satellite(name=TLEs[i][0][2:], satrec=satrec, positions=positions[i], velocities=velocities[i]))

satobj = time.time()
print('SATELLITE OBJECT : {}'.format(satobj-propagate))   

#FILTER
threeFilters = ThreeFilters(satellites)
filteredCandidatesList = []
threeFilters.set_separation_distance(separationDistance=separationDistance, padding=padding)
for primary in satellites:
    threeFilters.set_primary(primary=primary)
    filteredCandidates = threeFilters.pairwise_filter_satellite_candidates()
    filteredCandidatesList.append(filteredCandidates)

filter = time.time()
print('FILTER : {}'.format(filter-satobj))   

pass