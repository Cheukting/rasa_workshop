# Step Into the AI Era: Chatbots that know if you are angry

In this workshop, we will try to build a chatbot that will ask for the user's contact details (compile to GDPR) and feedback of an event that they may have attended.


## Install Rasa and set up the environment

Open a terminal.

Clone this repo form Github:

`git clone (insert link) .`

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

## Not talked to the representatives
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
