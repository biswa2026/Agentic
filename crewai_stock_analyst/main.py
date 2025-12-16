from crewai import Crew
from agents import resercher_agent, write_agent
from task import research_task, writing_task
import yaml

def run():
    # Optional: load crew-level config from YAML
    with open("config/crew.yaml", "r") as f:
        crew_config = yaml.safe_load(f)

    # Build crew entirely in Python
    crew = Crew(
        name=crew_config.get("name", "Python Crew POC"),
        description=crew_config.get("description", ""),
        agents=[resercher_agent,write_agent],
        tasks=[research_task,writing_task],
        process=crew_config.get("process", "sequential"),
        verbose=crew_config.get("verbose", True)
    )
    result=crew.kickoff()
    print('======final output=====')
    print(result)

if __name__=='__main__':
    run()
