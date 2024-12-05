# Personalized Medical Dialogue using a Large Language Model
## Overview
This project implements a system enabling clinicians to ask natural language questions about patient observations and receive accurate, human-like responses. Using a combination of large language models (LLMs) and FHIR server queries, the system mitigates risks of hallucinations by leveraging structured tool-calling methods to ensure reliable and factual responses.

## Features 
- Natural Language Queries: Clinicians can ask structured or unstructured questions about patient data. 
- FHIR Integration: Queries retrieve data directly from a FHIR server storing synthetic EHR data. 
- Hallucination Mitigation: Combines LLM-generated dialogue with validated data from Python functions. 
- Evaluation Metrics: Precision, Recall, and F1 scores to measure system performance.

## System Architecture
The system includes the following components:

- HAPI FHIR Server: Stores patient records in a Postgres database within a Docker instance. 
- Large Language Model: Utilizes Llama 3.1 70B via API from the Center for Applied AI’s LLM Factory.
- LangChain Tool Calling: Extracts query parameters and matches them with predefined Python functions for data retrieval.
- CLI User Interface: Accepts clinician queries and provides responses. (Website UI under development.)

## Evaluation
The system was evaluated using five types of queries across multiple test cases:

- Patient observations. 
- Care team information. 
- Patient filtering by date of birth. 
- Common medications by age group. 
- General knowledge questions.

Results (Sample Size: 50 Queries):
- Specificity: 1.000
- Precision: 1.000 
- Recall: 0.875 
- Accuracy: 0.900 
- F1 Score: 0.933


## How to Run It
1. `pip install -r requirements.txt`
2. Rename `secret_keys.py.example` to `secret_keys.py`
3. Input LLM Factory API key into `secret_keys.py` file
4. Run the script using `python main.py`


## References
1. Bumgardner et al. (2024). Institutional Platform for Secure Self-Service Large Language Model Exploration. [arXiv:2402.00913](http://arxiv.org/abs/2402.00913)
2. Walonoski et al. (2018). Synthea: An approach, method, and software mechanism for generating synthetic patients and the synthetic electronic health care record. [JAMIA](https://doi.org/10.1093/jamia/ocx079)
3. LangChain Documentation. Build an Agent. [LangChain Docs](https://python.langchain.com/docs/tutorials/agents/11)
