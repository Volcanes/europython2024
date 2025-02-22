# SPDX-License-Identifier: BSD-3-Clause

# flake8: noqa F401
from collections.abc import Callable

import numpy as np

from vendeeglobe import (
    Checkpoint,
    Heading,
    Instructions,
    Location,
    Vector,
    config,
)
from vendeeglobe.utils import distance_on_surface


class Bot:
    """
    This is the ship-controlling bot that will be instantiated for the competition.
    """

    def __init__(self):
        self.team = "VOLCANES"  # This is your team name
        # This is the course that the ship has to follow
        self.course = [
            Checkpoint(latitude=43.797109, longitude=-11.264905, radius=50, reached = False),
            # Checkpoint(longitude=-29.908577, latitude=17.999811, radius=50, reached = False),
            Checkpoint(latitude=14.248565, longitude=-60.412676, radius=2),#MARTINICA
            Checkpoint(latitude=12.150527, longitude=-78.672976, radius=50),
            Checkpoint(latitude=9.515025, longitude=-80.073577, radius=10),
            Checkpoint(latitude=8.516784, longitude=-79.617645, radius=10),
            Checkpoint(latitude=5.827189, longitude=-78.451480, radius=10),
            Checkpoint(latitude=-2.810658, longitude=-88.351144, radius=10),#galapagos
            # Checkpoint(latitude=-11.441808, longitude=-29.660252, radius=50, reached = True), #cabo de hornos
            # Checkpoint(longitude=-63.240264, latitude=-61.025125, radius=50, reached = True), #cabo de hornos
            # Checkpoint(latitude=2.806318, longitude=-168.943864, radius=1990.0, reached = False), #medio pacifico
            Checkpoint(latitude=-9.193349, longitude=-157.769442, radius=5, reached = False),#TAUTUA
            Checkpoint(latitude=2.806318, longitude=-168.943864, radius=1990.0, reached = False),
            Checkpoint(latitude=-21.037543, longitude=-166.432127, radius=10),
            #Checkpoint(latitude=-62.052286, longitude=169.214572, radius=50.0),
            Checkpoint(latitude=-30.554692, longitude=169.897996, radius=50.0, reached = False),#entre new zeland y au 1
            Checkpoint(latitude=-46.522587, longitude=150.333942, radius=50.0, reached = False),#entre new zeland y au 1
            Checkpoint(latitude=-15.668984, longitude=77.674694, radius=1190.0, reached = False),#OCEANO INDICO
            Checkpoint(latitude=-9.755187, longitude=68.988547, radius=5.0, reached = False),#Britské indickoocenánské území
            Checkpoint(latitude=8.465130, longitude=58.359375, radius=20.0, reached = False),
            Checkpoint(latitude=14.539278, longitude=54.250488, radius=10.0, reached = False),
            Checkpoint(latitude=11.808570, longitude=44.230957, radius=10.0, reached = False),
            Checkpoint(latitude=12.594193, longitude=43.372650, radius=10.0, reached = False),
            Checkpoint(latitude=13.612443, longitude=42.506104, radius=10.0, reached = False),
            Checkpoint(latitude=25.705723, longitude=35.496826, radius=10.0, reached = False),
            Checkpoint(latitude=27.563881, longitude=34.183960, radius=10.0, reached = False),
            Checkpoint(latitude=28.376983, longitude=33.217163, radius=2.0),
            Checkpoint(latitude=29.636541, longitude=32.590942, radius=2.0), # aqui se encalla
            Checkpoint(latitude=31.300379, longitude=32.375931, radius=2.0),
            Checkpoint(latitude=31.733170, longitude=32.484979, radius=2.0), #desahogo port said
            Checkpoint(latitude=35.981561, longitude=16.638299, radius=2.0),
            Checkpoint(latitude=36.839545, longitude=13.255174, radius=2.0),
            Checkpoint(latitude=38.572027, longitude=6.855156, radius=2.0), #Cerdegna
            Checkpoint(latitude=36.283686, longitude=-2.567299, radius=2.0), 
            Checkpoint(latitude=35.903356, longitude=-6.063741, radius=2.0),
            Checkpoint(latitude=35.995427, longitude=-11.870269, radius=2.0),
            Checkpoint(latitude=43.797109, longitude=-11.264905, radius=2, reached = False),
            #Checkpoint(latitude=-39.438937, longitude=19.836265, radius=50.0),
            #Checkpoint(latitude=14.881699, longitude=-21.024326, radius=50.0),
            #Checkpoint(latitude=44.076538, longitude=-18.292936, radius=50.0),
            Checkpoint(
                latitude=config.start.latitude,
                longitude=config.start.longitude,
                radius=5,
            ),
        ]

    def run(
        self,
        t: float,
        dt: float,
        longitude: float,
        latitude: float,
        heading: float,
        speed: float,
        vector: np.ndarray,
        forecast: Callable,
        world_map: Callable,
    ) -> Instructions:
        """
        This is the method that will be called at every time step to get the
        instructions for the ship.

        Parameters
        ----------
        t:
            The current time in hours.
        dt:
            The time step in hours.
        longitude:
            The current longitude of the ship.
        latitude:
            The current latitude of the ship.
        heading:
            The current heading of the ship.
        speed:
            The current speed of the ship.
        vector:
            The current heading of the ship, expressed as a vector.
        forecast:
            Method to query the weather forecast for the next 5 days.
            Example:
            current_position_forecast = forecast(
                latitudes=latitude, longitudes=longitude, times=0
            )
        world_map:
            Method to query map of the world: 1 for sea, 0 for land.
            Example:
            current_position_terrain = world_map(
                latitudes=latitude, longitudes=longitude
            )

        Returns
        -------
        instructions:
            A set of instructions for the ship. This can be:
            - a Location to go to
            - a Heading to point to
            - a Vector to follow
            - a number of degrees to turn Left
            - a number of degrees to turn Right

            Optionally, a sail value between 0 and 1 can be set.
        """
        # Initialize the instructions
        instructions = Instructions()

        # TODO: Remove this, it's only for testing =================
        current_position_forecast = forecast(
            latitudes=latitude, longitudes=longitude, times=0
        )
        current_position_terrain = world_map(latitudes=latitude, longitudes=longitude)
        # ===========================================================

        # Go through all checkpoints and find the next one to reach
        for ch in self.course:
            # Compute the distance to the checkpoint
            dist = distance_on_surface(
                longitude1=longitude,
                latitude1=latitude,
                longitude2=ch.longitude,
                latitude2=ch.latitude,
            )
            # Consider slowing down if the checkpoint is close
            jump = dt * np.linalg.norm(speed)
            if dist < 2.0 * ch.radius + jump:
                instructions.sail = 1
            else:
                instructions.sail = 1.0
            # Check if the checkpoint has been reached
            if dist < ch.radius:
                ch.reached = True
            if not ch.reached:
                instructions.location = Location(
                    longitude=ch.longitude, latitude=ch.latitude
                )
                break

        return instructions
