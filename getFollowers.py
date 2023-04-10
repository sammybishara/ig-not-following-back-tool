from selenium import webdriver
from selenium.webdriver.firefox.options import Options
from argparse import ArgumentParser
from glob import glob
from os.path import expanduser
from platform import system
from sqlite3 import OperationalError, connect
from instaloader import Instaloader, Profile, ConnectionException

def get_cookiefile():
    default_cookiefile = {
        "Windows": "~/AppData/Roaming/Mozilla/Firefox/Profiles/*/cookies.sqlite",
        "Darwin": "~/Library/Application Support/Firefox/Profiles/*/cookies.sqlite",
    }.get(system(), "~/.mozilla/firefox/*/cookies.sqlite")
    cookiefiles = glob(expanduser(default_cookiefile))
    if not cookiefiles:
        raise SystemExit("No Firefox cookies.sqlite file found. Use -c COOKIEFILE.")
    return cookiefiles[0]


def import_session(cookiefile, sessionfile):
    print("Using cookies from {}.".format(cookiefile))
    conn = connect(f"file:{cookiefile}?immutable=1", uri=True)
    try:
        cookie_data = conn.execute(
            "SELECT name, value FROM moz_cookies WHERE baseDomain='instagram.com'"
        )
    except OperationalError:
        cookie_data = conn.execute(
            "SELECT name, value FROM moz_cookies WHERE host LIKE '%instagram.com'"
        )
    instaloader = Instaloader(max_connection_attempts=1)
    instaloader.context._session.cookies.update(cookie_data)
    username = instaloader.test_login()
    if not username:
        raise SystemExit("Not logged in. Are you logged in successfully in Firefox?")
    print("Imported session cookie for {}.".format(username))
    instaloader.context.username = username
    instaloader.save_session_to_file(sessionfile)
    return username



def print_not_following(username : str):
    loader = Instaloader()
    loader.load_session_from_file(username) # (load session created w/
                               #  `instaloader -l USERNAME`)
                               
    profile = Profile.from_username(loader.context, username)
    
    # finds followers who are not follwoing the profile back and prints them 
    not_following_back = set(profile.get_followees()) - set(profile.get_followers())
    
    for profile in not_following_back:
        print(profile.username)
                               
    
# launches firefox with the given user profile 
def open_firefox(profile_path : str):
    options = Options()
    options.add_argument("-profile")
    options.add_argument(profile_path)
    driver = webdriver.Firefox(options=options)
    driver.get("https://www.instagram.com/")
    return driver 
        
             
if __name__ == '__main__':
    
    profile_path = input('Enter firefox profile path: ')
    driver = open_firefox(profile_path)
    p = ArgumentParser()
    p.add_argument("-c", "--cookiefile")
    p.add_argument("-f", "--sessionfile")
    args = p.parse_args()
    
    try:
        # imports instagram session from firefox browser 
        username = import_session(args.cookiefile or get_cookiefile(), args.sessionfile)
        driver.quit()
        print_not_following(username)
        
    except (ConnectionException, OperationalError) as e:
        raise SystemExit("Cookie import failed: {}".format(e))
    
    
    
    
    
    
    
    