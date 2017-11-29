import urllib.request
from bs4 import BeautifulSoup
import string
from pathlib import Path
import os


def get_html(url):
    response = urllib.request.urlopen(url)
    return response.read()


def parse_fight_events(html, file):
    soup = BeautifulSoup(html)
    table = soup.find('table', class_="b-statistics__table-events")

    fight_events = []
    fight_num = len(table.find_all('tr')[3:]) + 1

    for row in table.find_all('tr')[3:]:

        cols = row.find_all('td')

        fight_event_name = cols[0].a.text
        fight_event_name = fight_event_name.split()
        fight_event_name = ' '.join(fight_event_name)

        fight_city = cols[1].text
        fight_city = fight_city.split()
        fight_city = ' '.join(fight_city)

        fight_date = cols[0].span.text
        fight_date = fight_date.split()
        fight_date = ' '.join(fight_date)

        fight_num -= 1
        fight_events.append([
            fight_num,
            fight_event_name,
            fight_date,
            fight_city])

    save_fight_events(fight_events, file)

def remove_last_symbol(temp, file):
    str_temp = ""
    for line in temp:
        str_temp += line
    file.write(str_temp[:len(str_temp) - 1])


def save_fight_events(fight_events, file):
    for fight_event in fight_events:

        file.write(str(fight_event[0]) + ';')
        fight_event = fight_event[1:]

        file.write(';'.join(fight_event))
        file.write('|\n')


def main():
    os.remove("fight_events.txt")
    file = open("fight_events.txt", 'w')
    temp = open('temp.txt', 'w')

    parse_fight_events(get_html("http://www.fightmetric.com/statistics/events/\
completed?page=all"), temp)
    temp.close()
    temp = open('temp.txt', 'r')

    remove_last_symbol(temp, file)

    temp.close()
    file.close()

    os.remove('temp.txt')

main()
