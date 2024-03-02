import requests
from bs4 import BeautifulSoup
from tkinter import *
from tkinter import messagebox
import re
import urllib.parse
import pandas as pd
from  validate_email import validate_email
from collections import deque
import app


# Function to extract emails
def fetch_emails():

    # Get input URL 
    url = website_entry.get()
    urls = deque([url])

    # Track URLs visited
    scraped_urls = set()
    result = {'Website':[], 'Email':[]}

    # DataFrame to store emails
    df=pd.DataFrame(result)

    # Limit page visits
    count = 0

    # BFS crawl
    while len(urls):

        # Visit limit check
        if count == 100:
            break
        count+=1
        url = urls.popleft()
        scraped_urls.add(url)

        # Get base URL
        parts = urllib.parse.urlsplit(url)
        base_url = '{0.scheme}://{0.netloc}'.format(parts)
        
        # Construct absolute URL
        path = url[:url.rfind('/')+1] if '/' in parts.path else url
        try:
            # Request page
            response = requests.get(url)
            #response.raise_for_status()
        except (requests.exceptions.MissingSchema, requests.exceptions.ConnectionError, requests.exceptions.InvalidURL, requests.exceptions.HTTPError):
            continue

        # Parse HTML    
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Find email IDs 
        email_ids = re.findall(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b', soup.text)

        # Validate and store emails
        for email in email_ids:
            if validate_email(email):
                new_row = {'Website':url, 'Email':email}
                df=df._append(new_row, ignore_index=True)
        
        #Find links for further crawling
        for anchor in soup.find_all("a"):
            link = anchor.attrs['href'] if 'href' in anchor.attrs else ''
            if link.startswith('/'):
                link=base_url + link
            elif not link.startswith('http'):
                link = path + link
            if not link in urls and not link in scraped_urls:
                urls.append(link)
        scraped_urls.add(url)

    # Display result
    if df.shape[0] == 0:
        messagebox.showinfo("Result", "No email ids found.")
    else:
        df_str = df.to_string(index=False)
        messagebox.showinfo("Result", df_str)

# GUI initialization
app = Tk()
app.title("Email Extractor")

# Label and Entry for input URL
Label(app, text="Enter a website url:").grid(row=0, column=0, padx=10, pady=10)

# Store input URL
website_entry = Entry(app)
website_entry.grid(row=0, column=1, padx=10, pady=10)

# Trigger email extraction on button click
Button(app, text="Extract Emails", command=fetch_emails).grid(row=1, column=1, padx=10, pady=10)

# Start GUI event loop
app.mainloop()