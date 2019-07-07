# Step Into the AI Era: Chatbots that know if you are angry

In this workshop, we will build a chatbot that will ask for an individual's contact details (compliant to GDPR) and for feedback for an event that they may have attended.


## Install Rasa and set up the environment

Open a terminal.

Clone this repo from Github:

`git clone https://github.com/Cheukting/rasa_workshop.git`

Enter the directory:

`cd rasa_workshop`

Create a new [conda](https://docs.conda.io/projects/conda/en/latest/user-guide/tasks/manage-environments.html) or [virtualenv](https://github.com/pyenv/pyenv-virtualenv) environment.

`conda create --name rasa_workshop`

or

`pyenv virtualenv <version> rasa_workshop`

where `<version>` is the python version (Rasa require python>=3.5)

> Notes:
> If virtualenv is too difficult to set up (e.g. using Windows), you can use [venv](https://docs.python.org/3/library/venv.html) instead

Install the requirements:

`pip install -r requirement.txt`

> Notes:
> If you are using conda and have problems with pip install, you may try installing individual packages using [conda-forge](https://conda-forge.org/docs/user/introduction.html)

## Create a new project

Creat a new directory (you could replace `my_chatbot` to any name you like):

`mkdir my_chatbot`

Go to the directory:

`cd my_chatbot`

Initiate a project:

`rasa init --no-prompt`

Rasa will create a list of files for you, but we mostly care about the following:

* `actions.py` : code for your custom actions
* `config.yml` : configuration of your NLU and Core models
* `data/nlu.md` : your NLU training data
* `data/stories.md` : your stories
* `domain.yml` : your assistant’s domain

We will explain what they are and how to set them up in this workshop.

##  NLU and Pipeline setup

First we will need to train the NLU, which is a natural language processing tool for intent classification and entity extraction.

Open `data/nlu.md` with the text editor or IDE of your choice.

In the file, we see that some examples for different intents are already supplied. The intents are defined by lines starting with `##`. Intents are a way to group messages with the same meaning, and example messages are provided below each intent. NLU's job will be to predict the correct intent for each new message your user sends your chatbot.

For our use case, since we will be doing sentiment analysis using [Natural Language Toolkit (NLTK)](https://www.nltk.org/), we can delete the sections for `mood_great` and `mood_unhappy`.

Feel free to add more examples for the other intents: the more examples, the better the understanding of NLU and your chatbot.

Collecting user's data is one of the goals of our bot. To enable this, we need to add more intents for data capturing, such as: `self_intro`, `give_email`, `give_tel`.

Here are some examples for the additional intents, please feel free to add more:

```
## intent:self_intro
- I am [Mary](PERSON)
- My name is [Anna](PERSON)

## intent:give_email
- my email is [joe@aol.com](email)
- [123@123.co.uk](email)

## intent:give_tel
- my number is [01234567890](tel)
- contact me at [07896234653](tel)
```

We can see that below the intents the examples have a slightly different structure than before. That is because each example contains an entity, which is a specific part of the text that needs to be identified. An entity has two terms and these function as a key-value pair: `[entity](entity name)`. Often we would like the named entity to map to more than one entity and thus we can give multiple examples for each entity name, as we do above. We now have three entities: `PERSON`, `email` and `tel`.

`PERSON` is a entity provided by SpaCy. To help capture `email` and `tel`, we will also use [regex](https://www.rexegg.com/). To do so, put this in `nlu.md` as well:

```
## regex:email
- [\w-]+@([\w-]+\.)+[\w-]+

## regex:tel
- (0)([0-9][\s]*){10}
```

If you are a regex expert, you can change it to a better expression. 😉

After that, we have to setup the [NLP pipeline](http://rasa.com/docs/rasa/nlu/choosing-a-pipeline/), which can be done by editing `config.yml`. This configuration file defines the NLU and Core components that your model will use.  

In `config.yml` change the `supervised_embeddings` to `pretrained_embeddings_spacy` so that we use the pretrained SpaCy embedding pipeline. You can find out more about NLU pipelines [here](https://rasa.com/docs/rasa/nlu/choosing-a-pipeline/#choosing-a-pipeline).

## Train and test NLU

The following 2 commands download and set up the Spacy model that we will be using. In the terminal:

`python -m spacy download en_core_web_md`

`python -m spacy link en_core_web_md en`

Then we tell rasa to train the NLU.

`rasa train nlu`

The trained model should be saved under `models/`.

 Now we can test the NLU model that we trained:

`rasa shell nlu`

After loading (may take a moment) you can type in messages and see the prediction that the NLU  returns. If you are not happy with the result, you can go back and add more examples to the `nlu.md` and then train the NLU again (`rasa train nlu`). Repeat the training and testing until you are happy.

*Congratulations, you have complete 1/3 of the workshop, feel free to take a 3 mins break*

Now we will train our chatbots how to respond to messages. This is called dialogue management, and is handled by Rasa Core.

## Planning the conversation

In this part, we will write the plan for the flow of the conversation. It will be written in `data/stories.md`. The flow of the conversation will be broken into 3 parts:

1. greeting -> ask if user has attended event:

    yes ->  (go to part 2.a)

    no -> (go to part 2.b)

2. a) ask for feedback -> ask if we can contact them

   b) encourage them to go next year -> ask if we can contact them

   yes ->  (go to part 3.a)

   no -> (go to part 3.b)

3. a) contact form and see you next year

   b) see you next year

If you open and edit `data/stories.md`, you can see that there are example stories already written. The story `## say goodbye` enables the user to end the conversation at anytime. Keep `## say goodbye` and delete the rest of the file. We will write our own stories for the conversation flow outlined above.

The skeleton for the 3 parts of our conversation flow looks like this:

```
## greetings
* greet
  <something>
> check ask experience

## I have been to the event
> check ask experience
* affirm
  <something>
> check ask contact

## Not been to the event
> check ask experience
* deny
  <something>
> check ask contact

## get contact info
> check ask contact
* affirm
  <something>

## do not contact me
> check ask contact
* deny
  <something>
```

 We will fill in `<something>` later. The lines with `>`, e.g. `> check ask experience`, are a checkpoints which link the different parts of the stories together. So instead of creating multiple dialogue stories where users answer the questions differently, we can use checkpoints to map different paths.

Line starting with `*` are for when our chatbot recognises an intent. For example, `* affirm` will trigger when the NLU predicts an `affirm` intent.

## Domain and templates

We also need to tell the chatbot what action to take and what to answer when it reaches certain points in the conversation. To do this, we define a `Domain` for our chatbot, which is our chatbot's 'universe'. Your chatbot's domain specifies the `intents`, `entities`, `slots`, and `actions` your bot needs to know about. We will define these further below. The domain is recorded in `domain.yml`. If you open up `domain.yml`, you can see the `DefaultDomain`. You can delete the contents of that file and then we'll create a domain for our chatbot.

The NLU model has defines the `intents`, and `entities` which need to be in the bots domain.

#### Adding intents

Remember the intents we defined in `nlu.md`? Let's put them in `domain.yml`:

```
intents:
- greet
- goodbye
- affirm
- deny
- self_intro
- give_email
- give_tel
```

#### Adding entities

Similarly, add the entities that we defined in `nlu.md`:

```
entities:
- PERSON
- email
- tel
```

We will also be adding `slots` and `actions` to our bot's domain. `Slots` store information that we want to keep track of in a conversation. `Actions` are things your bot can do, including:
  respond to a user,
  make an external API call,
  query a database, or
  just about anything!

We'll also be adding optional additional information to our bot's domain, including `forms`and `templates`.

#### Adding slots

Slots enable us to store information about a conversation and the user having that conversation. For our chatbot, we would like to gather each user's `name`, `email` and `tel` number and user `feedback`:

```
slots:
  name:
    type: unfeaturized
  email:
    type: unfeaturized
  tel:
    type: unfeaturized
  feedback:
      type: unfeaturized
```

`unfeaturized` means that this information does not affect the flow of the conversation.


#### Adding forms

To capture a user's contact information and feedback, we will use form actions. Let's define them like this for now:

```
forms:
  - experience_form
  - contact_form
```

#### Adding actions

There are two main kinds of actions for our chatbot. The first are Utterance Actions, which send a message to a user and start with `utter_`. The second are Custom Actions, which run code you have written to enable your chatbot to perform specific custom actions. Our form actions are a type of custom action, and we will write the code for those actions further in the workshop.

For now, we will define our `utter` actions.

```
actions:
- utter_greet
- utter_happy
- utter_goodbye
- utter_thanks
- utter_ask_contact
- utter_ask_experience
- utter_ask_name
- utter_ask_email
- utter_ask_tel
- utter_ask_feedback
- utter_submit
- utter_wrong_email
- utter_wrong_tel
- utter_encourage
```

These are the different utterances of dialog for our chatbot. You will see them come into place as we complete our chatbot. You may come back and change the `utter` actions later if you want.

#### Adding templates

Now we will add Utterance Templates, which are the messages our chatbot will send to the user. We need to define the response text for each `utter` action listed in our domain. If we have more than one response text for an `utter` action, then one of them will be chosen at random for the chatbot's response. It's good design to have multiple responses so as to generate variety in your bot's dialogue.

For the utterance templates, the utterance can be used directly as an action.

```
templates:
  utter_greet:
  - text: "Hello! My name is Alex."

  utter_happy:
  - text: "Great!"
  - text: "Awesome!"

  utter_goodbye:
  - text: "Bye!"
  - text: "Have a nice day!"

  utter_thanks:
  - text: "Thank you for chatting, please feel free to talk to me again."

  utter_ask_contact:
  - text: "Do you want to be contacted regarding EuroPython next year?"

  utter_ask_experience:
  - text: "Have you been to EuroPython this year?"

  utter_ask_name:
  - text: "What's your name?"

  utter_ask_email:
  - text: "What's your email address?"

  utter_ask_tel:
  - text: "What's your contact number?"

  utter_ask_feedback:
  - text: "So, how was your experience in EuroPython?"

  utter_submit:
  - text: "You information collected will not be shared to 3rd party."

  utter_wrong_email:
  - text: "This doesn't look like an email..."

  utter_wrong_tel:
  - text: "This doesn't look like a phone number..."

  utter_encourage:
  - text: "It's a shame, we would like to meet you there next year."

```

Please feel free to change the response texts and add more response texts for each `utter` action.

For now, we are done with `domain.yml`; let's go back to `stories.md`

## Finishing the stories

Now we know what's available in the `domain`, let's fill in the `<something>` in the skeleton we had before:

```
## greetings
* greet
- utter_greet
- utter_ask_experience
> check ask experience

## I have been to the event
> check ask experience
* affirm
- utter_happy
- experience_form
- form{"name": "experience_form"}
- form{"name": null}
- utter_ask_contact
> check ask contact

## Not been to the event
> check ask experience
* deny
- utter_encourage
- utter_ask_contact
> check ask contact

## get contact info
> check ask contact
* affirm
- utter_happy
- contact_form
- form{"name": "contact_form"}
- form{"name": null}
- utter_thanks

## do not contact me
> check ask contact
* deny
- utter_thanks
```

Notice that some of our actions start with `form`, these are the form actions that we defined in our domain. For example, `- form{"name": "experience_form"}` states to use the action form `experience_form`. After we are done, it will be reset to `null` to continue the conversation.

Let's set up our form actions now.

## Form actions

Now we come to the fun part! Our form actions are custom actions that we are using to collect the user's information. Before we do anything, first we need to add the `FormPolicy` to the configuration. Go to `config.yml` and under `policies` add:

```YAML
  - name: FormPolicy
```

When a custom action is predicted in our dialogue, Core will call an endpoint we specify in `endpoint.yml`. This endpoint should be a webserver that reacts to this call, runs the code for the custom action, and optionally returns information to modify the dialogue state.


To enable the action endpoint, go to `endpoint.yml` and uncomment the following:

```YAML
 action_endpoint:
   url: "http://localhost:5055/webhook"
```

The custom action scripts we write will be hosted on a server setup by Rasa at port 5055.

Open `actions.py`. From the default file, uncomment the following lines:

```python
from typing import Any, Text, Dict, List

from rasa_sdk import Action, Tracker
from rasa_sdk.executor import CollectingDispatcher
```

These import an object that is used to communicate with the Rasa framework. On top of that, we also need:

```python
from rasa_sdk.forms import FormAction
```

This additional import allows us to write custom form action classes which inherit from `FormAction`.

#### ExperienceForm

Let's define the `experience_form`, adding it below our imports in `actions.py`:

```python
class ExperienceForm(FormAction):
    """Form action to capture user experience"""

    def name(self):
        # type: () -> Text
        """Unique identifier of the form"""
        return "experience_form"

    @staticmethod
    def required_slots(tracker):
        # type: () -> List[Text]
        """A list of required slots that the form has to fill
           this form collect the feedback of the user experience"""
        return ["feedback"]

    def submit(self, dispatcher, tracker, domain):
        # type: (CollectingDispatcher, Tracker, Dict[Text, Any]) -> List[Dict]
        """Define what the form has to do
           after all required slots are filled.
           Generates sentiment analysis
           using the user's feedback"""
        return []

    def slot_mappings(self):
        # type: () -> Dict[Text: Union[Dict, List[Dict]]]
        """A dictionary to map required slots to
            - an extracted entity
            - intent: value pairs
            - a whole message
            or a list of them, where a first match will be picked"""
        return {"feedback": [self.from_text()]}

```

This form will collect the text the user inputs in the `feedback` slot. When the form is triggered, the action `utter_ask_feedback` is activated and the user input after that will be captured. Have a look at the doc string of each methods and make sure you understand what each function does, we will use them again in the more complicated `contact_form`.

#### ContactForm

Similarly, we define `contact_form`:

```python
class ContactForm(FormAction):
    """Form action to capture contact details"""

    def name(self):
        # type: () -> Text
        """Unique identifier of the form"""
        return "contact_form"

    @staticmethod
    def required_slots(tracker):
        # type: () -> List[Text]
        """A list of required slots that the form has to fill"""
        return ["name", "email", "tel"]

    def submit(self, dispatcher, tracker, domain):
        # type: (CollectingDispatcher, Tracker, Dict[Text, Any]) -> List[Dict]
        """Define what the form has to do
           after all required slots are filled"""

        dispatcher.utter_template('utter_submit', tracker)
        return []

    def slot_mappings(self):
        # type: () -> Dict[Text: Union[Dict, List[Dict]]]
        """A dictionary to map required slots to
            - an extracted entity
            - intent: value pairs
            - a whole message
            or a list of them, where a first match will be picked"""

        return {"name": [self.from_entity(entity="PERSON",
                                          intent="self_intro"),
                         self.from_text()],
                "email": [self.from_entity(entity="email"),
                          self.from_text()],
                "tel": [self.from_entity(entity="tel"),
                        self.from_text()]}

```

This time the slot mapping is more complicated, using `from_entity` we can specify the slot to be fill with a certain recognised entity / intent instead of free text. However, we put `from_text` in the list after `from_entity` as a fail safe catching the information if the user's input is not recognisable.

#### Validating slots

For the `email` and `tel` the user input, we want to validate them. To do so, we add more methods to our `ContactForm` class:

```python
@staticmethod
def is_email(string: Text) -> bool:
    """Check if a string is valid email"""
    pattern = re.compile("[\w-]+@([\w-]+\.)+[\w-]+")
    return pattern.match(string)

@staticmethod
def is_tel(string: Text) -> bool:
    """Check if a string is valid email"""
    pattern_uk = re.compile("(0)([0-9][\s]*){10}")
    pattern_world = re.compile("^(00|\+)[\s]*[1-9]{1}([0-9][\s]*){9,16}$")
    return pattern_uk.match(string) or pattern_world.match(string)

def validate_email(
     self,
        value: Text,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: Dict[Text, Any],
    ) -> Optional[Text]:
    if self.is_email(value):
        return {"email": value}
    else:
        dispatcher.utter_template('utter_wrong_email', tracker)
        # validation failed, set this slot to None, meaning the
        # user will be asked for the slot again
        return {"email": None}

def validate_tel(
     self,
        value: Text,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: Dict[Text, Any],
    ) -> Optional[Text]:
    if self.is_tel(value):
        return {"tel": value}
    else:
        dispatcher.utter_template('utter_wrong_tel', tracker)
        # validation failed, set this slot to None, meaning the
        # user will be asked for the slot again
        return {"tel": None}
```

Notice we have used `re` module, so we have to import it:

```python
import re
```

Also, we have use one more `typing`: `Optional`. We have to import it as well:

```python
from typing import Any, Text, Dict, List, Optional
```

Here we have defined 2 helper methods: `is_email` and `is_tel` which will use Regex to check if the input matches an email format and phone number format. We also have validate methods for each of them. If the format does not match what we expected, we will reset the slot to `None` and use an `utter` action to ask again.

## Train and test your Chatbots

Now it's time to train and test our chatbot!! 🎉

To train the bot using the settings that we have set up, in the terminal run:

```
rasa train
```

When it is done, you can see that a new model is saved. Now let's try it out. First, make sure the server hosting the action script is up and running:

```
rasa run actions
```

Now the server is running, let's open an other terminal and then type:

```
rasa shell --endpoint endpoint.yml
```
(Note: you may need to activate the environment you created for the workshop.)

The command above will call Rasa to run the chatbot with the endpoint. Now you can talk to it!

#### Restart the action server

In you have made changes to your `actions.py` and want to start the server with the new script, you have to kill the server that is already running. Follow the following steps to kill the server:

1. find the `PID` of the process:
```
sudo lsof -i tcp:5055
```
2. kill the process:
```
kill -9 <PID>
```
fill in the `<PID>` with the  `PID` you found in step 1.

*You have complete 2/3 of the workshop! Yes, there's more. Feel free to take a 3 mins break*

## Using NLTK to analyse the sentiment

Here comes the fun part!! We will use NLTK, a suite of libraries for natural language processing, to analyse the sentiment of the `feedback` so we know if the feedback is positive or negative.

Before we add code in the action script, let's add 2 more slots in our `domain.yml`:

```YAML
feedback_class:
  type: unfeaturized
feedback_score:
  type: unfeaturized
```

This 2 slots will store the result of the analysis. Then head to `actions.py`. First we have to import and download the resources in NLTK:

```python
import nltk
nltk.download('vader_lexicon')
from nltk.sentiment.vader import SentimentIntensityAnalyzer
```

This is a built-in sentiment analyzer in NLTK and it's super easy to use. Then we add the following to the `submit` method of `ExperienceForm`:

```python
sid = SentimentIntensityAnalyzer()

all_slots = tracker.slots
for slot, value in all_slots.items():
    if slot in self.required_slots(tracker):
        res = sid.polarity_scores(value)
        score = res.pop('compound', None)
        classi, confidence = max(res.items(), key=lambda x: x[1])
        # classification of the feedback, could be pos, neg, or neu
        all_slots[slot+'_class'] = classi
        # sentiment score of the feedback, range form -1 to 1
        all_slots[slot+'_score'] = score
```

and return the new values of the slots:

```python
return [SlotSet(slot, value) for slot, value in all_slots.items()]
```
Here we use the analyzer to get the classification for the feedback, and its score, and store them in the new slots. To do so, we have to use a event in Rasa called `SlotSet`; let's import it at the beginning:

```python
from rasa_sdk.events import SlotSet
```

Now you can restart the action server and test the chatbot again (remember to retrain it as we have changed the `domain.yml`). Make sure the chatbot works as before.

We cannot see the difference in the Rasa shell as the slots are not shown anywhere in the conversation. In the next part, we will generate a report using a web framework.

## Generate user report

To display the information that we collected from the user, we have to generate a report. You can use any web framework of your choice but we'll use a lightweight framework called [CherryPy](https://docs.cherrypy.org/en/latest/index.html).


#### Set up CherryPy server 🍒
Since we are not teaching web development here, we will just tell you how to set it up with CherryPy. First open a new directory and go there. In the terminal:

```
mkdir report
cd report
```
create 3 files as follow:

1. result.css
```css
body {
    padding-left: 15px;
}
```

2. result.html
```html
<html>
    <head>
    <link rel="stylesheet" href="result.css">
    </head>
    <body>
        <h1>{name} survey result</h1>
        {result}
    </body>
</html>
```

3. result.py
```python
import cherrypy
import os
class SurveyResult(object):
    @cherrypy.expose
    def index(self, name=None, result=None):
        return open("result.html").read().format(name=name, result=result)
conf={'/result.css':
                    { 'tools.staticfile.on':True,
                      'tools.staticfile.filename': os.path.abspath("./result.css"),
                    }
      }
if __name__ == '__main__':
    cherrypy.quickstart(SurveyResult(), config=conf)
```

Then in the terminal:

```
python result.py
```
It will set up a web app running at port 8080. Just like with the action script server, we will leave it running and open a new terminal.

#### Action for showing report

After setting up the report server, we have to add the `Action` in the action script to send the request when the conversation is ended, but before that, we will need to add `- action_show_result` under `actions` in `domain.yml` and at the end of the `## get contact info` and `## do not contact me` stories in `data/stories.md`.

In `actions.py` add the following:

```python
class ActionShowResult(Action):
    """open the html showing the result of the user survey"""
    def name(self):
        # type: () -> Text
        return "action_show_result"

    def run(self, dispatcher, tracker, domain):
        # type: (CollectingDispatcher, Tracker, Dict[Text, Any]) -> List[Dict[Text, Any]]

        result = tracker.slots
        name = result['name']
        if name is None:
            name = 'Anonymous'
        else:
            name = name + "'s"
        http_result =""""""
        for key, value in result.items():
            if key != 'requested_slot':
                http_result += """<p>{}: {}</p>""".format(key, value)

        # url of the server set up by result.py
        url = 'http://localhost:8080/?name={}&result={}'.format(name, http_result)
        webbrowser.open(url)

        return []
```

We'll need to import `webbrowser`:

```python
import webbrowser
```

This will gather the slots and send them with the request to the report server.

Now restart the action server and re-train rasa and test the chatbot.

## Fallback dialog

So far everything should work fine if the user has been good. However, what if the user gives an unexpected answer and the NLU fails to determine what to do. Here we use a fallback action to prompt the user to try again. First we have to enable `FallbackPolicy`, in `config.yml` under `policies`, add:

```YAML
- name: "FallbackPolicy"
  nlu_threshold: 0.4
  core_threshold: 0.3
  fallback_action_name: "action_default_fallback"
```

`action_default_fallback` is a default action in Rasa Core which sends the `utter_default` template message to the user. So in `domain.yml`, add `- utter_default` under `actions` and `templates`:

```
utter_default:
- text: "Sorry, I don't understand."
- text: "I am not sure what you mean."
```

Now you can re-train and test the chatbot. Make sure you try to be a naughty user.

*Congratulations! You have complicated the Rasa workshop... for now. Please feel free to integrate more functions to it, experiment and have fun.*

## What's beyond

For more things you can do with Rasa, please refer to the [Rasa documentation](http://rasa.com/docs/rasa/).


We are always looking for more content, so if you have a good idea, please feel free to contribute.
