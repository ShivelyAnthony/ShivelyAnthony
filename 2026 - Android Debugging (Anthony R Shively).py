#2026 Anthony R Shively (Mercer Ohio 1997)

import os
import subprocess

subprocess.run(["adb", "kill-server"])
subprocess.run(["adb", "start-server"])
subprocess.run(["adb", "devices", "-l"])
input('Press Enter')
print("--- LIVE ADB LOGCAT ---")
subprocess.run(["adb", "logcat", "-v", "time"])

input("Press Enter to exit...")