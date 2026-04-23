# Ezer PDF Extractor - extractor.py
# -------------------------------------------------------
# PURPOSE: This file is the first step in Ezer's pipeline.
# It takes a denial letter PDF, reads the text inside it,
# and sends that text to Claude AI to extract key fields.
# -------------------------------------------------------

# IMPORT STATEMENTS
# Think of imports like opening your toolbox before starting work.
# Each import brings in a specific tool we need.

import fitz  
# fitz is the PyMuPDF library.
# PyMuPDF is a tool that can open PDF files and read the text inside them.
# Just like how you open a PDF in Adobe Reader, fitz opens it in Python.

import pdfplumber  
# pdfplumber is another PDF reading tool.
# It is especially good at reading tables inside PDFs.
# We import it here for future use when we need table data.

import os  
# os is Python's built-in tool for talking to your operating system.
# We use it here specifically to read your API key from the .env file.
# os.getenv("ANTHROPIC_API_KEY") means "go find this variable in my environment".

from anthropic import Anthropic
# This imports the official Anthropic Python library.
# It gives us a clean way to send messages to Claude AI and receive responses.
# Think of it as the phone we use to call Claude.

from dotenv import load_dotenv
# load_dotenv is a function from the python-dotenv library.
# Its job is to read your .env file and load everything inside it
# into memory so other parts of the code can access it.
# Without this, os.getenv("ANTHROPIC_API_KEY") would return nothing
# because Python would not know where to look for it.

load_dotenv("backend/.env")
# This actually runs the load_dotenv function.
# "backend/.env" is the path to your .env file.
# This must be called BEFORE we create the Anthropic client below,
# because the client needs the API key to be in memory first.
# We call it here in extractor.py as well as in main.py
# because extractor.py may sometimes run independently.


# -------------------------------------------------------
# CLIENT SETUP
# -------------------------------------------------------

client = Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))
# This creates our connection to Claude AI.
# os.getenv reads your API key from the .env file safely.
# We store this connection in a variable called 'client'.
# Every time we want to talk to Claude, we use this client.


# -------------------------------------------------------
# FUNCTION 1: extract_text_from_pdf
# -------------------------------------------------------

def extract_text_from_pdf(pdf_path: str) -> str:
    """
    WHAT THIS FUNCTION DOES:
    Opens a PDF file and reads all the text inside it.
    
    ANALOGY:
    Think of this like a person reading a printed letter 
    and typing out everything they see into a text document.
    
    INPUT:
    pdf_path = the location of the PDF file on your Mac
    Example: "/Users/badalsatapathy/Documents/denial_letter.pdf"
    
    OUTPUT:
    Returns a long string containing all the text from the PDF.
    If the PDF has 2 pages, it returns text from both pages combined.
    """
    
    text = ""
    # We start with an empty string.
    # We will keep adding text to this as we read each page.
    
    try:
        # 'try' means: attempt the following code.
        # If something goes wrong, do not crash — go to 'except' instead.
        
        doc = fitz.open(pdf_path)
        # fitz.open opens the PDF file, just like double-clicking it.
        # 'doc' now holds the entire PDF in memory.
        
        for page in doc:
            # 'for page in doc' means: go through each page one by one.
            # If the PDF has 4 pages, this loop runs 4 times.
            
            text += page.get_text()
            # page.get_text() reads all the text on that one page.
            # += means "add this to whatever text we already have".
            # So we are building up the full text page by page.
        
        doc.close()
        # Always close the file when you are done reading it.
        # Like closing a book after reading it.
        
    except Exception as e:
        # If anything went wrong above, we land here.
        # 'e' contains the error message explaining what went wrong.
        print(f"PyMuPDF extraction failed: {e}")
        # We print the error so we can see it in Terminal and debug it.
    
    return text.strip()
    # .strip() removes any extra spaces or blank lines at the start and end.
    # return sends the extracted text back to whoever called this function.


# -------------------------------------------------------
# FUNCTION 2: extract_fields_with_claude
# -------------------------------------------------------

