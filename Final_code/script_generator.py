import google.generativeai as genai
import json


# Replace with your Gemini-1.5-Flash API key
API_KEY = "AIzaSyCmwU30Y5Y4En8hLIR51710YEKbUIKLMmo"

# Configure the API key
genai.configure(api_key=API_KEY)


def generate_script(topic:str)->str:
    # Define the initial prompt
    if topic=="" or not topic:
        raise Exception("Topic not provided properly. Expected a string of aleast a word but found {}.".format(topic if topic else '"None"'))
    prompt = (
        """You are a seasoned content writer for a YouTube Shorts channel, specializing in facts videos. 
        Your facts shorts are concise, each lasting less than 60 seconds (approximately 150 words). 
        They are incredibly engaging and original. When a user requests a specific type of facts short, you will create it.

        For instance, if the user asks for:
        Weird facts
        You would produce content like this:

        Weird facts you don't know:
        - Bananas are berries, but strawberries aren't.
        - A single cloud can weigh over a million pounds.
        - There's a species of jellyfish that is biologically immortal.
        - Honey never spoils; archaeologists have found pots of honey in ancient Egyptian tombs that are over 3,000 years old and still edible.
        - The shortest war in history was between Britain and Zanzibar on August 27, 1896. Zanzibar surrendered after 38 minutes.
        - Octopuses have three hearts and blue blood.

        You are now tasked with creating the best short script based on the user's requested type of 'facts'.

        Keep it brief, highly interesting, and unique.

        Stictly output the script in a JSON format like below, and only provide a parsable JSON object with the key 'script'.

        # Output
        {"script": "Here is the script ..."}
        """
    )

    # Start a chat session with the model
    model = genai.GenerativeModel(model_name="models/gemini-pro")
    chat = model.start_chat()

    # Send the system prompt
    chat.send_message(prompt)

    # Send the user's topic as a message
    response = chat.send_message(topic)

    # Extract the generated content
    content = response.text

    # Handle edge cases where the JSON is not properly formatted
    json_start_index = content.find("Body:")
    content = content[json_start_index+len("Body:") :].replace("*","").replace("\n", "")
    script = content

    return script

if __name__ == "__main__":
    topic = r"create an ad video for saree sale for diwali with 50% Off on all purchases."
    # topic = ""
    script = generate_script(topic)
    print("Generated Script:")
    print(script)