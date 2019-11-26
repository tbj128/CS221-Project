"""
Prepares an input file with each row being a patient and derived columns from every data
set using information from the first 24 hours
"""

import csv
from collections import defaultdict
from datetime import datetime, timedelta
import sys

from extractor_utils import calculate_trend

def produce_output(project_dir, output_location, first_hours=24, max_rows=None):
    #
    # Load admissions information
    #
    print("Processing derived admissions file")
    admissions_headers = []
    hadmid_to_admission_info = {}
    with open(project_dir + "/admissions.derived.csv", 'r') as csv_file:
        csv_reader = csv.reader(csv_file, delimiter=',')
        i = 0
        for row in csv_reader:
            if i == 0:
                admissions_headers = row
                i += 1
                continue
            hadmid = row[0]
            hadmid_to_admission_info[hadmid] = row


    #
    # Load lab information
    #
    print("Processing lab file")

    lab_header = []

    # lab -> hadmid
    lab_to_hadmid = defaultdict(set)

    # hadmid -> lab -> labvalues
    hadmid_to_raw_lab_info = {}
    with open(project_dir + "/labevents.csv", 'r') as csv_file:
        csv_reader = csv.reader(csv_file, delimiter=',')
        i = 0
        for row in csv_reader:
            if i == 0:
                lab_header = row
                i += 1
                continue
            hadmid = row[0]
            if hadmid not in hadmid_to_raw_lab_info:
                hadmid_to_raw_lab_info[hadmid] = defaultdict(list)
            admittime = datetime.strptime(hadmid_to_admission_info[hadmid][1], '%Y-%m-%dT%H:%M:%S')
            offset = (datetime.strptime(row[1], '%Y-%m-%d %H:%M:%S') - admittime) / timedelta(hours=1)
            offset = round(offset, 3)
            if offset <= first_hours:
                lab = row[3]
                val = row[6]
                if val == "":
                    # Skip because this is not a numeric value
                    continue
                val = round(float(val), 3)
                lab_to_hadmid[lab].add(hadmid)
                hadmid_to_raw_lab_info[hadmid][lab].append((offset, val))

            if i % 100000 == 0:
                print("   Labs processed {} events".format(i))

            if max_rows is not None and i > max_rows:
                break
            i += 1


    hadmid_to_processed_lab_info = {}
    for hadmid, raw_lab_info in hadmid_to_raw_lab_info.items():
        hadmid_row = []
        for lab, _ in lab_to_hadmid.items():
            if lab in raw_lab_info:
                # Calculate average among all lab values
                hadmid_row.append(sum([t[1] for t in raw_lab_info[lab]]) / float(len(raw_lab_info[lab])))
                # Calculate trend over the time period
                hadmid_row.append(calculate_trend(raw_lab_info[lab]))
            else:
                hadmid_row.append(0)
                hadmid_row.append(0)
        hadmid_to_processed_lab_info[hadmid] = hadmid_row


    #
    # Load prescription information
    #
    print("Processing prescriptions file")

    prescription_header = []
    all_drugs = set()

    # hadmid -> drug
    hadmid_to_drug = defaultdict(set)
    with open(project_dir + "/prescriptions.csv", 'r') as csv_file:
        csv_reader = csv.reader(csv_file, delimiter=',')
        i = 0
        for row in csv_reader:
            if i == 0:
                prescription_header = row
                i += 1
                continue
            if row[4] == "" or row[1] == "" or row[2] == "":
                i += 1
                continue


            hadmid = row[0]
            drug = row[4]

            admittime = datetime.strptime(hadmid_to_admission_info[hadmid][1], '%Y-%m-%dT%H:%M:%S')
            drug_start_offset = (datetime.strptime(row[1], '%Y-%m-%d %H:%M:%S') - admittime) / timedelta(hours=1)
            drug_end_offset = (datetime.strptime(row[2], '%Y-%m-%d %H:%M:%S') - admittime) / timedelta(hours=1)
            if drug_start_offset <= first_hours and drug_end_offset >= 0:
                # Drug was given within the 24 hour window
                all_drugs.add(drug)
                hadmid_to_drug[hadmid].add(drug)

            if i % 100000 == 0:
                print("   Drugs processed {} events".format(i))
            if max_rows is not None and i > max_rows:
                break
            i += 1

    hadmid_to_processed_drug_info = {}
    for hadmid, drugs in hadmid_to_drug.items():
        hadmid_row = []
        for d in all_drugs:
            if d in drugs:
                hadmid_row.append(1)
            else:
                hadmid_row.append(0)
        hadmid_to_processed_drug_info[hadmid] = hadmid_row

    #
    # Load chart information
    #
    print("Processing chart information file")

    chartevent_header = []

    # chartevent -> hadmid
    chartevent_to_hadmid = defaultdict(set)

    # hadmid -> chartevent -> chartevent value
    hadmid_to_raw_chart_info = {}
    with open(project_dir + "/chartevents.csv", 'r') as csv_file:
        csv_reader = csv.reader(csv_file, delimiter=',')
        i = 0
        for row in csv_reader:
            if i == 0:
                chartevent_header = row
                i += 1
                continue
            hadmid = row[0]
            if hadmid not in hadmid_to_raw_chart_info:
                hadmid_to_raw_chart_info[hadmid] = defaultdict(list)
            admittime = datetime.strptime(hadmid_to_admission_info[hadmid][1], '%Y-%m-%dT%H:%M:%S')
            offset = (datetime.strptime(row[1], '%Y-%m-%d %H:%M:%S') - admittime) / timedelta(hours=1)
            offset = round(offset, 3)
            if offset <= first_hours:
                chartitemid = row[2]
                if chartitemid == "220045" or chartitemid == "211":
                    chart = "Heart Rate"
                elif chartitemid == "618" or chartitemid == "220210":
                    chart = "Respiratory Rate"
                elif chartitemid == "220180" or chartitemid == "8441":
                    chart = "Diastolic"
                elif chartitemid == "220179" or chartitemid == "455":
                    chart = "Systolic"
                elif chartitemid == "220277" or chartitemid == "211":
                    chart = "O2"
                elif chartitemid == "223834" or chartitemid == "470":
                    chart = "O2 Flow"
                elif chartitemid == "223762" or chartitemid == "677":
                    chart = "Temperature"

                val = row[5]
                if val == "":
                    # Skip because this is not a numeric value
                    continue
                val = float(val)
                chartevent_to_hadmid[chart].add(hadmid)
                hadmid_to_raw_chart_info[hadmid][chart].append((offset, val))

            if max_rows is not None and i > max_rows:
                break

            if i % 100000 == 0:
                print("   Charts processed {} events".format(i))
            i += 1

    hadmid_to_processed_chart_info = {}
    for hadmid, raw_chart_info in hadmid_to_raw_chart_info.items():
        hadmid_row = []
        for chart, _ in chartevent_to_hadmid.items():
            if chart in raw_chart_info:
                # Calculate average among all chart values
                hadmid_row.append(sum([t[1] for t in raw_chart_info[chart]]) / float(len(raw_chart_info[chart])))
                # Calculate trend over the time period
                hadmid_row.append(calculate_trend(raw_chart_info[chart]))
            else:
                hadmid_row.append(0)
                hadmid_row.append(0)
        hadmid_to_processed_chart_info[hadmid] = hadmid_row


    #
    # Join the events back into one file
    #
    print("Joining all events")

    with open(output_location, 'w') as w_file:
        csv_writer = csv.writer(w_file, delimiter=',')

        #### Build Headers ####
        headers = [
            "status",
            "los",
            "age",
            "gender",
            "insurance",
            "language",
            "religion",
            "marital_status",
            "ethnicity"
        ]

        for l in lab_to_hadmid.keys():
            headers.append(l)
            headers.append(l + "-trend")

        for d in all_drugs:
            headers.append(d)

        for c in chartevent_to_hadmid.keys():
            headers.append(c)
            headers.append(c + "-trend")

        csv_writer.writerow(headers)


        #### Derive Content ####
        for hadmid, row in hadmid_to_admission_info.items():
            output_row = [row[9], round(float(row[10]), 3)]
            output_row.extend(row[2:9])
            labevent_row = hadmid_to_processed_lab_info[hadmid] if hadmid in hadmid_to_processed_lab_info else \
                [0 for _ in range(2*len(lab_to_hadmid.keys()))]
            output_row.extend(labevent_row)
            drug_row = hadmid_to_processed_drug_info[hadmid] if hadmid in hadmid_to_processed_drug_info else \
                [0 for _ in range(len(all_drugs))]
            output_row.extend(drug_row)
            chartevent_row = hadmid_to_processed_chart_info[hadmid] if hadmid in hadmid_to_processed_chart_info else \
                [0 for _ in range(2*len(chartevent_to_hadmid.keys()))]
            output_row.extend(chartevent_row)

            for i in range(len(output_row)):
                if isinstance(output_row[i], float):
                    output_row[i] = round(output_row[i], 3)

            csv_writer.writerow(output_row)


