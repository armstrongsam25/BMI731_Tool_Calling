from langchain.agents import AgentExecutor, create_tool_calling_agent
from langchain_caai.caai_emb_client import caai_emb_client
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.tools import StructuredTool
from langchain_openai import ChatOpenAI

from fhir_functions import *
from secret_keys import LLM_FACTORY_API_KEY


def find_care_team(first_name: str, last_name: str) -> dict:
	return get_care_team(first_name, last_name)


find_care_team = StructuredTool.from_function(
	func=find_care_team,
	name="Find Care Team",
	description="Looks up the care team for a patient based on their first and last name.",
)


def birthdate(start: str, end: str) -> dict:
	return birthdate_query(start, end)


birthdate = StructuredTool.from_function(
	func=birthdate,
	name="Birthdate",
	description="Retrieves a list of patients with birth dates between 2 dates. The date format must be YYYY-mm-dd.",
)

def observations(patient_fname: str, patient_lname: str) -> dict:
	return observations_query(patient_fname, patient_lname)


observations = StructuredTool.from_function(
	func=observations,
	name="Observations for a patient",
	description="Retrieves all observations for a given patient.",
)


def medications_for_age_group(start_age: str, end_age: str) -> dict:
	return get_meds_for_age_group(start_age, end_age)


meds_for_age_group = StructuredTool.from_function(
	func=medications_for_age_group,
	name="Medications for an age group",
	description="Retrieves an ordered list of the most prescribed medications for an age range.",
)

tools = [find_care_team, birthdate, meds_for_age_group, observations]

if __name__ == '__main__':
	llm_api_key = LLM_FACTORY_API_KEY
	llm_api_base = 'https://data.ai.uky.edu/llm-factory/openai/v1'
	llm_api_base_local = 'https://data.ai.uky.edu/llm-factory/openai/v1'

	embeddings = caai_emb_client(
		model="",
		api_key=llm_api_key,
		api_url=llm_api_base,
	)

	prompt = ChatPromptTemplate.from_messages(
		[
			("system", "You are a helpful assistant"),
			("placeholder", "{chat_history}"),
			("human", "{input}"),
			("placeholder", "{agent_scratchpad}"),
		]
	)

	llm = ChatOpenAI(
		model_name="/models/functionary-small-v2.5",
		openai_api_key=llm_api_key,
		openai_api_base=llm_api_base,
		verbose=True,
		streaming=False,
	)

	agent = create_tool_calling_agent(llm, tools, prompt)
	agent_executor = AgentExecutor(agent=agent, tools=tools, verbose=True, stream_runnable=False)


	names_eval = ['Shondra529 Armstrong51', 'Angelika194 Tremblay80', 'Bernice532 Ziemann98', 'Candace369 Emmerich580',
				  'Cleveland582 Gulgowski816', 'John1 Cena99', 'Alien12 NotReal33', 'Fake3 Person84', 'Cool55 Guy34',
				  'John32 Name89']
	for i, _ in enumerate(names_eval):
		try:
			q1 = agent_executor.invoke({"input": f"What observations have been recorded for {names_eval[i]}?"})
			print(f"QUESTION: {q1['input']}\n")
			print(q1['output'])
			print('\n\n')
		except:
			print("LLM Factory rejected request...")
			print('\n\n')
	# 7/10 correct (token limit reached)


	for i, _ in enumerate(names_eval):
		q2 = agent_executor.invoke({"input": "Who is on the care team for "+names_eval[i]+"?"})
		print(f"QUESTION: {q2['input']}\n")
		print(q2['output'])
		print('\n\n')
	# 10/10 correct



	date_range_eval = ['02/15/1999', '02/15/2000', '02/15/2001', '02/15/2002', '02/15/2003', '02/15/2004', '02/15/2005',
					   '02/15/2006', '02/15/2007', '02/15/2008', '02/15/2009']

	for i, _ in enumerate(date_range_eval):
		if i == len(date_range_eval) - 1:
			break
		q1 = agent_executor.invoke({"input": "Who are the patients with birthdays between " + date_range_eval[i] + " and " + date_range_eval[i + 1] + "?"})
		print(f"QUESTION: {q1['input']}\n")
		print(q1['output'])
		print('\n\n')
	# 10/10 correct



	age_ranges_eval = ['0-10', '11-20', '21-30', '31-40', '41-50', '51-60', '61-70', '71-80', '81-90', '91-100']

	for i, _ in enumerate(age_ranges_eval):
		q3 = agent_executor.invoke(
			{"input": "Give me the top 10 most taken medications for ages " + age_ranges_eval[i] + "?"})
		print(f"QUESTION: {q3['input']}\n")
		print(q3['output'])
		print('\n\n')
	# 10/10 correct





#########################
# 	Other questions		#
#########################



	# testing if the LLM can still act like an LLM
	random_questions_eval = ['What is the historical average temperature in Lexington, KY in November?',
							 'What comes next in this sequence: 1, 2, 3, D?',
							 'If a train leaves Chicago traveling east at 80 mph and another leaves New York traveling west at 60 mph, where is the conductor of the second train sitting?',
							 'Which is heavier: a pound of feathers or a pound of gold?',
							 'I have a box with six apples. You take three away. How many apples do you have?',
							 'How many letters are in the answer to this question?',
							 'A farmer has 17 sheep, and all but nine run away. How many sheep are left?',
							 'Can an all-powerful being create a stone so heavy that even it cannot lift it?',
							 'Is the statement “This sentence is false” true or false?',
							 'Spell the word “silk” out loud. What do cows drink?'
							 ]
	# Question not related to medical dataset
	for i, _ in enumerate(random_questions_eval):
		q4 = agent_executor.invoke({"input": random_questions_eval[i]})
		print(f"QUESTION: {q4['input']}\n")
		print(q4['output'])
		print('\n\n')
		break
	# 10/10 correct (or not bad answers)
