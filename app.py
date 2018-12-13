import subprocess
from os.path import abspath, dirname, isfile
from os import sep, system, walk, remove
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
    crontab_data = ""
    if isfile(file_path()):
        f = open(file_path(), "a+")
    else:
        crontab_data = subprocess.run(['crontab', '-l'], stdout=subprocess.PIPE).stdout.decode('utf-8')
        f = open(file_path(), "w+")

    cron_text = cp[0] + " " + cp[1] + " * * " + cp[2] + " " + cron_file
    f.write(crontab_data+cron_text + " >/dev/null 2>&1")
    f.write("\n")
    f.close()
    system("cat " + file_path() + " | crontab -")


def response_rectifier(text, msg_type="error"):
    if msg_type == "error":
        text = text + "\nType '/reminder help' to see all options."
    elif msg_type == "help":
        text = text + "`/reminder list` to see all reminders.\n" \
               "`/reminder del command_name` to delete a reminder.\n" \
               "`/reminder 10 17 1,2,5 town-square \"Hello @channel check this.\" ReminderName` to add a reminder.\n" \
               "Where format is `min 24hour weekedays channel_name \"your message\" AUniqueName`\n" \
               "1=Monday, 2=Tuesday, 5=Friday."

    return text


def mattermost_post(hook, channel, text, name, username):
    if re_match('^[a-zA-Z0-9_]+$', name):
        current_path = abspath(dirname(__file__)) + sep + "cron_item" + sep
        file_name = current_path + name + username + ".sh"
        if isfile(file_name):
            return "EX"
        text = quote_plus("\n".join(text.replace("\"", "").split("<br />")))

        """
           payload=%7B%22channel%22%3A%20%22random%22%2C%20%22text%22%3A%20%22%40channel%20%0A%0AExercise%20time%20boys%20and%20girls.%20%3Aman_cartwheeling%3A%20%3Arunning_man%3A%0AWish%20everyone%20participate%20willingly.%0A%22%2C%20%22username%22%3A%20%22TAO%22%7D
        """
        base_text = "curl -X POST " + hook\
                    + " -H 'Content-Type: application/x-www-form-urlencoded' " \
                     "-H 'cache-control: no-cache' -d payload=%7B%22channel%22%3A%20%22"+\
                    channel+"%22%2C%20%22text%22%3A%20%22"+ text +"%0A%22%2C%20%22username%22%3A%20%22Reminder%22%7D"
        # base_text = base_text.replace("__channel__", channel).replace("__hook__", hook).replace("__MMTEXT__", text)

        f = open(file_name, "w")
        f.write(base_text)
        f.close()
        system("chmod +x "+file_name)
        return file_name
    return "IN"


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

                # 0 MIN 1 HOUR 2 DAY 3 CHANNEL 4 TEXT 5 NAME
                try:
                    min_val = int(cp[0])
                    hour_val = int(cp[1])
                    day_val = int(cp[2].replace(",", ""))
                    print(day_val)
                except ValueError as ex:
                    return jsonify({"text": response_rectifier("Check your format. Error: `"+str(ex)+"`", "error")})

                resp = mattermost_post(HOOK, cp[3], cp[4], cp[5], username)

                if min_val > 60 or min_val < 0:
                    resp['text'] = response_rectifier('Invalid Minute Value')
                elif hour_val > 24 or hour_val < 1:
                    resp['text'] = response_rectifier('Invalid Hour Value')
                elif day_val > 1234567:
                    reply['text'] = response_rectifier("""Invalid Day Value. Value should be comma separated.\
                     Example: 1 for Monday, 1,2 For Monday and Tuesday.""")
                elif resp == "EX":
                    reply['text'] = response_rectifier("A reminder already set with this name.", "")
                elif resp == "IN":
                    reply['text'] = "Invalid Reminder Name. Name should be AlphaNumeric."
                elif resp:
                    crontab_write(cp, resp)
                    reply["text"] = 'Cron Set Successfully as `'+cp[5]+'`'
                else:
                    reply['text'] = response_rectifier("Make sure Reminder name is **Valid, AplphaNumeric and Unique**.")

            elif len(command_parser) == 1:
                if command_parser[0] == "help":
                    admin_hint = ""
                    if username in ADMIN_USER:
                        admin_hint = "To delete others reminder type `/reminder del_others ReminderName`\n"
                    reply['text'] = response_rectifier(admin_hint, "help")
                    return jsonify(reply)
                current_path = abspath(dirname(__file__))
                reminder_list = []
                reminder_list_admin= []
                for (dir_path, dir_name, file_names) in walk(current_path+sep+"cron_item"):
                    for file_name in file_names:
                        if username+".sh" in file_name:
                            reminder_list.append(file_name.replace(username+".sh", ""))
                        else:
                            reminder_list_admin.append(file_name)
                items = "\n".join(reminder_list)
                other_items = "\n".join(reminder_list_admin)
                if items:
                    reply['text'] = "**Your List:** \n"+items
                    if other_items and username in ADMIN_USER:
                        reply['text'] = reply['text']+"Other users reminders.\n**Type `del_others ReminderName` to delete.**\n"+other_items

                else:
                    reply['text'] = response_rectifier("You haven't added anything!")
            elif len(command_parser) == 2:
                if command_parser[0] == "del":
                    action_file = abspath(dirname(__file__))+sep+"cron_item"+sep+command_parser[1]+username+".sh"
                    validation = re_match('^[a-zA-Z0-9_]+$', command_parser[1])
                    if validation and isfile(action_file):
                        print(action_file)
                        new_file = []
                        with open(file_path()) as f:
                            lines = f.readlines()
                            for line in lines:
                                if action_file not in line:
                                    new_file.append(line)
                        file_format = "".join(new_file)
                        with open(file_path(), "w+") as f:
                            f.write(file_format)
                        remove(action_file)
                        system("cat " + file_path() + " | crontab -")
                        reply['text'] = "Reminder deleted as `"+command_parser[1]+"`"
                    else:
                        reply['text'] = response_rectifier("Make Sure File Name is Valid.")
                elif command_parser[0] == "del_others":
                    if username in ADMIN_USER:
                        action_file = abspath(dirname(__file__)) + sep + "cron_item" + sep + command_parser[
                            1] + ".sh"
                        validation = re_match('^[a-zA-Z0-9_]+$', command_parser[1])
                        if validation and isfile(action_file):
                            print(action_file)
                            new_file = []
                            with open(file_path()) as f:
                                lines = f.readlines()
                                for line in lines:
                                    if action_file not in line:
                                        new_file.append(line)
                            file_format = "".join(new_file)
                            with open(file_path(), "w+") as f:
                                f.write(file_format)
                            remove(action_file)
                            system("cat " + file_path() + " | crontab -")
                            reply['text'] = "Reminder deleted as `" + command_parser[1] + "`"
                        else:
                            reply['text'] = response_rectifier("Make Sure File Name is Valid.")
                    else:
                        reply['text'] = "For admin user only."
            else:
                reply['text'] = response_rectifier("Invalid Command format.")
        else:
            reply['text'] = response_rectifier("Invalid User/Format.")
    else:
        reply["text"] = "Invalid Slash Token. Contact authorised person."
    return jsonify(reply)


if __name__ == "__main__":
    app.run(debug=DEBUG, host=HOST, port=PORT)
