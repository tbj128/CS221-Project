"""
Joins the admissions, lab, chart, and prescriptions datasets into one single dataset,
with each row being a patient+time combination.

Note that any numeric column are split into two columns containing:
   1) the average numeric values across all timepoints within the first X hours
   2) the trend of numeric values across all timepoints within the first X hours
      (trendline linear regression of that feature using least squares)

This means that a single patient who stays five days in the ICU will have five separate
rows in this joined dataset. The LOS will likewise decrement by one for each day that
the patient stays in the ICU.

Example Columns:
    hadmid, timestep (days), los_remaining, feature1, feature2, ...

"""

import csv
from collections import defaultdict
from datetime import datetime, timedelta
import sys
import math

from extractor_utils import calculate_trend

def produce_output(project_dir, output_location, sample_first_only):
    #
    # Load admissions information
    #
    print("Processing derived admissions file")
    hadmid_to_admission_info = {}
    with open(project_dir + "/admissions.derived.csv", 'r') as csv_file:
        csv_reader = csv.reader(csv_file, delimiter=',')
        i = 0
        for row in csv_reader:
            if i == 0:
                i += 1
                continue
            hadmid = row[0]
            if hadmid not in hadmid_to_admission_info:
                hadmid_to_admission_info[hadmid] = row
            if sample_first_only:
                break

    #
    # Load lab information
    #
    print("Processing lab file")

    first_sample_hamid = None

    # lab -> hadmid
    lab_to_hadmid = defaultdict(set)

    # hadmid -> time -> lab -> labvalues
    hadmid_to_raw_lab_info = {}
    with open(project_dir + "/labevents.csv", 'r') as csv_file:
        csv_reader = csv.reader(csv_file, delimiter=',')
        i = 0
        for row in csv_reader:
            if i == 0:
                i += 1
                continue

            if sample_first_only and first_sample_hamid is not None and first_sample_hamid != row[0]:
                break
            elif sample_first_only and first_sample_hamid is None:
                first_sample_hamid = row[0]

            hadmid = row[0]

            admittime = datetime.strptime(hadmid_to_admission_info[hadmid][1], '%Y-%m-%dT%H:%M:%S')
            offset = (datetime.strptime(row[1], '%Y-%m-%d %H:%M:%S') - admittime) / timedelta(hours=1)
            offset = round(offset, 3)
            days_since_admittance = math.floor(offset / 24) + 1

            if hadmid not in hadmid_to_raw_lab_info:
                hadmid_to_raw_lab_info[hadmid] = {}
            if days_since_admittance not in hadmid_to_raw_lab_info[hadmid]:
                hadmid_to_raw_lab_info[hadmid][days_since_admittance] = defaultdict(list)

            lab = row[3]
            val = row[6]
            if val == "":
                # Skip because this is not a numeric value
                continue
            val = round(float(val), 3)
            lab_to_hadmid[lab].add(hadmid)
            hadmid_to_raw_lab_info[hadmid][days_since_admittance][lab].append((offset, val))

            if i % 100000 == 0:
                print("   Labs processed {} events".format(i))
            i += 1

    hadmid_to_time_to_processed_lab_info = {}
    for hadmid, day_offset_map in hadmid_to_raw_lab_info.items():
        hadmid_to_time_to_processed_lab_info[hadmid] = {}
        for day_offset, raw_lab_info in day_offset_map.items():
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
            hadmid_to_time_to_processed_lab_info[hadmid][day_offset] = hadmid_row


    #
    # Load prescription information
    #
    print("Processing prescriptions file")

    all_drugs = set()
    first_sample_hamid = None

    # hadmid -> days_since_admittance -> drug
    hadmid_to_time_to_drug = defaultdict(set)
    with open(project_dir + "/prescriptions.csv", 'r') as csv_file:
        csv_reader = csv.reader(csv_file, delimiter=',')
        i = 0
        for row in csv_reader:
            if i == 0:
                i += 1
                continue
            if row[4] == "" or row[1] == "" or row[2] == "":
                i += 1
                continue


            if sample_first_only and first_sample_hamid is not None and first_sample_hamid != row[0]:
                break
            elif sample_first_only and first_sample_hamid is None:
                first_sample_hamid = row[0]

            hadmid = row[0]
            drug = row[4]

            admittime = datetime.strptime(hadmid_to_admission_info[hadmid][1], '%Y-%m-%dT%H:%M:%S')
            drug_start_offset = (datetime.strptime(row[1], '%Y-%m-%d %H:%M:%S') - admittime) / timedelta(hours=1)
            drug_end_offset = (datetime.strptime(row[2], '%Y-%m-%d %H:%M:%S') - admittime) / timedelta(hours=1)

            all_drugs.add(drug)
            hour_offset = max(drug_start_offset, 0)
            while hour_offset < drug_end_offset:
                # Drug was administered on this relative date
                day_offset = int(hour_offset / 24)
                if hadmid not in hadmid_to_time_to_drug:
                    hadmid_to_time_to_drug[hadmid] = {}
                if day_offset not in hadmid_to_time_to_drug[hadmid]:
                    hadmid_to_time_to_drug[hadmid][day_offset] = set()
                hadmid_to_time_to_drug[hadmid][day_offset].add(drug)
                hour_offset += 24

            if i % 100000 == 0:
                print("   Drugs processed {} events".format(i))
            i += 1

    hadmid_to_time_to_processed_drug_info = {}
    for hadmid, time_info in hadmid_to_time_to_drug.items():
        for day_offset, drugs in time_info.items():
            hadmid_row = []
            for d in all_drugs:
                if d in drugs:
                    hadmid_row.append(1)
                else:
                    hadmid_row.append(0)
            if hadmid not in hadmid_to_time_to_processed_drug_info:
                hadmid_to_time_to_processed_drug_info[hadmid] = {}
            hadmid_to_time_to_processed_drug_info[hadmid][day_offset] = hadmid_row

    #
    # Load chart information
    #
    print("Processing chart information file")

    first_sample_hamid = None

    # chartevent -> hadmid
    chartevent_to_hadmid = defaultdict(set)

    # hadmid -> time -> chartevent -> chartevent value
    hadmid_to_time_to_raw_chart_info = {}
    with open(project_dir + "/chartevents.csv", 'r') as csv_file:
        csv_reader = csv.reader(csv_file, delimiter=',')
        i = 0
        for row in csv_reader:
            if i == 0:
                i += 1
                continue

            if sample_first_only and first_sample_hamid is not None and first_sample_hamid != row[0]:
                break
            elif sample_first_only and first_sample_hamid is None:
                first_sample_hamid = row[0]

            hadmid = row[0]
            admittime = datetime.strptime(hadmid_to_admission_info[hadmid][1], '%Y-%m-%dT%H:%M:%S')
            offset = (datetime.strptime(row[1], '%Y-%m-%d %H:%M:%S') - admittime) / timedelta(hours=1)
            offset = round(offset, 3)
            days_since_admittance = math.floor(offset / 24) + 1

            if hadmid not in hadmid_to_time_to_raw_chart_info:
                hadmid_to_time_to_raw_chart_info[hadmid] = {}
            if days_since_admittance not in hadmid_to_time_to_raw_chart_info[hadmid]:
                hadmid_to_time_to_raw_chart_info[hadmid][days_since_admittance] = defaultdict(list)

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
            hadmid_to_time_to_raw_chart_info[hadmid][days_since_admittance][chart].append((offset, val))

            if i % 100000 == 0:
                print("   Charts processed {} events".format(i))
            i += 1

    hadmid_to_time_to_processed_chart_info = {}
    for hadmid, time_info in hadmid_to_time_to_raw_chart_info.items():
        for day_offset, raw_chart_info in time_info.items():
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
            if hadmid not in hadmid_to_time_to_processed_chart_info:
                hadmid_to_time_to_processed_chart_info[hadmid] = {}
            hadmid_to_time_to_processed_chart_info[hadmid][day_offset] = hadmid_row


    #
    # Join the events back into one file
    #
    print("Joining all events")

    with open(output_location, 'w') as w_file:
        csv_writer = csv.writer(w_file, delimiter=',')

        #### Build Headers ####
        headers = [
            "timestep",
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
            los = int(float(row[10]))
            # TODO: Try keeping the same data from the last time step if current time step is unknown
            for day in range(los):
                output_row = [day, row[9], round(float(row[10]) - day, 3)]
                output_row.extend(row[2:9])
                if hadmid in hadmid_to_time_to_processed_lab_info:
                    if day in hadmid_to_time_to_processed_lab_info[hadmid]:
                        output_row.extend(hadmid_to_time_to_processed_lab_info[hadmid][day])
                    else:
                        # Use zeros for unknown
                        output_row.extend([0 for _ in range(2 * len(lab_to_hadmid.keys()))])
                else:
                    output_row.extend([0 for _ in range(2 * len(lab_to_hadmid.keys()))])

                if hadmid in hadmid_to_time_to_processed_drug_info:
                    if day in hadmid_to_time_to_processed_drug_info[hadmid]:
                        output_row.extend(hadmid_to_time_to_processed_drug_info[hadmid][day])
                    else:
                        output_row.extend([0 for _ in range(len(all_drugs))])
                else:
                    output_row.extend([0 for _ in range(len(all_drugs))])

                if hadmid in hadmid_to_time_to_processed_chart_info:
                    if day in hadmid_to_time_to_processed_chart_info[hadmid]:
                        output_row.extend(hadmid_to_time_to_processed_chart_info[hadmid][day])
                    else:
                        output_row.extend([0 for _ in range(2*len(chartevent_to_hadmid.keys()))])
                else:
                    output_row.extend([0 for _ in range(2*len(chartevent_to_hadmid.keys()))])

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
sample_first_only = bool(sys.argv[3]) if len(sys.argv) > 3 else False # If true, produce a file containing only the first sample (assumes files are sorted order)
produce_output(project_dir, output_location, sample_first_only)
