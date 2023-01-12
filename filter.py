from satellite import Satellite
from threefilters import ThreeFilters

from datetime import datetime, timedelta
from sgp4.api import Satrec, SatrecArray, jday
import numpy as np
from tqdm import tqdm
import pickle

#PARAMETERS
tleFileName = './TLE/tle_all.txt'
timeWindow = (datetime(2023,1,4,0,0,0), datetime(2023,1,5,0,0,0))
timeStep = timedelta(seconds=4)
separationDistance:float = 10
padding:float = 30

#PARSE TLE FILES
TLEs = []
with open(tleFileName, 'r') as f:
    lines = f.readlines()
    TLEs = [(lines[3*i].rstrip(), lines[3*i+1].rstrip(), lines[3*i+2].rstrip()) for i in range(int(len(lines)/3))]

# TLEs = [TLEs[0],TLEs[1098]]

#PARSE JD, FR
windowSize = int((timeWindow[1]-timeWindow[0])/timeStep)
currtime = timeWindow[0]

jds, frs = np.empty(windowSize, dtype=np.float32), np.empty(windowSize, dtype=np.float32)
for i in range(windowSize):
    jd, fr = jday(currtime.year, currtime.month, currtime.day, currtime.hour, currtime.minute, currtime.second)

    jds[i], frs[i] = jd, fr
    currtime += timeStep 
 
#GENERATE SATREC OBJECT AND PROPAGATE
for _ in tqdm(range(1), desc='Propagating Satellites'):
    satrecs = [Satrec.twoline2rv(TLE[1], TLE[2]) for TLE in TLEs]
    satrecArray = SatrecArray(satrecs)
    errors, positions, velocities = satrecArray.sgp4(jds, frs)   

#GENERATE SATELLITE CLASS OBJECTS
satellites = []
propagationErrors = []
for i, satrec in enumerate(tqdm(satrecs, desc='Satellite Instances')):
    if np.any(errors[i]):
        propagationErrors.append(i)
        continue
    satellites.append(Satellite(name=TLEs[i][0][2:], satrec=satrec, positions=positions[i], velocities=velocities[i]))
print('\tPROPAGATION ERROR IN {} SATS'.format(len(propagationErrors)))

#FILTER
threeFilters = ThreeFilters()
filteredCandidatesList = []
threeFilters.set_separation_distance(separationDistance=separationDistance, padding=padding)
for i in tqdm(range(len(satellites)), desc='Filtering'):
    threeFilters.set_primary_N_secondaries(primary=satellites[i], secondaries=satellites[i+1:])
    filteredCandidates = threeFilters.pairwise_filter_satellite_candidates()
    filteredCandidatesList.append(filteredCandidates)

filteredCandidatesFileName = './filteredCandidates_{}_{}_{}.pickle'.format(timeStep, separationDistance, padding)
with open(filteredCandidatesFileName, 'wb') as f:
    pickle.dump(filteredCandidatesList, f)
pass