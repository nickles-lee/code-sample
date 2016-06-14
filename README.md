# Overview:

## network\_bench\_logger

This was a project that was developed at a hackathon
for surveying network conditions for users on a train.

This is meant to be paired with an iOS app that collects
metrics related to the current data network, be it WiFi or
cellular. Due to permission restrictions, it was necessary
to measure network quality as ping times and packet loss rates.

The iOS code is not included, as I only did architecture work
on that, and the code was written by a team member.

The backend was written fully by me, and its primary function is
in resolving a train_id and a timestamp down to interpolated GPS
coordinates in order to avoid GPS polling, which drains phone
batteries. It is currently nonfunctional because the API key
(which should have been put in its own module) expired at
the end of the weekend.

###	files:
* backend.py: Quick Flask server that accepts JSON and publishes to Kafka
* bootstrap.sh: Shell script that spins up a local Kafka topic/Elastic index
* lpgps.py: Contains logic for retrieving train route info (polymap format)
  and approximating GPS coordinate from timestamp.
* requirements.txt: Everyone's favorite way to document Python dependencies
* start_logstash.sh: Basic Logstash connector for ingesting to ES from Kafka

Unfortunately the Elastic mapping is missing

## auth\_forwarder:
This is part of a very quick 3 hour hack that is designed to facilitate
easier sign-ins to a webapp. The original workflow was that users would
provide their credentials in a form, and they would be issued a 24 hour
ephemeral login, which they would have to manually authenticate with.

The alternate workflow that was developed was:

1. Enter information into app, where it will be saved for future use
2. Submit info to Flask service, which queries the legacy credential server
3. Credentials are received from the credential server
4. A "create session" request is sent to the WebApp, and session is created
5. The user is redirected to the login page for the webapp, and necessary
	authentication information is appended as GET parameters.

   This is not secure, but after discussion with the people running the app,
and considering the 24-hour ephemeral nature of the logins, we ruled this
an acceptable risk.
6. The WebApp has no awareness of the GET parameters that injected.
7. JS Injection via a Chrome/Firefox extension occurs, session cookies are
	set, and the user is dropped into an authenticated session.

###	files:
* auth_forwarder.py: Handles credential request & session setup
* content_script.js: Content Script from Chrome Extension, used for JS
	injection to set session cookies and redirect to user session.

### Impact:
45 second manual process is reduced to a 5 second automatic process
