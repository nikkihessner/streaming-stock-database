# src/file_watcher.py

from pathlib import Path

from stock_pipeline.utils.file_utils import list_xlsx_files, build_file_metadata

DATA_DIR = Path("/app/data")

def main() -> None:
    files = list_xlsx_files(DATA_DIR)
    if not files:
        print("No .xlsx files found in ", DATA_DIR)
        return
    
    for f in files:
        meta = build_file_metadata(f)
        print(meta) # later: send to Kafka instead of print 

if __name__ == "__main__":
    main()