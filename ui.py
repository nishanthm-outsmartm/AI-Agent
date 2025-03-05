import streamlit as st
import requests

st.set_page_config(page_title="Content Generator", layout='centered')
st.header("AI Content Generator")

form_input = st.text_area('Type the topic or URL', height=150)
tasktype_option = st.selectbox('Task type:', ['Write a sales copy', 'Create a tweet', 'Write a product description', 'Explain a concept'])
age_option = st.selectbox('Target age group:', ['Kid', 'Adult', 'Senior Citizen'])
social_media = st.selectbox('Platform:', ['Instagram', 'Twitter', 'Facebook', 'LinkedIn', 'TikTok'])
content_style = st.selectbox('Style:', ['Persuasive', 'Humorous', 'Inspirational', 'Serious'])
num_outputs = st.slider('Number of outputs:', 1, 5, 1)

def fetch_url_content(input_text):
    if input_text.startswith(('http://', 'https://')):
        return f"Fetching URL content: {input_text}"
    return input_text

if st.button("Generate Content"):
    with st.spinner('Processing...'):
        url_content = fetch_url_content(form_input)
        if url_content.startswith("Fetching URL content"):
            st.write(url_content)
        else:
            query = form_input

        response = requests.post('http://localhost:5000/generate', json={
            'query': query,
            'age_option': age_option,
            'tasktype_option': tasktype_option,
            'social_media': social_media,
            'content_style': content_style,
            'num_outputs': num_outputs
        })

        if response.status_code == 200:
            responses = response.json()
            st.success("Generated Content:")
            for i, response in enumerate(responses):
                st.subheader(f"Version {i+1}:")
                st.write(response)
        else:
            st.error(f"API Error: {response.status_code}")

