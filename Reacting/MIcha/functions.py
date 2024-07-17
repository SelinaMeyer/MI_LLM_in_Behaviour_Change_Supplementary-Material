import gradio as gr
import openai
import pandas as pd
import requests
import os
#from transformers import AutoModelForSequenceClassification, TrainingArguments, AutoTokenizer, TextClassificationPipeline
import transformers
from dotenv.main import load_dotenv
load_dotenv()

valence_classifier = "https://wesjdtmpccksqsve.us-east-1.aws.endpoints.huggingface.cloud"
label_classifier = "https://tg2d2goi7hnreugx.us-east-1.aws.endpoints.huggingface.cloud"
sublabel_classifier = "https://h59vaffmn78wu85a.us-east-1.aws.endpoints.huggingface.cloud"


'''valence_classifier = "https://api-inference.huggingface.co/models/selmey/behaviour-change-valence-german"
label_classifier = "https://api-inference.huggingface.co/models/selmey/behaviour-change-labels-german"
sublabel_classifier = "https://api-inference.huggingface.co/models/selmey/behaviour-change-sublabel-german"'''

headers = {"Authorization": f"Bearer {os.getenv('HF_TOKEN')}",
           "Content-Type": "application/json",}
behaviours = pd.read_csv("resources/Behaviours.csv", sep=";")
openai.api_key = os.getenv('OPENAI_KEY')
    
def enable_buttons(type):
    return (hide_txtbx, show_mrkdwn, enable_btn, enable_btn, enable_btn)

def get_utterance_classifications(payload):
    """
    Function is passed the user utterance and classifies valence, labels and sublabels. 
    Sublabel-classifier is only used, if the returned label of the label-classifier is "Reason". 
    Each classification is logged to the log-file, including all confidence-scores
    """
    valence_classification = requests.post(valence_classifier, headers=headers, json={"inputs" : payload, "options":{"wait_for_model":True}})
    label_classification = requests.post(label_classifier, headers=headers, json={"inputs" : payload, "options":{"wait_for_model":True}})

    valence_json = valence_classification.json()
    label_json = label_classification.json()

    # If using Inference API:
    '''classifications = {"valence": valence_json[0][0]["label"], 
                       "valence_score": valence_json[0][0]["score"],
                       "label": label_json[0][0]["label"],
                       "label_score": label_json[0][0]["score"]}
    if classifications["label"] == "Reason":
        sublabel_classification = requests.post(sublabel_classifier, headers=headers, json={"inputs" : payload, "options":{"wait_for_model":True}})
        sublabel_json = sublabel_classification.json()
        print(sublabel_json)
        classifications["sublabel"] = sublabel_json[0][0]["label"]
        classifications["sublabel_score"] = sublabel_json[0][0]["score"]
    else:
        classifications["sublabel"] = None
        classifications["sublabel_score"] = None
    return classifications  '''

    # if using inference endpoints:
    classifications = {"valence": valence_json[0]["label"], 
                       "valence_score": valence_json[0]["score"],
                       "label": label_json[0]["label"],
                       "label_score": label_json[0]["score"]}
    if classifications["label"] == "Reason":
        sublabel_classification = requests.post(sublabel_classifier, headers=headers, json={"inputs" : payload, "options":{"wait_for_model":True}})
        sublabel_json = sublabel_classification.json()
        #print(sublabel_json)
        classifications["sublabel"] = sublabel_json[0]["label"]
        classifications["sublabel_score"] = sublabel_json[0]["score"]
    else:
        classifications["sublabel"] = None
        classifications["sublabel_score"] = None
        
    return classifications


def get_label(output):
    """
    Looking up the label with the highest score from the classification return, 
    to determine utterance type.
    Also returns the score of the highest level to check for potential 
    ambivalence in case of valence
    This function works for each label-level
    """
    highest_score = max(output[0], key=lambda x: x['score'])
    return highest_score['label'], highest_score['score']

'''def get_and_classify_user_turn(user_utterance):
    """
    Function is passed the user utterance and classifies valence, labels and sublabels. 
    If classifier-confidence for valence-class is lower than 0.8, 
    the user turn is classified as "ambivalent".
    Sublabel-classifier is only used, if the returned label of the label-classifier is "Reason". 
    Each classification is logged to the log-file, including all confidence-scores
    """
    
    sublabel = None
    sublabel_score = 0
    
    output_valence = valence_pipe.predict(user_utterance)
    valence, val_score = get_label(output_valence)
    
    output_label = label_pipe.predict(user_utterance)
    label, label_score = get_label(output_label)
    
    if(label == "Reason"):
        output_sublabel = sublabel_pipe.predict(user_utterance)
        sublabel, sublabel_score = get_label(output_sublabel)

    classifications = {"valence": valence, 
                       "valence_score": val_score,
                       "label": label,
                       "label_score": label_score,
                       "sublabel": sublabel,
                       "sublabel_score": sublabel_score}
    
    # For debugging purposes
    print(classifications)
    
    return classifications'''

def get_appropriate_action(valence, label, most_common, previous_turn_type, sublabel=None):
    chosen_behaviour = pd.DataFrame()
    
    appropriate_behaviours = behaviours[behaviours["Valence"] == valence].copy()
    appropriate_behaviours = appropriate_behaviours[appropriate_behaviours["Action"] != most_common].copy()
    #print(f"Häufigste Action {most_common} wird herausgefiltert")
    if sublabel != None:
        appropriate_behaviours = appropriate_behaviours[appropriate_behaviours["Sublabel"] == sublabel].copy()
    else: 
        appropriate_behaviours = appropriate_behaviours[appropriate_behaviours["Label"] == label].copy()
    if (previous_turn_type == "Question"):
        try: 
            appropriate_behaviours = appropriate_behaviours[appropriate_behaviours["Action Type"] != "Question"].sample(1)
            chosen_behaviour = appropriate_behaviours.sample(1)
        except:
            chosen_behaviour = behaviours[behaviours["Action"] == "Continuing the Paragraph"].sample(1)
            
    # incorporate link to state tracker here (i.e. starting with a simple count on how many times each behaviour 
    # has been used in a session and disqualify those that have already been used a lot
    else:
        chosen_behaviour = appropriate_behaviours.sample(1)
    #print(chosen_behaviour["Action"].values[0])
    return chosen_behaviour["Action"].values[0], chosen_behaviour["Description"].values[0]

    
