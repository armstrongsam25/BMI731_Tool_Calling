from collections import defaultdict

import requests
from datetime import datetime, timedelta


def get_patient_name_bday(url):
	response = requests.get(url)

	# Check the response
	if response.status_code == 200:
		response_json = response.json()
		if "issue" not in response_json.keys():
			return response_json['name'][0]['given'][0] + ' ' + response_json['name'][0]['family'], response_json[
				'birthDate']
		else:
			return None, None

	else:
		print(f"Failed to get data: {response.status_code}")
		return None, None


def birthdate_query(start, end):
	url = "http://localhost:8080/fhir/Patient"
	params = {
		"birthdate": ["ge" + start, "le" + end],  # 2000-02-15
		"_pretty": "false",
		"_count": 100000
	}

	response = requests.get(url, params=params)

	# Check the response
	if response.status_code == 200:
		patients = dict()
		response_json = response.json()

		for patient in response_json['entry']:
			name, birthdate = get_patient_name_bday(patient['fullUrl'])
			if name == None or birthdate == None:
				continue
			else:
				patients[name] = birthdate

		return patients
	else:
		print(f"Failed to get data: {response.status_code}")
		return None


def get_patient_id(f_name, l_name):
	url = "http://localhost:8080/fhir/Patient"
	params = {
		"family": l_name,
		"given": f_name,
		"_pretty": "false",
		"_count": 100000
	}

	response = requests.get(url, params=params)

	# Check the response
	if response.status_code == 200:
		response_json = response.json()
		if response_json['total'] > 0:
			return response_json['entry'][0]['resource']['id']
		else:
			return None
	else:
		print(f"Failed to get data: {response.status_code}")
		return None


def get_care_team(f_name, l_name):
	id = get_patient_id(f_name, l_name)
	if id == None:
		return []
	care_team = set()

	url = "http://localhost:8080/fhir/CareTeam"
	params = {
		"subject": id,
		"_pretty": "false",
		"_count": 100000
	}

	response = requests.get(url, params=params)

	# Check the response
	if response.status_code == 200:
		response_json = response.json()

		for resource in response_json['entry']:
			for doc in resource['resource']['participant']:
				if doc['member']['reference'].startswith("Practitioner"):
					care_team.add(doc['member']['display'])

		return list(care_team)
	else:
		print(f"Failed to get data: {response.status_code}")
		return []


def calculate_birthdate_range(min_age, max_age):
	today = datetime.today()
	end_date = today - timedelta(days=(min_age * 365))  # Youngest person's birthdate
	start_date = today - timedelta(days=(max_age * 365))  # Oldest person's birthdate
	return start_date.strftime("%Y-%m-%d"), end_date.strftime("%Y-%m-%d")

def get_medications(id, medication_counts):
	url = "http://localhost:8080/fhir/MedicationAdministration"
	params = {
		"subject": id,
		"_pretty": "false",
		"_count": 100000
	}

	response = requests.get(url, params=params)

	# Check the response
	if response.status_code == 200:
		response_json = response.json()
		if response_json['total'] > 0:
			for entry in response_json['entry']:
				medication_name = entry['resource']['medicationCodeableConcept']['text']
				medication_counts[medication_name] += 1

		return medication_counts

	else:
		print(f"Failed to get data: {response.status_code}")
		return None, None

def get_meds_for_age_group(start_age, end_age):
	start, end = calculate_birthdate_range(int(start_age), int(end_age))

	url = "http://localhost:8080/fhir/Patient"
	params = {
		"birthdate": ["ge" + start, "le" + end],
		"_pretty": "false",
		"_count": 100000
	}

	response = requests.get(url, params=params)

	# Check the response
	if response.status_code == 200:
		patients = dict()
		response_json = response.json()

		medication_counts = defaultdict(int)

		for patient in response_json.get('entry', []):
			id = patient['resource']['id']
			name, birthdate = get_patient_name_bday(patient['fullUrl'])
			if name and birthdate:
				patients[name] = {"birthdate": birthdate, "url": patient['fullUrl']}
				get_medications(id, medication_counts)

		return dict(sorted(medication_counts.items(), key=lambda item: item[1], reverse=True))
	else:
		print(f"Failed to get data: {response.status_code}")
		return dict()


# get list of meds for each patient

# count the occurences of meds


if __name__ == '__main__':
	# print(birthdate_query("1999-02-15", "2000-02-15"))

	# print(get_care_team('Shondra529', 'Armstrong51'))
	print(get_meds_for_age_group(0, 65))
