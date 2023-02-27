from flask import Flask, render_template, request, url_for, redirect, flash, session
import time, threading, logging
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
    if request.method == "POST":
        if helpers.database.users.check_user(request.form['user']):
            session["user"] = request.form["user"]
            flash("Login successful")
        else:
            helpers.database.users.create_user(request.form['user'])
            flash(f"Login created: {request.form['user']}")
        return redirect('/')
    return render_template("login.html")

@app.route('/logout')
def web_logout():
    if "user" in session:
        session.pop("user")
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
    
def run_the_task():
    helpers.tasks.anime_task()

scheduler = BackgroundScheduler()
scheduler.add_job(func=run_the_task, trigger="interval", minutes=10)
scheduler.start()

if __name__ == "__main__":
    app.run(host='0.0.0.0')