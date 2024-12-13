'''This is the main file that app will use and using this app user can upload their
 python file and check for errors and suggestions to improve the code redability'''
import streamlit as st
import pylint.lint
import tempfile
import io
import os
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.messages import HumanMessage
from langchain_core.output_parsers import StrOutputParser

# Set the OpenAI API key
os.environ["OPENAI_API_KEY"] = st.secrets["Open_key"] 

# Creating a ChatOpenAI instance
llm = ChatOpenAI(
    model="gpt-4o-mini",
    temperature=0
)

# Display a title
st.write("This app is a simple file upload app.")

# Creating a file uploader
uploaded_file = st.file_uploader("Choose a Python file it should be utf-8 incoded", type=["py"])

# checking if file is uploaded and displaying the file details
if uploaded_file is not None:
    st.write("Filename:", uploaded_file.name)
    st.write("File type:", uploaded_file.type)
    st.write("File size:", uploaded_file.size, "bytes")

    # Display the file content in a text area
    file_content = uploaded_file.getvalue().decode("utf-8")
    st.text_area("File content:", file_content, height=200)

    # Saving the uploaded file to a temporary file
    with tempfile.NamedTemporaryFile(delete=False) as temp_file:
        temp_file.write(uploaded_file.getvalue())
        temp_file_path = temp_file.name

    
    pylint_output = io.StringIO()
    pylint_args = [temp_file_path]
    pylint.lint.Run(pylint_args, exit=False, reporter=pylint.reporters.text.TextReporter(pylint_output))
    pylint_output.seek(0)
    feedback = pylint_output.read()

    # Extracting pylint score
    score = pylint.lint.Run([temp_file_path], exit=False).linter.stats.global_note
    st.write("Pylint score:", score)
    st.text_area("Pylint feedback:", feedback, height=400)

    q_prompt = '''You are python code analyzer whose job is to analyze the code given by user.
    You will be provided with the code and also feedback form the pylint.
    From the feedback given by the pylint suggest the user how to improve the code and its readability to increase pylint score.
    Do not provide the final answer by modifying their code but give them example on what was the issue and how they should fix it.'''

    prompt = ChatPromptTemplate.from_messages(
        [
            (
                "system",
                q_prompt,
            ),
            MessagesPlaceholder(variable_name="messages"),
        ]
    )
    output_parser= StrOutputParser()
    chain = prompt | llm | output_parser
    a=chain.invoke(
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
    st.write(a)

else:
    st.write("Upload a Python file")