-- Get admissions pneumonia subset
select c.*,
case when round(DATETIME_DIFF(c.admittime, p.dob, DAY) / 365.242, 4) > 89 then 91.4 else round(DATETIME_DIFF(c.admittime, p.dob, DAY) / 365.242, 4) end as age,
p.gender,
d.SHORT_TITLE
from `physionet-data.mimiciii_clinical.admissions` c
INNER JOIN
(
  select a.HADM_ID, min(b.SHORT_TITLE) as SHORT_TITLE from `physionet-data.mimiciii_clinical.diagnoses_icd` a, `physionet-data.mimiciii_clinical.d_icd_diagnoses` b
  where
  a.ICD9_CODE = b.ICD9_CODE
  AND (b.SHORT_TITLE like '%neumonia%'
  OR b.LONG_TITLE like '%neumonia%')
  AND a.SEQ_NUM <= 3
  GROUP BY a.HADM_ID
) d
ON c.HADM_ID = d.HADM_ID
INNER JOIN `physionet-data.mimiciii_clinical.patients` p
ON c.SUBJECT_ID = p.SUBJECT_ID
AND c.HAS_CHARTEVENTS_DATA = 1
ORDER BY ADMITTIME



-- Get chartevents pneumonia subset
select c.HADM_ID, c.CHARTTIME, e.ITEMID, e.LABEL, c.VALUE, c.VALUENUM, c.VALUEUOM, c.WARNING from `physionet-data.mimiciii_clinical.chartevents` c, `physionet-data.mimiciii_clinical.d_items` e
INNER JOIN
(
    select a.HADM_ID from `physionet-data.mimiciii_clinical.diagnoses_icd` a, `physionet-data.mimiciii_clinical.d_icd_diagnoses` b
    where
    a.ICD9_CODE = b.ICD9_CODE
    AND (b.SHORT_TITLE like '%neumonia%'
    OR b.LONG_TITLE like '%neumonia%')
    AND a.SEQ_NUM <= 3
    GROUP BY a.HADM_ID
) d
ON c.HADM_ID = d.HADM_ID
INNER JOIN`physionet-data.mimiciii_clinical.admissions` adm
ON adm.HADM_ID = c.HADM_ID
AND adm.HAS_CHARTEVENTS_DATA = 1
WHERE c.ITEMID = e.ITEMID
AND c.ERROR != 1
AND c.ITEMID IN (223762, 220179, 220180, 223834, 220277, 220045, 220210, 211, 8441, 455, 618, 646, 470, 677)
ORDER BY c.HADM_ID, c.CHARTTIME, e.LABEL



-- Get lab events pneumonia subset
select c.HADM_ID, c.CHARTTIME, e.ITEMID, e.LABEL, e.FLUID, c.VALUE, c.VALUENUM, c.VALUEUOM from `physionet-data.mimiciii_clinical.labevents` c, `physionet-data.mimiciii_clinical.d_labitems` e
INNER JOIN
(
  select a.HADM_ID from `physionet-data.mimiciii_clinical.diagnoses_icd` a, `physionet-data.mimiciii_clinical.d_icd_diagnoses` b
  where
  a.ICD9_CODE = b.ICD9_CODE
  AND (b.SHORT_TITLE like '%neumonia%'
  OR b.LONG_TITLE like '%neumonia%')
  AND a.SEQ_NUM <= 3
  GROUP BY a.HADM_ID
) d
ON c.HADM_ID = d.HADM_ID
INNER JOIN`physionet-data.mimiciii_clinical.admissions` adm
ON adm.HADM_ID = c.HADM_ID
AND adm.HAS_CHARTEVENTS_DATA = 1
WHERE c.ITEMID = e.ITEMID
ORDER BY c.HADM_ID, c.CHARTTIME, e.LABEL


-- Get prescription pneumonia subset
select c.HADM_ID, c.STARTDATE, c.ENDDATE, c.DRUG, c.FORMULARY_DRUG_CD, c.PROD_STRENGTH, c.DOSE_VAL_RX, c.DOSE_UNIT_RX, c.ROUTE from `physionet-data.mimiciii_clinical.prescriptions` c
INNER JOIN
(
  select a.HADM_ID from `physionet-data.mimiciii_clinical.diagnoses_icd` a, `physionet-data.mimiciii_clinical.d_icd_diagnoses` b
  where
  a.ICD9_CODE = b.ICD9_CODE
  AND (b.SHORT_TITLE like '%neumonia%'
  OR b.LONG_TITLE like '%neumonia%')
  AND a.SEQ_NUM <= 3
  GROUP BY a.HADM_ID
) d
ON c.HADM_ID = d.HADM_ID
INNER JOIN`physionet-data.mimiciii_clinical.admissions` adm
ON adm.HADM_ID = c.HADM_ID
AND adm.HAS_CHARTEVENTS_DATA = 1
ORDER BY c.HADM_ID, c.STARTDATE, c.DRUG
