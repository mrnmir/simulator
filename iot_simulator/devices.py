from dataclasses import dataclass
import random


@dataclass
class BaseStation:
    """Base station with fixed location and transmission parameters.
    """    
    id: int
    x: float
    y: float
    frequency: float  
    transmit_power: float


@dataclass
class UserDevice:
    """User device with a location and movement capabilities.
    """    
    id: int
    x: float
    y: float
    speed: float 

    def move(self, area_size: float):
        """Move randomly within the simulation area.

        Parameters
        ----------
        area_size : float
            The size of the simulation area.
        """
        dx = random.uniform(-self.speed, self.speed)
        dy = random.uniform(-self.speed, self.speed)
        self.x = max(0, min(area_size, self.x + dx))
        self.y = max(0, min(area_size, self.y + dy))
