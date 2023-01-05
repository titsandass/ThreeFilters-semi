from orbit import Orbit
from sgp4.api import Satrec, jday
import numpy as np

class Satellite():
    def __init__(self, TLE):
        # super().__init__()
        self.name = None
        self.TLE = TLE
        self.satellite = None

        self.orbits = list()

    def set_satrec_object(self):
        self.satellite = Satrec.twoline2rv(self.TLE[1].rstrip(), self.TLE[2].rstrip())
    
    def generate_orbit(self, timestep, timewindow):
        windowSize = (timewindow[1]-timewindow[0])/timestep
        currtime = timewindow[0]

        jds, frs = np.empty(int(windowSize)+1), np.empty(int(windowSize)+1)
        for i in range(int(windowSize+1)):
            jd, fr = jday(currtime.year, currtime.month, currtime.day, currtime.hour, currtime.minute, currtime.second)

            jds[i] = jd
            frs[i] = fr

            currtime += timestep
            # self.satellite.sgp4(jd, fr)
            # print(self.satellite.am, self.satellite.em, self.satellite.Om, self.satellite.mm, self.satellite.nm)

            # if i==100:
            #     break


        e, pos, vel = self.satellite.sgp4_array(jds, frs)
        print(self.satellite.im, self.satellite.om)
        





