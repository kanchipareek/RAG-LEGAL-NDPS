import json 
import os 
import time 
from datetime import datetime

# folder where all trace files will be saved
TRACE_DIR = "logs/trace"

def init_trace(query):
    """
    Call this when a user asks a question. 
    It creates a new "trace" -  basically a notebook where we wil write down 
    everything that happens while writing this question.
    """
    # create the trace folder if it doesn't exist
    os.makedirs(TRACE_DIR, exist_ok=True)

    # start a new page in our notebook with the question and the current date/time 
    trace = {
        "query": query,
        "timestamp": datetime.now().isoformat(),
        "stages": {}
    }
    return trace


def log_stage(trace, stage_name, data):
    """
    Call this after each step of the pipeline (retrieval, reranking, etc.)
    It's like writing a new entry in our notebook: "At this step, this happened."

    trace       — the notebook we started with init_trace()
    stage_name  — what step we're at (e.g. "retrieval", "reranking")
    data        — whatever info we want to record (scores, chunk IDs, etc.)
    """

    # Write this step's results into the notebook with the current time
    trace["stages"][stage_name] = {
        "data": data,                             # What happened at this step
        "timestamp": datetime.now().isoformat()   # When this step ran
    }


def save_trace(trace):
    """
    Call this at the very end, after the answer has been generated.
    Saves the entire notebook to a JSON file so you can open it later and
    see exactly what happened for this question.
    """

    # Make a filename from the timestamp (e.g. trace_2026-09-09T18-30-00.json)
    # We replace colons with dashes because Windows doesn't allow colons in filenames
    safe_timestamp = trace["timestamp"].replace(":", "-")
    filename = f"trace_{safe_timestamp}.json"
    filepath = os.path.join(TRACES_DIR, filename)

    # Write the notebook to a file
    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(trace, f, ensure_ascii=False, indent=2)

    print(f"Trace saved to {filepath}")
    return filepath