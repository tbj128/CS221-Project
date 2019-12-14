## Improving Prognosis of ICU Patients with Pneumonia
CS 221 | Boyang Tom Jin

---

### Overview
This repo contains the code and Jupyter notebooks that were used to investigate the length of stay and discharge status 
of ICU patients with pneumonia. 

### Data
This project uses the [MIMIC-III data set](https://mimic.physionet.org/), a freely-available electronic medical record 
data set of over 40,000 ICU patients over a span of 11 years. This data set is access-restricted, and access requires 
formal approval after completion of a data handling course. 

As such, the processed data used by this project is not provided along with the notebooks. Please reach out to the 
author at tomjin [at] stanford.edu if you have any further questions.

Normally, the data would live in the `/data` root directory structure. As such, the notebooks may refer to some of the 
following files:
- `/data`
   - `/exp`
      - `/pneumonia-t3`
         - `/first24hours.csv`: Data aggregated from the first 24 hours of each patient. (2537 features without one-hot encoding)
         - `/first24hours.filtered.csv`: Data aggregated from the first 24 hours of each patient after filtering out columns with more than 70% zero values. (118 features without one-hot encoding)
         - `/first48hours.csv`: Data aggregated from the first 48 hours of each patient. (2686 features without one-hot encoding)
         - `/first48hours.filtered.csv`: Data aggregated from the first 48 hours of each patient after filtering out columns with more than 70% zero values. (249 features without one-hot encoding)
         - `/timestep.filtered.csv`: Data aggregated for each day of each patient stay after filtering out columns with more than 70% zero values. (154 features without one-hot encoding)

#### Example Data
The notebooks can be run with example files provided. To do so, replace the following files with the example files:
- `first24hours.csv` or `first24hours.filtered.csv`: Replace with https://t.ly/BwJzB
- `timestep.filtered.csv`: Replace with https://t.ly/GjrKb

### Project Structure
- `/notebooks`: 
   - `/feature_selection_demographic_population.ipynb`: Investigation into the important features that may distinguish 
   between different subpopulations on the basis of demographic data including age, ethnicity, gender, etc.
   - `/los_prediction_after_feature_selection.ipynb`: LOS regression problem that uses only features selected through 
   feature selection to improve overall performance. Features linear regression, deep neural networks. 
   - `/los_prediction_feedforward_dnn.ipynb`: LOS regression problem using all features. Features deep neural networks.
   - `/los_prediction_linear_regression.ipynb`: LOS regression problem using all features. Features linear regression 
   with varying regularization.
   - `/los_prediction_lstm.ipynb`: LOS regression problem using the time-step data. Features recurrent neural networks 
   (particularly long short-term memory).
- `/src`: 
   - `/baseline`: Code to extract the data used for the baseline and to run linear regression to obtain baseline results.
   - `/extractors`: 
      - `/eicu`: Code to extract the raw data from the eICU dataset (not used)
      - `/mimiciii`: Code to extract and perform data preparation on the the raw MIMIC-III data. For instance, to produce the first 48-hour data set, we would need to run `python3.6 prepare_first_x_hours.py <dir of MIMIC-III raw files> <output file> 48`
   - `/oracle`: Code to extract the data used for the oracle and to run linear regression to obtain oracle results.

