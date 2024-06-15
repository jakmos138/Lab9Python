import smtplib
import json
import argparse
import requests
from bs4 import BeautifulSoup
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime


def load_credentials(config_file):
    with open(config_file, 'r') as file:
        config = json.load(file)
    return config['username'], config['password']


def send_email(subject, body, recipient_email=None, config_file='config.json'):
    sender_email, password = load_credentials(config_file)

    # If recipient was provided send an email to them, otherwise to self
    recipient_email = recipient_email if recipient_email else sender_email

    # Create the email
    msg = MIMEMultipart()
    msg['From'] = sender_email
    msg['To'] = recipient_email
    msg['Subject'] = subject

    msg.attach(MIMEText(body, 'plain'))

    # Send the email
    try:
        with smtplib.SMTP('smtp.gmail.com', 587) as server:
            server.starttls()  # Secure the connection
            server.login(sender_email, password)
            server.sendmail(sender_email, recipient_email, msg.as_string())
        print("Email sent successfully.")
    except Exception as e:
        print(f"Failed to send email: {e}")


def get_cat_facts(number_of_facts):
    url = "https://cat-fact.herokuapp.com/facts/random"
    try:
        response = requests.get(url, params={'amount': number_of_facts})
        response.raise_for_status()
        facts = response.json()
        for i, fact in enumerate(facts, start=1):
            print(f"Fact {i}: {fact['text']}")
    except requests.RequestException as e:
        print(f"Failed to retrieve cat facts: {e}")


def get_teachers_by_letter(letter):
    url = f"https://wit.pwr.edu.pl/wydzial/struktura-organizacyjna/pracownicy?letter={letter}"
    try:
        response = requests.get(url)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')
        researchers = soup.find_all('div', class_='news-box')

        if not researchers:
            print(f"No researchers found with last names on '{letter}'.")
            return

        print(f"The list of researchers - {letter}")
        for researcher in researchers:
            name = researcher.find('a').string.strip()
            email_tag = researcher.find('p')
            email = email_tag.string.strip() if email_tag else "No email given"
            print(f"{name} - {email}")
    except requests.RequestException as e:
        print(f"Failed to retrieve researchers: {e}")


def run():
    desc = "Send an email, display cat facts, or list researchers by letter."
    parser = argparse.ArgumentParser(
        description=desc)
    parser.add_argument('--mail', type=str, help="The content of the email.")
    # Extra functionality to allow sending to anyone
    parser.add_argument('--recipient', type=str,
                        help="The recipient email address (default: sender)")
    parser.add_argument('--cat-facts', type=int,
                        help="The number of cat facts to display.")
    parser.add_argument('--teachers', type=str,
                        help="The letter to list researchers by.")
    args = parser.parse_args()

    if args.mail:
        # Get current date and time
        current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        subject = f"Lab message sent on {current_time}"
        # Send the email
        send_email(subject, args.mail, args.recipient)
    elif args.cat_facts:
        get_cat_facts(args.cat_facts)
    elif args.teachers:
        get_teachers_by_letter(args.teachers)
    else:
        print("Please provide an argument:", end=" ")
        print("--mail for sending an email,", end=" ")
        print("--cat-facts for displaying cat facts,", end=" ")
        print("or --teachers for listing researchers by letter.")


if __name__ == "__main__":
    run()
