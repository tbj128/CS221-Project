"""
Extracts admissions information and derives any necessary fields
"""

import csv
from datetime import datetime, timedelta
import sys


def produce_output(project_dir):
    with open(project_dir + "/admissions.csv", 'r') as csv_file:
        csv_reader = csv.reader(csv_file, delimiter=',')
        with open(project_dir + "/admissions.derived.csv", 'w') as w_file:
            csv_writer = csv.writer(w_file, delimiter=',')
            csv_writer.writerow(["hadmid", "admittime", "age", "gender", "insurance", "language", "religion", "marital_status", "ethnicity", "status", "los"]);
            colname_to_col = {}
            i = 0
            for row in csv_reader:
                if i == 0:
                    j = 0
                    while j < len(row):
                        colname_to_col[row[j]] = j
                        j += 1
                elif i > 0:
                    hadmid = row[colname_to_col["HADM_ID"]]
                    admittime = datetime.strptime(row[colname_to_col["ADMITTIME"]], '%Y-%m-%dT%H:%M:%S')
                    dischtime = datetime.strptime(row[colname_to_col["DISCHTIME"]], '%Y-%m-%dT%H:%M:%S')
                    age = row[colname_to_col["age"]]
                    gender = row[colname_to_col["gender"]]
                    insurance = row[colname_to_col["INSURANCE"]]
                    language = row[colname_to_col["LANGUAGE"]]
                    religion = row[colname_to_col["RELIGION"]]
                    marital_status = row[colname_to_col["MARITAL_STATUS"]]
                    ethnicity = row[colname_to_col["ETHNICITY"]]
                    status = row[colname_to_col["HOSPITAL_EXPIRE_FLAG"]]
                    los = (dischtime - admittime) / timedelta(days=1)
                    csv_writer.writerow([hadmid, row[colname_to_col["ADMITTIME"]], age, gender, insurance, language, religion, marital_status, ethnicity, status, los, row[colname_to_col["DISCHTIME"]]])
                i += 1


########################################################################

# admissions.csv
# ROW_ID,SUBJECT_ID,HADM_ID,ADMITTIME,DISCHTIME,DEATHTIME,ADMISSION_TYPE,ADMISSION_LOCATION,DISCHARGE_LOCATION,INSURANCE,LANGUAGE,RELIGION,MARITAL_STATUS,ETHNICITY,EDREGTIME,EDOUTTIME
# ,DIAGNOSIS,HOSPITAL_EXPIRE_FLAG,HAS_CHARTEVENTS_DATA,age,gender,SHORT_TITLE
# 35574,29156,161773,2100-06-09T01:39:00,2100-06-19T08:15:00,2100-06-19T08:15:00,EMERGENCY,EMERGENCY ROOM ADMIT,DEAD/EXPIRED,Private,CANT,UNOBTAINABLE,MARRIED,WHITE,2100-06-08T23:29:0
# 0,2100-06-09T02:34:00,RESPIRATORY DISTRESS,1,1,72.1275,M,Meth sus pneum d/t Staph

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
produce_output(project_dir)
