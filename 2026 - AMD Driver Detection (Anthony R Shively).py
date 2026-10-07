#2026 - Anthony R Shively (Mercer Ohio 1997)

#New-Item -ItemType Directory -Path C:\Temp\AMD106 -Force; pnputil /export-driver oem106.inf C:\Temp\AMD106; Get-ChildItem C:\Temp\AMD106 -Recurse -Filter *.inf | Select-String "PCI\\VEN_1002&DEV_67DF|1A601043"

import subprocess
import re
print('')
#result = subprocess.run("ipconfig", shell=True, capture_output=True, text=True)
#print(result.stdout)
try:
    result = subprocess.run( ["pnputil", "/enum-drivers"], capture_output=True, text=True, encoding="utf-8", errors="replace" )
    lines = result.stdout.splitlines()
    for i, line in enumerate(lines):
        if re.search(r"Class Name:\s+Display adapters", line, re.IGNORECASE):
            start = max(0, i - 5)
            end = min(len(lines), i + 6)
            print("\n".join(lines[start:end]))
            print()
except Exception as e:
    print('Program Issues:', e)
    input('Stopped')
input('Exit Program')