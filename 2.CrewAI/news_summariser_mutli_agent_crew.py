from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from crewai import Agent, Task, Process , Crew
from crewai.tools import tool
from datetime import date
from langchain_community.tools import TavilySearchResults


load_dotenv()
llm = ChatOpenAI()

@tool
def get_todays_date():
    '''
    Fetches current date and time
    '''
    return date.today().strftime("%Y-%m-%d")

@tool 
def search_web_tool(query : str):
    '''
    Search the web and returns the results

    '''
    search_tool = TavilySearchResults(max_results=5)
    return search_tool.run(query)


tools = [search_web_tool,get_todays_date]

scraper_agent = Agent(name = "Scraper Agent",
    role="Automated News Data Collector",
    goal="Retrieve the most recent news articles on a user-specified topic, ensuring each article includes its title, publication date, summary, and source URL.",
    backstory="A highly efficient digital journalist, adept at scanning reputable news sources to collect up-to-date articles. This agent ensures each news item is accompanied by accurate metadata, including the date of publication, to establish context and timeliness",
    tools = tools,
    llm=llm
)

verify_agent = Agent(name = "Verify Agent",
    role="Decide if the news is fake or real",
    goal='''Assess the credibility of each collected news article by cross-referencing sources, checking for factual consistency, and identifying potential misinformation. Annotate each article as "Verified" or "Potentially Fake," providing a rationale and referencing the publication date for context.''',
    backstory="An expert fact-checker with experience in investigative journalism and digital forensics. This agent specializes in evaluating the trustworthiness of news, ensuring only reliable and timely information is passed forward.",
    llm=llm
)

summary_agent = Agent(name = "Summary Agent",
    role="Summairze the news obtained from the verify agent",
    goal="Synthesize the verified news articles into a concise, easy-to-read report. Highlight key developments, trends, and dates, ensuring the summary is actionable and relevant for decision-makers",
    backstory="A skilled AI information specialist, trained to distill complex news into clear, brief summaries tailored for busy professionals. This agent emphasizes the most recent and authenticated information, always referencing the dates of the articles to maintain relevance.",
    llm=llm
)


task1 = Task(
    description="Search and collect recent news articles related to '{topic}' and include their sources.",
    agent=scraper_agent,
    expected_output="A list of 3-5 recent news articles with their titles, summaries, and URLs."
)

task2 = Task(
    description="Evaluate the authenticity of the collected news articles and flag any potentially fake ones.",
    agent=verify_agent,
    expected_output="A filtered and annotated list of real and fake articles with reasoning."
)

task3 = Task(
    description="Summarize the real news articles into a concise report suitable for a busy executive.",
    agent=summary_agent,
    expected_output="A 3-5 sentence summary of the most relevant and verified news."
)

crew = Crew(
    agents=[scraper_agent, verify_agent, summary_agent],
    tasks=[task1, task2, task3],
    process=Process.sequential  
)
result = crew.kickoff(inputs={"topic": "Indian test cricket scorecard for yesterday"})
print(result)