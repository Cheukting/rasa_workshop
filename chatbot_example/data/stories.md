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
- action_show_result

## do not contact me
> check ask contact
* deny
- utter_thanks
- action_show_result

## say goodbye
* goodbye
  - utter_goodbye
