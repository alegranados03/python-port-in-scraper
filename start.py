from dotenv import load_dotenv

load_dotenv()
import time
import subprocess
import schedule
import sys

# from main import Main


def fetch():
    result = subprocess.run([sys.executable, "main.py"])
    if result.returncode == 100:
        print("Script exited with an error due to resources. Restarting...")
    else:
        print("Script finished with exit code {}".format(result.returncode))


if __name__ == "__main__":
    schedule.every(10).seconds.do(fetch)

    while True:
        schedule.run_pending()
        time.sleep(1)
