import json
from typing import Any, List, Mapping, Optional

import requests
from langchain.callbacks.manager import CallbackManagerForLLMRun
from langchain.llms.base import LLM


class CustomLLM(LLM):
    url: str
    max_tokens: int = 512

    @property
    def _llm_type(self) -> str:
        return "custom"

    @property
    def _identifying_params(self) -> Mapping[str, Any]:
        """Get the identifying parameters."""
        return {"url": self.url}

    def _call(self,
              prompt: str,
              stop: Optional[List[str]] = None,
              run_manager: Optional[CallbackManagerForLLMRun] = None,
              ) -> str:
        # if stop is not None:
        #     raise ValueError("stop kwargs are not permitted.")
        data = {
            "inputs": prompt,
            "parameters": {
                "temperature": 0.0,
                "max_tokens": self.max_tokens
            }
        }
        res = requests.post(self.url, json.dumps(data))
        content = json.loads(res.content)['generated_text'].strip()
        return content


if __name__ == "__main__":
    from urllib.parse import urljoin

    llm = CustomLLM(url=urljoin("https://9919-34-81-77-222.ngrok-free.app", "generate"), max_tokens=512)
    prompt = """SYSTEM: You are a helpful, respectful and honest assistant. Always answer as helpfully as possible, 
    while being safe.  Your answers should not include any harmful, unethical, racist, sexist, toxic, dangerous, 
    or illegal content. Please ensure that your responses are socially unbiased and positive in nature. If a question 
    does not make any sense, or is not factually coherent, explain why instead of answering something not correct. If 
    you don't know the answer to a question, please don't share false information.: USER: {query} ASSISTANT:"""

    print(llm(prompt.format(
        query="What is the current financial conditions of the Tesla also include all the facts and references").strip()).strip())
