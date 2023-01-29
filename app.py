from flask import Flask, request, abort
from linebot import (LineBotApi, WebhookHandler)
from linebot.exceptions import (InvalidSignatureError)
from linebot.models import *
from random import randint, random
from datetime import date
from time import time as t
import os
import psycopg2
import pkg_resources
pkg_resources.require("googletrans==3.1.0a0")
import googletrans

app = Flask(__name__)
line_bot_api = LineBotApi('fenSu73BZugLhqUSHlM4sCn8N96EM5GyGL8fZ94b08d5Rq//nbJW1Rt4lrsKUQDuEMTuKiyADofAU6TVMTcim4wDjvSxFopiPOTmuFJx8T/uppq19HPXIFaBnGmnPq4Sid2ANHnqMnPKz2PX5TNlVAdB04t89/1O/w1cDnyilFU=')
handler = WebhookHandler('813dd53913d86c280c920e605a0cc1cb')
translator = googletrans.Translator()


@app.route("/callback", methods=['POST'])
def callback():
    signature = request.headers['X-Line-Signature']
    body = request.get_data(as_text=True)
    app.logger.info("Request body: " + body)
    try:
        handler.handle(body, signature)
    except InvalidSignatureError:
        abort(400)
    return 'OK'


@handler.add(MessageEvent, message=TextMessage)
def handle_message(event):
    ducks = {'Archie': 'Ueebac62da11acc018847944b1d1bf1f8', 'Kita': 'Ub66a0a6b6bdc9770a0eb30db63e7a08f'}
    omcID = "C3e810369fe7fd60e213006be1d4900a5"
    # omcSID = "C786765f0f194d1986f3ca2d385ea7670"
    origMsg = event.message.text.strip()
    userMsg = origMsg.lower().replace(" ", "")
    listMsg = origMsg.lower().split(" ")
    normalListMsg = origMsg.split(" ")
    cmdBody = ""
    for i, word in enumerate(listMsg):
        if i != 0:
            cmdBody += word + " "
    cmdBody.strip()
    reply = True
    imageReply = False
    msg = ""
    url = ""
    username = ""
    con = None
    cur = None
    notify = True

    # start exception handling for database
    try:
        con = psycopg2.connect(DATABASE_URL, sslmode='require')
        cur = con.cursor()

        sql = f"SELECT * FROM members WHERE uid = '{event.source.user_id}'"
        cur.execute(sql)
        records = cur.fetchall()
        if len(records) != 0:
            if records[0][4] == 'F':
                notify = False
        
        if listMsg[0] == "/boot" and event.source.user_id == ducks["Archie"]:
          pass
        # help commands
        elif userMsg == "/?":
            msg = "COMMAND DUMP:\n/help\n/help misc\n/help event\n/help fun\n/changelog\n/suggest\n/feed\n/duckgame\n/petsheet\n/bathe|bath\n/compliment\n/ac\n/joke\n/aj\n/ball\n/blog\n/createcommand|cc\n/cic\n/it\n/initiate\n/bank\n/pay\n/cf\n/cf join\n/cf cancel\n/hl|hitlist"
        elif userMsg == "/help":
            msg = "/? - command dump\n/help fun - lists fun commands\n/help event - lists event based commands\n/help misc - lists general commands\n/changelog - view a list of changes made in the recent updates to Sir Quacksly"
        elif userMsg == "/helpevent":
            msg = "WIP (not the one you're thinking of TLR)"
        elif userMsg == "/helpmisc":
            msg = "COMMANDS:\n/suggest [suggestion] - make a suggestion of what to add to the bot\n/blog [name] [compliments] [insults] - log what a player has done at the ball\n/ball [name] - check the ball logs for a player\n/createcommand|cc [command] [response] - create a new command, the command name cannot contain a space\n/commanddesc|cd [command] [desc] - submit a description for /help\n/cic [command] [imageurl] - create a command with an image response\n/it [image url] - test if an image url will work\n/hitlist [name] - update a players last neg kick date"
        elif userMsg == "/helpfun":
            msg = "COMMANDS:\n/ac [compliment] - add a compliment\n/aj [joke] - add a joke\n/cf [name] [amount] [heads/tails] - create coinflip\n/cf join [name] - join coinflip\n/cf cancel [name] - cancel coinflip"
        elif userMsg == "/changelog":
            msg = "Q-6.2: made a hitlist for negotiation kicks"

        # some random commands
        elif (event.source.user_id == ducks["Kita"] and "drown" in listMsg) or listMsg[0] == "/drown":
            sql = f"SELECT * FROM members WHERE uid = '{event.source.user_id}'"
            cur.execute(sql)
            records = cur.fetchall()
            if len(records) == 0:
                url = "https://www.marvelsynergy.com/images/howard-the-duck.png"
                imageReply = True
            else:
                msgs = []
                m_id, m_un, m_csh, m_day, m_not = records[0]
                sql = f"UPDATE members SET money = {int(m_csh) - 200} WHERE uid = '{event.source.user_id}';"
                cur.execute(sql)
                con.commit()
                msgs += [ImageSendMessage(original_content_url="https://www.marvelsynergy.com/images/howard-the-duck.png", preview_image_url="https://www.marvelsynergy.com/images/howard-the-duck.png")]
                msgs += [TextSendMessage(text="Hey!\nThat's not very nice, here's a 200 coin fine\n>.<")]
                line_bot_api.reply_message(event.reply_token, msgs)
                reply = False
        elif listMsg[0] == "/spank":
            msg = f"{cmdBody} 🫲🏻🫲🏻🫲🏻🫲🏻"
        elif listMsg[0] == "/kiss":
            msg = f"{cmdBody} 💋💋💋💋💋"

        # compliments
        elif listMsg[0] == "/compliment":
            cur.execute("SELECT * FROM compliments;")
            records = cur.fetchall()
            msg = records[randint(0, len(records) - 1)][1]
        elif listMsg[0] in ["/ac", "/acompliment", "/addcompliment"]:
            cur.execute(f"INSERT INTO compliments(compliment) VALUES ('{cmdBody}')")
            con.commit()
            if notify:
                msg = "compliment added"
            else:
                reply = False

        # jokes
        elif listMsg[0] == "/joke":
            cur.execute("SELECT * FROM jokes;")
            records = cur.fetchall()
            msg = records[randint(0, len(records) - 1)][1]
        elif listMsg[0] in ["/aj", "/addjoke", "/ajoke"]:
            cur.execute(f"INSERT INTO jokes(joke) VALUES ('{cmdBody}')")
            con.commit()
            msg = "joke added"
            if notify:
                msg = "joke added"
            else:
                reply = False

        # make suggestions
        elif listMsg[0] in ["/suggest", "/suggestion"]:
            line_bot_api.push_message(ducks['Archie'], TextSendMessage(text=cmdBody))
            if notify:
                msg = 'suggestion made! thank you (^>^)'
            else:
                reply = False

        # create basic commands
        elif listMsg[0] in ["/cc", "/createcommand"]:
            response = ""
            command = listMsg[1]
            for i, word in enumerate(origMsg.split()):
                if i != 0 and i != 1:
                    response += word + " "
            if listMsg[1][0] == "/":
                command = listMsg[1][1:]
            sql = f'''INSERT INTO commands (request, response) VALUES ('/{command}', '{response.strip()}');'''
            cur.execute(sql)
            con.commit()
            if notify:
                msg = "command created"
            else:
                reply = False
        # create image commands
        elif listMsg[0] in ["/cic", "/createimagecommand"]:
            response = origMsg.split()[2]
            command = listMsg[1] if listMsg[1][0] != "/" else listMsg[1][1:]
            sql = f'''INSERT INTO imagecs (request, response, creator) VALUES ('/{command}', '{response}', '{event.source.user_id}');'''
            cur.execute(sql)
            con.commit()
            if notify:
                msg = "command created"
            else:
                reply = False

        # image testing
        elif listMsg[0] == "/it":
            url = normalListMsg[1]
            imageReply = True

        # ball logging
        elif listMsg[0] in ["/blog", "/ball"]:
            if len(listMsg) == 2:
                name = listMsg[1] if listMsg[1][0] != "(" else listMsg[1][5:]
                cur.execute(f"SELECT * FROM ball WHERE username = '{name}';")
                records = cur.fetchall()
                if len(records) == 0:
                    msg = f"no record for {name}"
                else:
                    msg = f"{name}'s record: {records[0][1]} compliments and {records[0][2]} insults"
            elif len(listMsg) == 4:
                name = listMsg[1] if listMsg[1][0] != "(" else listMsg[1][5:]
                cur.execute(f"SELECT * FROM ball WHERE username = '{name}';")
                records = cur.fetchall()
                if len(records) == 0:
                    sql = f"INSERT INTO ball (username, compliment, insult) VALUES ('{name}', {listMsg[2]}, {listMsg[3]});"
                    cur.execute(sql)
                    con.commit()
                else:
                    sql = f"UPDATE ball SET compliment = {int(listMsg[2]) + records[0][1]}, insult = {int(listMsg[3]) + records[0][2]} WHERE username = '{name}';"
                    cur.execute(sql)
                    con.commit()
                if notify:
                    msg = f"added {listMsg[2]} compliment/s and {listMsg[3]} insult/s to {name}"
                else:
                    reply = False
            else:
                msg = "incorrect syntax; /ball [name] or /ball [name] [num compliments] [num insults]"

        # neg kicks
        elif listMsg[0] in ["/hitlist", "/hl"]:
            if len(listMsg) == 1:
                cur.execute("SELECT * FROM neg;")
                records = cur.fetchall()
                if len(records) == 0:
                    msg = "no records in table"
                else:
                    msg = "negotiation kicks :>"
                    for record in records:
                        msg += f"\n{record[0]} last kicked us on {str(record[1])}"
            elif len(listMsg) == 2:
                name = listMsg[1] if listMsg[1][0] != "(" else listMsg[1][5:]
                cur.execute(f"SELECT * FROM neg WHERE kicker = '{name}';")
                records = cur.fetchall()
                if len(records) == 0:
                    sql = f"INSERT INTO neg (kicker, lastkicked) VALUES ('{name}', '{date.today()}');"
                    cur.execute(sql)
                    con.commit()
                else:
                    sql = f"UPDATE neg SET lastkicked = '{date.today()}' WHERE kicker = '{name}';"
                    cur.execute(sql)
                    con.commit()
                if notify:
                    msg = f"updated {name}'s last kick to {date.today()}"
                else:
                    reply = False
            else:
                msg = "please enter their name as one word e.g. /hitlist oneword"

        # list table
        elif listMsg[0] == "/list":
            cur.execute(f"SELECT * FROM {listMsg[1]};")
            msg = f"{listMsg[1]} contains:>"
            records = cur.fetchall()
            for record in records:
                msg += f"\n{record}"

        # sql commands
        # /select ;column|column;table;condition = value|condition = value...
        elif listMsg[0] == "/select":
            if event.source.user_id != ducks['Archie']:
                msg = "you lack authorisation for this command"
            else:
                chunks = origMsg.split(";")
                sql = f"SELECT {chunks[1]} FROM"
                for i, column in enumerate(chunks[2].split("|")):
                    if i == 0:
                        sql += column
                    else:
                        sql += f", {column}"
                if len(chunks) == 4:
                    for i, condition in enumerate(chunks[3].split("|")):
                        condition = condition.split()
                        c = f"{condition[0]} {condition[1]} "
                        if condition[0] in ["compliment", "insult", "id", "money"]:
                            c += condition[2]
                        else:
                            c += f"'{condition[2]}'"
                        if i == 0:
                            sql += f" WHERE {c}"
                        else:
                            sql += f' AND {c}'
                cur.execute(sql)
                records = cur.fetchall()
                msg = f"{records}"
        # /insert ;table;value|value|value...
        elif listMsg[0] == "/insert":
            if event.source.user_id != ducks['Archie']:
                msg = "you lack authorisation for this command"
            else:
                chunks = origMsg.split(";")
                sql = f"INSERT INTO {chunks[1]} VALUES ("
                for i, val in enumerate(chunks[2].split("|")):
                    if i == 0:
                        sql += f"'{val}'"
                    elif chunks[1] == "ball" or (chunks[1] == "members" and i == 2) or (chunks[1] == "bot" and i in [3, 4, 5, 6]):
                        sql += f", {val}"
                    else:
                        sql += f", '{val}'"
                sql += ")"
                cur.execute(sql)
                con.commit()
                msg = "record inserted"
        # /delete ;table;condition = value|condition = value...
        elif listMsg[0] == "/delete":
            if event.source.user_id != ducks['Archie']:
                msg = "you lack authorisation for this command"
            else:
                chunks = origMsg.split(";")
                sql = f"DELETE FROM {chunks[1]} WHERE"
                for i, condition in enumerate(chunks[2].split("|")):
                    condition = condition.split()
                    c = f"{condition[0]} {condition[1]} "
                    if condition[0] in ["compliment", "insult", "id", "money"]:
                        c += condition[2]
                    else:
                        c += f"'{condition[2]}'"
                    if i == 0:
                        sql += f" {c}"
                    else:
                        sql += f' AND {c}'
                cur.execute(sql)
                con.commit()
                msg = "record/s deleted"
        # /update ;table;att=val|att=val;condition = val|condition = val"
        elif listMsg[0] == "/update":
            if event.source.user_id != ducks['Archie']:
                msg = "you lack authorisation for this command"
            else:
                chunks = origMsg.split(";")
                sql = f"UPDATE {chunks[1]} SET"
                for i, att in enumerate(chunks[2].split(",")):
                    att = att.split("=")
                    c = f"{att[0]} = "
                    if att[0] in ["compliment", "insult", "id", "money"]:
                        c += att[1]
                    else:
                        c += f"'{att[1]}'"
                    if i == 0:
                        sql += f" {c}"
                    else:
                        sql += f', {c}'
                for i, condition in enumerate(chunks[3].split("|")):
                    condition = condition.split()
                    c = f"{condition[0]} {condition[1]} "
                    if condition[0] in ["compliment", "insult", "id", "money"]:
                        c += condition[2]
                    else:
                        c += f"'{condition[2]}'"
                    if i == 0:
                        sql += f" WHERE {c}"
                    else:
                        sql += f' AND {c}'
                cur.execute(sql)
                con.commit()
                msg = "record updated"
        # /sql SQL STATEMENT
        elif listMsg[0] == "/sql":
            if event.source.user_id != ducks['Archie']:
                msg = "you lack authorisation for this command"
            else:
                cur.execute(cmdBody)
                if listMsg[1] == "select":
                    records = cur.fetchall()
                    msg = f"{records}"
                else:
                    con.commit()
                    msg = f"SQL executed"

        # add member to members table
        elif listMsg[0] == "/initiate":
            sql = f"SELECT * FROM members WHERE uid = '{event.source.user_id}'"
            cur.execute(sql)
            records = cur.fetchall()
            if len(records) == 0:
                profile = line_bot_api.get_group_member_profile(omcID, event.source.user_id)
                sql = f"INSERT INTO members VALUES ('{profile.user_id}', '{profile.display_name}', 100, '{date.today()}', 'T');"
                cur.execute(sql)
                con.commit()
                msg = "welcome to the ducknasty"
            else:
                if records[0][1] == line_bot_api.get_group_member_profile(omcID, event.source.user_id).display_name:
                    msg = "you have already been initialised"
                else:
                    sql = f"UPDATE members SET username = '{line_bot_api.get_group_member_profile(omcID, event.source.user_id).display_name}' WHERE uid = '{event.source.user_id}';"
                    cur.execute(sql)
                    con.commit()
                    msg = "username updated"
        elif listMsg[0] == "/indoctrinate" and event.source.user_id == ducks["Archie"]:
            sql = f"SELECT * FROM members WHERE uid = '{normalListMsg[1]}'"
            cur.execute(sql)
            records = cur.fetchall()
            if len(records) == 0:
                profile = line_bot_api.get_group_member_profile(omcID, normalListMsg[1])
                sql = f"INSERT INTO members VALUES ('{profile.user_id}', '{profile.display_name}', 100, '{date.today()}', 'T');"
                cur.execute(sql)
                con.commit()
                msg = f"welcome to the ducknasty {profile.display_name} 😈"
            else:
                msg = "they have already been initialised"

        # manually create members
        elif listMsg[0] == "/cm":
            if event.source.user_id != ducks['Archie']:
                msg = "you lack authorisation for this command"
            else:
                username = ""
                for i, sec in enumerate(normalListMsg):
                    if i != 0 and i != 1:
                        username += sec + " "
                username = username.strip()
                sql = f"INSERT INTO members VALUES ('{normalListMsg[1]}', '{username}', 0, '{date.today()}', 'T');"
                cur.execute(sql)
                con.commit()
                msg = f'{username} initiated'
        # check balance
        elif listMsg[0] == "/bank":
            if len(listMsg) == 1:
                sql = f"SELECT * FROM members WHERE uid = '{event.source.user_id}'"
            else:
                username = ""
                for i, sec in enumerate(normalListMsg):
                    if i != 0:
                        username += sec + " "
                username = username.strip()
                sql = f"SELECT * FROM members WHERE username = '{username[1:]}'"
            cur.execute(sql)
            records = cur.fetchall()
            if len(records) == 0:
                if len(listMsg) == 1:
                    msg = "you have not joined the ducknasty yet (/initiate)"
                else:
                    msg = f"{username[1:]} has not joined the ducknasty yet (/initiate)"
            else:
                if len(listMsg) == 1:
                    msg = f"you have {records[0][2]} coins"
                else:
                    msg = f"{username[1:]} has {records[0][2]} coins"
        # pay
        elif listMsg[0] == "/give":
            username = ""
            for i, sec in enumerate(normalListMsg):
                if i != 0 and i != len(normalListMsg) - 1:
                    username += sec + " "
            username = username.strip()
            sql = f"SELECT * FROM members WHERE username = '{username[1:]}'"
            cur.execute(sql)
            records = cur.fetchall()
            if len(records) == 0:
                msg = "either they have not joined the ducknasty, or have since changed their username "
            else:
                payee = records[0]
                sql = f"SELECT * FROM members WHERE uid = '{event.source.user_id}'"
                cur.execute(sql)
                records = cur.fetchall()
                if len(records) == 0:
                    msg = "you have not joined the ducknasty yet (/initiate)"
                else:
                    payer = records[0]
                    if int(listMsg[-1]) <= 5:
                        msg = "you can only give more than 5 coins"
                    elif str(payer[1]) == "Feyre" and str(payee[1]) == "Ruaidhri":
                        msg = "not happening <3"
                    elif int(listMsg[-1]) <= int(payer[2]):
                        tax = 0
                        # tax = int(int(listMsg[-1]) * 0.05)
                        sql = f"UPDATE members SET money = {int(float(payer[2])) - int(float(listMsg[-1]))} WHERE uid = '{event.source.user_id}';"
                        cur.execute(sql)
                        con.commit()
                        sql = f"UPDATE members SET money = {int(float(payee[2])) + int(float(listMsg[-1])) - int(tax)} WHERE username = '{username[1:]}';"
                        cur.execute(sql)
                        con.commit()
                        # sql = f"SELECT * FROM members WHERE uid = '0';"
                        # cur.execute(sql)
                        # records = cur.fetchall()
                        # sql = f"UPDATE members SET money = {int(records[0][2]) + tax} WHERE uid = '0';"
                        # cur.execute(sql)
                        # con.commit()
                        msg = f"{int(listMsg[-1]) - tax} coins transferred to {username[1:]}"
                        # msg += f"; {tax} coins tax given to me ^>^"
                    else:
                        msg = "you do not have enough coins to give this"
        # inject
        elif listMsg[0] == "/inject":
            if event.source.user_id != ducks["Archie"]:
                msg = "you lack authorisation for this command"
            else:
                username = ""
                for i, sec in enumerate(normalListMsg):
                    if i != 0 and i != len(normalListMsg) - 1:
                        username += sec + " "
                username = username.strip()
                sql = f"SELECT * FROM members WHERE username = '{username[1:]}'"
                cur.execute(sql)
                records = cur.fetchall()
                if len(records) == 0:
                    msg = "either they have not joined the ducknasty, or they have changed their username since"
                else:
                    sql = f"UPDATE members SET money = {int(records[0][2]) + int(listMsg[len(normalListMsg) - 1])} WHERE username = '{username[1:]}';"
                    cur.execute(sql)
                    con.commit()
                    msg = f"{listMsg[len(normalListMsg) - 1]} coins added to {username[1:]}"
        # coinflip
        elif listMsg[0] == "/cf":
            if len(listMsg) == 1:
                # list current bets
                sql = "SELECT * FROM cf"
                cur.execute(sql)
                records = cur.fetchall()
                if len(records) == 0:
                    msg = "there are currently no bets"
                else:
                    msg = "CURRENT BETS:>"
                    for record in records:
                        msg += f"\n{record[0]} for {record[2]} coins on {record[3]};"
            elif listMsg[1] == "join":
                # join cf
                # check if initialised
                sql = f"SELECT * FROM members WHERE uid = '{event.source.user_id}'"
                cur.execute(sql)
                records = cur.fetchall()
                if len(records) == 0:
                    msg = "you have not joined the ducknasty yet (/initiate)"
                else:
                    record = records[0]
                    # check for game
                    sql = f"SELECT * FROM cf WHERE name = '{listMsg[2]}'"
                    cur.execute(sql)
                    records = cur.fetchall()
                    if len(records) == 0:
                        msg = f"game not found ({listMsg[2]})"
                    else:
                        # check coins
                        bet = int(records[0][2])
                        if bet <= int(record[2]):
                            # grab member information
                            sql = f"UPDATE members SET money = {int(record[2]) - bet} WHERE uid = '{event.source.user_id}';"
                            cur.execute(sql)
                            con.commit()
                            # flip coin
                            flip = ["heads", "head", "h"] if random() < 0.5 else ["tails", "tail", "t"]
                            # award winner
                            winner = records[0][1] if records[0][3] in flip else event.source.user_id
                            sql = f"SELECT * FROM members WHERE uid = '{winner}';"
                            cur.execute(sql)
                            records = cur.fetchall()
                            win = int(bet * 2)
                            # win = int(win * 0.95)
                            sql = f"UPDATE members SET money = {int(records[0][2]) + win} WHERE uid = '{winner}';"
                            cur.execute(sql)
                            con.commit()
                            # tax = (bet * 2) - win
                            # sql = f"SELECT * FROM members WHERE uid = '0';"
                            # cur.execute(sql)
                            # records = cur.fetchall()
                            # sql = f"UPDATE members SET money = {int(records[0][2]) + tax} WHERE uid = '0';"
                            # cur.execute(sql)
                            # con.commit()
                            # delete cf request
                            sql = f"DELETE FROM cf WHERE name = '{listMsg[2]}'"
                            cur.execute(sql)
                            con.commit()
                            msg = f"{flip[0]}, {line_bot_api.get_group_member_profile(omcID, winner).display_name} wins {win} coins"
                            # msg += f"; {tax} coins tax given to me ^>^"
                        else:
                            msg = "you do not have enough coins for this bet"
            elif listMsg[1] == "cancel":
                # cancel cf
                if len(listMsg) != 3:
                    msg = "incorrect syntax: /cf cancel name"
                else:
                    sql = f"SELECT * FROM cf WHERE name = '{listMsg[2]}' AND creator = '{event.source.user_id}'"
                    cur.execute(sql)
                    records = cur.fetchall()
                    if len(records) == 0:
                        msg = "no game found"
                    else:
                        bet = int(records[0][2])
                        sql = f"SELECT * FROM members WHERE uid = '{event.source.user_id}'"
                        cur.execute(sql)
                        records = cur.fetchall()
                        sql = f"UPDATE members SET money = {int(records[0][2]) + bet} WHERE uid = '{event.source.user_id}';"
                        cur.execute(sql)
                        con.commit()
                        sql = f"DELETE FROM cf WHERE name = '{listMsg[2]}' AND creator = '{event.source.user_id}'"
                        cur.execute(sql)
                        con.commit()
                        msg = "bet canceled"
            elif len(listMsg) == 4:
                # create bet
                # check name availability
                sql = f"SELECT * FROM cf WHERE name = '{listMsg[1]}'"
                cur.execute(sql)
                records = cur.fetchall()
                if len(records) == 0:
                    # check for account
                    sql = f"SELECT * FROM members WHERE uid = '{event.source.user_id}'"
                    cur.execute(sql)
                    records = cur.fetchall()
                    if len(records) == 0:
                        msg = "you have not joined the ducknasty yet (/initiate)"
                    else:
                        # check flip choice
                        if listMsg[3] in ["heads", "head", "h", "tails", "tail", "t"]:
                            # check money
                            if int(records[0][2]) >= int(listMsg[2]) >= 0:
                                sql = f"UPDATE members SET money = {int(records[0][2]) - int(listMsg[2])} WHERE uid = '{event.source.user_id}';"
                                cur.execute(sql)
                                con.commit()
                                # /cf name amount head/tail
                                sql = f"INSERT INTO cf VALUES ('{listMsg[1]}', '{event.source.user_id}', '{listMsg[2]}','{listMsg[3]}');"
                                cur.execute(sql)
                                con.commit()
                                msg = f"betting {listMsg[2]} coins on {listMsg[3]}, to join type /cf join {listMsg[1]}"
                            else:
                                msg = "you do not have enough coins for this bet"
                        else:
                            msg = "flip choice invalid choose 'heads' or 'tails'"
                else:
                    msg = f"game name taken ({listMsg[1]})"
        # mute acknowledgements
        elif listMsg[0] == "/mute":
            sql = f"SELECT * FROM members WHERE uid = '{event.source.user_id}'"
            cur.execute(sql)
            records = cur.fetchall()
            if len(records) == 0:
                if len(listMsg) == 1:
                    msg = "you have not joined the ducknasty yet (/initiate)"
            else:
                if records[0][4] == 'F':
                    msg = "you have already muted acknowledgements"
                else:
                    sql = f"UPDATE members SET notifs = 'F' WHERE uid = '{event.source.user_id}';"
                    cur.execute(sql)
                    con.commit()
                    msg = "muted acknowledgements"
        elif listMsg[0] == "/unmute":
            sql = f"SELECT * FROM members WHERE uid = '{event.source.user_id}'"
            cur.execute(sql)
            records = cur.fetchall()
            if len(records) == 0:
                if len(listMsg) == 1:
                    msg = "you have not joined the ducknasty yet (/initiate)"
            else:
                if records[0][4] == 'T':
                    msg = "you have already unmuted acknowledgements"
                else:
                    sql = f"UPDATE members SET notifs = 'T' WHERE uid = '{event.source.user_id}';"
                    cur.execute(sql)
                    con.commit()
                    msg = "unmuted acknowledgements"
        # translator
        elif listMsg[0] == "/setlanguage":
            if len(listMsg) == 2:
                if listMsg[1] in googletrans.LANGUAGES.keys() or listMsg[1] == 'off':
                    sql = f"SELECT * FROM translator WHERE uid = '{event.source.user_id}'"
                    cur.execute(sql)
                    records = cur.fetchall()
                    if len(records) == 0:
                        sql = f"INSERT INTO translator VALUES ('{event.source.user_id}', '{listMsg[1]}');"
                        cur.execute(sql)
                        con.commit()
                        msg = "language preference set"
                    else:
                        sql = f"UPDATE translator SET language = '{listMsg[1]}' WHERE uid = '{event.source.user_id}';"
                        cur.execute(sql)
                        con.commit()
                        msg = "language preference updated"
                else:
                    msg = f"please enter valid language code: {googletrans.LANGUAGES.keys()}"
            else:
                msg = "incorrect syntax: /setlanguage [language]\ne.g. /setlanguage en\n or /setlanguage off to stop"
        elif listMsg[0][1:] in googletrans.LANGUAGES.keys() and origMsg[0] == "/":
            msg = f"{line_bot_api.get_group_member_profile(omcID, event.source.user_id).display_name}: {translator.translate(cmdBody, dest=listMsg[0][1:]).text}"

        # hidden commands
        elif listMsg[0] == "/rm":
            rich_menu_to_create = RichMenu(
                size=RichMenuSize(width=2500, height=843),
                selected=False,
                name="Nice richmenu",
                chat_bar_text="Tap here",
                areas=[RichMenuArea(
                    bounds=RichMenuBounds(x=0, y=0, width=2500, height=843),
                    action=URIAction(label='Go to line.me', uri='https://line.me'))]
            )
            rich_menu_id = line_bot_api.create_rich_menu(rich_menu=rich_menu_to_create)
            line_bot_api.link_rich_menu_to_user(event.source.user_id, rich_menu_id)
            reply = False
        elif listMsg[0] == "/push":
            line_bot_api.push_message(omcID, TextSendMessage(text=cmdBody))
        # reply with different msg contexts
        elif listMsg[0] == "/mt":
            msg = f"{origMsg}\n{userMsg}\n{listMsg}\n{cmdBody}"
        # grab msg ids
        elif listMsg[0] == "/msgi":
            msgtype = event.source.type
            msg = f"type: {msgtype}"
            if msgtype == 'group':
                msg += f"\ngid: {event.source.group_id}"
            if msgtype == 'room':
                msg += f"\nrid: {event.source.room_id}"
            msg += f"\nuid: {event.source.user_id}"
        # grab bot info
        elif listMsg[0] == "/bio":
            bot_info = line_bot_api.get_bot_info()
            msg = f"{bot_info.display_name}\n{bot_info.user_id}\n{bot_info.basic_id}\n{bot_info.premium_id}\n{bot_info.picture_url}\n{bot_info.chat_mode}\n{bot_info.mark_as_read_mode}"
        # test quacksly status
        elif listMsg[0] == "/test":
            msg = "up and running..."

        # reset tables
        elif listMsg[0] == "/ap":
            if event.source.user_id != ducks['Archie']:
                msg = "you lack authorisation for this command"
            else:
                try:
                    cur.execute(f"SELECT * FROM {listMsg[1]};")
                    records = cur.fetchall()
                    line_bot_api.push_message(ducks['Archie'], TextSendMessage(text=str(records)))
                except (Exception, psycopg2.Error):
                    pass
                cur.execute(f"DROP TABLE IF EXISTS {listMsg[1]};")
                sql = None
                if listMsg[1] == "members":
                    sql = '''CREATE TABLE members 
                        (uid TEXT PRIMARY KEY NOT NULL UNIQUE,
                        username	TEXT NOT NULL UNIQUE,
                        money	INT NOT NULL,
                        daily   TEXT,
                        notifs  TEXT);'''
                elif listMsg[1] == "ball":
                    sql = '''CREATE TABLE ball 
                        (username	TEXT PRIMARY KEY NOT NULL UNIQUE,
                        compliment	INT,
                        insult INT);'''
                elif listMsg[1] == "commands":
                    sql = '''CREATE TABLE commands 
                        (request	TEXT PRIMARY KEY NOT NULL UNIQUE,
                        response	TEXT NOT NULL);'''
                elif listMsg[1] == "jokes":
                    sql = '''CREATE TABLE jokes 
                        (id	    SERIAL PRIMARY KEY NOT NULL UNIQUE,
                        joke	TEXT NOT NULL);'''
                elif listMsg[1] == "compliments":
                    sql = '''CREATE TABLE compliments 
                        (id	    SERIAL PRIMARY KEY NOT NULL UNIQUE,
                        compliment	TEXT NOT NULL);'''
                elif listMsg[1] == "imagecs":
                    sql = '''CREATE TABLE imagecs 
                        (request	TEXT PRIMARY KEY NOT NULL UNIQUE,
                        response	TEXT NOT NULL,
                        creator     TEXT NOT NULL);'''
                elif listMsg[1] == "cf":
                    sql = '''CREATE TABLE cf
                        (name	TEXT PRIMARY KEY NOT NULL UNIQUE,
                        creator TEXT NOT NULL,
                        bet     	TEXT NOT NULL,
                        choice     TEXT NOT NULL);'''
                elif listMsg[1] == "neg":
                    sql = '''CREATE TABLE neg
                            (kicker	TEXT PRIMARY KEY NOT NULL UNIQUE,
                            lastkicked TEXT NOT NULL);'''
                elif listMsg[1] == "bot":
                    sql = '''CREATE TABLE bot
                            (command TEXT PRIMARY KEY NOT NULL UNIQUE,
                            response TEXT,
                            image TEXT,
                            paymin INT,
                            paymax INT,
                            cooldown INT,
                            lastused INT,
                            negresponse TEXT);'''
                elif listMsg[1] == "translator":
                    sql = '''CREATE TABLE translator
                        (uid	TEXT PRIMARY KEY NOT NULL UNIQUE,
                        language TEXT NOT NULL);'''
                cur.execute(sql)
                con.commit()
                msg = f"{listMsg[1]} table reset"

        elif listMsg[0] == "/reload" and event.source.user_id == ducks["Archie"]:
          logs = '''enter table log here'''.split('\n')
          for index in range(len(logs)):
            if index != 0:
              sql = f'''INSERT INTO {listMsg[1]} VALUES {logs[index]}'''
              cur.execute(sql)
              con.commit()
          msg = f"{listMsg[1]} records reloaded"
          
        ##### TEMP COMMANDS #####
        elif listMsg[0] == "/temp":
            if event.source.user_id != ducks['Archie']:
                msg = "you lack authorisation for this command"
            else:
                sql = f'''INSERT INTO bot VALUES ('/bath', 'https://i.pinimg.com/originals/f4/aa/76/f4aa7698c24366dc5f82fe8a97da2333.jpg', 'T', 20, 30, 3600, 0, 'I am not very dirty right now');'''
                cur.execute(sql)
                con.commit()
                msg = "command added"

        # test if command in db
        elif userMsg[0] == "/":
            req = listMsg[0]
            if len(listMsg) > 1:
                req = userMsg
            cur.execute(f"SELECT * FROM bot WHERE command = '{req}';")
            response = cur.fetchall()
            if len(response) == 0:
                cur.execute(f"SELECT * FROM commands WHERE request = '{req}';")
                response = cur.fetchall()
                if len(response) == 0:
                    cur.execute(f"SELECT * FROM imagecs WHERE request = '{req}';")
                    response = cur.fetchall()
                    if len(response) == 0:
                        msg = "i couldn't find that command"
                    else:
                        url = f"{response[0][1]}"
                        imageReply = True
                else:
                    msg = f"{response[0][1]}"
            else:
                sql = f"SELECT * FROM members WHERE uid = '{event.source.user_id}'"
                cur.execute(sql)
                records = cur.fetchall()
                if len(records) == 0:
                    msg = "you have not joined the ducknasty yet (/initiate)"
                else:
                    msgs = []
                    m_id, m_un, m_csh, m_day, m_not = records[0]
                    r_cmd, r_res, r_img, r_pmin, r_pmax, r_cd, r_lu, r_nr = response[0]
                    usetime = t()
                    if usetime < r_cd + r_lu:
                        msg = r_nr
                    else:
                        payout = randint(r_pmin, r_pmax)
                        sql = f"UPDATE members SET money = {m_csh + payout} WHERE uid = '{event.source.user_id}';"
                        cur.execute(sql)
                        con.commit()
                        sql = f"UPDATE bot SET lastused = {usetime} WHERE command = '{r_cmd}';"
                        cur.execute(sql)
                        con.commit()
                        if r_img == "T":
                            msgs += [ImageSendMessage(original_content_url=r_res, preview_image_url=r_res)]
                        else:
                            msgs += [TextSendMessage(text=r_res)]
                        msgs += [TextSendMessage(text=f"Thank you! Here's a {payout} coin tip ^>^")]
                        line_bot_api.reply_message(event.reply_token, msgs)
                        reply = False

        # message is not intended for duckbot
        else:
            # daily coins
            sql = f"SELECT * FROM members WHERE uid = '{event.source.user_id}'"
            cur.execute(sql)
            records = cur.fetchall()
            if len(records) != 0:
                member = records[0]
                # if one day since last collection
                if str(date.today()) != str(member[3]):
                    sql = f"UPDATE members SET money = {int(member[2]) + 50}, daily = '{date.today()}' WHERE uid = '{event.source.user_id}';"
                    cur.execute(sql)
                    con.commit()
                    if member[4] == "T":
                        msg = "+50 daily coins"
                    else:
                        reply = False
            else:
                reply = False

            # translator
            '''
            if len(origMsg) > 3:
                srcLanguage = translator.detect(str(origMsg)).lang
                sql = f"SELECT uid, language FROM translator WHERE language != '{srcLanguage}' AND language != 'off';"
                cur.execute(sql)
                records = cur.fetchall()
                if len(records) != 0:
                    for record in records:
                        line_bot_api.push_message(record[0], TextSendMessage(text=line_bot_api.get_group_member_profile(omcID, event.source.user_id).display_name + ": " + translator.translate(origMsg, dest=record[1]).text))
            '''
    # end exception handling
    except (Exception, psycopg2.Error) as e:
        msg = f"error: {e}"
    finally:
        if con:
            cur.close()
            con.close()

    # attuned response
    if reply:
        if imageReply:
            message = ImageSendMessage(original_content_url=url, preview_image_url=url)
        else:
            message = TextSendMessage(text=msg)
        line_bot_api.reply_message(event.reply_token, message)


if __name__ == "__main__":
    port = int(os.environ.get('PORT', 5000))
    DATABASE_URL = os.environ['DATABASE_URL']
    app.run(host='0.0.0.0', port=port)
# git add .
# git commit -am ""
# git push heroku master
