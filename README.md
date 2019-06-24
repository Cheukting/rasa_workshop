# Step Into the AI Era: Chatbots that know if you are angry

In this workshop, we will try to build a chatbot that will ask for the user's contact details (compile to GDPR) and feedback of an event that they may have attended.


## Install Rasa and set up the environment

Open a terminal.

Clone this repo form Github:

`git clone https://github.com/Cheukting/rasa_workshop .`

Enter the directory:

`cd rasa_workshop`

(optional) Create a new [pyenv](https://github.com/pyenv/pyenv-virtualenv) or [conda](https://docs.conda.io/projects/conda/en/latest/user-guide/tasks/manage-environments.html) environment

Install the requirements:

`pip install -r requirement.txt`

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

## Pipeline and NLU setup

Now we will need to train the NLU, which is a natural language processing tool for intent classification and entity extraction.

Open `data/nlu.md` with text editor or IDE of your choice.

We see in the default example that some examples for different intents are set up. In our use case, since we will be doing sentiment analysis using NLTK, we can delete the sections for `mood_great` and `mood_sad`. Feel free to add more example for the other intents, the more example the better is the understanding of the chatbot.

Besides, since our bot will collect user's data, we need a few more intents for data capturing: `self_intro`, `give_email`, `give_tel`

Here is some example, please feel free to add more:

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

In these examples, we can see that we are also giving example for the entity: `PERSON`, `email` and `tel`. `PERSON` is a entity provided by SpaCy. To help capture `email` and `tel`, we also use [regex](https://www.rexegg.com/).

Put this is `nlu.md` as well:

```
## regex:email
- [\w-]+@([\w-]+\.)+[\w-]+

## regex:tel
- (0)([0-9][\s]*){10}
```

If you are a regex expert, you can change it to a better expression.

After that, we have to setup the [NLP pipeline](http://rasa.com/docs/rasa/nlu/choosing-a-pipeline/), it can be done by editing `config.yml`. Here we will change the `supervised_embeddings` to `pretrained_embeddings_spacy` so we will be using pretrained SpaCy embedding pipeline instead.

## Train and test NLU

Now we can train and test the NLU. In the terminal:

`python -m spacy download en_core_web_md`

`python -m spacy link en_core_web_md en`

`rasa train nlu`

The first 2 commends download and set up the Spacy model that we will be using. While the last commend tell rasa to train the NLU. The trained model should be saved under `models/`

Now we can test the NLU that we trained:

`rasa shell nlu`

After loading (may take a while) you can type in messages and can see the prediction that the NLU gave. If you are not happy with the result, you can go back to add more examples to the `nlu.md` and train the NLU again (`rasa train nlu`). Repeat the training and testing until you are happy.

*Congratulations, you have complete 1/3 of the workshop, feel free to take a 3 mins break*

## Planning the conversation

In this part, we have to write the plan for the flow of the conversation. It will be written in `data/stories.md`. The flow of the conversation will be broken in to 3 parts:

1. greeting -> ask if user has attended event:

    yes ->  (go to part 2.a)

    no -> (go to part 2.b)

2. a) ask for feedback -> ask if we can contact them

   b) encourage them to go next year -> ask if we can contact them

   yes ->  (go to part 3.a)

   no -> (go to part 3.b)

3. a) contact form and see you next year

   b) see you next year

If you open and edit `data/stories.md`, you can see that there are example stories already written. Except the `## say goodbye` which we are going to keep (it is for the user to end the conversation at anytime), we can delete the rest of it and write our own.

The skeleton of the above 3 parts should be like this:

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

Here we will fill in `<something>` later but let me explain the use of checkpoints. For the line with `>` e.g. `> check ask experience` is a checkpoint which we can link the different part of the stories together. So instead giving example of stories which users answer the questions differently, we can use checkpoints to layout different paths.

For the line with `*` it is when the chatbot recognize an intent. For example `* affirm` will be triggered when the NLU predicted an `affirm` intent.

## Domain and templates

We also need to tell the chatbot what action to take and what to answer then it reaches certain point of the conversation. This will be recorded in `domain.yml`, we also define the intents, entities and slots (information that we capture) in that file.

#### Adding intents

Remember what intents we have defined in `nlu.md`? Let's put it in `domain.yml`:

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

#### Adding slots

