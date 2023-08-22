import os
import re
from typing import List, Union
from urllib.parse import urljoin

import gradio as gr
from langchain import LLMChain
from langchain.agents import Tool, AgentExecutor, LLMSingleActionAgent, AgentOutputParser
from langchain.memory import ConversationSummaryBufferMemory
from langchain.prompts import BaseChatPromptTemplate
from langchain.schema import AgentAction, AgentFinish, HumanMessage
from serpapi import GoogleSearch

from custom_llm import CustomLLM
from custom_tool import run

URL = os.environ.get("URL_ENDPOINT")

tool_used_count = 0


def search_the_web(query):
    # url = "https://www.google.com/search?q=" + query
    # response = requests.get(url)
    # return response.content
    params = {
        "api_key": "d5c1632f211f688eed5274bbfebd58bb3962994704b651a732040f7b0f7cebee",
        "engine": "google",
        "q": query,
        "location": "Delhi, India",
        "google_domain": "google.co.in",
        "gl": "in",
        "hl": "en"
    }

    res = GoogleSearch(params)
    results = res.get_dict()
    if "organic_results" not in results:
        return None
    links = [item.get('link', None) for item in results['organic_results']]

    # Usually 1st link is the most relevant link (trusting the Google xD)
    answer = run(links[0], query)
    return answer


tools = [
    Tool(
        name="Search",
        func=search_the_web,
        description="useful for when you need to answer questions about current events, data. You should ask targeted questions"
    )
]

template = """
SYSTEM: You are a world class researcher, who can do detailed research on any topic and produce facts based results; you do not make things up, you will try as hard as possible to gather facts & data to back up the research            

Please make sure you complete the objective above with the following rules:

1. You should do enough research to gather as much information as possible about the objective
2. If there are url of relevant links & articles, you will scrape it to gather more information
3. You are allowed to use the tools only 1 time
4. You should not make things up, you should only write facts & data that you have gathered
5. In the final output, You should include all reference data & links to back up your research; You should include all reference data & links to back up your research
6. In the final output, You should include all reference data & links to back up your research; You should include all reference data & links to back up your research

You have access to the following tools:

{tools}

Use the following format:

Question: the input question you must answer to find the best factual information about query
Thought: you should always think about what to do with respect to the response you have
Action: the action to take, should be one of [{tool_names}]
Action Input: the input to the action
Response: Results obtained from performing the action, put all the response of tools here
Observation: Deeply analyze the result of the action while remembering the figures, numbers and references
Thought: I now know the final answer
Final Answer: Use the following format for final answer
    Results: Write the data you got as Response 
    Conclusion: Write the final observation
    References: Write all the references or links obtained / used during the entire research

User: {input}
Assistant:
{agent_scratchpad}"""


class CustomPromptTemplate(BaseChatPromptTemplate):
    template: str
    tools: List[Tool]

    def format_messages(self, **kwargs):
        # Get the intermediate steps (AgentAction, Observation tuples)
        # Format them in a particular way
        intermediate_steps = kwargs.pop("intermediate_steps")
        thoughts = ""
        for action, observation in intermediate_steps:
            thoughts += action.log
            thoughts += f"\nObservation: {observation}\nThought: "
        # Set the agent_scratchpad variable to that value
        kwargs["agent_scratchpad"] = thoughts
        # Create a tools variable from the list of tools provided
        kwargs["tools"] = "\n".join([f"{tool.name}: {tool.description}" for tool in self.tools])
        # Create a list of tool names for the tools provided
        kwargs["tool_names"] = ", ".join([tool.name for tool in self.tools])
        formatted = self.template.format(**kwargs)
        return [HumanMessage(content=formatted)]


prompt = CustomPromptTemplate(
    template=template,
    tools=tools,
    input_variables=["input", "intermediate_steps"]
)


class CustomOutputParser(AgentOutputParser):

    def parse(self, llm_output: str) -> Union[AgentAction, AgentFinish]:
        global tool_used_count
        # Check if agent should finish
        if "Final Answer:" in llm_output:
            return AgentFinish(
                return_values={"output": llm_output.split("Final Answer:")[-1].strip().replace("\n", "<br>")},
                log=llm_output,
            )
        if tool_used_count < 1:
            regex = r"Action\s*\d*\s*:(.*?)\nAction\s*\d*\s*Input\s*\d*\s*:[\s]*(.*)"
            match = re.search(regex, llm_output, re.DOTALL)
            if not match:
                raise ValueError(f"Could not parse LLM output: `{llm_output}`")
            action = match.group(1).strip()
            action_input = match.group(2)
            tool_used_count += 1
            return AgentAction(tool=action, tool_input=action_input.strip(" ").strip('"'), log=llm_output)


def main(query, max_tokens):
    output_parser = CustomOutputParser()
    llm = CustomLLM(url=urljoin(URL, "generate"), max_tokens=max_tokens)
    memory = ConversationSummaryBufferMemory(
        memory_key="memory", return_messages=True, llm=llm, max_token_limit=1000)
    # LLM chain consisting of the LLM and a prompt
    llm_chain = LLMChain(llm=llm, prompt=prompt)
    tool_names = [tool.name for tool in tools]
    agent = LLMSingleActionAgent(
        llm_chain=llm_chain,
        output_parser=output_parser,
        stop=['\nObservation'],
        allowed_tools=tool_names
    )
    agent_executor = AgentExecutor.from_agent_and_tools(agent=agent, tools=tools, verbose=True, memory=memory)
    return agent_executor.run(query)


# Gradio settings
theme = gr.themes.Monochrome(
    primary_hue="indigo",
    secondary_hue="blue",
    neutral_hue="slate",
    radius_size=gr.themes.sizes.radius_sm,
    font=[gr.themes.GoogleFont("Open Sans"), "ui-sans-serif", "system-ui", "sans-serif"])

description = """<div style="text-align: center;"> <center><img src='https://raw.githubusercontent.com/practice404/L-WAVE/main/assets/banner.png' width='70%'/></center> 
<br> <h1><u> L-WAVE: LLaMA Web Access and Visual Enhancement </u></h1> </div> <br> <div style="text-align: center;"> L-WAVE is an innovative project 
that seamlessly integrates the power of a cutting-edge Llama2 model with the vast resources of the web. With the 
ability to access unknown information through intelligent Google searches, L-WAVE empowers users with instant 
knowledge retrieval. Not only does L-WAVE provide text-based answers, but it also boasts an impressive image 
rendering feature that brings visual context to your inquiries. Harnessing the strengths of both the Llama model and 
the web, L-WAVE is your ultimate companion for uncovering insights and visualizing information. Experience the future 
of information access with L-WAVE. </div>"""

with gr.Blocks(theme=theme, analytics_enabled=False) as demo:
    with gr.Column():
        gr.Markdown(description)
        with gr.Row():
            with gr.Column():
                with gr.Accordion("Settings", open=True):
                    with gr.Row():
                        column_1 = gr.Column()
                        with column_1:
                            max_new_tokens = gr.Slider(
                                label="Max new tokens",
                                value=256,
                                minimum=0,
                                maximum=4096,
                                step=64,
                                interactive=True,
                                info="The maximum numbers of new tokens",
                            )
        with gr.Row():
            with gr.Column():
                instruction = gr.Textbox(
                    placeholder="Enter your query here",
                    lines=5,
                    label="Input",
                    elem_id="q-input",
                )
                submit = gr.Button("Generate", variant="primary")
                output = gr.Markdown(label="Output")

    submit.click(
        main,
        inputs=[instruction, max_new_tokens],
        outputs=[output],
    )
demo.queue(concurrency_count=16).launch(debug=True)
