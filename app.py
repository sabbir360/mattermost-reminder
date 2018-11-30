from os.path import abspath, dirname, isfile
from os import sep, system
from flask import Flask, request, jsonify
from urllib.parse import quote_plus
from re import split as re_sp
from re import match as re_match
from config import *

app = Flask(__name__)


def file_path():
    current_path = abspath(dirname(__file__))
    return current_path+sep+"crontab.tab"


def crontab_write(cp, cron_file):
    # write crontab
    current_path = abspath(dirname(__file__)) + sep
    f = open(file_path(), "w+")
    cron_text = cp[0] + " " + cp[1] + " * * " + cp[2] + " " + cron_file
    f.write(cron_text + " >/dev/null 2>&1")
    f.write("\n")
    f.close()
    system("cat " + file_path() + " | crontab -")


def mattermost_post(hook, channel, text, name, username):
    if re_match('^[a-zA-Z0-9_]+$', name):
        current_path = abspath(dirname(__file__)) + sep + "cron_item" + sep
        file_name = current_path + name + username + ".sh"
        if isfile(file_name):
            return None
        text = quote_plus("\n".join(text.replace("\"", "").split("<br />")))

        base_text = "curl -X POST " + hook\
                    + " -H 'Content-Type: application/x-www-form-urlencoded' " \
                     "-H 'cache-control: no-cache' -d payload=%7B%22channel%22%3A%20%22"+\
                    channel+"%22%2C%20%22text%22%3A%20%22"+ text +"%22%7D"
        # base_text = base_text.replace("__channel__", channel).replace("__hook__", hook).replace("__MMTEXT__", text)

        f = open(file_name, "w")
        f.write(base_text)
        f.close()
        system("chmod +x "+file_name)
        return file_name
    return None


@app.route('/', methods=['POST'])
def reminder():
    data = request.form
    reply = {}
    if data.get("token", None):
        username = data.get("user_name", None)
        text = data.get("text", None)
        if username and text:
            text = "<br />".join(text.split("\n"))
            command_parser = [p for p in re_sp("( |\\\".*?\\\"|'.*?')", text) if p.strip()]

            # format: min hour days,1,2 channel text
            print(command_parser)
            if len(command_parser) == 6:  # add
                cp = command_parser
                resp = mattermost_post(HOOK, cp[3], cp[4], cp[5], username)
                if resp:
                    crontab_write(cp, resp)
                    reply["text"] = 'Cron Set Successfully as `'+cp[5]+username+'`'
                else:
                    reply['text'] = "Make sure file name is **Valid and Unique**."

            elif len(command_parser) == 1:
                pass  # list
            elif len(command_parser) == 2:
                pass  # del
            else:
                reply['text'] = "Invalid Command format"
        else:
            reply['text'] = "Invalid User/Format."
    else:
        reply["text"] = "Invalid Slash Token"
    return jsonify(reply)


if __name__ == "__main__":
    app.run(debug=DEBUG, host=HOST, port=PORT)
