# Mattermost JIRA Web Hook

### Prerequisites
 - Python (2/3)
 - Mattermost slashcommand. ([Go Here](https://docs.mattermost.com/developer/webhooks-incoming.html#) to create guide.)
 - Create a python file from `config.py.sample` as `config.py`
 - Change information based on yours on `config.py`
 - Configure JIRA Web hook (Configure the webhook in your JIRA project) by following [this link](https://docs.mattermost.com/integrations/jira.html#configure-the-webhook-in-your-jira-project)
### How to test
- Run `pip install -r requirements.txt`
- Then on your project directory run `python app.py`

### Deployment 
Follow [flask reference](http://flask.pocoo.org/docs/dev/tutorial/deploy/)

**N.B: For JIRA webhook you need to set a valid host/endpoint**