Before we define actions, we also want to define a few more stuff. Slots are the information that we wants to capture from the user. So far we want to capture their `name`, `email` and `tel` number:

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

`unfeaturized` just mean that this information will not affect the flow of the conversation.

#### Adding entities

Similarly, add the entities that we defined in `nlu.md`:

```
entities:
- PERSON
- email
- tel
```

#### Adding forms

We will use action forms to capture user's contact information and feedback, it will be more clear when we write the actions for them. Let's define it here like this for now:

```
forms:
  - experience_form
  - contact_form
```

#### Adding actions

We have 2 kind of action: One is `utter` that you see in the example, those are the dialog that the chatbot will 'say' to the users. The other is custom action. In this part, we will only add `utter` actions.

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
- utter_unclear
- utter_submit
- utter_wrong_email
- utter_wrong_tel
- utter_encourage
```

These are the different `utter` of dialogs we would have, you will see them come into places when we complete the other parts of the projects, you may come back to change it later if you want.

#### Adding templates

For the above `utter` we need to fill in the templates of what text will be used. If there's more then one, it will be randomly choose to use one for that dialog. Try to put it more than one so there's variety in the bot's dialog.

```
templates:
  utter_greet:
  - text: "Hello! My name is Alex."

  utter_happy:
  - text: "Great!"
  - text: "Awesome!"

  utter_unclear:
  - text: "Sorry, I don't understand."
  - text: "I am not sure what you mean."

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

Please feel free to add more or change the text for each `utter`

We are done with `domain.yml` for now, let's go back to `stories.md`

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

Notice that `- form{"name": "experience_form"}` we are calling to use the action form `experience_form`. After we are done, it will be reset to `null` to continue the conversation.

## Form actions

Now come to the fun part, we will use action forms to collect the user's information. Before we do anything, first we need to add the `FormPolicy` to the configuration, goto `config.yml` and add:

```
  - name: FormPolicy
```
under `policies`. Also, we need to enable the aciton endpoint. Goto `endpoint.yml` and un0comment the following:

```
 action_endpoint:
   url: "http://localhost:5055/webhook"
```
The action scripts will be hosted in a server setup by Rasa at port 5055.

Then let's have a look at `actions.py`. From the examples in the default file, there are:

```
from typing import Any, Text, Dict, List

from rasa_sdk import Action, Tracker
from rasa_sdk.executor import CollectingDispatcher
```
which imports some object that is used to communicated with the Rasa framework. On top of that, we also need:

```
from rasa_sdk.forms import FormAction
```

which allows us to write custom form action classes (classes inherit from `FormAction`).

#### ExperienceForm

First we define the `experience_form`:

```
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
           after all required slots are filled
           basically it generate sentiment analysis
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

It is very simple, it just collect the text that was input by the user in the `feedback` slot. When the form is triggered, the action `utter_ask_feedback` is activated and the user input after that will be captured. Have a look at the doc string of each methods and make sure you understand what each function does, we will use them again in the more complicated `contact_form`.

#### ContactForm

Similarly, we define `contact_form`:

```
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
This time the slot mapping is more complicated, using `from_entity` we can specify the slot to be fill with a certain recognised entity / intent in stead of free text. However, we put `from_text` in the list after `from_entity` as a fail save catching the information if the user's input is not recognisable.

#### Validating slots

For the `email` and `tel` the user input, we want to validate them. so in the `ContactForm` class, we added more methods:

```
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
```
import re
```
Also, we have use one more `typing`: `Optional`. We have to import it as well:
```
from typing import Any, Text, Dict, List, Optional
```
Here we have defined 2 helper methods: `is_email` and `is_tel` which will use Regex to check if the input matches an email format and phone number format. After that , we also set up 2 validate method for each of them. If the format is not does not match what we expected, we will reset the slot to `None` and use the `utter` to ask again.

## Train and test your Chatbots

Once you are ready, it's time to train and test our chatbot (deep breath). So to train the bot using the settings that we have set up, in the terminal:

```
rasa train
```

when it is done, you can see that a new model is saved. Now let's try it out. First, make the server hosting the action script up and running:

```
rasa run actions
```
Now the server is running, let's open an other terminal and then type:
```
rasa shell --endpoint endpoint.yml
```
It will call Rasa to run the chatbot with the endpoint and now you can talk to it.

#### Restart the action Server

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
