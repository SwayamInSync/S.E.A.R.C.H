from llama_index.llms import LlamaCPP
from llama_index.llms.llama_utils import completion_to_prompt


model_url = "https://huggingface.co/TheBloke/zephyr-7B-beta-GGUF/resolve/main/zephyr-7b-beta.Q4_K_S.gguf"


def messages_to_prompt_zephyr(messages):
    prompt = ""
    for message in messages:
        if message.role == 'system':
            prompt += f"<|system|>\n{message.content}</s>\n"
        elif message.role == 'user':
            prompt += f"<|user|>\n{message.content}</s>\n"
        elif message.role == 'assistant':
            prompt += f"<|assistant|>\n{message.content}</s>\n"

    if not prompt.startswith("<|system|>\n"):
        prompt = "<|system|>\n</s>\n" + prompt

    prompt = prompt + "<|assistant|>\n"

    return prompt


llm = LlamaCPP(
    model_url=model_url,
    temperature=0.1,
    max_new_tokens=256,
    context_window=3900,
    generate_kwargs={"temperature": 0.7, "top_k": 50, "top_p": 0.95},
    model_kwargs={"n_gpu_layers": 1},
    messages_to_prompt=messages_to_prompt_zephyr,
    completion_to_prompt=completion_to_prompt,
    verbose=True,
)


if __name__ == "__main__":
    response_iter = llm.stream_complete(
        "Hello there")
    for response in response_iter:
        print(response.delta, end="", flush=True)
