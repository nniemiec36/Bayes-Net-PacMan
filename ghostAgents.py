from game import Agent
from game import Directions

class StationaryGhostAgent( Agent ):
    def __init__( self, index ):
        self.index = index

    def getAction( self, state ):
        return Directions.STOP
