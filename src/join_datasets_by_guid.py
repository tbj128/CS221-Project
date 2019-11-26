"""
Join lab dataset with the patient.csv dataset based on a specific lab measurement
"""

import csv

import sys


def join(file2, file1, labname):
    with open("../data/eicu/" + file1, 'r') as csv_file1:
        csv_reader1 = csv.reader(csv_file1, delimiter=',')

        id_to_lab_result = {}
        id_col1 = 1
        for row in csv_reader1:
            if row[4] == labname:
                id_to_lab_result[row[id_col1]] = row[5]

        with open("../data/eicu/" + file2, 'r') as csv_file2:
            csv_reader2 = csv.reader(csv_file2, delimiter=',')
            with open("../data/eicu/" + file1 + "." + file2, 'w') as csv_file:
                csv_writer = csv.writer(csv_file, delimiter=',')
                for row in csv_reader2:
                    id = row[0]
                    row.append(id_to_lab_result[id] if id in id_to_lab_result else "")
                    csv_writer.writerow(row)


########################################################################


data1 = sys.argv[1] # Patient.csv dataset (each row is a unique patient GUID in file)
data2 = sys.argv[2] # Lab file
labname = sys.argv[3]

join(data1, data2, labname)

