import pickle
from sgp4.api import Satrec, SatrecArray
from sgp4.conveniences import jday_datetime
from datetime import datetime, timedelta
import numpy as np
import tqdm

with open('./filteredCandidates_04_10_30.pickle', 'rb') as f:
    filteredCandidates = pickle.load(f)

tleFileName = './TLE/tle_all.txt'
timeWindow = (datetime(2023,1,4,0,0,0), datetime(2023,1,5,0,0,0))
FilterTimeStep = timedelta(seconds=4)
CATimeStep = timedelta(milliseconds=1)
threshold = 10

timeformat = '%Y-%m-%dT%H:%M:%S.%f'

TLEs = []
with open(tleFileName, 'r') as f:
    lines = f.readlines()
    TLEs = [(lines[3*i].rstrip(), lines[3*i+1].rstrip(), lines[3*i+2].rstrip()) for i in range(int(len(lines)/3))]
satrecs = [Satrec.twoline2rv(TLE[1], TLE[2]) for TLE in TLEs]
satrecNums = [satrec.satnum for satrec in satrecs]

CAResults = []
for primaryIdx in tqdm(range(len(filteredCandidates))):
    primary = satrecs[primaryIdx]
    for secondaryNum, timeSpans in filteredCandidates[primaryIdx]:
        secondaryIdx = satrecNums.index(secondaryNum)
        secondary = satrecs[secondaryIdx]
        for startT, endT in timeSpans: 

            startT  = timeWindow[0] + startT*FilterTimeStep - FilterTimeStep
            endT    = timeWindow[0] + endT*FilterTimeStep + FilterTimeStep

            windowSize = int((endT-startT)/CATimeStep)

            currtime = startT
            jds, frs = np.empty(windowSize, dtype=np.float32), np.empty(windowSize, dtype=np.float32)
            for idx in range(windowSize):
                jd, fr = jday_datetime(currtime)
                jds[idx], frs[idx] = jd, fr
                currtime += CATimeStep

            satrecArray = SatrecArray([primary, secondary])
            _, positions, _ = satrecArray.sgp4(jds, frs)
            primaryPositions, secondaryPositions = positions

            dist = np.linalg.norm(primaryPositions-secondaryPositions, axis=1)
            distDiffIndices = np.where(dist <= threshold)[0]
            if distDiffIndices.size == 0:
                continue

            diff = np.where(np.diff(distDiffIndices) != 1)[0] + 1
            if diff.size != 0:
                raise ValueError('???')
            DCA = dist.min()
            TCA = startT + np.argmin(dist)*CATimeStep
            TCAStart, TCAEnd = startT + CATimeStep*distDiffIndices[0], startT + CATimeStep*distDiffIndices[-1]

            CAResults.append((primary.satnum, secondary.satnum, TCAStart.strftime(timeformat), TCA.strftime(timeformat), TCAEnd.strftime(timeformat)))

with open('./result/CA/{}_{}.txt'.format(timeWindow[0].strftime(timeformat), timeWindow[1].strftime(timeformat)), 'w') as f:
    f.writeline('Primary\t\tSecondary\t\tTCAStart\t\tTCA\t\tTCAEnd')
    for primary, secondary, tcaStart, tca, tcaEnd in CAResults:
        f.writeline('{}\t\t{}\t\t{}\t\t{}\t\t{}'.format(primary, secondary, tcaStart, tca, tcaEnd))
