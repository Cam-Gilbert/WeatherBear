import re

'''
Storm object. Holds information specific to a storm.
'''
class Storm:
    
    def __init__(self, name, id, region, storm_center, movement, pressure, type, wind_speed, discussion, shapefile_path, advisories = None, local_statements = None):
        '''
        Storm constructor

        @param name string name of the storm
        @param id string id of the storm (used for downloading shapefiles) atcf 
        @param region string region that the storm is in, will always be Atlantic, Eastern_Pacific, or Central_Pacific
        @param storm_center lat, lon string representing the storms central position
        @param movement integer representing the storms current movement, default units in mph
        @param pressure float representing the storms central pressure, default units in mb
        @param type str representing the storms type (tropical storm, hurricane, etc..)
        @param advisories list of recent advisories from the nhc
        @param local statements dic of local statements from the nws, and the local offices name, and coordinates for plotting. 
        @param discussion string discussion for the storm from the nhc
        @param shapefile_path the path to the shapefiles used for plotting storm information.
        '''
        self.name = name
        self.id = id
        self.region = region
        self.storm_center = storm_center
        # convert that string to a lat/lon tuple
        self.movement = movement
        self.pressure = pressure # in mb by default
        self.type = type
        # Peel just the value out of wind speed string
        match = re.match(r'\d+', wind_speed.strip())
        self.wind_speed = int(match.group()) if match else None # in mph by default
        self.advisories = advisories or []
        self.local_statements = local_statements or []
        self.discussion = discussion 
        self.shapefile_path = shapefile_path
    
    def has_local_statements(self):
        '''
        Checks if the storm has any local statements
        
        @return true if there are local statements, false otherwise
        '''
        return bool(self.local_statements)
    
    def to_dict(self):
        '''
        To_dict method for testing
        '''
        return {
            "name": self.name,
            "id": self.id,
            "region": self.region,
            "storm_center": self.storm_center,
            "movement": self.movement,
            "pressure": self.pressure,
            "wind_speed": self.wind_speed,
            "type": self.type,
            "advisories": self.advisories,
            "local_statements": self.local_statements,
            "discussion": self.discussion,
            "shapefile_path": self.shapefile_path
        }
        
        