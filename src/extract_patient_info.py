"""
Extracts all data regarding a particular patient-stay.
"""

import csv
import sys
import subprocess


def scan_file_for_relevant_lines(file, id):
    retarr = [[file[0]]]
    with open("../data/eicu/" + file[0], 'r') as csv_file:
        csv_reader = csv.reader(csv_file, delimiter=',')
        for row in csv_reader:
            # Write just the first row
            retarr.append(row)
            break

    try:
        if file[1] == 1:
            output = subprocess.check_output(["grep", "," + id + ",", "../data/eicu/" + file[0]])
        else:
            output = subprocess.check_output(["grep", "^" + id + ",", "../data/eicu/" + file[0]])
        arr = output.decode("utf-8").split('\n')
        for a in arr:
            retarr.append([a.strip()])
        return retarr
    except subprocess.CalledProcessError:
        return []


########################################################################


patient_id = sys.argv[1]
output_path = sys.argv[2]

files = [
    ["patient.csv", 0],
    ["diagnosis.csv", 1],
    ["apacheApsVar.csv", 1],
    ["lab.csv", 1],
    ["microLab.csv", 1],
    ["pastHistory.csv", 1],
    ["medication.csv", 1]
]

output = []
for file in files:
    print("Looking through file " + file[0])
    output.extend(scan_file_for_relevant_lines(file, patient_id))
    output.append([])
    output.append([])

with open(output_path, 'w') as csv_file:
    csv_writer = csv.writer(csv_file, delimiter=',')
    for row in output:
        if len(row) == 1:
            for r in csv.reader(row[0].split("\n"), delimiter=',', quotechar="\""):
                csv_writer.writerow(r)
        else:
            csv_writer.writerow(row)