def extract_fields_with_claude(pdf_text: str) -> dict:
    """
    WHAT THIS FUNCTION DOES:
    Takes the raw text from the denial letter and sends it to Claude AI.
    Claude reads it and pulls out the specific fields Ezer needs.
    
    ANALOGY:
    Imagine giving a denial letter to a very smart paralegal.
    You say: find me the insurer name, the policy number, 
    the rejection reason, and the date. 
    Claude is that paralegal.
    
    INPUT:
    pdf_text = the raw text we extracted in Function 1
    
    OUTPUT:
    Returns a dictionary — think of it as a table with 
    labels on the left and values on the right.
    Example:
    INSURER: HDFC ERGO
    CCN: RC-HS25-15034871
    REJECTION_REASON: indication for hospitalisation cannot be established
    """
    
    prompt = f"""
You are Ezer, an AI assistant that helps policyholders understand 
insurance denial letters in India.

Read this insurance denial letter text carefully and extract 
the following information:

1. Insurer name (e.g. HDFC ERGO, Star Health, ICICI Lombard)
2. Policy number or HDFC ERGO ID
3. CCN number (Claim Control Number or reference number)
4. Rejection reason (exact words from the letter)
5. Date of denial
6. Hospital name (if mentioned)
7. Patient name (if mentioned)
8. Denial type (Cashless or Reimbursement)

Return your answer in this exact format:
INSURER: [insurer name]
POLICY_NUMBER: [policy number]
CCN: [CCN or reference number]
REJECTION_REASON: [exact rejection reason]
DATE: [date of denial]
HOSPITAL: [hospital name or NOT FOUND]
PATIENT: [patient name or NOT FOUND]
DENIAL_TYPE: [Cashless or Reimbursement or NOT FOUND]

If you cannot find a field, write NOT FOUND for that field.

Here is the denial letter text:

{pdf_text}
"""
    # This is the instruction we give Claude.
    # The f" at the start means this is an f-string —
    # Python will automatically insert {pdf_text} into the message.
    # So Claude receives our instructions AND the actual denial letter text.

    message = client.messages.create(
        model="claude-sonnet-4-6",
        # Which Claude model to use. Sonnet is fast and accurate.
        max_tokens=1000,
        # Maximum length of Claude's response.
        # 1000 tokens is roughly 750 words — more than enough for our fields.
        messages=[
            {"role": "user", "content": prompt}
            # We send our prompt as a user message to Claude.
            # role: "user" means this is coming from the person asking.
            # content: prompt is the actual message text.
        ],
    )
    
    response_text = message.content[0].text
    # message.content is a list of response blocks from Claude.
    # [0] means take the first block.
    # .text gets the actual text content from that block.
    # This gives us Claude's full response as a string.
    
    fields = {}
    # We create an empty dictionary to store our extracted fields.
    # A dictionary in Python works like this:
    # fields["INSURER"] = "HDFC ERGO"
    # fields["CCN"] = "RC-HS25-15034871"
    
    for line in response_text.strip().split('\n'):
        # We go through Claude's response line by line.
        # .split('\n') breaks the response at every new line.
        # So each line like "INSURER: HDFC ERGO" becomes one item.
        
        if ':' in line:
            # We only process lines that have a colon in them.
            # This filters out any blank lines or unexpected text.
            
            key, value = line.split(':', 1)
            # We split the line at the first colon.
            # "INSURER: HDFC ERGO" becomes:
            # key = "INSURER"
            # value = " HDFC ERGO"
            # The '1' means split only at the FIRST colon,
            # in case the value itself contains a colon.
            
            fields[key.strip()] = value.strip()
            # .strip() removes extra spaces.
            # We store it in our dictionary.
            # fields["INSURER"] = "HDFC ERGO"
    
    return fields
    # Return the completed dictionary to whoever called this function.


# -------------------------------------------------------
# FUNCTION 3: process_denial_letter
# -------------------------------------------------------

def process_denial_letter(pdf_path: str) -> dict:
    """
    WHAT THIS FUNCTION DOES:
    This is the main function that Ezer calls.
    It combines Function 1 and Function 2 into one clean step.
    
    ANALOGY:
    This is the manager function. It does not do the work itself.
    It calls Function 1 to read the PDF,
    then calls Function 2 to extract the fields,
    then returns the final result.
    
    INPUT:
    pdf_path = location of the denial letter PDF on your Mac
    
    OUTPUT:
    A complete dictionary with all extracted fields from the letter.
    """
    
    print(f"Processing: {pdf_path}")
    # print() shows a message in your Terminal.
    # This helps you see what is happening when you run the code.
    # f"Processing: {pdf_path}" inserts the actual file path into the message.
    
    pdf_text = extract_text_from_pdf(pdf_path)
    # Call Function 1 to read the PDF.
    # Store the extracted text in pdf_text.
    
    if not pdf_text:
        # If pdf_text is empty, the PDF could not be read.
        # This might happen if the PDF is corrupted or password protected.
        return {"error": "Could not extract text from PDF"}
        # Return an error message instead of crashing.
    
    print(f"Extracted {len(pdf_text)} characters from PDF")
    # len(pdf_text) counts how many characters were extracted.
    # This helps us confirm the PDF was read successfully.
    
    fields = extract_fields_with_claude(pdf_text)
    # Call Function 2 to send the text to Claude.
    # Store Claude's extracted fields in the fields dictionary.
    
    fields["RAW_TEXT"] = pdf_text[:500]
    # We also store the first 500 characters of raw text.
    # [:500] means take only the first 500 characters.
    # This is useful for debugging — seeing what the PDF actually contained.
    
    return fields
    # Return the complete fields dictionary.
    # This is what the rest of Ezer will use.