def get_bot_message(context_utterances, topic, action, description):
    messages = []
    prompt = {"role": "system", "content": f"""You are a therapist and help the user with their goal \"{topic}\". 
              Never talk about yourself in the following and concentrate fully on the user. 
              Do not give active tips. If the user is talking about another topic, don't respond and lead them back to the {topic}. 
              Always speak in the second person singular. You use the conversation strategy \"{action}\.". 
              Definition of {action}: \"{description}\" Halte dich möglichst kurz."""}
    messages.append(prompt)
    messages += context_utterances
    # print(f"Prompt passed to GPT: \n {messages}")
    # add tenacity retry: https://tenacity.readthedocs.io/en/latest/
    response = openai.ChatCompletion.create(model="gpt-4", 
                                        messages=messages,
                                        temperature=0.7,
                                        max_tokens=100,
                                        top_p=1, 
                                        frequency_penalty=0.0,
                                        presence_penalty=0.0,
                                        stop=["?"])
    '''if (str(prompt).find(response['choices'][0]['message']['content']) != -1):
        print(response['choices'][0]['message']['content'])
        print("Output contains copy of prompt. Generating again") 
        output = get_bot_turn(action, description, context_utterances)
    output = edit_output(response['choices'][0]['message']['content'])'''
    output = response['choices'][0]['message']['content']
    return output

def get_vanilla_message(context_utterances, topic):
    messages = []
    prompt = {"role": "system", "content": f"""You are a therapist and help the user with their goal \"{topic}\". 
              Never talk about yourself in the following and concentrate fully on the user. 
              Do not give active tips. If the user is talking about another topic, don't respond and lead them back to the {topic}. 
              Always speak in the second person singular. Keep it as short as possible."""}
    messages.append(prompt)
    messages += context_utterances
    #print(f"Prompt passed to GPT: \n {messages}")
    # add tenacity retry: https://tenacity.readthedocs.io/en/latest/
    response = openai.ChatCompletion.create(model="gpt-4", 
                                        messages=messages,
                                        temperature=0.7,
                                        max_tokens=100,
                                        top_p=1, 
                                        frequency_penalty=0.0,
                                        presence_penalty=0.0,
                                        stop=["?"])
    output = response['choices'][0]['message']['content']
    return output

def get_no_system_prompt_message(context_utterances):
    messages = []
    prompt = {"role": "system", "content": ""}
    messages.append(prompt)
    messages += context_utterances
    #print(f"Prompt passed to GPT: \n {messages}")
    # add tenacity retry: https://tenacity.readthedocs.io/en/latest/
    response = openai.ChatCompletion.create(model="gpt-4", 
                                        messages=messages,
                                        temperature=0.7,
                                        max_tokens=100,
                                        top_p=1, 
                                        frequency_penalty=0.0,
                                        presence_penalty=0.0,
                                        stop=["?"])
    output = response['choices'][0]['message']['content']
    return output

def get_summary(context_utterances):
    """
    Takes in all user utterances in the conversation so far and 
    passes them to GPT-3 for summarization. Returns the GPT-3 output
    """
    messages = []
    prompt = {"role": "system", "content":"Du bist ein Therapeut und hattest ein Coaching-Gespräch mit einem Klienten. Fasse die wichtigsten Punkte der Aussagen des Klienten zusammen und gib sie in der zweiten Person singular wieder. Stelle keine Fragen und gehe nicht auf die letzte Nachricht des Klienten ein. Fasse nur die bisherigen Aussagen des Klienten zusammen."}
    messages.append(prompt)
    #print(prompt)
    messages += context_utterances
    response = openai.ChatCompletion.create(model="gpt-4", 
                                        messages=messages,
                                        temperature=0.7,
                                        max_tokens=200,
                                        top_p=1, 
                                        frequency_penalty=0.0,
                                        presence_penalty=0.0)
    reply_start = "Lass mich unser bisheriges Gespräch zusammenfassen. "
    reply_end = " Habe ich noch etwas vergessen?"
    return reply_start + response['choices'][0]['message']['content'] + reply_end

enable_btn = gr.Button.update(interactive=True)
disable_btn = gr.Button.update(interactive=False)
show_btn = gr.Button.update(visible=True)
hide_btn = gr.Button.update(visible=False)
show_txtbx = gr.Textbox.update(visible=True)
hide_txtbx = gr.Textbox.update(value= "", visible=False)
disable_txtbx = gr.Textbox.update(interactive=False)
enable_txtbx = gr.Textbox.update(interactive=True)
show_drpdwn = gr.Dropdown.update(visible=True)
hide_drpdwn = gr.Dropdown.update(visible=False)
show_lkrt = gr.Slider.update(visible=True)
hide_lkrt = gr.Slider.update(visible=False)
show_mrkdwn = gr.Markdown.update(visible=True)
hide_mrkdwn = gr.Markdown.update(visible=False)
show_block_part = gr.update(visible=True)
hide_block_part = gr.update(visible=False)
show_chtbt = gr.Chatbot.update(visible=True)
hide_chtbt = gr.Chatbot.update(visible=False)