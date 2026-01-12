
import sys
import os
import time
import subprocess

def main():
    print("Running Spark Verification...")
    print("This will start the Spark Streaming Job. Press Ctrl+C to stop.")
    
    # We run the job as a subprocess to keep the main shell free if needed,
    # but for verification we usually want to see the output directly.
    
    job_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '../processing/spark/streaming/spark_streaming_job.py'))
    
    # Run with limited timeout or just let it run
    cmd = [sys.executable, job_path]
    
    try:
        # Use shell=True for Windows env var expansion if needed, but usually not for direct python calls
        subprocess.run(cmd, check=True)
    except KeyboardInterrupt:
        print("\nStopping Spark Job...")

if __name__ == "__main__":
    main()
