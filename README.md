# Find Store

Command-line application that directs a user to the store nearest to the address they provide.

# Dependencies
Developed and tested using:
* Python 2.7.12
* Pytest 4.3.0 for python 2.7
* Sqlite3

# Instructions
1. Clone or download this entire repository
1. Get a Google Maps API key, then use it to set the API_KEY variable in secrets.py
1. `chmod +x find_stores.py`
1. `./find_stores.py --zip=<zip> etc.`
1. To run test suite: `pytest`

# Developer Notes
Caveat: to run strictly according to spec (for example, find_store --address="address"), you must do the following:
1. Add this app's directory to your PATH
1. `ln -s find_stores.py find_stores`
1. `chmod +x find_stores.py`

## Assumptions and Methodology:
* I defaulted the output parameter to text, and the units parameter to miles.
* I use the Google Maps Geocode API to gather the latitude and longitude of the user's inputted address. That is the only time I make the call, as the store location directory already contains those values.
* I converted the .csv file to a sqlite3 database. It is held in memory and doesn't take much more room than the raw text, and I thought it would come in handy. Jury's out on whether it actually came in handy, but I generally like data inside databases, and if this were a production application, it makes sense to persist this sort of information.
* I absolutely refuse to commit API keys in code, so I set up a secrets file (secrets.py) where you can insert your own, or if you need one, I can provide it to you in a more secure way than committing it to a Github repo. :)
* All in all, I implemented this in 6 hours, about 2 hours actually implementing the script, 1 hour learning about how to calculate distances on the surface of an ellipsoidal planet, and the rest of the time setting up the tests, db, etc. as lightweight as possible.
* I had a surprising amount of fun with this, thank you for the opportunity.

## Findings and Apologies:
* The Google geocode API accepts zip codes as valid address input, so the --zip parameter can be viewed as extraneous.
* In the same vein, the API also accepts 'asdf' as a valid address, etc., and will give the user a result. I did not implement any checking of the address or zip code fields.
* I implemented what I consider a meager number of tests, but hopefully I demonstrated enough competency with mocks and assertions, and illustrated my general pattern of unit testing. There is one integration test that actually calls the Google Maps API. The rest are mocked/straight input-output tests to optimize for test suite runtime.

```
Find Store
  find_store will locate the nearest store (as the crow flies) from stores.db,
  print the matching store address, as well as the distance to that store.

Usage:
  find_store --address="<address>"
  find_store --address="<address>" [--units=(mi|km)] [--output=text|json]
  find_store --zip=<zip>
  find_store --zip=<zip> [--units=(mi|km)] [--output=text|json]

Options:
  --zip=<zip>          Find nearest store to this zip code. If there are multiple best-matches, return the first.
  --address            Find nearest store to this address. If there are multiple best-matches, return the first.
  --units=(mi|km)      Display units in miles or kilometers [default: mi]
  --output=(text|json) Output in human-readable text, or in JSON (e.g. machine-readable) [default: text]

Example
  find_store --address="1770 Union St, San Francisco, CA 94123"
  find_store --zip=94115 --units=km
```
