"""
Our oracle will only train on the age, gender, and number of days with prescriptions
"""

import csv
from datetime import datetime, timedelta
import numpy as np



def get_note_events():
    hamid_to_status = {}

    with open("../data/mimiciii/NOTEEVENTS.csv", 'r') as csv_file:
        csv_reader = csv.reader(csv_file, delimiter=',')
        i = 0
        for row in csv_reader:
            if i > 0:
                text = row[10].lower()

                if "deceased" in text or "dead" in text or "expired" in text:
                    hamid_to_status[row[2]] = 0
                else:
                    hamid_to_status[row[2]] = 1
                #
                # try:
                #     index = text.index("Discharge Condition:")
                #     candidate = text[index:]
                #     if "deceased" in candidate or "dead" in candidate or "expired" in candidate:
                #         hamid_to_status[row[2]] = 1
                #     else:
                #         hamid_to_status[row[2]] = 0
                # except ValueError:
                #     hamid_to_status[row[2]] = 0
                if i % 100000 == 0:
                    print("Done " + str(i))
            i += 1
    return hamid_to_status


def get_prescription_days():
    hamid_to_prescription_days = {}

    # with open("../data/mimiciii/pneumonia.PRESCRIPTIONS.csv", 'r') as csv_file:
    with open("../data/mimiciii/pneumonia.LABEVENTS.csv", 'r') as csv_file:
        csv_reader = csv.reader(csv_file, delimiter=',')
        i = 0
        for row in csv_reader:
            if i > 0:
                if row[2] not in hamid_to_prescription_days:
                    hamid_to_prescription_days[row[2]] = set()

                if row[4] == "":
                    i += 1
                    continue
                presc_start = datetime.strptime(row[4], '%Y-%m-%d %H:%M:%S')
                hamid_to_prescription_days[row[2]].add(presc_start.date())
            i += 1
    return hamid_to_prescription_days


def get_age():
    subject_to_min_admittime = {}
    subject_to_hamids = {}
    hamid_to_age = {}
    hamid_to_gender = {}

    with open("../data/mimiciii/ADMISSIONS.csv", 'r') as csv_file:
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
    with open("../data/mimiciii/PATIENTS.csv", 'r') as csv_file:
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
    hamid_to_status = get_note_events()
    hamid_to_age, hamid_to_gender = get_age()
    prescription_mapping = get_prescription_days()

    with open("../data/mimiciii/pneumonia.ADMISSIONS.csv", 'r') as csv_file:
        csv_reader = csv.reader(csv_file, delimiter=',')
        with open("../data/exp/ORACLE.csv", 'w') as w_file:
            csv_writer = csv.writer(w_file, delimiter=',')
            i = 0
            for row in csv_reader:
                if i > 0:
                    admittime = datetime.strptime(row[3], '%Y-%m-%d %H:%M:%S')
                    dischtime = datetime.strptime(row[4], '%Y-%m-%d %H:%M:%S')
                    status = hamid_to_status[row[2]] if row[2] in hamid_to_status else 0
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
                        prescription_days = prescription_mapping[row[2]] if row[2] in prescription_mapping else []
                        csv_writer.writerow([row[2], age, gender, status, len(prescription_days), los / timedelta(days=1), 1 if alive else 0])
                i += 1


########################################################################

produce_output()
