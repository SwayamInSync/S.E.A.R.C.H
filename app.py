import gradio as gr
from jinja2 import Template

from app_utils import template, desc
from tools import get_html_content
from main import process


def main(query, *extra_args):
    try:
        result = process(query, extra_args)
        text_content = get_html_content(result['content'])
        jinja_template = Template(template)
        rendered_html = jinja_template.render(
            content=text_content,
            images=result['images'],
            references=result['references']
        )
        return str(rendered_html)
    except Exception as e:
        print(f"An error occurred: {e}")
        return "<p>An error occurred while processing your query.</p>"


with gr.Blocks() as demo:
    with gr.Row():
        with gr.Column():
            gr.HTML(
                "<center><h1> S.E.A.R.C.H : Systematic Engine for Analyzed Retrieval and Contextual Handling </h1></center>")
            gr.HTML(desc)
    with gr.Row():
        gr.Text("Pick Extra functionalities for query")
    with gr.Row():
        is_web = gr.Checkbox(label="Use Internet")
        is_code = gr.Checkbox(label="Code Interpreter")
        is_img_query = gr.Checkbox(label="Image Search")
        is_sub_query = gr.Checkbox(label="Sub-Query Engine")
    with gr.Row():
        with gr.Column():
            query_input = gr.Textbox(
                placeholder="Enter your query here...", label="Search")
            submit_button = gr.Button("Get Answer")
    result_output = gr.HTML()
    try:
        submit_button.click(
            main,
            inputs=[query_input, is_web, is_code, is_img_query, is_sub_query],
            outputs=result_output
        )
    except Exception as e:
        print(e)

demo.queue().launch(share=True)
