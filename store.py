import csv
import os
from datetime import datetime


def get_filename(state, city=None):
    dt = datetime.now().strftime("%Y-%m-%d_%H:%M:%S")
    if city:
        return "{}_{}_{}.csv".format(state, city, dt)
    else:
        return "{}_{}.csv".format(state, dt)


def save_result(result, state, city=None):
    filename = get_filename(state, city)
    with open(os.path.join(os.path.dirname(os.path.abspath(__file__)), filename), "w") as f:
        output = csv.writer(f)
        output.writerow(result[0].keys())
        for row in result:
            output.writerow(row.values())
