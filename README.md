# L-WAVE: LlaMA Web Access and Visual Enhancement

![](https://raw.githubusercontent.com/practice404/L-WAVE/main/assets/banner.png)

## Table of Contents

* [Introduction](#introduction)
* [Installation](#installation)
* [Usage](#usage)
* [Demo](#Demo)

## Introduction

L-WAVE is an innovative project that seamlessly integrates the power of a cutting-edge Llama2 model with the vast resources of the web. With the ability to access unknown information through intelligent Google searches, L-WAVE empowers users with instant knowledge retrieval. Not only does L-WAVE provide text-based answers, but it also boasts an impressive image rendering feature that brings visual context to your inquiries. Harnessing the strengths of both the Llama model and the web, L-WAVE is your ultimate companion for uncovering insights and visualizing information. Experience the future of information access with L-WAVE.

## Demo

https://github.com/practice404/L-WAVE/assets/74960567/ab98159b-c66c-46a2-883e-cda04b8a548e

## Installation

To install this project, follow these steps:

1. Clone the repository to your local machine.
2. Install the dependencies.
3. Get your API keys from 
   1. [SerpAI](https://serpapi.com/)
   2. [Browserless](https://www.browserless.io/)
   3. AuthToken from [ngrok](https://ngrok.com/)

4. Put [ngrok](https://ngrok.com/) AuthToken in the [LLaMA2_13B_Hosting](https://github.com/practice404/L-WAVE/blob/main/LLaMA2_13B_Hosting.ipynb)  notebook
5. Upload and execute [LLaMA2_13B_Hosting](https://github.com/practice404/L-WAVE/blob/main/LLaMA2_13B_Hosting.ipynb)  notebook [Google Colab](https://colab.research.google.com/) and obtain the `MODEL_ENDPOINT`

## Usage

Run the following command inside terminal

```bash
export SERPER_API=<SERP_API> && export BROWSERLESS_API=<BROWSERLESS_API> && export URL_ENDPOINT=<MODEL_ENDPOINT> && gradio app.py
```


