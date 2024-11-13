from dotenv import load_dotenv
import imaplib
import email
import os
from bs4 import BeautifulSoup

# Load environment variables
load_dotenv()

username = os.getenv("EMAIL")
password = os.getenv("PASSWORD")

def connect_to_email():
    try:
        mail = imaplib.IMAP4_SSL("imap.gmail.com")
        mail.login(username, password)
        mail.select("inbox")
        print("Connected to inbox.")
        return mail
    except Exception as e:
        print(f"Error connecting to email: {e}")
        return None

def extract_links_from_html(html_content):
    soup = BeautifulSoup(html_content, 'html.parser')
    links = [link['href'] for link in soup.find_all("a", href=True) if "unsubscribe" in link['href'].lower()]
    return links

def search_email():
    mail = connect_to_email()
    if mail is None:
        print("Failed to connect to email server.")
        return []

    links = []
    try:
        _, search_result = mail.search(None, 'TEXT "unsubscribe"')
        if search_result[0] == b'': 
            print("No emails with 'unsubscribe' found.")
            return links

        data = search_result[0].split()
        print(f"Found {len(data)} emails with 'unsubscribe' links.")
        for num in data:
            _, data = mail.fetch(num, "(RFC822)")
            message = email.message_from_bytes(data[0][1])
            if message.is_multipart():
                for part in message.walk():
                    if part.get_content_type() == 'text/html':
                        html_content = part.get_payload(decode=True).decode()
                        links.extend(extract_links_from_html(html_content))
            else:
                content_type = message.get_content_type()
                content = message.get_payload(decode=True).decode()
                if content_type == 'text/html':
                    links.extend(extract_links_from_html(content))
                    
    except Exception as e:
        print(f"Error during email search and processing: {e}")
    finally:
        mail.logout()
        print("Logged out from the email server.")
        
    return links

def saveLinks(links):
    if links:
        with open('unsubscribe_links.txt', 'w') as file:
            file.write("\n".join(links))
        print("Links saved to 'unsubscribe_links.txt'.")
    else:
        print("No links to save.")

links = search_email()
saveLinks(links)
