'''This is the main file that app will use and using this app user can upload their
 python file and check for errors and suggestions to improve the code redability'''
import streamlit as st
import pylint.lint
import tempfile
import io

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

    # Run pylint on the temporary file
    # Capture pylint output
    pylint_output = io.StringIO()
    pylint_args = [temp_file_path]
    pylint.lint.Run(pylint_args, exit=False, reporter=pylint.reporters.text.TextReporter(pylint_output))
    print("Hello")
    print(pylint_output)
    pylint_output.seek(0)
    print(pylint_output)
    feedback = pylint_output.read()

    # Extract pylint score
    score = pylint.lint.Run([temp_file_path], exit=False).linter.stats.global_note
    st.write("Pylint score:", score)
    st.text_area("Pylint feedback:", feedback, height=400)

else:
    st.write("Upload a Python file")