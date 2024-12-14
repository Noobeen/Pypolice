'''This is a streamlit application for web app that integrates pylint \
    with LLM to provide feedback on python to users'''
import os
import tempfile
import io

import streamlit as st
import pylint.lint
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.messages import HumanMessage
from langchain_core.output_parsers import StrOutputParser


# Accessing the OpenAI API key from the secrets.toml and setting it as an environment variable
os.environ["OPENAI_API_KEY"] = st.secrets["Open_key"]

# Initializing LLM model
llm = ChatOpenAI(
    model="gpt-4o-mini",
    temperature=0
)


# Displaying the title and a brief description of the app
st.title("PyPolice")
st.header("Plz upload your python file ")


# Creating a file uploader on the Streamlit app
uploaded_file = st.file_uploader("Choose a Python file form your machine", type=["py"])

# checking if file is uploaded or not and displaying the file details
if uploaded_file is not None:
    st.write("Filename:", uploaded_file.name)
    st.write("File type:", uploaded_file.type)
    st.write("File size:", uploaded_file.size, "bytes")

    # Displaying the file content in a text area
    file_content = uploaded_file.getvalue().decode("utf-8")
    st.text_area("File content:", file_content, height=400)

    # Saving the uploaded file to a temporary file
    with tempfile.NamedTemporaryFile(delete=False) as temp_file:
        temp_file.write(uploaded_file.getvalue())
        temp_file_path = temp_file.name

    # invoking pylint on the temporary file and storing the output in a feedback
    pylint_output = io.StringIO()
    pylint_args = ["--max-line-length=150",temp_file_path]
    pylint.lint.Run(pylint_args, exit=False,reporter=pylint.reporters.text.TextReporter(pylint_output))
    pylint_output.seek(0)
    feedback = pylint_output.read()
    score = pylint.lint.Run([temp_file_path], exit=False).linter.stats.global_note

    # Creating Prompt for LLM that provide the context
    CONTEXT_FOR_LLM = '''You are python code analyzer whose job is to analyze the code given by user but not rewrite for them.\
    You will have code and also feedback and score from the pylint.\
    From the feedback given by the pylint, you should detailly mention all errors.\
    Then suggest user on how to improve the code and its readability to increase pylint score.\
    Do not provide the final answer by modifying their code; but instead give them hint or example on what was the issue and how they should fix it.\
    Motivate them to get perfect pylint score'''

    # Creating chat promt template
    prompt_template = ChatPromptTemplate.from_messages(
        [
            (
                "system",
                CONTEXT_FOR_LLM,
            ),
            MessagesPlaceholder(variable_name="messages"),
        ]
    )

    # Creating parser for LLM response
    output_parser= StrOutputParser()

    # Creating chain
    chain = prompt_template | llm | output_parser

    # Invoking the chain
    response=chain.invoke(
    {
        "messages": [
            HumanMessage(
                content=f'''This the user python code
                {file_content}
                Now this is the pylint Feedback:
                {feedback}
                '''
            ),
        ],
    }
    )

    #finally displaying all the details in the app
    st.header("Score")
    st.write(score)
    st.header("Feedback")
    st.write(response)

else:
    st.write("Upload a Python file")
