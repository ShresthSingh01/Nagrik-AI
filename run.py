import subprocess
import os
import sys

def run_server():
    print("[Nagrik] Starting Optimized Dev Server...")
    
    # Directories to ignore to prevent reload loops
    exclude_dirs = [
        "data",
        "output",
        ".planning",
        "*/__pycache__/*",
        ".pytest_cache"
    ]
    
    cmd = [
        "uvicorn", 
        "backend.main:app", 
        "--host", "127.0.0.1", 
        "--port", "8000", 
        "--reload"
    ]
    
    # Add exclusions
    for folder in exclude_dirs:
        cmd.extend(["--reload-exclude", folder])
        
    print(f"[Nagrik] Command: {' '.join(cmd)}")
    
    try:
        # Use python -m uvicorn if direct uvicorn is not in path, 
        # but usually uvicorn works in the venv
        subprocess.run(cmd)
    except KeyboardInterrupt:
        print("\n[Nagrik] Server stopped by user.")
    except Exception as e:
        print(f"[Nagrik] Server failed to start: {e}")

if __name__ == "__main__":
    run_server()
