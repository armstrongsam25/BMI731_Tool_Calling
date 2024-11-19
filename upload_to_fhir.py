import os
import time
import requests
import json

FHIR_SERVER_URL = "http://localhost:8080/fhir"
DATA_DIR = "../data/fhir"


def upload_fhir_resource(file_path):
	with open(file_path, 'r', encoding='utf-8') as file:
		resource_data = json.load(file)
		resource_type = resource_data.get("resourceType")

		if resource_type:
			if resource_type == "Bundle" and resource_data.get("type") == "transaction":
				url = FHIR_SERVER_URL
			else:
				url = f"{FHIR_SERVER_URL}/{resource_type}"

			headers = {"Content-Type": "application/fhir+json"}
			response = requests.post(url, headers=headers, json=resource_data)

			if response.status_code in (200, 201):
				print(f"Successfully uploaded {resource_type}: {file_path}")
			else:
				print(f"Failed to upload {resource_type}: {file_path} - Status Code: {response.status_code}, Response: {response.text}")
		else:
			print(f"No resourceType found in {file_path}")

for filename in os.listdir(DATA_DIR):
	if filename.endswith('.json'):
		file_path = os.path.join(DATA_DIR, filename)
		upload_fhir_resource(file_path)
		time.sleep(0.25)
