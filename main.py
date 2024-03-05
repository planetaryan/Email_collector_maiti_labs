import flet as ft
import re  
import requests  
from bs4 import BeautifulSoup  
from collections import deque 
from urllib.parse import urlsplit, urljoin, unquote 
from tld import get_fld  
from tld.exceptions import TldDomainNotFound 

def main(page: ft.Page):

    def button_click(e):
        user_url = str(txtfld.value)


        if not user_url.startswith("http"):
            user_url = "https://" + user_url


        unscraped_url = deque([user_url])


        scraped_url = set()


        list_emails = set()

        while unscraped_url:

            url = unscraped_url.popleft()
            

            scraped_url.add(url)
            page.add(ft.Text(value="Searching for Emails in %s" % url))
            # print("Searching for Emails in %s" % url)

            try:

                response = requests.get(url)
            except (requests.exceptions.MissingSchema, requests.exceptions.ConnectionError, requests.exceptions.InvalidURL):
              
                
                continue

            if response.status_code != 200:
                continue

          
            new_emails = re.findall(r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b", response.text, re.I)


            new_emails = [unquote(email) for email in new_emails]

            page.add(ft.Text(value="New emails found:"+str(new_emails)))
            # print("New emails found:", new_emails)


            list_emails.update(new_emails)

     
            soup = BeautifulSoup(response.text, 'html.parser')
            page.add(ft.Text(value="Email Extracted: " + str(len(list_emails))))
            # print("Email Extracted: " + str(len(list_emails)))

           
            for tag in soup.find_all("a"):
                
                if "href" in tag.attrs:
                   
                    weblink = tag.attrs["href"]
                    if weblink.startswith(('http://', 'https://')):
                        try:

                            weblink_domain = get_fld(weblink)
                            user_url_domain = get_fld(user_url)
                            
                            
                            if weblink_domain == user_url_domain and not weblink.endswith('.pdf'):
                               
                                if weblink not in unscraped_url and weblink not in scraped_url:
                                    unscraped_url.append(weblink)
                        except TldDomainNotFound as e:
                            page.add(ft.Text(value="Error parsing domain from URL: "+str(e)))
                            # print("Error parsing domain from URL:", e)
                            continue
                    else:

                        continue
        page.add(ft.Text(value=str(list_emails)))
        
        




        
    
    page.scroll=True
    page.add(ft.Text(value="Email Collector"))
    page.add(ft.Text(value="Enter a web domain!"))

    


    txtfld=ft.TextField(hint_text="Ex. www.google.com",width=500)
    page.add(txtfld)

    button=ft.ElevatedButton("Scrape Emails", on_click=button_click)
    page.add(button)
    




ft.app(target=main)
