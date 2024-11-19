from langchain.agents import AgentExecutor, create_tool_calling_agent
from langchain_caai.caai_emb_client import caai_emb_client
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.tools import StructuredTool
from langchain_openai import ChatOpenAI

from fhir_functions import *
from secrets import LLM_FACTORY_API_KEY

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



def medications_for_age_group(start_age: str, end_age: str) -> dict:
	return get_meds_for_age_group(start_age, end_age)


meds_for_age_group = StructuredTool.from_function(
	func=medications_for_age_group,
	name="Medications for an age group",
	description="Retrieves an ordered list of the most prescribed medications for an age range.",
)

tools = [find_care_team, birthdate, meds_for_age_group]

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

	q1 = agent_executor.invoke({"input": "Who are the patients with birthdays between 02/15/1999 and 02/15/2000?"})
	print(f"QUESTION: {q1['input']}\n")
	print(q1['output'])
	print('\n\n')

	q2 = agent_executor.invoke({"input": "Who is on the care team for Shondra529 Armstrong51?"})
	print(f"QUESTION: {q2['input']}\n")
	print(q2['output'])
	print('\n\n')

	# This data set is filled with very old people, so the high end of the range should be something like 65 or so
	q3 = agent_executor.invoke({"input": "What are the most taken medications for ages 55-95?"})
	print(f"QUESTION: {q3['input']}\n")
	print(q3['output'])
	print('\n\n')