########################################################################

# admissions.derived.csv
# [not present] hadmid, age, gender, insurance, language, religion, marital_status, ethnicity, status, los
# 161773,72.1275,M,Private,CANT,UNOBTAINABLE,MARRIED,WHITE,1,10.275
# 113808,48.2201,F,Private,,PROTESTANT QUAKER,MARRIED,WHITE,0,8.579166666666667

# labevents.csv
# HADM_ID,CHARTTIME,ITEMID,LABEL,FLUID,VALUE,VALUENUM,VALUEUOM
# 100006,2108-04-06 11:30:00,50868,Anion Gap,Blood,19,19,mEq/L
# 100006,2108-04-06 11:30:00,51137,Anisocytosis,Blood,1+,,

# prescriptions.csv
# HADM_ID,STARTDATE,ENDDATE,DRUG,FORMULARY_DRUG_CD,PROD_STRENGTH,DOSE_VAL_RX,DOSE_UNIT_RX,ROUTE
# 100006,2108-04-06 00:00:00,2108-04-14 00:00:00,Albuterol Neb Soln,ALBU3H,0.083%;3ML VL,1,NEB,IH
# 100006,2108-04-06 00:00:00,2108-04-10 00:00:00,Azithromycin,ZITHR250,250MG CAP,250,mg,PO

# chartevents.csv
# HADM_ID,CHARTTIME,ITEMID,LABEL,VALUE,VALUENUM,VALUEUOM,WARNING
# 100087,2126-11-01 17:49:00,220045,Heart Rate,78,78,bpm,0
# 100087,2126-11-01 17:51:00,220180,Non Invasive Blood Pressure diastolic,87,87,mmHg,0

project_dir = sys.argv[1]
output_location = sys.argv[2]
first_hours = int(sys.argv[3]) if len(sys.argv) > 3 else 24
max_lines = int(sys.argv[4]) if len(sys.argv) > 4 else None
produce_output(project_dir, output_location, first_hours, max_lines)
