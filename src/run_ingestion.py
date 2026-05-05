import subprocess
import sys
from pathlib import Path

def run_phase(script_name):
    script_path = Path(__file__).resolve().parent / "phase1_ingestion" / script_name
    print(f"\n{'='*50}\nRunning {script_name}...\n{'='*50}")
    result = subprocess.run([sys.executable, str(script_path)])
    if result.returncode != 0:
        print(f"Error: {script_name} failed with exit code {result.returncode}")
        sys.exit(1)

if __name__ == "__main__":
    phases = [
        "phase1_1_fetch.py",
        "phase1_2_extract.py",
        "phase1_3_clean.py",
        "phase1_4_chunk.py",
        "phase1_5_embed.py",
        "phase1_6_vector_db.py"
    ]
    
    for phase in phases:
        run_phase(phase)
        
    print("\n✅ Ingestion pipeline completed successfully.")
