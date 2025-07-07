from langchain_openai import ChatOpenAI
from dotenv import load_dotenv
load_dotenv()
from crewai import Agent, Task, Crew
llm = ChatOpenAI()

agent = Agent(
    role="Writer",
    goal="Generate blog content about generative AI",
    backstory="You are a skilled tech writer known for simplifying complex AI topics for a general audience.",

    llm=llm
)

task = Task(
    description="Write a short blog post about the impact of generative AI.",
    expected_output="A 3-paragraph blog post suitable for a general tech audience.",
    agent=agent
)

crew = Crew(
    agents=[agent],
    tasks=[task]
)

result = crew.kickoff()
print(result)