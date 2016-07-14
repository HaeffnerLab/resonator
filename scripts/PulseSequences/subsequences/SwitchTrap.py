from common.okfpgaservers.pulser.pulse_sequences.pulse_sequence import pulse_sequence

class switch_trap(pulse_sequence):

    required_parameters = [
                  ('SwitchTrap','switch_duration'),
                  ('SwitchTrap','switch_enable')
                  ]

    def sequence(self):
        psw = self.parameters.SwitchTrap
        if psw.switch_enable:
            dur = psw.switch_duration
            self.end = self.start + dur
            self.addTTL('RF_switch', self.start, dur)
