
import pandas as pd
import numpy as np
from pathlib import Path


CSV_FILE = "renewable_dispatch.csv"
MEAN_PRICE = 0.10


class ReseDispatchDown:

    def __init__(self, csv_file, mean_electricity_price):

        self.csv_file = csv_file
        self.mean_electricity_price = float(
            mean_electricity_price
        )

        if self.mean_electricity_price < 0:
            raise ValueError(
                "Mean electricity price cannot be negative"
            )

        self.results = {}


    # READ CSV DATA
   

    def load_data(self):

        df = pd.read_csv(self.csv_file)

        print("CSV loaded successfully!")
        print("Columns found:", df.columns.tolist())

        required_columns = [
            "available_mw",
            "dispatch_down_mw"
        ]

        for col in required_columns:
            if col not in df.columns:
                raise ValueError(
                    f"Missing required column: {col}"
                )

        # Convert Pandas data to NumPy arrays
        available_mw = pd.to_numeric(
            df["available_mw"],
            errors="raise"
        ).to_numpy(dtype=float)

        dispatch_down_mw = pd.to_numeric(
            df["dispatch_down_mw"],
            errors="raise"
        ).to_numpy(dtype=float)

        if len(available_mw) == 0:
            raise ValueError("CSV contains no hourly data")

        if not (
            np.all(np.isfinite(available_mw))
            and np.all(np.isfinite(dispatch_down_mw))
        ):
            raise ValueError("CSV contains invalid numbers")

        if np.any(available_mw < 0):
            raise ValueError("Available MW cannot be negative")

        if np.any(dispatch_down_mw < 0):
            raise ValueError("Dispatch-down cannot be negative")

        if np.any(dispatch_down_mw > available_mw):
            raise ValueError(
                "Dispatch-down exceeds available MW"
            )

        return available_mw, dispatch_down_mw

    # HELPER METHOD
   

    def calculate_hourly_price(self, hourly_energy_mwh):

        mean_energy = np.mean(hourly_energy_mwh)

        if mean_energy == 0:
            return np.zeros_like(hourly_energy_mwh)

        # Scale hourly price relative to mean output
        hourly_price = (
            self.mean_electricity_price
            * hourly_energy_mwh
            / mean_energy
        )

        return hourly_price

    # CALCULATE HOURLY OUTPUTS
   

    def evaluate(self):

        available_mw, dispatch_down_mw = self.load_data()

        # 1. Hourly power output (MW)
        hourly_output_mw = (
            available_mw - dispatch_down_mw
        )

        # 2. Hourly energy generation (MWh)
        # Each row represents one hour
        hourly_energy_mwh = hourly_output_mw * 1.0

        # 3. Convert hourly MWh to GWh
        hourly_energy_gwh = (
            hourly_energy_mwh / 1000
        )

        # 4. Cumulative hourly generation (GWh)
        cumulative_energy_gwh_hourly = np.cumsum(
            hourly_energy_gwh
        )

        # 5. Total cumulative generation (GWh)
        cumulative_energy_gwh_total = np.sum(
            hourly_energy_gwh
        )

        # 6. Hourly scaled electricity price (€/kWh)
        hourly_price = self.calculate_hourly_price(
            hourly_energy_mwh
        )

        # 7. Convert energy from MWh to kWh
        hourly_energy_kwh = (
            hourly_energy_mwh * 1000
        )

        # 8. Hourly electricity cost (€)
        hourly_cost_of_electricity = (
            hourly_energy_kwh * hourly_price
        )

        # STORE RESULTS IN DICTIONARY
    

        self.results = {

            "hourly_output_mw":
                hourly_output_mw,

            "cumulative_energy_gwh_total":
                cumulative_energy_gwh_total,

            "cumulative_energy_gwh_hourly":
                cumulative_energy_gwh_hourly,

            "hourly_cost_of_electricity":
                hourly_cost_of_electricity

        }

        return self.results



# FIND CSV FILE


def find_csv(filename):

    script_folder = Path(__file__).resolve().parent

    locations = [
        script_folder / filename,
        script_folder.parent / filename,
        script_folder.parent.parent / filename,
        Path.cwd() / filename
    ]

    for location in locations:

        if location.is_file():
            print("Found CSV:", location)
            return location

    raise FileNotFoundError(
        f"Cannot find {filename}. "
        "Check the filename and folder."
    )


# RUN PROGRAM

