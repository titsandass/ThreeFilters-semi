from satellite import Satellite
from datetime import datetime, timedelta

timewindow = (datetime(2023,1,4,12,0,0), datetime(2023,1,5,12,0,0))
timestep = timedelta(seconds=1)

TLE = [
'0 VANGUARD 2',
'1    11U 59001A   23003.55578838  .00001221  00000-0  65779-3 0  9997',
'2    11  32.8631 162.0729 1463903 104.1194 272.5998 11.86302677727177',
]

sat = Satellite(TLE)
sat.set_satrec_object()
sat.generate_orbit(timestep, timewindow)

pass