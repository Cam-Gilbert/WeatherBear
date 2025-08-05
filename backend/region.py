from backend.storm import Storm

class Region:
    def __init__(self, name, discussion = None, storms = None):
        
        self.name = name
        self.discussion = discussion
        self.storms = storms or []

    
    def add_storm(self, storm):
        '''
        Adds a storm to the regions storms list.
        '''
        # Add storm to list
        if not any(s.id == storm for s in self.storms):
            self.storms.append(storm)
            self.sort_storms()

    
    def get_storm(self, name = None, id = None):
        '''
        Gets a storm from the regions storm list based off of the storms name or id, program trys to match name first and falls back to id 
        if it cannot find a name. 
        
        @param name str of storms name
        @param id str of storms id
        @return the storm object requested or None
        '''
        storm = None

        if name:
            storm = next((s for s in self.storms if s.name.lower() == name.lower()), None)

        if storm is None and id:
            storm = next((s for s in self.storms if s.id.lower() == id.lower()), None)

        if storm is None:
            print(f"⚠️ Failed to find storm with name={name} or id={id}")

        return storm
    
    def is_active(self):
        '''
        Checks if the current region is active by checking if the discussion is present. Not sure if this will be needed because I do not know if discussions stop being 
        produced outside of the season at the moment

        @return true if discussion is present, false otherwise
        '''
        return bool(self.discussion)
    
    def to_dict(self):
        '''
        to_dict method for easy testing a json loading

        @return a dictionary representing the region
        '''
        return {
            "name": self.name,
            "discussion": self.discussion,
            "storms": [s.to_dict() for s in self.storms]
        }  

    def sort_storms(self):
        '''
        Sort storms in the storm list by wind speed
        '''
        self.storms.sort(key=lambda s: s.wind_speed or 0, reverse = True)