if __name__ == "__main__":

    csv_path = find_csv(CSV_FILE)

    model = ReseDispatchDown(
        csv_file=csv_path,
        mean_electricity_price=MEAN_PRICE
    )

    results = model.evaluate()

    # PRINT RESULTS
   

    print("\n========== RESULTS ==========")

    print("\nHourly Output (MW):")
    print(results["hourly_output_mw"])

    print("\nCumulative Energy (GWh) - Hourly:")
    print(results["cumulative_energy_gwh_hourly"])

    print("\nTotal Energy Generation (GWh):")
    print(results["cumulative_energy_gwh_total"])

    print("\nHourly Electricity Cost (€):")
    print(results["hourly_cost_of_electricity"])

    # ---------------------------------
    # SAVE RESULTS AS CSV
    # ---------------------------------

    output_df = pd.DataFrame({

        "hourly_output_mw":
            results["hourly_output_mw"],

        "cumulative_energy_gwh_hourly":
            results["cumulative_energy_gwh_hourly"],

        "hourly_cost_of_electricity":
            results["hourly_cost_of_electricity"]

    })

    output_file = (
        Path(__file__).resolve().parent
        / "dispatch_down_results.csv"
    )

    output_df.to_csv(
        output_file,
        index=False
    )

    print("\nProcessing complete!")
    print("Results saved to:", output_file)

    # =====================================
    # CREATE GRAPHS
    # =====================================

    import matplotlib.pyplot as plt

    graph_folder = (
        Path(__file__).resolve().parent / "graphs"
    )
    graph_folder.mkdir(exist_ok=True)

    # Use timestamps if present in CSV
    original_data = pd.read_csv(csv_path)

    if "timestamp" in original_data.columns:
        dates = pd.to_datetime(
            original_data["timestamp"],
            errors="coerce"
        )

        if dates.notna().all():
            x = dates
            x_label = "Date"
        else:
            x = np.arange(
                1, len(results["hourly_output_mw"]) + 1
            )
            x_label = "Hour"
    else:
        x = np.arange(
            1, len(results["hourly_output_mw"]) + 1
        )
        x_label = "Hour"

    # -------------------------------------
    # GRAPH 1: HOURLY ELECTRICAL OUTPUT
    # -------------------------------------

    plt.figure(figsize=(12, 5))

    plt.plot(
        x,
        results["hourly_output_mw"]
    )

    plt.title("Hourly Renewable Electricity Output")
    plt.xlabel(x_label)
    plt.ylabel("Power Output (MW)")
    plt.grid(True)
    plt.tight_layout()

    plt.savefig(
        graph_folder / "hourly_output.png",
        dpi=300
    )

    # -------------------------------------
    # GRAPH 2: CUMULATIVE ENERGY
    # -------------------------------------

    plt.figure(figsize=(12, 5))

    plt.plot(
        x,
        results["cumulative_energy_gwh_hourly"]
    )

    plt.title("Cumulative Energy Generation")
    plt.xlabel(x_label)
    plt.ylabel("Cumulative Energy (GWh)")
    plt.grid(True)
    plt.tight_layout()

    plt.savefig(
        graph_folder / "cumulative_energy.png",
        dpi=300
    )

    # -------------------------------------
    # GRAPH 3: HOURLY ELECTRICITY COST
    # -------------------------------------

    plt.figure(figsize=(12, 5))

    plt.plot(
        x,
        results["hourly_cost_of_electricity"]
    )

    plt.title("Hourly Electricity Cost")
    plt.xlabel(x_label)
    plt.ylabel("Electricity Cost (€)")
    plt.grid(True)
    plt.tight_layout()

    plt.savefig(
        graph_folder / "hourly_cost.png",
        dpi=300
    )

    # -------------------------------------
    # GRAPH 4: TOTAL ENERGY GENERATION
    # -------------------------------------

    total_energy = results[
        "cumulative_energy_gwh_total"
    ]

    plt.figure(figsize=(7, 5))

    plt.bar(
        ["Total Generation"],
        [total_energy]
    )

    plt.title("Total Renewable Energy Generation")
    plt.ylabel("Energy (GWh)")
    plt.grid(axis="y")
    plt.tight_layout()

    plt.savefig(
        graph_folder / "total_energy.png",
        dpi=300
    )

    # -------------------------------------
    # SHOW GRAPHS
    # -------------------------------------

    print("\nAll four graphs created!")
    print("Graphs saved in:", graph_folder)

    plt.show()
