"""
Produces a small data set based only on the patient data used for baseline.
Baselines act as a "lower-bound" performance for our model.

Note: baseline will only train on the age and gender of patients

This file must be run prior to running baseline.py

"""

import csv
from datetime import datetime, timedelta
import numpy as np


def get_age():
    subject_to_min_admittime = {}
    subject_to_hamids = {}
    hamid_to_age = {}
    hamid_to_gender = {}

    with open("../../data/mimiciii/ADMISSIONS.csv", 'r') as csv_file:
        csv_reader = csv.reader(csv_file, delimiter=',')
        i = 0
        for row in csv_reader:
            if i > 0:
                admittime = datetime.strptime(row[3], '%Y-%m-%d %H:%M:%S')
                if row[1] in subject_to_min_admittime:
                    if admittime < subject_to_min_admittime[row[1]]:
                        # print("Orig " + str(subject_to_min_admittime[row[1]]) + " new " + str(admittime))
                        subject_to_min_admittime[row[1]] = admittime
                else:
                    subject_to_min_admittime[row[1]] = admittime
                if row[1] not in subject_to_hamids:
                    subject_to_hamids[row[1]] = []
                subject_to_hamids[row[1]].append(row[2])
            i += 1

    # Age is the difference between DOB and first admit time
    with open("../../data/mimiciii/PATIENTS.csv", 'r') as csv_file:
        csv_reader = csv.reader(csv_file, delimiter=',')
        i = 0
        for row in csv_reader:
            if i > 0:
                if row[1] in subject_to_min_admittime:
                    dob = datetime.strptime(row[3], '%Y-%m-%d %H:%M:%S')
                    age = subject_to_min_admittime[row[1]] - dob

                    for h in subject_to_hamids[row[1]]:
                        hamid_to_age[h] = age.days / float(365)
                        hamid_to_gender[h] = row[2]
            i += 1
    return hamid_to_age, hamid_to_gender


def produce_output():
    hamid_to_age, hamid_to_gender = get_age()

    with open("../../data/mimiciii/pneumonia.ADMISSIONS.csv", 'r') as csv_file:
        csv_reader = csv.reader(csv_file, delimiter=',')
        with open("../../data/exp/BASELINE.csv", 'w') as w_file:
            csv_writer = csv.writer(w_file, delimiter=',')
            i = 0
            for row in csv_reader:
                if i > 0:
                    admittime = datetime.strptime(row[3], '%Y-%m-%d %H:%M:%S')
                    dischtime = datetime.strptime(row[4], '%Y-%m-%d %H:%M:%S')
                    los = dischtime - admittime
                    age = hamid_to_age[row[2]]
                    alive = row[5] == ""
                    if age > 100:
                        age = 89 + np.random.choice([i for i in range(10)], 1, p=[(10 - x)/float(55) for x in range(10)])
                        age = age[0]
                    if age > 10:
                        gender = hamid_to_gender[row[2]]
                        if gender == "M":
                            gender = 1
                        else:
                            gender = 0
                        csv_writer.writerow([age, gender, los / timedelta(days=1), 1 if alive else 0])
                i += 1


########################################################################

produce_output()
