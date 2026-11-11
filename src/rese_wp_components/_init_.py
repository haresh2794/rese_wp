class RenewableEnergy:


    def __init__(self):
        # Configuration and inputs
        self.capacity_mw = 100

        # Input data
        self.hourly_cf = None
        #outputs

        # Computed attributes / values
        self.hourly_output_mw = None #Standard naming 
        self.cumulative_energy_gwh = None

        # Results dictionary
        self.results = None #standard naming