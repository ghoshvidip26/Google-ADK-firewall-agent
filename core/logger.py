import os
import json
from datetime import datetime

def logEvent(data):
    os.makedirs("sessions",exist_ok=True)
    payload = {
        "timestamp": str(datetime.now()),
        **data
    }

    with open("sessions/trace.jsonl", "a") as f:
        f.write(json.dumps(payload))
        f.write("\n")