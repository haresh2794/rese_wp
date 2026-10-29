import numpy as np
#comment 

class RenewableEnergy:

    def __init__(self):
        # Configuration and Inputs
        self.capacity_mw = 100

        self.hourly_cf = None

        #Output
        # Computed attributes / values # if we dont init it might take first scenario outputs as the second scenario's input
        self.hourly_output_mw = None #Standard naming # 
        self.cumulative_energy_gwh_hourly = None

        # Results dictionary
        self.results = None #Standard naming


    #------------------------------------------------------------
    # Configuration
    #-------------------------------------------------------------


    def configure(self, config=None):
        if config is None:
            return

        self.capacity_mw = config.get("capacity_mw",self.capacity_mw)

        self.hourly_cf = config.get("hourly_cf", self.hourly_cf)



    #------------------------------------------------------------
    # HELPER METHODS
    #-------------------------------------------------------------

    def _calculate_hourly_output(self, hourly_cf):

        return hourly_cf * self.capacity_mw

    def _calculate_cumulative_energy_gwh(self, hourly_output_mw):

        return np.cumsum(hourly_output_mw) / 1000


    #------------------------------------------------------------
    # Evaluate
    #-------------------------------------------------------------
    #IMPORATANT
    def evaluate(self):

        if self.hourly_cf is None:
            raise ValueError(
                "hourly_cf must be provided in the configuration."
            )


        # Calculate hourly output
        self.hourly_output_mw = self._calculate_hourly_output(
            self.hourly_cf
        )

        # Calculate cumulative energy
        self.cumulative_energy_gwh_hourly = (
            self._calculate_cumulative_energy_gwh(
                self.hourly_output_mw
            )
        )
       

        self.results = {
            "hourly_output_mw": self.hourly_output_mw,
            "cumulative_energy_gwh_hourly": self.cumulative_energy_gwh_hourly,
        }
        

        return self.results