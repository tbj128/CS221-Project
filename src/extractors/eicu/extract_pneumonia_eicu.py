"""
Scans the eICU datasets and subsets the datasets for only those patients admitted into ICU with pneumonia

Note: This script was not actually used because the MIMIC-III dataset was selected over the eICU dataset
"""

import csv


def get_patients_with_pneumonia():
    patients = []
    with open("../../../data/eicu/patient.csv", 'r') as csv_file:
        csv_reader = csv.reader(csv_file, delimiter=',')
        with open("../../../data/eicu/pneumonia.patient.csv", 'w') as csv_file:
            csv_writer = csv.writer(csv_file, delimiter=',')
            i = 0
            for row in csv_reader:
                if i == 0:
                    csv_writer.writerow(row)
                elif "pneumonia" in row[7].lower():
                    patients.append(row[0])
                    csv_writer.writerow(row)
                i += 1
    print("Found " + str(len(patients)) + " with pneumonia")
    return patients


def produce_file_subset(file, patient_ids):
    with open("../../../data/eicu/" + file, 'r') as csv_file:
        csv_reader = csv.reader(csv_file, delimiter=',')
        with open("../../../data/eicu/pneumonia." + file, 'w') as csv_file:
            csv_writer = csv.writer(csv_file, delimiter=',')
            i = 0
            for row in csv_reader:
                if i == 0:
                    csv_writer.writerow(row)
                elif row[1] in patient_ids:
                    csv_writer.writerow(row)
                if i % 100000 == 0:
                    print("     Processed: " + str(i))
                i += 1


########################################################################

files = [
    # "diagnosis.csv",
    # "apacheApsVar.csv",
    # "lab.csv",
    # "microLab.csv",
    # "pastHistory.csv",
    # "medication.csv"
    "infusionDrug.csv"
]

patient_ids = set(get_patients_with_pneumonia())
for file in files:
    print("Processing file " + file)
    produce_file_subset(file, patient_ids)

