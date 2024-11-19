import json
import os
import pandas as pd
from multiprocessing import Pool
from datetime import datetime

json_directory = '../data/fhir'


def load_fhir_bundles(directory):
	bundles = []
	for filename in os.listdir(directory):
		if filename.endswith('.json'):
			with open(os.path.join(directory, filename), 'r', encoding='utf-8') as f:
				bundle = json.load(f)
				bundles.append(bundle)
	return bundles


def extract_resources_from_bundle(bundle):
	resources = []
	for entry in bundle.get('entry', []):
		resource = entry.get('resource')
		if resource:
			resources.append(resource)
	return resources


def extract_all_resources(bundles):
	all_resources = []
	for bundle in bundles:
		resources = extract_resources_from_bundle(bundle)
		all_resources.extend(resources)
	return all_resources

def process_bundle(bundle):
	resources = extract_resources_from_bundle(bundle)
	return resources

def extract_patient_info(resources):
	patients = []
	for resource in resources:
		if resource.get('resourceType') == 'Patient':
			patient_info = {
				'id': resource.get('id'),
				'gender': resource.get('gender'),
				'birthDate': resource.get('birthDate'),
				'name': " ".join([name.get('text', '') for name in resource.get('name', [])])
			}
			patients.append(patient_info)
	return pd.DataFrame(patients)

def extract_observations(resources):
	observations = []
	for resource in resources:
		if resource.get('resourceType') == 'Observation':
			observation = {
				'id': resource.get('id'),
				'status': resource.get('status'),
				'code': resource.get('code', {}).get('text', ''),
				'value': resource.get('valueQuantity', {}).get('value', None),
				'unit': resource.get('valueQuantity', {}).get('unit', ''),
				'date': resource.get('effectiveDateTime', None),
				'patient_id': resource.get('subject', {}).get('reference', '').split(':')[-1]  # Extract patient ID
			}
			observations.append(observation)
	return pd.DataFrame(observations)

def extract_medications(resources):
	medications = []
	for resource in resources:
		if resource.get('resourceType') == 'MedicationAdministration':
			medication = {
				'id': resource.get('id'),
				'status': resource.get('status'),
				'medication_code': resource.get('medicationCodeableConcept', {}).get('text', ''),
				'effective_date': resource.get('effectiveDateTime', None),
				'patient_id': resource.get('subject', {}).get('reference', '').split(':')[-1]  # Extract patient ID
			}
			medications.append(medication)
	return pd.DataFrame(medications)


# Calculate age from birthDate
def calculate_age(birth_date):
	if birth_date:
		birth_date = pd.to_datetime(birth_date)
		today = datetime.today()
		age = today.year - birth_date.year - ((today.month, today.day) < (birth_date.month, birth_date.day))
		return age
	return None


if __name__ == '__main__':
	fhir_bundles = load_fhir_bundles(json_directory)

	with Pool() as pool:
		all_resources_list_of_lists = pool.map(process_bundle, fhir_bundles)

	all_resources = [resource for sublist in all_resources_list_of_lists for resource in sublist]

	print(f"Total number of resources: {len(all_resources)}")
	print()

	# Now extract patient and observation information
	patient_df = extract_patient_info(all_resources)
	observation_df = extract_observations(all_resources)
	medications_df = extract_medications(all_resources)

	print(patient_df.head())
	print(observation_df.head())
	print(patient_df.columns)
	print(observation_df.columns)
	print()

	patient_df['age'] = patient_df['birthDate'].apply(calculate_age)

	gender_counts = patient_df['gender'].value_counts()
	print(gender_counts)
	print()

	numerical_obs = observation_df['value'].dropna()  # Drop missing values
	summary_stats = {
		'mean': numerical_obs.mean(),
		'median': numerical_obs.median(),
		'min': numerical_obs.min(),
		'max': numerical_obs.max()
	}

	print(summary_stats)
	print()

	observation_counts = observation_df['code'].value_counts()
	print(f'Daily observation counts: \n {observation_counts}')

	observation_df['date'] = pd.to_datetime(observation_df['date'], errors='coerce', utc=True)

	daily_observation_counts = observation_df.dropna(subset=['date']).groupby(observation_df['date'].dt.date).size()

	# Display the counts
	print(daily_observation_counts)
	print()

	# Create age groups
	bins = [0, 18, 35, 50, 65, 100]  # Define age bins
	labels = ['0-18', '19-35', '36-50', '51-65', '66+']
	patient_df['age_group'] = pd.cut(patient_df['age'], bins=bins, labels=labels, right=False)

	# Count patients in each age group
	age_group_counts = patient_df['age_group'].value_counts().sort_index()

	# Display the age group counts
	print(age_group_counts)

	# # Display patient DataFrame with new age groups
	# print(patient_df[['id', 'gender', 'age', 'age_group']].head())
	print()

	# Group by 'patient_id' and count the number of observations
	observations_per_patient = observation_df.groupby('patient_id').size().reset_index(name='observation_count')

	# Display the resulting DataFrame
	print(observations_per_patient.head())
	print()

	print(":::Medications:::")
	medications_per_patient = (
		medications_df
		.groupby('patient_id')
		.agg({
			'medication_code': list,
			'effective_date': list,
			'status': list
		})
		.reset_index()
	)

	# medications_per_patient.to_csv("meds_per_patient.csv")
	print(medications_per_patient.head())
