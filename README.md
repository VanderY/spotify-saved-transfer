# Spotify saved tracks transferer

You can transfer saved tracks from one account to another
with the help of this simple script.

## Installation
Copy `.env.example` file and paste it as `.env`

```shell
cp .env.example .env
```

Go to [spotify for developers](https://developer.spotify.com/)
and log in to your account. Then click to your username and go to dashboard.
Click create new app and fill in required fields.

**Important:** fill `http://localhost:8888/` in `redirect URI` field
and check `Web API` in `Which API/SDKs are you planning to use?` section.

Click save and go to setting of this application.
You need to copy `Cliend ID` and `Client Secret` and paste it in `.env` file.

Install dependencies

```shell
pip install -r requirements.txt
```

---

## Usage

Simply run
```shell
python3 main.py
```

Immediately after start you'll be asked to log in to account.
Log in account, **from which** you want to pull tracks. 

After successful login in terminal you will see list of all saved on this account tracks.
Then follow instructions in terminal, log in account, where you want to push your tracks
and watch it doing its job.

---