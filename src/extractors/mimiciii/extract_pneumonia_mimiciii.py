"""
Scans the MIMIC-III datasets and subsets the datasets for only those patients admitted into ICU with pneumonia

Note: This script was not used in the end as the filtered was instead done through a SQL query

"""

import csv


def get_lab_item_mapping():
    map = {}
    with open("../../../data/mimiciii/D_LABITEMS.csv", 'r') as csv_file:
        csv_reader = csv.reader(csv_file, delimiter=',')
        for row in csv_reader:
            map[row[1]] = row[2]
    return map


def get_icd_codes():
    pneumonia_codes = []
    with open("../../../data/mimiciii/D_ICD_DIAGNOSES.csv", 'r') as csv_file:
        csv_reader = csv.reader(csv_file, delimiter=',')
        for row in csv_reader:
            if "pneumonia" in row[3].lower():
                pneumonia_codes.append(row[1])
    print("Found " + str(len(pneumonia_codes)) + " codes")
    return pneumonia_codes


def get_patients_with_pneumonia():
    hamid = set()
    pneumonia_codes = set(get_icd_codes())
    with open("../../../data/mimiciii/DIAGNOSES_ICD.csv", 'r') as csv_file:
        csv_reader = csv.reader(csv_file, delimiter=',')
        for row in csv_reader:
            if row[4] in pneumonia_codes:
                hamid.add(row[2])

    with open("../../../data/mimiciii/ADMISSIONS.csv", 'r') as csv_file:
        csv_reader = csv.reader(csv_file, delimiter=',')
        with open("../data/mimiciii/pneumonia.ADMISSIONS.csv", 'w') as csv_file:
            csv_writer = csv.writer(csv_file, delimiter=',')
            i = 0
            for row in csv_reader:
                if i == 0:
                    csv_writer.writerow(row)
                elif row[2] in hamid:
                    csv_writer.writerow(row)
                i += 1
    return hamid


def produce_file_subset(file, patient_ids):
    mapping = get_lab_item_mapping()

    with open("../../../data/mimiciii/" + file, 'r') as csv_file:
        csv_reader = csv.reader(csv_file, delimiter=',')
        with open("../../../data/mimiciii/pneumonia." + file, 'w') as csv_file:
            csv_writer = csv.writer(csv_file, delimiter=',')
            i = 0
            for row in csv_reader:
                if i == 0:
                    csv_writer.writerow(row)
                elif row[2] in patient_ids:
                    new_row = []
                    new_row.extend(row)
                    if file == "LABEVENTS.csv":
                        new_row.append(mapping[row[3]])
                    csv_writer.writerow(new_row)
                if i % 100000 == 0:
                    print("     Processed: " + str(i))
                i += 1


########################################################################

files = [
    # "PRESCRIPTIONS.csv",
    "LABEVENTS.csv"
]

patient_ids = set(get_patients_with_pneumonia())
for file in files:
    print("Processing file " + file)
    produce_file_subset(file, patient_ids)

