from satellite import Satellite

from typing import List, Tuple
import numpy as np

class ThreeFilters:
    def __init__(self):
        pass

    def set_primary_N_secondaries(self, primary:Satellite, secondaries:List[Satellite]):
        self.primary = primary
        self.satelliteCandidates = secondaries
    
    def set_separation_distance(self, separationDistance:float, padding:float):
        self.separationDistance = separationDistance
        self.padding = padding
    
    def pairwise_filter_satellite_candidates(self):
        self._perigee_apogee_filter()
        self._orbit_time_filter()
        # self._orbit_path_filter()
        # self._time_filter()
    
        return self.filteredCandidates
    
    def _perigee_apogee_filter(self):
        primary = self.primary
        
        self.filteredCandidates = []
        for secondary in self.satelliteCandidates:           
            smallQ = max(primary.perigee, secondary.perigee)
            largeQ = min(primary.apogee, secondary.apogee)
            if smallQ - largeQ > self.separationDistance + self.padding:
                continue
            self.filteredCandidates.append(secondary)

    def _orbit_path_filter(self):
        primary = self.primary
        
        filteredCandidates = []
        for secondary in self.filteredCandidates:
            posDiff = np.linalg.norm(primary.positions - secondary.positions, axis=1)
            minPos = posDiff.min()
            if minPos > self.separationDistance + self.padding:
                continue
            filteredCandidates.append(secondary)
        self.filteredCandidates = filteredCandidates
        
    def _time_filter(self):
        primary = self.primary
        primaryNormalVectors = np.cross(primary.positions, primary.velocities)
        primaryNormalVector = np.mean(primaryNormalVectors, axis=0)
        primaryNormalVectorMagnitude = np.linalg.norm(primaryNormalVector)
        
        filteredCandidates = []
        for secondary in self.filteredCandidates:
            secondaryNormalVectors = np.cross(secondary.positions, secondary.velocities)
            secondaryNormalVector = np.mean(secondaryNormalVectors, axis=0)
            secondaryNormalVectorMagnitude = np.linalg.norm(secondaryNormalVector)            
            
            sec2PriProjHeight = np.abs(np.dot(secondary.positions, primaryNormalVector)) / primaryNormalVectorMagnitude
            sec2PriIndices = np.where(sec2PriProjHeight <= self.separationDistance + self.padding)[0]
            if sec2PriIndices.size == 0:
                continue
            
            pri2SecProjHeight = np.abs(np.dot(primary.positions, secondaryNormalVector)) / secondaryNormalVectorMagnitude
            pri2SecIndices = np.where(pri2SecProjHeight <= self.separationDistance + self.padding)[0]
            if sec2PriIndices.size == 0:
                continue
            
            intersectionIndices = sec2PriIndices[np.where(np.isin(sec2PriIndices, pri2SecIndices))]
            if intersectionIndices.size == 0:
                continue
            
            diff = np.where(np.diff(intersectionIndices) != 1)[0] + 1
            if diff.size == 0:
                timeSpan = [(intersectionIndices[0], intersectionIndices[-1])]
            else:
                timeSpan = [(intersectionIndices[0], intersectionIndices[diff[0]-1])]
                for i in range(len(diff)-1):
                    timeSpan.append((intersectionIndices[diff[i]], intersectionIndices[diff[i+1]-1]))
                timeSpan.append((intersectionIndices[diff[-1]], intersectionIndices[-1]))
            
            filteredCandidates.append((secondary, timeSpan))
        self.filteredCandidates = filteredCandidates
            
    def _orbit_time_filter(self):
        primary = self.primary

        filteredCandidates = []
        for secondary in self.filteredCandidates:
            dist = np.linalg.norm(primary.positions - secondary.positions, axis=1)
            minDist = dist.min()
            if minDist > self.separationDistance + self.padding:
                continue             

            distUnderSD_Idx = np.where(dist <= self.separationDistance + self.padding)[0]

            diffIdx = np.where(np.diff(distUnderSD_Idx) != 1)[0] + 1
            if diffIdx.size == 0:
                timeSpan = [(distUnderSD_Idx[0], distUnderSD_Idx[-1])]
            else:
                timeSpan = [(distUnderSD_Idx[0], distUnderSD_Idx[diffIdx[0]-1])]
                for i in range(len(diffIdx)-1):
                    timeSpan.append((distUnderSD_Idx[diffIdx[i]], distUnderSD_Idx[diffIdx[i+1]-1]))
                timeSpan.append((distUnderSD_Idx[diffIdx[-1]], distUnderSD_Idx[-1]))
            
            filteredCandidates.append((secondary.satnum, timeSpan))
        self.filteredCandidates = filteredCandidates 