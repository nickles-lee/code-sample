#!/usr/bin/python3

import requests
from flask import Flask, request, send_from_directory, redirect
import time
import re

app = Flask(__name__, static_url_path='')


@app.route('/is_a_goat')
def is_a_goat(goat):
    return True


@app.route('/', methods=['GET'])
def serve_landing():
    return send_from_directory('.', 'index.html')


@app.route('/request_login', methods=['POST'])
def request_login():
    # Request auth tokens
    auth_page = requests.get('https://REDACTED_SIGN_IN.herokuapp.com/')
    token = re.search("(name=\"authenticity_token\" value=)\"(.*)\"", auth_page.text, re.M)
    token = auth_page.text[token.start() + 33:token.end() - 1]

    print("Requested auth tokens")
    # Prepare credential request
    headers = {'Origin': ' https', 'Accept-Language': ' en-US,en;q=0.8', 'Accept-Encoding': ' gzip, deflate',
               'Accept': ' text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
               'User-Agent': ' Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_4) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/50.0.2661.75 Safari/537.36',
               'Connection': ' keep-alive',
               'Cookie': ' _login_dialer_session={}'.format(auth_page.cookies.get('_login_dialer_session')),
               # 'Cookie': ' _login_dialer_session=UVNZdUhXYlR2Wjd4b1JOdUM0MmIvZnNNTmtQS1lNbUZTb0JlMGIwUDVId0pQYkVEWUJVajQvMjRyUlJ6T1I2cE1JVUZFaTRuNUg5RTFITWZCZVBabWE4YlYyMWpYN3VwOHNSbFlUcXlTR2JKbmRLcGIwaUdFN3VLbzB3UEphWVBFVkEySkJBMmJ0b1RpYkF4TXdQYmpnPT0tLXRFMndQNTRYRjNoMnFZQS9FVWdTV1E9PQ%3D%3D--cb8e68ac584c7e1edcfe0a32542e7652b070e0fb',
               'Cache-Control': ' max-age=0', 'Referer': ' https', 'Upgrade-Insecure-Requests': ' 1',
               'Content-Type': ' application/x-www-form-urlencoded'}

    form_data = {}
    form_data['utf8'] = request.form['utf8']
    form_data['authenticity_token'] = token
    if form_data['authenticity_token'] is None:
        return "Fail"
    form_data['signup[firstname]'] = request.form['signup[firstname]']
    form_data['signup[lastname]'] = request.form['signup[lastname]']
    form_data['signup[email]'] = request.form['signup[email]']
    form_data['signup[zip]'] = request.form['signup[zip]']
    form_data['signup[calling_from]'] = request.form['signup[calling_from]']
    form_data['signup[spanish]'] = request.form['signup[spanish]']
    form_data['commit'] = request.form['commit']

    r = requests.post('https://REDACTED_SIGN_IN.herokuapp.com/signups', data=form_data, headers=headers)
    print("Requested credentials")
    # Takes credential result page as input, returns LiveVox credentials
    acct = re.search("(\\t\\t\\t<div class=\"account\">\\n\\t\\t\\t\\t<h3>)(.*)(</h3>)", r.text, re.M)
    passwd = re.search("(\\t\\t\\t<div class=\"password\">\\n\\t\\t\\t\\t<h3>)(.*)(</h3>)", r.text, re.M)

    acct = r.text[acct.start() + 33:acct.end() - 5]
    passwd = r.text[passwd.start() + 34:passwd.end() - 5]
    print("Scraped account details successfully.")

    # Prepare LiveVox login forms
    skill_id = get_target_skillId(acct)
    vox_login_post_data = {
        'agentLoginID': acct,
        'client_id': 71623,
        'extension': 1234,
        'login_page': 'https://lvacd.livevox.com//CLIENTID/AgentLogin',
        'password': passwd,
        'skillID': skill_id}
    print("Requested Vox session")
    vox_login = requests.post('https://lvacd.livevox.com/VirtualACD_2.8.119/Logon', vox_login_post_data)

    vox_session_id = vox_login.cookies.get('JSESSIONID')
    vox_session_token = vox_login.headers.get('token')
    print("Redirecting user")
    return redirect(
        "https://na3.livevox.com/CLIENTID/AgentLogin?&jsessionid={}&token={}&agentName={}".format(vox_session_id,
                                                                                                       vox_session_token,
                                                                                                       acct), code=302)


def get_target_skillId(username):
    print("Retrieved Skill_ID in top position")
    base_url = 'https://lvacd.livevox.com/VirtualACD_2.8.119/GetAgentDetail?&agentLoginID={}&_={}&client_id=71623'.format(
        username, time.time() * 1000)
    r = requests.get(base_url, data={'client_id': 71623})
    return r.json()['skills'][0]['skillID']


if __name__ == '__main__':
    # app.run(host='0.0.0.0', port=5001)
    app.run(host='0.0.0.0', port=80)