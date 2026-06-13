class ProportionalController:
    def __init__(self, kp):
        self.kp = kp

    def apply(self, error):
        return self.kp * error