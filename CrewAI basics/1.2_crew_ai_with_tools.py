from langchain_openai import ChatOpenAI
from crewai import Task, Agent, Crew, Process

from datetime import datetime

from dotenv import load_dotenv
from langchain_community.tools import TavilySearchResults
from crewai.tools import tool

llm = ChatOpenAI()

@tool 
def search_web_tool(query : str):
    '''
    Search the web and returns the results

    '''
    search_tool = TavilySearchResults(max_results=3)
    return search_tool.run(query)

guide_expert = Agent(
role="Travel guide",
    goal="Provides information on things to do in the city based on the user's interests",
    backstory="""A local expert with a passion for sharing the best experiences and hidden gems of their city.""",
    tools=[search_web_tool],
    verbose= True, 
    max_iter=3,
    allow_delegation= False,
    llm=llm
)

# Agent city expert
location_expert = Agent(
    role="Travel Trip Expert",
    goal="Adapt to the user destination vity language (French if city in French Country. Gather helpful information about to the city and city during travel.",
    backstory="""A seasoned traveler who has explored various destinations and knows the ins and outs of travel logistics.""",
    tools=[search_web_tool],
    verbose=True,
    max_iter=5,
    llm=llm,
    allow_delegation=False,
    )

planner_expert = Agent(
    role="Travel Planning Expert",
    goal="Compiles all gathered information to provide a comprehensive travel plan.",
    backstory="""
    You are a professional guide with a passion for travel.
    An organizational wizard who can turn a list of possibilities into a seamless itinerary.
    """,
    tools=[search_web_tool],
    verbose=True,
    max_iter=5,
    llm=llm,
    allow_delegation=False,
    )


from_city = "India"
destination_city = "Rome"
date_from = "29 August 2025"
date_to = "7th September 2025"
interests = "sight seeing and good food"

location_task = Task(
    description=f"""
    In French : This task involves a comprehensive data collection process to provide the traveler with essential information about their destination. It includes researching and compiling details on various accommodations, ranging from budget-friendly hostels to luxury hotels, as well as estimating the cost of living in the area. The task also covers transportation options, visa requirements, and any travel advisories that may be relevant.
    consider also the weather conditions forcast on the travel dates. and all the events that may be relevant to the traveler during the trip period.
    
    Traveling from : {from_city}
    Destination city : {destination_city}
    Arrival Date : {date_from}
    Departure Date : {date_to}

    Follow this rules : 
    1. if the {destination_city} is in a French country : Respond in FRENCH.
    """,
    expected_output=f"""
    if the {destination_city} is in a French country : Respond in FRENCH.
    In markdown format : A detailed markdown report that includes a curated list of recommended places to stay, a breakdown of daily living expenses, and practical travel tips to ensure a smooth journey.
    """,
    agent=location_expert,
    output_file='city_report.md',
)

guide_task = Task(
    description=f"""
    if the {destination_city} is in a French country : Respond in FRENCH.
    Tailored to the traveler's personal {interests}, this task focuses on creating an engaging and informative guide to the city's attractions. It involves identifying cultural landmarks, historical spots, entertainment venues, dining experiences, and outdoor activities that align with the user's preferences such {interests}. The guide also highlights seasonal events and festivals that might be of interest during the traveler's visit.
    Destination city : {destination_city}
    interests : {interests}
    Arrival Date : {date_from}
    Departure Date : {date_to}

    Follow this rules : 
    1. if the {destination_city} is in a French country : Respond in FRENCH.
    """,
    expected_output=f"""
    An interactive markdown report that presents a personalized itinerary of activities and attractions, complete with descriptions, locations, and any necessary reservations or tickets.
    """,

    agent=guide_expert,
    output_file='guide_report.md',
)

planner_task = Task(
    description=f"""
    This task synthesizes all collected information into a detaileds introduction to the city (description of city and presentation, in 3 pragraphes) cohesive and practical travel plan. and takes into account the traveler's schedule, preferences, and budget to draft a day-by-day itinerary. The planner also provides insights into the city's layout and transportation system to facilitate easy navigation.
    Destination city : {destination_city}
    interests : {interests}
    Arrival Date : {date_from}
    Departure Date : {date_to}

    Follow this rules : 
    1. if the {destination_city} is in a French country : Respond in FRENCH.
    """,
    expected_output="""
    if the {destination_city} is in a French country : Respond in FRENCH.
    A rich markdown document with emojis on each title and subtitle, that :
    In markdown format : 
    # Welcome to {destination_city} :
    A 4 paragraphes markdown formated including :
    - a curated articles of presentation of the city, 
    - a breakdown of daily living expenses, and spots to visit.
    # Here's your Travel Plan to {destination_city} :
    Outlines a daily detailed travel plan list with time allocations and details for each activity, along with an overview of the city's highlights based on the guide's recommendations
    """,
    context=[location_task, guide_task],
    #context=context,
    agent=planner_expert,
        output_file='travel_plan.md',
        )

crew = Crew(
agents=[location_expert, guide_expert, planner_expert],
tasks=[location_task, guide_task, planner_task],
process=Process.sequential,
full_output=True,
share_crew=False,
verbose=True
)

result = crew.kickoff()
