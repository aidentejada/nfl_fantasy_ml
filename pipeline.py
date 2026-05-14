# courtesy of Claudio Opussium the 4.7th
from pathlib import Path
import runpy
import sys


PROJECT_ROOT = Path(__file__).resolve().parent
DATA_DIR = PROJECT_ROOT / "data"

PIPELINE_STEPS = [
    "01_pull_data.py",
    "02_clean_data.py",
    "03_feature_engineering.py",
    "04_label_creation.py",
]


def ensure_data_folder() -> None:
    DATA_DIR.mkdir(exist_ok=True)


def run_step(script_name: str) -> None:
    script_path = PROJECT_ROOT / script_name

    if not script_path.exists():
        raise FileNotFoundError(f"Could not find required script: {script_name}")

    print("\n" + "=" * 60)
    print(f"Running {script_name}")
    print("=" * 60)

    runpy.run_path(str(script_path), run_name="__main__")

    print(f"Finished {script_name}")


def main() -> None:
    print("Starting NFL fantasy sleeper data pipeline...")

    ensure_data_folder()

    for script in PIPELINE_STEPS:
        try:
            run_step(script)
        except ModuleNotFoundError as error:
            print("\nPipeline stopped because a required package is missing.")
            print(f"Missing module: {error.name}")

            if error.name == "nflreadpy":
                print("\nInstall it with:")
                print("  pip install nflreadpy")

            sys.exit(1)

        except Exception as error:
            print(f"\nPipeline failed while running {script}")
            print(f"Error: {error}")
            sys.exit(1)

    print("\n" + "=" * 60)
    print("Pipeline complete!")
    print("Generated files should be in the data/ folder.")
    print("=" * 60)


if __name__ == "__main__":
    main()