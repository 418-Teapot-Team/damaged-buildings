from langchain_openai import ChatOpenAI
from langchain.agents import initialize_agent, AgentType
from langchain_community.utilities import SerpAPIWrapper
from langchain_core.tools import Tool
from langchain_groq import ChatGroq
from openai import OpenAI
from dotenv import load_dotenv
import os

load_dotenv()

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

input_query = "What is the price of used Volkswagen Golf 4? Prease return your anser only as numbers"
response = client.responses.create(
    model="gpt-4.1",
    tools=[{
        "type": "web_search_preview",
        "search_context_size": "low",
    }],
    input=input_query, 
)
print("OPEN AI ", response.output_text)


# # llm = ChatOpenAI(
# #     model="gpt-4o",
# #     temperature=0.2,
# #     api_key=os.getenv("OPENAI_API_KEY")
# # )
# llm = ChatGroq(
#             model="llama-3.1-8b-instant",
#             api_key=os.getenv("GROQ_API_KEY"),
#             temperature=0.1,
#         )

# search = SerpAPIWrapper(serpapi_api_key=os.getenv("SERP_API_KEY"))

# custom_tool = Tool(
#     name="web search",
#     description="Search the web for information",
#     func=search.run,
# )

# agent = initialize_agent(
#     tools=[custom_tool],
#     llm=llm,
#     agent=AgentType.ZERO_SHOT_REACT_DESCRIPTION,
#     verbose=True
# )

# response = agent.invoke({
#     "input": input_query
# })

# print("\n=== Final Answer ===")
# print("LLAMA OUTPUT", response['output'])
