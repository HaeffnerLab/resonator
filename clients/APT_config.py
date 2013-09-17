class stageConfiguration(object):
    """
    Stores complete configuration for each of the channels
    """
    #list of devices in the form [(stage_name, stage_serial), ...]
    devicenames = [('blue UD',83836221),('Blue RL', 83833894),('Red UD', 83836799),('Red RL',83836807)]
    pitch_dict = {}
    #Different pitches of lead screw: Orders:[(blue UD),(Blue RL),(Red UD),(Red RL)]
    #pitch in float number

    def get_pitch(self,serialNumber):
        try:
            pitch = self.pitch_dict[serialNumber]
        except KeyError:
            pitch = 1
        return pitch
