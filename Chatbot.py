from pydoc import cli
import streamlit as st
from anthropic import Anthropic
from anthropic import HUMAN_PROMPT, AI_PROMPT
import re

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
    """
    Return Type: Int/float - Success or Str: Error message(
    Returns the result of evaluating a mathematical expression.

    """
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
    """
    Function to check we can establish connetion with Claude API or not.
    """    
    # Send the request to the Claude API
    response = client.completions.create(
        model="claude-instant-1.2",
        max_tokens_to_sample=100,
        prompt=f"{HUMAN_PROMPT} Hello, Claude{AI_PROMPT}",
        )

    # Print the response
    st.write(response.completion)
    
def expander_content():
    "Please Update the Antrhopic API Key to use the app"
    anthropic_api_key = st.text_input("Anthropic API Key", key="anthropic_api_key", type="password")
    "[Get an Anthropic AI API key](https://console.anthropic.com/settings/keys)"
    "[View the source code]()"
    "[![Open in GitHub Codespaces](https://github.com/codespaces/badge.svg)](https://codespaces.new/streamlit/llm-examples?quickstart=1)"
    st.info("Please add your Anthropic API key to continue.")
    if not anthropic_api_key:
        pass
        #st.stop()
    if anthropic_api_key:
        client = Anthropic(api_key=anthropic_api_key)
        #MODEL_NAME = "claude-3-opus-20240229"
        ## Function to load OpenAI model and get respones
        try:
            connect_with_claude(client)
            st.session_state['connection'] = True
            return client
        except Exception as e:
            st.error("Invalid API Key"+str(e))
            print(e)
            #st.session_state['google_api_key'] = None
            del anthropic_api_key
            #del google_api_key
            return False
            #st.stop()

def chat_with_claude(client,user_message):
    st.write("User Message: "+user_message)
    print(f"\n{'='*50}\nUser Message: {user_message}\n{'='*50}")
    MODEL_NAME = "claude-3-opus-20240229"
    message = client.beta.tools.messages.create(
        model=MODEL_NAME,
        max_tokens=4096,
        messages=[{"role": "user", "content": user_message}],
        tools=tools,
    )

    print(f"\nInitial Response:")
    print(f"Stop Reason: {message.stop_reason}")
    print(f"Content: {message.content}")
    st.write(message.content)
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



def main():
    st.set_page_config(page_title="Chatbot")
    anthropic_api_key = None
    expand_flag = True
    client = None
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
            client = expander_content()
    else:
        pass
        #with st.expander("Settings", expanded=expand_flag):
        #    client = expander_content()
    if anthropic_api_key:
        st.title("💬 CLaude LLM")
        st.caption("🚀 A streamlit chatbot powered with Anthropic Claude")
        #expand_flag = True
        st.write("Eg:-What is the result of 1,984,135 * 9,343,116?")
        client = Anthropic(api_key=anthropic_api_key)
        if prompt := st.chat_input("Please Give artithmetic expression in words"):
            st.write(prompt)
            st.write(client)
            if client:
                print("wow")
                response = chat_with_claude(client, prompt)
                st.write(response)
        
if __name__ == "__main__":
    main()