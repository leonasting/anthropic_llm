from http import client
import streamlit as st
import re
#import os
#import pathlib
#import textwrap
from IPython.display import display
from IPython.display import Markdown
from anthropic import Anthropic


def calculate(expression):
    # Remove any non-digit or non-operator characters from the expression
    expression = re.sub(r'[^0-9+\-*/().]', '', expression)
    
    try:
        # Evaluate the expression using the built-in eval() function
        result = eval(expression)
        return str(result)
    except (SyntaxError, ZeroDivisionError, NameError, TypeError, OverflowError):
        return "Error: Invalid expression"

tools = [
    {
        "name": "calculator",
        "description": "A simple calculator that performs basic arithmetic operations.",
        "input_schema": {
            "type": "object",
            "properties": {
                "expression": {
                    "type": "string",
                    "description": "The mathematical expression to evaluate (e.g., '2 + 3 * 4')."
                }
            },
            "required": ["expression"]
        }
    }
    ]
#import google.generativeai as genai

def expander_content():
    "Please Update the Antrhopic API Key to use the app"
    anthropic_api_key = st.text_input("Anthropic API Key", key="anthropic_api_key", type="password")
    "[Get an Anthropic AI API key](https://console.anthropic.com/settings/keys)"
    "[View the source code]()"
    "[![Open in GitHub Codespaces](https://github.com/codespaces/badge.svg)](https://codespaces.new/streamlit/llm-examples?quickstart=1)"

    st.info("Please add your Anthropic API key to continue.")
    if not anthropic_api_key:
        st.stop()
    
    if anthropic_api_key:
        client = Anthropic(api_key=anthropic_api_key)
        MODEL_NAME = "claude-3-opus-20240229"
        ## Function to load OpenAI model and get respones
        try:
            model = genai.GenerativeModel('gemini-pro')
            chat = model.start_chat(history=[])
            response=get_gemini_response(chat,"Greetings with current time in single sentence.")
            st.session_state['connection'] = True
            #return chat
        except Exception as e:
            st.error("Invalid API Key")
            print(e)
            #st.session_state['google_api_key'] = None
            del google_api_key
            #del google_api_key
            st.stop()

def get_gemini_response(chat,question):
    """
    chat - chatbot object(geminit model chat object)
    question - user query/prompt(string)
    """
    
    response =chat.send_message(question,stream=True)
    return response




def main():
    st.set_page_config(page_title="Chatbot")
    google_api_key = None
    expand_flag = True
    
    if 'google_api_key'in  st.session_state:
        google_api_key = st.session_state['google_api_key']

    if 'connection' in st.session_state:
        if st.session_state['connection'] == True:
            expand_flag = False
    else:
        st.session_state['connection'] = False

        
    
    # Open sidebar by default for mobile devices
    if expand_flag:
        with st.expander("Settings", expanded=expand_flag):
            expander_content()
    else:
        with st.expander("Settings", expanded=expand_flag):
            expander_content()
    if google_api_key:
        
        st.title("💬 Omni LLM")
        st.caption("🚀 A streamlit chatbot powered by Google Generative LLM")


        #st.header("Gemini LLM Application")
        # Initialize session state for chat history if it doesn't exist
        if 'chat_history' not in st.session_state:
            st.session_state['chat_history'] = []


        if prompt := st.chat_input():
            if 'chat_model' not in st.session_state:
                model = genai.GenerativeModel('gemini-pro')
                chat_model = model.start_chat(history=[])
                #st.session_state['chat_model'] = chat_model           
        

            response=get_gemini_response(chat_model,prompt)
            # Add user query and response to session state chat history
            st.session_state['chat_history'].append(("You", prompt))
            st.subheader("Omni:")
            res=[]
            for chunk in response:
                st.write(chunk.text)
                res.append(chunk.text)
            
            st.session_state['chat_history'].append(("Bot", "".join(res)))
        with st.sidebar:   
            with st.expander("history", expanded=False):  
                if st.session_state['chat_history']:
                    "The Chat History is"
                    
                    for role, text in st.session_state['chat_history'][::-1]:
                        st.write(f"{role}: {text}")
                    

if __name__ == "__main__":
    main()