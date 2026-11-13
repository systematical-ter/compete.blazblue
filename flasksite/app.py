import configparser
import datetime
import html
import re

import calendarpi
import dateutil
from flask import Flask, render_template, url_for

app = Flask(__name__)

config = configparser.ConfigParser()
config.optionxform = str # type: ignore
config.read("config.env")
calendars = config['CALENDARS']
colors = config['COLORS']

# Source - https://stackoverflow.com/a/2003896
# Posted by Roger Pate
# Retrieved 2026-11-07, License - CC BY-SA 2.5
# Modified to only return a single date (the sunday of this week)
def get_sunday(date):
  """Return the full week (Sunday first) of the week containing the given date.

  'date' may be a datetime or date instance (the same type is returned).
  """
  day_idx = (date.weekday() + 1) % 7  # turn sunday into 0, monday into 1, etc.
  sunday = date - datetime.timedelta(days=day_idx)
  return sunday

def clean_item(item: str) -> str :
    # remove spans
    item = item.replace("<span>","")\
                .replace("</span>","")

    # remove brs
    item = item.replace("<br>","") \
                .replace("<br/>","")

    # strip whitespaces
    item = item.strip()

    return item

def strip_list_items(event_desc) -> dict:
    # strip out exactly the items in the first unordered list found
    # then use html.escape to ensure nothing weird is in them

    list_reg = r"<ul>.+?<\/ul>"
    list_item_reg = r"<li>(?P<content>.+?)<\/li>"

    res = {"items":[]}

    list_res = re.search(list_reg, event_desc)
    if list_res is None:
        return res

    item_res = re.findall(list_item_reg, list_res.group())
    if item_res is None:
        return res

    for item in item_res:
        res['items'].append(html.escape(clean_item(item), quote=False))

    return res

def strip_info_from_description(event_desc):
    # Strip out particular information of interest from the event description
    # Why?
    #   Doesn't seem like google does any sanitization of event descriptions.
    #   Quick searches show several wordpress vulnerabilities because it
    #       straight renders google event descriptions.
    #   While it'd be reasonable to assume that since only like, one person
    #       has the ability to create events, they should be safe...
    #       a failure could be so bad so fast without any warning that
    #       I don't really want to fuck with the chance.
    #   So I'm just looking at how the event descriptions are usually
    #       constructed and using that to guesstimate how I can peel out
    #       points of interest to display.
    # Warning:
    #   THIS IS VERY FRAGILE.
    #   It more or less depends on Eterna always putting the bracket details
    #       as a bulleted list.
    #   Is what it is; this is fine for a first solution.

    if "thun" in event_desc:
        print(event_desc)
    twitch_link = r"(?P<url>twitch\.tv\/[a-zA-Z_0-9]+)($|&amp;sa=.+|\")"
    discord_link = r"(?P<url>discord\.gg\/[a-zA-Z_0-9]+)($|&amp;sa=.+|\")"
    twitter_link = r"(?P<url>x\.com\/[a-zA-Z_0-9]+)($|&amp;sa=.+|\"|\?s=20)"
    matcherino_link = r"(?P<url>matcherino\.com\/t\/[a-zA-Z_0-9]+)($|&amp;sa=.+|\")"
    bracket_link = r"(?P<url>start\.gg\/(tournament\/)?[a-zA-Z0-9_\-]+)(\/details|$|&amp;sa=.+|\")"
    challonge_link = r"(?P<url>challonge\.com\/(communities\/)?[a-zA-Z0-9]+)($|&amp;sa=.+|\")"
    youtube_link = r"(?P<url>youtube\.com\/@[a-zA-Z]+)(\/featured|$|&amp;sa=.+|\")"

    # google LOVES putting their own bullshit in front of some links!!!
    image_link = r"(&quot;|\")<a href=\"(https://www.google.com/url\?q=)*(?P<url>.+?)(\"|&amp;)"

    twch = re.search(twitch_link, event_desc)
    di = re.search(discord_link, event_desc)
    twit = re.search(twitter_link, event_desc)
    ma = re.search(matcherino_link, event_desc)
    br = re.search(bracket_link, event_desc)
    ch = re.search(challonge_link, event_desc)
    yt = re.search(youtube_link, event_desc)

    details = strip_list_items(event_desc)

    # TODO: also copy out the tags, can use that to filter on the site later

    image = re.search(image_link, event_desc)

    res = {'details': '', 'links': {}}

    if twch is not None:
        res['links']['twitch'] = twch.groupdict()['url']
    if yt is not None:
        res['links']['youtube'] = yt.groupdict()['url']
    if di is not None:
        res['links']['discord'] = di.groupdict()['url']
    if twit is not None:
        res['links']['twitter'] = twit.groupdict()['url']
    if ma is not None:
        res['links']['matcherino'] = ma.groupdict()['url']
    if br is not None:
        res['links']['start'] = br.groupdict()['url']
    if ch is not None:
        res['links']['challonge'] = ch.groupdict()['url']
    if details is not None:
        res['details'] = details['items']
    if image is not None:
        res['image'] = html.escape(image.groupdict()['url'])

    return res

@app.route('/')
def home():

    thisweek_events = []
    this_sunday = get_sunday(datetime.datetime.now(tz=datetime.UTC))
    min_date = this_sunday + datetime.timedelta()
    max_date = this_sunday + datetime.timedelta(days=20)

    print(list(colors.keys()))
    ev = {}
    for calendar, url in calendars.items():
        if calendar is not None:
            ev[calendar] = calendarpi.get_events(min_date, max_date, url)
    if len(ev.keys()) == 0:
        return render_template('error.html', message="No events returned...")

    i = 0
    for key in ev:  # noqa: PLC0206
        for event in ev[key]:
            event['id'] = i
            i +=1
            # fetch stripped out URLs and details
            dat = strip_info_from_description(event['description'])
            event['start']['dateObj'] = dateutil.parser.isoparse(event['start']['dateTime'])
            event['links'] = dat.get('links', [])
            event['details'] = dat.get('details', [])
            event['image'] = dat.get('image',url_for('static', filename='images/missing_image.png'))
            
            # remove some substrings.
            event['summary'] = event['summary'].replace("Series Event - ","").replace("Event Series: ","")

            # nuke all HTML symbols in the event name so if someone tries to do injection stuff it just word vomits
            event['summary'] = html.escape(event['summary'], quote=False)
            event['calendar'] = key
            thisweek_events.append(event)

    thisweek_events.sort(key=lambda event: event['start']['dateTime'])

    return render_template('calendar.html', now=datetime.datetime.now(datetime.UTC), events=ev, colors=colors, thisweek_events=thisweek_events, min_date=min_date, max_date=max_date)

@app.route("/" + config["GOOGLE"]["google_verification"])
def google_site_verf():
    return render_template(config["GOOGLE"]["google_verification"])
