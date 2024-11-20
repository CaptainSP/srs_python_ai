import os
from dotenv import load_dotenv
import google.generativeai as genai
import typing_extensions as typing
import json
from Markdown2docx import Markdown2docx
import gradio as gr

print(gr.__version__)


load_dotenv()


GEMINI_API_KEY = os.getenv('GEMINI_API_KEY')

# Configure the GemAI API with the fetched API key
genai.configure(api_key=GEMINI_API_KEY)

question_asker_instruction = """
### System Instruction for SRS Preparer Agent

**Objective:** The agent's objective is to gather necessary information and generate a one-paragraph system requirements document (SRS).

**Process:**

1. **Initialize**: Start by greeting the user and indicating that you will be asking a set of questions to gather details for the SRS paragraph. Do not forget, this parapgraph will be used to create a simple python code not a big project. The question must be maximum of 2 sentences.

2. **Ask Questions**: You are allowed to ask up to 3 questions to gather required details.
   - Make sure the questions are open-ended to gather detailed responses.
   - Examples of questions:
     - "What is the primary purpose of the system?"
     - "Who are the intended users of this system?"
     - "What are the key functionalities that the system should support?"

3. **Generate SRS Paragraph**:
   - If the agent satisfies the information requirement or reaches the question limit (3 questions):
     - Construct a one-paragraph SRS document using the gathered information.
     - The paragraph should clearly state the system purpose, intended users, and key functionalities.

4. **Return JSON Object**:
   - Format your response as a JSON object in the following structure:
     ```json
     {
       "hasQuestion": boolean,
       "question": string,
       "document": string
     }
     ```
   - `hasQuestion`: Set to `true` if you asked a question.
   - `question`: The question content if hasQuestion is `true`; not necessary if hasQuestion is `false`.
   - `document`: The generated SRS paragraph if hasQuestion is `false`; empty otherwise.

**Example Workflow**:

1. **First iteration**:
   ```json
   {
     "hasQuestion": true,
     "question": "What is the primary purpose of the system?",
   }
   ```

2. **Second iteration** (after receiving user's response):
   ```json
   {
     "hasQuestion": true,
     "question": "Who are the intended users of this system?",
   }
   ```

3. **Third iteration** (after receiving user's response):
   ```json
   {
     "hasQuestion": false,
     "document": "The system is designed to provide an efficient online banking service for individual users and business clients. It allows users to manage accounts, perform transactions, and access financial services securely through an intuitive web interface."
   }
   ```

"""

srs_preparer_instruction = """

### System Instruction for Python Code Writer Agent

**Objective:** The agent's objective is to generate Python code based on a provided SRS document and return the code output enclosed within "::output::" tags.

**Process:**

1. **Receive SRS Document**:
   - Start by receiving the SRS document from the SRS writer agent.
   - This document will describe the system requirements and functionalities to be implemented in Python.

2. **Analyze the SRS Document**:
   - Carefully read and analyze the SRS document to understand the system's purpose, intended users, and key functionalities.
   - Identify the specific features and components that need to be implemented in Python.

3. **Generate Python Code**:
   - Write Python code snippets that fulfill the requirements outlined in the SRS document.
   - Ensure the code is functional, well-documented, and adheres to best coding practices.
   - Verify that the code covers all aspects specified in the SRS document.

4. **Format Output**:
   - Once the code is written and reviewed, format the output to match the specified structure.
   - The code should be enclosed within "::output::" tags for clarity and ease of extraction.

**Example Workflow**:

1. **Receive SRS Document**:
   - The SRS document might specify functionalities such as user authentication, data processing, etc.
   ```
   SRS Document:
   "The system should allow users to register, log in, and process data entries securely."
   ```

2. **Generate Python Code Based on SRS**:
   ```python
   # User registration
   def register_user(username, password):
       # Code to register a user (e.g., save credentials to a database)
       pass

   # User login
   def login_user(username, password):
       # Code to authenticate a user (e.g., verify credentials from a database)
       pass

   # Data processing
   def process_data(data):
       # Code to process data entries securely
       pass
   ```

3. **Format Output**:
   - Enclose the code within "::output::" tags and return it as a plain text structure.
   ```
   ::output::
   def register_user(username, password):
       # Code to register a user (e.g., save credentials to a database)
       pass

   def login_user(username, password):
       # Code to authenticate a user (e.g., verify credentials from a database)
       pass

   def process_data(data):
       # Code to process data entries securely
       pass
   ::output::
   ```

"""

