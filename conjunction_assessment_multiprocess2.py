import pickle
from sgp4.api import Satrec, SatrecArray
from sgp4.conveniences import jday_datetime
from datetime import datetime, timedelta
import numpy as np
from multiprocessing import Pool, Manager

global filteredCandidates
global timeWindow
global FilterTimeStep
global CATimeStep
global threshold
global TLEs
global satrecs
global satrecNums

#primary 24392
#conjunctions 328671

def conjunction_assessment(primaryIdx, shm_satrecNums):
    CAResult = []
    primary = satrecs[primaryIdx]
    if len(filteredCandidates[primaryIdx]) == 0:
        return CAResult

    for secondaryNum, timeSpans in filteredCandidates[primaryIdx]:
        secondary = satrecs[satrecNums.index(secondaryNum)]
        satrecArray = SatrecArray([primary, secondary])
        
        jds, frs = [], []
        for startT, endT in timeSpans:
            startDateTime   = min(timeWindow[0] + startT*FilterTimeStep - FilterTimeStep, timeWindow[0])
            endDateTime     = max(timeWindow[0] + endT*FilterTimeStep + FilterTimeStep, timeWindow[1])
            windowSize      = int((endDateTime-startDateTime)/CATimeStep)

            for i in range(windowSize):
                jd, fr = jday_datetime(startDateTime + i*CATimeStep)
                jds.append(jd)
                frs.append(fr)
                
        jds, frs = np.array(jds, dtype=np.float32), np.array(frs, dtype=np.float32)
        _, positions, _ = satrecArray.sgp4(jds, frs)
        primaryPositions, secondaryPositions = positions        

        dist = np.linalg.norm(primaryPositions-secondaryPositions, axis=1)
        distUnderThreshold_idx = np.where(dist <= threshold)[0]
        if distUnderThreshold_idx.size == 0:
            continue

        DCA = dist.min()
        TCA = startDateTime + np.argmin(dist)*CATimeStep
        TCAStart, TCAEnd = startDateTime + CATimeStep*distUnderThreshold_idx[0], startDateTime + CATimeStep*distUnderThreshold_idx[-1]

        CAResult.append((primary.satnum, secondary.satnum, DCA, TCAStart.strftime(timeformat), TCA.strftime(timeformat), TCAEnd.strftime(timeformat)))
    shm_satrecNums.remove(primary.satnum)
    print('{} SATs Left'.format(len(shm_satrecNums)))

    return CAResult

with open('./filteredCandidates_multiprocess_0:00:01_10_10.pickle', 'rb') as f:
    filteredCandidates = pickle.load(f)

tleFileName = './TLE/tle_all.txt'
timeWindow = (datetime(2023,1,4,0,0,0), datetime(2023,1,5,0,0,0))
FilterTimeStep = timedelta(seconds=1)
CATimeStep = timedelta(milliseconds=100)
threshold = 10

workers=100
timeformat = '%Y-%m-%dT%H:%M:%S.%f'
TLEs = []
with open(tleFileName, 'r') as f:
    lines = f.readlines()
    TLEs = [(lines[3*i].rstrip(), lines[3*i+1].rstrip(), lines[3*i+2].rstrip()) for i in range(int(len(lines)/3))]
satrecs = [Satrec.twoline2rv(TLE[1], TLE[2]) for TLE in TLEs]
satrecNums = [satrec.satnum for satrec in satrecs]

manager = Manager()
shm_satrecNums = manager.list()
shm_satrecNums.extend(satrecNums)

CAResults = []

a = conjunction_assessment(0, shm_satrecNums)

# arguments = [(i, shm_satrecNums) for i in range(len(filteredCandidates))]
# with Pool(workers) as pool:
#     CAResults = pool.starmap(conjunction_assessment, arguments)
    
with open('./ca_multiprocess.pickle', 'wb') as f:
    pickle.dump(CAResults, f)       

    # with open('./result/CA/{}_{}.txt'.format(timeWindow[0].strftime(timeformat), timeWindow[1].strftime(timeformat)), 'w') as f:
    #     f.writeline('Primary\t\tSecondary\t\tTCAStart\t\tTCA\t\tTCAEnd')
    #     for primary, secondary, dca, tcaStart, tca, tcaEnd in CAResults:
    #         f.writeline('{}\t\t{}\t\t{}\t\t{}\t\t{}\t\t{}'.format(primary, secondary, dca, tcaStart, tca, tcaEnd))
