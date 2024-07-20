import os
from datetime import datetime

# Directories for reports and logs
report_dir = os.getenv('REPORT_DIR', '/reports')
log_dir = os.getenv('LOG_DIR', '/logs')

# Ensure the directories exist
os.makedirs(report_dir, exist_ok=True)
os.makedirs(log_dir, exist_ok=True)

# Create a report file
report_file = os.path.join(report_dir, f'report_{datetime.now().strftime("%Y%m%d%H%M%S")}.txt')
with open(report_file, 'w') as f:
    f.write('This is a report.\n')

# Create a log file
log_file = os.path.join(log_dir, f'log_{datetime.now().strftime("%Y%m%d%H%M%S")}.txt')
with open(log_file, 'w') as f:
    f.write('This is a log entry.\n')

print(f'Report saved to {report_file}')
print(f'Log saved to {log_file}')
