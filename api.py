import os
import requests
from langchain.prompts import PromptTemplate, FewShotPromptTemplate
from langchain.prompts.example_selector import LengthBasedExampleSelector
from dotenv import load_dotenv
from bs4 import BeautifulSoup
from flask import Flask, request, jsonify

load_dotenv()

app = Flask(__name__)

def get_url_content(url):
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')

        main_content = soup.find('main') or soup.find('article') or soup.body
        if main_content:
            text = ' '.join(main_content.stripped_strings)
            return text[:3000]
        return "Could not extract main content from the webpage"
    except Exception as e:
        return f"Error fetching URL content: {str(e)}"

@app.route('/generate', methods=['POST'])
def generate_content():
    data = request.json
    query = data['query']
    age_option = data['age_option']
    tasktype_option = data['tasktype_option']
    social_media = data['social_media']
    content_style = data['content_style']
    num_outputs = data['num_outputs']

    grok_url = "https://api.grok.com/openai/v1/chat/completions"
    grok_api_key = os.getenv('GROK_API_TOKEN')

    examples = []
    if age_option == "Kid":
        examples = [
            {"query": "What is a mobile?", "answer": "A mobile is a magical device that fits in your pocket!"},
            {"query": "Why is the sky blue?", "answer": "The sky wears its favorite blue color every day!"}
        ]
    elif age_option == "Adult":
        examples = [
            {"query": "What is a mobile?", "answer": "A mobile is a portable communication device."},
            {"query": "Why is the sky blue?", "answer": "Due to Rayleigh scattering of sunlight."}
        ]
    elif age_option == "Senior Citizen":
        examples = [
            {"query": "What is a mobile?", "answer": "A mobile phone is a device for calls, messages, and internet."},
            {"query": "Why is the sky blue?", "answer": "Atmospheric scattering makes the sky appear blue."}
        ]

    example_template = """Question: {query}\nResponse: {answer}"""
    example_prompt = PromptTemplate(
        input_variables=["query", "answer"],
        template=example_template
    )

    prefix = f"""You are a {age_option} creating {content_style} content for {social_media}. 
    Task: {tasktype_option}. Examples:"""
    suffix = "\nQuestion: {template_userInput}\nResponse: "

    example_selector = LengthBasedExampleSelector(
        examples=examples,
        example_prompt=example_prompt,
        max_length=200
    )

    new_prompt_template = FewShotPromptTemplate(
        example_selector=example_selector,
        example_prompt=example_prompt,
        prefix=prefix,
        suffix=suffix,
        input_variables=["template_userInput"],
        example_separator="\n"
    )

    prompt_data = new_prompt_template.format(template_userInput=query)

    payload = {
        "model": "grok-2-latest",
        "messages": [{"role": "user", "content": prompt_data}],
        "n": num_outputs
    }

    headers = {
        "Authorization": f"Bearer {grok_api_key}",
        "Content-Type": "application/json"
    }

    response = requests.post(grok_url, json=payload, headers=headers)
    if response.status_code == 200:
        result = response.json()
        return jsonify([choice['message']['content'] for choice in result['choices']])
    return jsonify({"error": f"API Error: {response.status_code} - {response.text}"}), response.status_code

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
