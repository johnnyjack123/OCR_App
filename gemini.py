from google import genai

# The client gets the API key from the environment variable `GEMINI_API_KEY`.
client = genai.Client()



def create_prompt(text):
    answer_structure = {"title": "title, choosen by you",
                    "text": "text, which you corrected"
                }
    
    prompt = f"""Correct mistakes in the following text. The text could be in any language, so please try to recognize the 
    language and adapt your answer in this language. The Text will have several mistakes due to its a raw output from an OCR process.
    Your task is to find mistakes in the text, such as some missing letters in word or even find missing words, to ensure the text is 
    grammerly correct and makes sense. If you are not able to get the meaning of a word or a sentence mark it between two **, two on
    beginning, two on ending, so it gets highlightet in an markdown editor.
    In addition create an matching name to the topic of the file in the same language as the file is written. The name should be a short 
    one. It is very important that you only answer in the following json-structur, dont write any other stuff:
    {str(answer_structure)}. Here is the text: {text}. It is really important that your answer ONLY contents the Dictionary, following 
    the structure I sent you. Please dont send any text Outside of the dict. Please do not write any stuff like which tings you changed, 
    just the dictionary.
    """
    return prompt

def correct_with_gemini(text):
    prompt = create_prompt(text)
    response = client.models.generate_content(
        model="gemma-3-27b-it", contents=prompt
    )
    return response.text
