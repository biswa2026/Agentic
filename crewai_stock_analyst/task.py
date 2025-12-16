from crewai import Task
from agents import resercher_agent,write_agent

research_task=Task(agent=resercher_agent,
     description='research about best stock to invest in india 2025',
     expected_output='wel defiend  research about best stocks')
writing_task=Task(agent=write_agent,description='using reasrch summary write 3 paragraph and other details on that stock',
                  expected_output='write clean and conscise summary in readable format with tables')
