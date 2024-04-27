from http import client
import anthropic
import streamlit as st
import re
#import os
#import pathlib
#import textwrap
from IPython.display import display
from IPython.display import Markdown
from anthropic import Anthropic

    

# Data Structure to define the tool for LLM to use. 
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

def calculate(expression):
    # Remove any non-digit or non-operator characters from the expression
    expression = re.sub(r'[^0-9+\-*/().]', '', expression)
    
    try:
        # Evaluate the expression using the built-in eval() function
        result = eval(expression)
        return str(result)
    except (SyntaxError, ZeroDivisionError, NameError, TypeError, OverflowError):
        return "Error: Invalid expression"



def process_tool_call(tool_name, tool_input):
    if tool_name == "calculator":
        return calculate(tool_input["expression"])


def connect_with_claude(client):
    MODEL_NAME = "Claude 2.1"
    message=client.beta.tools.messages.create(
        model=MODEL_NAME,
        max_tokens=100,
        messages=[{"role": "user", "content": "Hello, Claude!"}],
        tools=tools,
    )
    print(f"Initial Response: {message.content}")   




#import google.generativeai as genai
def chat_with_claude(user_message, client, MODEL_NAME, tools):
    print(f"\n{'='*50}\nUser Message: {user_message}\n{'='*50}")

    message = client.beta.tools.messages.create(
        model=MODEL_NAME,
        max_tokens=4096,
        messages=[{"role": "user", "content": user_message}],
        tools=tools,
    )

    print(f"\nInitial Response:")
    print(f"Stop Reason: {message.stop_reason}")
    print(f"Content: {message.content}")

    if message.stop_reason == "tool_use":
        tool_use = next(block for block in message.content if block.type == "tool_use")
        tool_name = tool_use.name
        tool_input = tool_use.input

        print(f"\nTool Used: {tool_name}")
        print(f"Tool Input: {tool_input}")

        tool_result = process_tool_call(tool_name, tool_input)

        print(f"Tool Result: {tool_result}")

        response = client.beta.tools.messages.create(
            model=MODEL_NAME,
            max_tokens=4096,
            messages=[
                {"role": "user", "content": user_message},
                {"role": "assistant", "content": message.content},
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "tool_result",
                            "tool_use_id": tool_use.id,
                            "content": tool_result,
                        }
                    ],
                },
            ],
            tools=tools,
        )
    else:
        response = message

    final_response = next(
        (block.text for block in response.content if hasattr(block, "text")),
        None,
    )
    print(response.content)
    print(f"\nFinal Response: {final_response}")

    return final_response




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


        #MODEL_NAME = "claude-3-opus-20240229"
        ## Function to load OpenAI model and get respones
        try:
            
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
    anthropic_api_key = None
    expand_flag = True
    
    if 'anthropic_api_key'in  st.session_state:
        anthropic_api_key = st.session_state['anthropic_api_key']

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
    if anthropic_api_key:
        
        st.title("💬 CLaude LLM")
        st.caption("🚀 A streamlit chatbot powered with Anthropic Claude")


        #st.header("Gemini LLM Application")
        # Initialize session state for chat history if it doesn't exist
        if 'chat_history' not in st.session_state:
            st.session_state['chat_history'] = []


        if prompt := st.chat_input():
            pass
            #if 'chat_model' not in st.session_state:
                
                
if __name__ == "__main__":
    main()