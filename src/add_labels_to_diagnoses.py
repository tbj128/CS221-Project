"""
Add labels to the DIAGNOSES_ICD.csv by using info from D_ICD_DIAGNOSES.csv
"""

import csv


def get_icd_code_mapping():
    map = {}
    with open("../data/mimiciii/D_ICD_DIAGNOSES.csv", 'r') as csv_file:
        csv_reader = csv.reader(csv_file, delimiter=',')
        for row in csv_reader:
            map[row[1]] = row[2]
    return map


def add_labels():
    mapping = get_icd_code_mapping()
    with open("../data/mimiciii/DIAGNOSES_ICD.csv", 'r') as csv_file:
        with open("../data/mimiciii/DIAGNOSES_ICD_LABELED.csv", 'w') as w_file:
            csv_writer = csv.writer(w_file, delimiter=',')
            csv_reader = csv.reader(csv_file, delimiter=',')
            for row in csv_reader:
                new_row = []
                new_row.extend(row)
                if row[4] in mapping:
                    new_row.append(mapping[row[4]])
                csv_writer.writerow(new_row)

########################################################################

add_labels()
