from flask import Flask, render_template, request, url_for, redirect, flash, session
import time, threading, logging, requests, os
from dotenv import load_dotenv
from apscheduler.schedulers.background import BackgroundScheduler


import helpers.scrapers.subsplease
import helpers.database.anime
import helpers.database.users
import helpers.database.webhook
import helpers.tasks


app = Flask(__name__, static_url_path='/static')
app.config['DEBUG'] = True
app.config['secret'] = 'rahasiawoi'
app.secret_key = 'rahasia banget woi'
app.config['SESSION_TYPE'] = 'filesystem'
load_dotenv()
CLIENT_ID = "1079833951796994058"
REDIRECT_URI = os.getenv("URL") + "/login/discord/callback"
CLIENT_SECRET = "Y_hDpNwVMhxYBdM7_bldlXdX91ykjizh"


@app.route('/')
def web_home():
    if "user" in session:
        user = session['user']
    else:
        user = None
    watchlist = helpers.database.anime.get_watchlist(user)
    providers = ["subsplease"]
    return render_template('index.html', watchlist = watchlist, user = user)

@app.route('/login', methods = ["GET", "POST"])
def web_login():
    if "user" in session:
        flash("You already log in")
        return redirect("/")
    discord_login_url = f"https://discord.com/api/oauth2/authorize?client_id={CLIENT_ID}&redirect_uri={REDIRECT_URI}&response_type=code&scope=identify"
    return redirect(discord_login_url)

@app.route("/login/discord/callback")
def login_discord_callback():
    code = request.args.get("code")
    payload = {
        "client_id": CLIENT_ID,
        "client_secret": CLIENT_SECRET,
        "grant_type": "authorization_code",
        "code": code,
        "redirect_uri": REDIRECT_URI,
        "scope": "identify"
    }
    headers = {
        "Content-Type": "application/x-www-form-urlencoded"
    }
    token_response = requests.post("https://discord.com/api/oauth2/token", data=payload, headers=headers)
    access_token = token_response.json()["access_token"]
    headers = {
        "Authorization": f"Bearer {access_token}"
    }
    user_response = requests.get("https://discord.com/api/users/@me", headers=headers)
    user_data = user_response.json()

    session["user"] = user_data["id"]
    session["discord_username"] = user_data['username']
    session["discord_avatar_url"] = f"https://cdn.discordapp.com/avatars/{user_data['id']}/{user_data['avatar']}.png"
    if helpers.database.users.check_user(user_data["id"])["status"]:
        flash("Login successful")
    else:
        helpers.database.users.create_user(user_data["id"])
        flash(f"Login created: {user_data['username']}")
    return redirect('/')


@app.route('/logout')
def web_logout():
    if "user" in session:
        session.pop("user", None)
        session.pop("discord_avatar_url", None)
        session.pop("discord_username", None)
        flash("Logout successful")
        return redirect("/")
    flash("You not log in")
    return redirect("/")

@app.route('/add', methods = ['GET', 'POST'])
def web_add_anime():
    if "user" not in session:
        flash("Please login")
        return redirect("/")
    if request.method == "POST":
        user = session['user']
        provider = request.form["provider"].lower()
        anime_watchlist = request.form.to_dict(flat=False)['anime_name']
        for anime in anime_watchlist:
            in_watchlist = helpers.database.anime.get_watchlist(user)['data']
            if {"provider": provider, "anime_name": anime} not in in_watchlist:
                helpers.database.anime.add_watchlist(user, provider, anime)
        flash('Anime has been added to your watchlist')
        return redirect('/')
    subsplease = sorted(helpers.scrapers.subsplease.get_schedule())
    watchlist = helpers.database.anime.get_watchlist(session['user'])
    anime_data = {'Subsplease': subsplease}
    return render_template('anime/add_anime.html', anime_data = anime_data, watchlist=watchlist)

@app.route('/delete')
def web_delete_anime():
    if request.args.get('id') == None or request.args.get('provider') == None or request.args.get('anime_name') == None :
        return redirect('/')
    helpers.database.anime.delete_watchlist(request.args.get('id'), request.args.get('provider'), request.args.get('anime_name'))
    flash('Watchlist deleted')
    return redirect('/')
    

@app.route('/webhook', methods=['GET', 'POST'])
def web_webhook():
    if "user" not in session:
        flash("Please login")
        return redirect("/")
    
    user = session['user']
    if request.method == "POST":
        webhook = request.form['webhook']
        url = request.form['url']
        helpers.database.webhook.add_webhook(user, webhook, url)
        flash("Added your webhook url for anime")
        return redirect('/')

    webhook_data = helpers.database.webhook.get_url(user)
    return render_template('webhook/add.html', webhook_data=webhook_data)

@app.route('/test')
def web_test():
    print(session['user'])
    return "OK"

def run_the_task():
    print("[Scheduler] Running task")
    helpers.tasks.anime_task()

scheduler = BackgroundScheduler()
scheduler.add_job(func=run_the_task, trigger="interval", minutes=10)
scheduler.start()

if __name__ == "__main__":
    app.run(host='0.0.0.0')