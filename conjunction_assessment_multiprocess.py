import pickle
from sgp4.api import Satrec, SatrecArray
from sgp4.conveniences import jday_datetime
from datetime import datetime, timedelta
import numpy as np
from multiprocessing import Pool

global filteredCandidates
global timeWindow
global FilterTimeStep
global CATimeStep
global threshold
global TLEs

def conjunction_assessment(primaryIdx):
    CAResult = []
    primary = Satrec.twoline2rv(TLEs[primaryIdx][1], TLEs[primaryIdx][2])
    for secondaryNum, timeSpans in filteredCandidates[primaryIdx]:
        secondaryIdx = satrecNums.index(secondaryNum)
        secondary = Satrec.twoline2rv(TLEs[secondaryIdx][1], TLEs[secondaryIdx][2])
        satrecArray = SatrecArray([primary, secondary])

        for startT, endT in timeSpans: 
            startDateTime  = min(timeWindow[0] + startT*FilterTimeStep - FilterTimeStep, timeWindow[0])
            endDateTime    = max(timeWindow[0] + endT*FilterTimeStep + FilterTimeStep, timeWindow[1])
            windowSize = int((endDateTime-startDateTime)/CATimeStep)

            jds, frs = np.empty(windowSize, dtype=np.float32), np.empty(windowSize, dtype=np.float32)
            for i in range(windowSize):
                jd, fr = jday_datetime(startDateTime + i*CATimeStep)
                jds[i], frs[i] = jd, fr
            _, positions, _ = satrecArray.sgp4(jds, frs)
            primaryPositions, secondaryPositions = positions

            dist = np.linalg.norm(primaryPositions-secondaryPositions, axis=1)
            distUnderThreshold_idx = np.where(dist <= threshold)[0]
            if distUnderThreshold_idx.size == 0:
                continue

            DCA = dist.min()
            TCA = startT + np.argmin(dist)*CATimeStep
            TCAStart, TCAEnd = startT + CATimeStep*distUnderThreshold_idx[0], startT + CATimeStep*distUnderThreshold_idx[-1]

            CAResult.append((primary.satnum, secondary.satnum, DCA, TCAStart.strftime(timeformat), TCA.strftime(timeformat), TCAEnd.strftime(timeformat)))
    return CAResult

with open('./filteredCandidates_multiprocess_0:00:01_10_10.pickle', 'rb') as f:
    filteredCandidates = pickle.load(f)

tleFileName = './TLE/tle_all.txt'
timeWindow = (datetime(2023,1,4,0,0,0), datetime(2023,1,5,0,0,0))
FilterTimeStep = timedelta(seconds=4)
CATimeStep = timedelta(milliseconds=10)
threshold = 10

workers=100
timeformat = '%Y-%m-%dT%H:%M:%S.%f'
TLEs = []
with open(tleFileName, 'r') as f:
    lines = f.readlines()
    TLEs = [(lines[3*i].rstrip(), lines[3*i+1].rstrip(), lines[3*i+2].rstrip()) for i in range(int(len(lines)/3))]
satrecs = [Satrec.twoline2rv(TLE[1], TLE[2]) for TLE in TLEs]
satrecNums = [satrec.satnum for satrec in satrecs]

CAResults = []
arguments = [i for i in range(len(filteredCandidates))]
with Pool(workers) as pool:
    CAResults = pool.map(conjunction_assessment, arguments)
    
with open('./ca_multiprocess.pickle', 'wb') as f:
    pickle.dump(CAResults, f)       

    # with open('./result/CA/{}_{}.txt'.format(timeWindow[0].strftime(timeformat), timeWindow[1].strftime(timeformat)), 'w') as f:
    #     f.writeline('Primary\t\tSecondary\t\tTCAStart\t\tTCA\t\tTCAEnd')
    #     for primary, secondary, dca, tcaStart, tca, tcaEnd in CAResults:
    #         f.writeline('{}\t\t{}\t\t{}\t\t{}\t\t{}\t\t{}'.format(primary, secondary, dca, tcaStart, tca, tcaEnd))
