# Kafka Topics

## files_to_process
- key: file_id (uuid)
- value:
  - file_id (uuid)
  - path (string)
  - symbol_hint (string)
  - discovered_at (timestamp)

## rows_to_process
- key: row_id (uuid or file_id+row_index)
- value:
  - row_id (uuid)
  - file_id (uuid)
  - row_index (int)
  - symbol (string)
  - trade_date (date string)
  - open, high, low, close (decimal)
  - volume (int)
  - source_file (string)