reviewer_instruction = """

---

### System Instruction for Tester Agent

**Objective:** The agent's objective is to evaluate the given code against its output or errors and determine whether a revision is required. The agent should then generate a message providing feedback and return a JSON object indicating the outcome.

**Process:**

1. **Receive Parameters**:
   - Accept two parameters:
     1. `code`: Python code to be evaluated.
     2. `output_or_errors`: Output or error messages resulting from running the code.

2. **Evaluate Code**:
   - Analyze the provided code and the associated output or errors to determine if the code executes correctly or if there are issues that need to be addressed.

3. **Check for Errors or Unexpected Output**:
   - Identify if there are any runtime errors or unexpected outputs that would necessitate a revision of the code.
   - Examples of issues to look for:
     - Syntax errors
     - Logical errors
     - Runtime errors
     - Output mismatches with expected results

4. **Generate Feedback**:
   - Based on the evaluation, generate an appropriate message providing feedback on the code status.
   - Determine if a revision is required:
     - If errors or issues are found, set `revisionRequired` to `true`.
     - If no issues are found, set `revisionRequired` to `false`.

5. **Return JSON Object**:
   - Format the response as a JSON object with the following structure:
     ```json
     {
       "revisionRequired": boolean,
       "message": string
     }
     ```

**Example Workflow**:

1. **Input Parameters**:
   - Example code and output with an error:
     ```python
     code = '''
     def add_numbers(a, b):
         return a + b
     
     result = add_numbers(5, '3')
     print(result)
     '''

     output_or_errors = "TypeError: unsupported operand type(s) for +: 'int' and 'str'"
     ```

2. **Analyze and Evaluate**:
   - Identify the issue with the code and prepare feedback:
     - The error is a TypeError because an integer and a string are added together.

3. **Generate Feedback and Determine Revision Requirement**:
   - Based on the error identified:
     ```json
     {
       "revisionRequired": true,
       "message": "TypeError: unsupported operand type(s) for +: 'int' and 'str'. Please ensure both arguments to the add_numbers function are of the same type."
     }
     ```

By following these instructions, the tester agent will systematically evaluate the provided code and its output or errors, generate appropriate feedback, and return a JSON object indicating whether a revision is required and why.


    """


class QuestionAskerResponseType(typing.TypedDict):
    hasQuestion: bool
    question: str
    document: str
    
class ReviewerResponseType(typing.TypedDict):
    revisionsRequired: bool
    message: str    

class BaseClass:
    def __init__(self, system_instruction, response_type, is_json=True):
        config = genai.GenerationConfig(
            response_mime_type="application/json",
            response_schema=response_type
        )
        if not is_json:
            config = genai.GenerationConfig(
                
            )
        self.sql_model = genai.GenerativeModel(
            model_name="gemini-1.5-flash",
            system_instruction=system_instruction,
            generation_config=config
        )
        self.sql_chat = self.sql_model.start_chat(history=[])

class QuestionAsker(BaseClass):
    def __init__(self, system_instruction=question_asker_instruction):
        super().__init__(system_instruction, QuestionAskerResponseType)
    
    def ask_question(self, user_input=None):
        output = ""
        if user_input is None:
            response = self.sql_chat.send_message("Hello i want to prepare a srs document.")
        else:
            response = self.sql_chat.send_message(user_input)
        print(response.text)    
        response_json = json.loads(response.text)
        question = response_json.get("question")
        output += "CRO: " + question + "\n"
        keep_asking = response_json.get("hasQuestion", False)
        document = response_json.get("document")
        return question, keep_asking, document

class SRSPreparer(BaseClass):
    def __init__(self, system_instruction=srs_preparer_instruction):
        super().__init__(system_instruction, None, is_json=False)
        
    def generate_output(self, output_cro):
        response = self.sql_chat.send_message(output_cro)
        print(response.text)
        response_output = response.text.split("::output::")[1].split("::output::")[0]
        print(response_output)
        return response_output

class Review(BaseClass):
    def __init__(self, system_instruction=reviewer_instruction):
        super().__init__(system_instruction, ReviewerResponseType)
        self.srs_preparer = SRSPreparer()
        
    def generate_output(self, output_cro, needs_review=False, review_message=None, reviewCount=0):
        print(output_cro)
        print(needs_review)
        print(review_message)
        if needs_review:
            output_cro = """
            
            Tester Agent: {review_message}
            
            """
        
        output = self.srs_preparer.generate_output(output_cro)
        
        evulated = None
        evulate_errors = None
        try:
            evulated = eval(output)
        except Exception as e:
            evulate_errors = str(e)
        
        request_str = f"""
        code = ```python
        {output}
        ```
        
        evulated = {evulated}
        
        output_or_errors = {evulate_errors}
        
        """
        
        
        response = self.sql_chat.send_message(request_str)
        response_json = json.loads(response.text)
        review_message = response_json.get("message")
        revision_required = response_json.get("revisionsRequired")
        if revision_required and reviewCount < 3:
            return self.generate_output(output_cro, True, review_message= review_message, reviewCount=reviewCount+1)
        return review_message
        
        
question_asker = QuestionAsker()
def map_gradio_to_gpt_history(gradio_history):
    gpt_history = []
    for message in gradio_history:
        # Extract role and content, ignoring metadata
        if (message["content"] != "" and message["content"] != "None"):
            gpt_message = {
            'role': message['role'],
            'content': message['content']
            }
            gpt_history.append(gpt_message)
    print(gpt_history)        
    return gpt_history

def converse(user_input, chat_history=[]):
    # set history to genai if its not empty
    # if chat_history:
    #     chat_history = map_gradio_to_gpt_history(chat_history)
    if user_input == "":
        return "Please provide an input", chat_history
    
    question, keep_asking, document = question_asker.ask_question(user_input)
    print(document)
    if keep_asking:
        return question
    else:
        srs_reviewer = Review()
        review_message = srs_reviewer.generate_output(document)
        return review_message

interface = gr.ChatInterface(fn=converse, type="messages", examples=["hello", "hola", "merhaba"], title="Echo Bot")

if __name__ == "__main__":
    interface.launch()
