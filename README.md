# Compete.Blazblue.Link

![site header](https://github.com/systematical-ter/compete.blazblue/blob/main/flasksite/static/images/header_shorter.png?raw=true)

A site that is a mirror of the data stored in the Wheel of Fate BBCF Calendar, available here: [compete.blazblue.link](https://compete.blazblue.link).

Purpose of this site is to make it easier for people to see the contents of the calendar, so they can stay aprised of current BBCF tournaments.

Functionally, the site is a simple Flask app that uses the Google Cloud API to pull information from the google calendar behind the Wheel of Fate. Tailwindcss is used to make it slightly prettier, and [vkurko's calendar js library](github.com/vkurko/calendar) is used for the calendar view.

# Setup

Two sets of dependences: Python and npm.

For Python, I _highly_ recommend the UV package manager. Simply download this repository and use `uv sync` to download the dependencies.

Tailwindcss, in this case, was installed using npx. If you don't want to do that, I've also had plenty of luck using the CLI directly instead. [Instructions are here](https://tailwindcss.com/docs/installation/tailwind-cli), follow the link that says "standalone executable".

# Requirements

There are a few keys and the like that I've kept private, and you will have to generate yourself.

## Google Credentials

The `service-credentials.json` that is referenced by `cloudlib.py` stores the credentials provided by google. Scroll to the service account instructions on the [google help page here](https://developers.google.com/workspace/guides/create-credentials). Download the `.json` file generated when you create a key for this service account and save it as `service_credentials.json` in the root of this project directory.

## Other Configurations

There's a few more details that I've kept private in a `config.env` file for security reasons. Use `EXAMPLE_ENV` as an idea for structure.

The `[GOOGLE]` section stores google verification information. If you try to verify your website for google search indexing using a specific method, it'll ask you to upload a file. Drop the file into `flasksite/static/templates` and put the name of the file here if you do that. If you don't, just set it to NONE and don't visit `(site address)/NONE`, because it'll return (probably) a 500 error.

The `CALENDARS` section stores the url of calendars you're operating on. You get this by having the calendar on your calendar list, going to "settings", and under "Integration Settings" there should be a "calendar id".

The `COLORS` section stores colors for the calendars you're operating on. Just put a hex code for each calendar. Make sure that the keys match. The site WILL crash if this isn't done properly atm.

# Development

To dev, have these two applications running:

Tailwind, to update pages + styles:
```
npx @tailwindcss/cli -i ./flasksite/static/styles/input.css -o ./flasksite/static/styles/output.css --watch
```

Or, if you are using the standalone executable:

```
tailwindcss -i ./flasksite/static/styles/input.css -o ./flasksite/static/styles/output.css --watch
```

Then, actually run flask:
```
cd flasksite
uv run flask run --debug --host 0.0.0.0
```

# Deployment

Coming soon.

The short of it is, you have to set up `gunicorn` and `nginx`, at least if you want to perfectly replicate what I did. You'll also probably want to run `let's cert`. 