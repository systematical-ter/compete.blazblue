import datetime
import html
import re

import cloudlib
from flask import Flask, render_template

app = Flask(__name__)

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

    twitch_link = r"(?P<url>twitch\.tv\/[a-zA-Z_0-9]+)($|&amp;sa=.+)"
    discord_link = r"(?P<url>discord.gg\/[a-zA-Z_0-9]+)($|&amp;sa=.+)"
    twitter_link = r"(?P<url>x.com\/[a-zA-Z_0-9]+)($|&amp;sa=.+)"
    matcherino_link = r"(?P<url>matcherino.com\/t\/[a-zA-Z_0-9]+)($|&amp;sa=.+)"
    bracket_link = r"(?P<url>start.gg\/[a-zA-Z0-9]+)($|&amp;sa=.+)"

    bracket_details = r"(?P<details>Bracket Details:<ul>.+<\/ul>)<br>"

    twch = re.search(twitch_link, event_desc)
    di = re.search(discord_link, event_desc)
    twit = re.search(twitter_link, event_desc)
    ma = re.search(matcherino_link, event_desc)
    br = re.search(bracket_link, event_desc)

    details = re.search(bracket_details, event_desc)
    # TODO: do additional stuff to forcibly pull out only the list items
    #   because right now someone can still inject whatever they want potentially

    # TODO: also copy out the tags, can use that to filter on the site later

    # TODO: Maybe also copy out the images lmao

    res = {'details': '', 'links': {}}

    if twch is not None:
        res['links']['twitch'] = twch.groupdict()['url']
    if di is not None:
        res['links']['discord'] = di.groupdict()['url']
    if twit is not None:
        res['links']['twitter'] = twit.groupdict()['url']
    if ma is not None:
        res['links']['matcherino'] = ma.groupdict()['url']
    if br is not None:
        res['links']['bracket'] = br.groupdict()['url']
    if details is not None:
        res['details'] = details.groupdict()['details']

    return res

@app.route('/')
def home():

    today_events = []
    this_sunday = get_sunday(datetime.datetime.now(tz=datetime.UTC))
    min_date = this_sunday + datetime.timedelta()
    max_date = this_sunday + datetime.timedelta(days=20)

    ev = cloudlib.get_events(min_date, max_date)
    if ev is None:
        return render_template('error.html', message="No events returned...")
    
    for event in ev:
        # fetch stripped out URLs and details
        dat = strip_info_from_description(event['description'])
        event['links'] = dat['links']
        event['details'] = dat['details']
        
        # remove some substrings.
        event['summary'] = event['summary'].replace("Series Event - ","").replace("Event Series: ","")

        # nuke all HTML symbols in the event name so if someone tries to do injection stuff it just word vomits
        event['summary'] = html.escape(event['summary'], quote=False)

        today_events.append(event)

    return render_template('calendar.html', events=ev, today_events=today_events, min_date=min_date, max_date=max_date)