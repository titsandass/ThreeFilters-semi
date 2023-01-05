from sgp4.api import SGP4_ERRORS
import numpy as np

class Satellite(object):
    def __init__(self, name, satrec, positions, velocities):
        from sgp4 import exporter
        
        self._name = name
        self._satrec = satrec
        self._positions = positions
        self._norms = np.linalg.norm(self._positions, axis=1)
        self._velocities = velocities
    
        self._TLE = exporter.export_tle(self._satrec)
        self._perigee = self._norms.min()
        self._apogee = self._norms.max()
    
    @property
    def name(self):
        return self._name    
    
    @property
    def satrec(self):
        return self._satrec    
    
    @property
    def inclination(self):
        return self._satrec.inclo
    
    @property
    def positions(self):
        return self._positions  
    
    @property
    def norms(self):
        return self._norms   
    
    @property
    def velocities(self):
        return self._velocities
    
    @property
    def TLE(self):
        return self._TLE

    @property
    def perigee(self):
        return self._perigee

    @property
    def apogee(self):
        return self._apogee



