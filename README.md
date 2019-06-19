# Step Into the AI Era: Chatbots that know if you are angry


## Install Rasa and set up the environment

Clone this repo form Github:

`git clone (insert link) .`

Enter the directory:

`cd rasa_workshop`

(optional) Create a new [pyenv] (https://github.com/pyenv/pyenv-virtualenv) or [conda](https://docs.conda.io/projects/conda/en/latest/user-guide/tasks/manage-environments.html) environment

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
* `data/nlu.md` :your NLU training data
* `data/stories.md` : your stories
* `domain.yml` : your assistant’s domain
