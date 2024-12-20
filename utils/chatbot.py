import streamlit as st
import openai
from streamlit_chat import message

minimum_responses = 1
warning_responses = 3
maximum_responses = 5


# Perform content filter to the response from chatbot
def content_filter(content_to_classify):
    response = openai.Completion.create(
        engine="content-filter-alpha",
        prompt="<|endoftext|>" + content_to_classify + "\n--\nLabel:",
        temperature=0,
        max_tokens=1,
        top_p=1,
        frequency_penalty=0,
        presence_penalty=0,
        logprobs=10
    )
    output_label = response["choices"][0]["text"]

    toxic_threshold = -0.355

    if output_label == "2":
        logprobs = response["choices"][0]["logprobs"]["top_logprobs"][0]

        if logprobs["2"] < toxic_threshold:
            logprob_0 = logprobs.get("0", None)
            logprob_1 = logprobs.get("1", None)

            if logprob_0 is not None and logprob_1 is not None:
                if logprob_0 >= logprob_1:
                    output_label = "0"
                else:
                    output_label = "1"
            elif logprob_0 is not None:
                output_label = "0"
            elif logprob_1 is not None:
                output_label = "1"

    if output_label not in ["0", "1", "2"]:
        output_label = "2"

    return output_label


# Request the response from OpenAI api
def request_response(user_input):

    print('request_response')
    print('prompt:', st.session_state['prompt'])

    prompt = st.session_state['prompt']
    prompt = prompt + 'Human: ' + user_input + '\n' + 'AI:'

    response_content = ""
    
    response = openai.ChatCompletion.create(
        model="gpt-4o",
        messages=[{"role": "user", "content": prompt}],
        temperature = 0,
        max_tokens=500,
        stream=True
    )

    # Stream the response and update the UI incrementally
    message_placeholder = st.empty()  # Placeholder for streaming text

    # Iterate over the streamed chunks
    for chunk in response:
        chunk_content = chunk['choices'][0]['delta'].get('content', '')
        if chunk_content:
            response_content += chunk_content  # Append chunk to the response content
            message_placeholder.write(response_content)  # Update the UI incrementally

    return response_content

   # response = openai.Completion.create(
   #     engine="davinci",
   #     prompt=prompt,
   #     temperature=0.9,
   #     max_tokens=150,
   #     top_p=1,
   #     frequency_penalty=0,
   #     presence_penalty=0.6,
   #     stop=["\n", " Human:", " AI:"],
   #     user=st.session_state['survey_id']
   # )

    #content = response.choices[0].text

    #content = response["choices"][0]["message"]["content"]

    #if content_filter(content) != '2':
    #    return content
   # return content 
   # return request_response(user_input)


# Get response from GPT-3
def get_response(user_input):

    # User input is empty
    if user_input == '':
        return None

    # The response count has reached the maximum responses
    if st.session_state['response_count'] >= maximum_responses:
        return None

    # The survey has been finished
    if st.session_state['survey_finished']:
        return None

    # Preliminary hello input
    if user_input in ['Hello', 'hello', 'Hello!', 'Hi', 'hi', 'HI', 'Hi!']:
        return 'Hello! I am the AI assistant. Let me know if you have any questions for the flood.'

    # Get response from gpt-3
    response = request_response(user_input)
    return response
