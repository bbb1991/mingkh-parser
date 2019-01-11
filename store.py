import csv
from datetime import datetime
import codecs


def get_filename(state, city=None):
    dt = datetime.now().strftime("%Y-%m-%d")
    if city:
        return r"{}_{}_{}.csv".format(state, city, dt)
    else:
        return r"{}_{}.csv".format(state, dt)


def save_result(result, state, city=None):
    filename = get_filename(state, city)
    with codecs.open(filename, "w", "utf-8") as f:
        output = csv.writer(f)
        output.writerow(result[0].keys())
        for row in result:
            output.writerow(row.values())
