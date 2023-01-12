from satellite import Satellite
from threefilters import ThreeFilters

from datetime import datetime, timedelta
from sgp4.api import Satrec, SatrecArray
from sgp4.conveniences import jday_datetime
import numpy as np
from tqdm import tqdm
import pickle
from multiprocessing import Pool, shared_memory

global satellites

def runFilter(separationDistance, padding, primaryIdx):
    threeFilters = ThreeFilters()
    
    threeFilters.set_separation_distance(separationDistance=separationDistance, padding=padding)
    threeFilters.set_primary_N_secondaries(primary=satellites[primaryIdx], secondaries=satellites[primaryIdx+1:])
    filteredCandidates = threeFilters.pairwise_filter_satellite_candidates()

    return filteredCandidates

workers = 100

#PARAMETERS
tleFileName = './TLE/tle_all.txt'
timeWindow = (datetime(2023,1,4,0,0,0), datetime(2023,1,5,0,0,0))
timeStep = timedelta(seconds=1)
separationDistance:float = 10
padding:float = 10

#PARSE TLE FILES
TLEs = []
with open(tleFileName, 'r') as f:
    lines = f.readlines()
    TLEs = [(lines[3*i].rstrip(), lines[3*i+1].rstrip(), lines[3*i+2].rstrip()) for i in range(int(len(lines)/3))]

#PARSE JD, FR
windowSize = int((timeWindow[1]-timeWindow[0])/timeStep)
currtime = timeWindow[0]

jds, frs = np.empty(windowSize, dtype=np.float32), np.empty(windowSize, dtype=np.float32)
for i in range(windowSize):
    jd, fr = jday_datetime(currtime)

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

shm_sats = shared_memory.SharedMemory(create=True, size=0)

# runFilter(separationDistance, padding, primary, secondaries)
arguments = [(separationDistance, padding, i) for i in range(len(satellites))]
with Pool(workers) as p:
    filteredCandidatesList = p.starmap(runFilter, arguments)

# filteredCandidatesList = []
filteredCandidatesFileName = './filteredCandidates_multiprocess_{}_{}_{}.pickle'.format(timeStep, separationDistance, padding)
with open(filteredCandidatesFileName, 'wb') as f:
    pickle.dump(filteredCandidatesList, f)
pass