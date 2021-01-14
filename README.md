#Wilmacrawler
Have you ever wondered, how nice it would be if you could have an API to Wilma, the communication platform used in public education in Finland?
Have you ever wondered, how nice would it be to have your schedule for the week automatically updated as your background image?

Wonder no more! This is my solution to those and many other wonders.

**Wilmacrawler** is uses Selenium to crawl the Wilma website, and presents the various information as a simple, one-call REST API.

####Disclaimer
You must host the server yourself, because as developer of this library, I cannot take the responsibility of handling other people's login credentials. 

Also, please keep in mind that xposing the API in it current state to the public internet is a security vulnerability. Even though no sensitive information is exposed, Python's `HTTPServer` isn't meant for public production, and has no protection against even rudimentary attacs. 

This project is solely meant to be used in a closed LAN network with no conceivable outside threats.

**Also, keep in mind that you are going to be storing your login credentials into a plain-text file, meaning that they are vulnerable to be compromised. Only do this if you are confident in your server's security, and other people using it.**

Unfortunately, as long as there isn't an official API, this is the only way.  

## 
1. Clone this repo into your computer and `cd` into it.
2. Activate the `virtualenv`: `chmod +x venv/bin/activate; venv/bin/activate`
2. Install dependencies: `pip3 install -r requirements.txt`.
3. Download latest geckodriver that suits your system from https://github.com/mozilla/geckodriver/releases.
4. Unzip the download, and place the unzipped file "geckodriver" somewhere in your `PATH`, for example `/usr/sbin/`.
5. Into the root of this repo, make a file called `credentials`. Type your Wilma username to the first line, and password to the second.
6. Now you can run `python3 src/server.py <address> <port>`. To accept connections from any address, set `<address>` to `"any"`.

##API
To get a response, send a `GET` request to the port you selected. Path doesn't matter.
The first request takes a while, but a cache is implemented for subsequent requests. 

If you want, you can have a look at an example respose at `samples/example_response.json`

As a response, you get a JSON object. The structure of the response is explained below:

The response has three top-level keys: `courses`, `teachers`, and `upcoming`.

`teachers` contains all your current semester's teachers. An entry for a teacher looks like this:
```json
{
    "long_name": "Hägar the Horrible",
    "role": "Fencing and Robberies",
    "short_name": "HOR"
    "email": "xXx_hägar.horrible101-xXx@live.no",
},
```
`short_name` is used as the key for an entry, and teachers are referenced throughout the response by it. 

`courses` contains all your current semester's classes as keys. Each key has a value, which looks like this:
```json
{
  "homework": [
    {
      "given_on": "2021-01-08",
      "homework": "grammar exercises 16,17 as homework"
    },
    {
      "given_on": "2021-01-07",
      "homework": "exercises 4 C + D"
    },
    ...
  ],
  "lesson_diary": [
    {
      "date": "2021-02-03",
      "lesson_number": "19",
      "lesson_topic": "evaluation day = arviointipäivä"
    },
    {
      "date": "2021-01-26",
      "lesson_number": "18",
      "lesson_topic": ""
    },
    ...
  ],
  "teacher": "SAA",
  "title": "ENA05.5"
}
```

`upcoming` represents all the upcoming events – usually your schedule. It is an array containing objects, each with `date` and `events` – an array of event objects:
```json
{
  "course": "LI01.13",
  "end_time": "9:45",
  "nth_lesson": 0,
  "room": "LI1",
  "start_time": "8:30",
  "type": "lesson"
},
```
Pretty self-explanatory, right?

##TODO
- [x] Implement schedule data retrieval
- [x] Implement homework and lesson diary data retrieval
- [ ] Complete teacher data retrival
- [ ] Implement reading messages, news, announcements, class selection etc.
