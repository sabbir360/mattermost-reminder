# Mattermost JIRA Web Hook

### Prerequisites
 - Python (3.5+), Only Tested on Ubuntu
 - Mattermost slashcommand. ([Go Here](https://docs.mattermost.com/developer/slash-commands.html) to create guide.)
 - Create a python file from `config.py.sample` as `config.py`
 - Change information based on yours on `config.py`

### Deployment
Follow [flask reference](http://flask.pocoo.org/docs/dev/tutorial/deploy/)

### How to set reminder
I'm assuming you've successfully configured `SlashCommand` as **reminder**.

So, type `/reminder help` to see available commands and use cases.


**N.B: For making reminder work webhook created user must have access to the prior channel**
