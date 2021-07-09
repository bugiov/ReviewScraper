from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.action_chains import ActionChains 
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoAlertPresentException
from selenium.common.exceptions import TimeoutException
from selenium.common.exceptions import NoSuchElementException
from bs4 import BeautifulSoup

import time
import traceback
import requests
import os
import posixpath as path
import sys
import json
import csv

lista_asin = []

def salva():
    global lista_asin
    #scrittura
    try:
        with open('./lista_asin.json', 'w') as outfile:
            json.dump(lista_asin, outfile)
            print("Scrittura file lista_asin.json riuscita")
    except IOError:
        print("Scrittura file lista_asin.json non riuscita")

def carica():
    global lista_asin
    lista_asin = []
    # carico i prodotti da file json
    try:
        with open('./lista_asin.json') as json_file:
            for i in json.load(json_file):
                lista_asin.append(i)
            print("Lettura file lista_asin.json riuscita")
    except IOError:
        print("Lettura file lista_asin.json non riuscita")

def main():
    global lista_asin

    # Initiate the browser
    options = Options()
    #Remove navigator.webdriver Flag for ChromeDriver version 79.0.3945.16 or over
    options.add_argument('--disable-blink-features=AutomationControlled')
    #change default resolution
    options.add_argument('window-size=1280,800')
    browser = webdriver.Chrome(executable_path="./chromedriver.exe", options=options)

    lista_profili = []  #[username, profilo]
    lista_prodotti = [] #[nome_prodotto, asin, data_pubb, profilo]

    car = input("Vuoi caricare la lista asin da file json ? (s o n): ")
    if car == 's':
        carica()

    manual = True

    carica_profili = input("Vuoi caricare profili e username da file? (s o n) : ")
    if carica_profili == 's':
        manual = False
    
    while manual == False:
        with open('profili.csv') as input_profili:
            csv_reader = csv.reader(input_profili, delimiter=";")
            line_count = 0
            for row in csv_reader:
                if line_count == 0:
                    line_count += 1
                else:
                    username = row[0]
                    profilo = row[1]
                    lista_profili.append([username, profilo])
            break
    
    while manual:
        #inserire nome
        username = input("Inserisci username (o nome): ")
        #inserire url profilo
        profilo = input("Inserisci url profilo: ")
        lista_profili.append([username, profilo])
        continuare = input("Vuoi inserire altri profili? (s o n): ")
        if continuare == 'n':
            break
    
    print("Sono stati inseriti " + str(len(lista_profili)) + " profili in totale")

    for p in lista_profili:
        print(p[1])
        browser.get(p[1])
        time.sleep(1)
        js = 'window.scrollTo(0,document.body.scrollHeight);'
        browser.execute_script(js)
        time.sleep(2)
        js = 'window.scrollTo(0,0);'
        browser.execute_script(js)
        time.sleep(1)

        # while True:
        content = browser.page_source
        soup = BeautifulSoup(content, 'html.parser')

        review = soup.find_all("div", {"class":'desktop card profile-at-card profile-at-review-box'})  # review

        for r in review:
            try:
                r.find("span", {"class":'a-size-small a-color-attainable profile-at-review-badge a-text-bold'})
            except:
                continue    #se non è vine, passa alla prossima
            
            link_container = r.find("a", {"class":'a-link-normal profile-at-product-box-link a-text-normal'})
            
            try:    #prodotto non più disponibile
                link = link_container['href']
            except:
                continue

            asin = link[-34:-24]

            contenuto = False
            for a in lista_asin:
                if a == asin:
                    contenuto = True
                    break
            if contenuto == False:
                lista_asin.append(asin)

                title_container = r.find_all("div", {"class":'a-section profile-at-product-title-container profile-at-product-box-element'})[0]
                title_container = title_container.find_all("span")[2]

                contenitore_data = r.find_all("span", {"class":'a-profile-descriptor'})[0]
                data_pubb = contenitore_data.text
                data_pubb = data_pubb.split('·')

                lista_prodotti.append([title_container.text, asin, data_pubb[1], p[1]])

    header = ['Nome prodotto', 'Link AMZ', 'ASIN', 'Data pubblicazione', 'Profilo']
    with open('review.csv', 'w', encoding='UTF8', newline='') as f:
        writer = csv.writer(f, delimiter = ';')
        writer.writerow(header)
        for i in lista_prodotti:
            writer.writerow([i[0], "http://www.amazon.it/dp/" + i[1], i[1], i[2], i[3]])

    sal = input("Vuoi salvare la lista asin in file json ? (s o n): ")
    if sal == 's':
        salva()

main()