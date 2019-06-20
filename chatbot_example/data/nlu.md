## intent:greet
- hey
- hello
- hi
- good morning
- good evening
- hey there

## intent:goodbye
- bye
- goodbye
- see you around
- see you later

## intent:affirm
- yes
- indeed
- of course
- that sounds good
- correct

## intent:deny
- no
- never
- I don't think so
- don't like that
- no way
- not really

## intent:self_intro
- I am [Mary](PERSON)
- My name is [Anna](PERSON)
- Hi! I am [John](PERSON)
- [Jason](PERSON)
- Hey, I am [Nick](PERSON)
- Hello, I am [Peter](PERSON)
- Hey ya'll my name is [Ann](PERSON)

## intent:give_email
- my email is [joe@aol.com](email)
- [123@123.co.uk](email)
- Email: [asdasd@asdasd.info](email)
- this is my email - [asd123@asd1.co.uk](email)
- here it is [123@123.co.uk](email)

## intent:give_tel
- my number is [01234567890](tel)
- contact me at [07896234653](tel)
- call me at [+853 9876 2345](tel)
- contact is [+44 7893096125](tel)
- tel number: [+33 9876 1234 083](tel)
- my contact is [+44 7893096125](tel)
- sure, my number is [+853 98762345](tel)

## regex:email
- [\w-]+@([\w-]+\.)+[\w-]+

## regex:tel
- (0)([0-9][\s]*){10}
