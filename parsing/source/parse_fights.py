import requests
import re
from bs4 import BeautifulSoup
import string
from pathlib import Path
import os


def get_html(url, headers):
    r = requests.get(url, headers=headers)
    return r


def parse(html, filename):
    soup = BeautifulSoup(html.text)
    table = soup.find('table', class_="b-statistics__table-events")
    fights = []
    fight_event_num = len(table.find_all('tr')[3:])

    headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_5) \
    AppleWebKit/537.36 (KHTML, like Gecko) Chrome/61.0.3163.100 Safari/537.36',
    'Referer': 'http://www.fightmetric.com/statistics/events/completed'}

    for row in table.find_all('tr')[3:]:
        col = row.find_all("td")
        link = col[0].a.get('href')
        html = get_html(link, headers=headers)
        fights = parse_fight_event(html, fight_event_num)
        save_fights(filename, fights)
        fight_event_num -= 1


def parse_fight_event(html, num):
    soup = BeautifulSoup(html.text)
    fights = []
    table = soup.find('table', class_="b-fight-details__table b-fight-details__table_style_margin-top b-fight-details__table_type_event-details js-fight-table")
    for row in table.find_all('tr')[1:]:
        cols = row.find_all('td')

        names = cols[1].find_all('p')
        temp = []

        for i in range(len(names)):
            fighter_name = names[i].a.text
            fighter_href = names[i].a.get('href')
            fighter_name = fighter_name.split()
            fighter_name = ' '.join(fighter_name)
            temp.append([fighter_name, fighter_href])

        names = temp

        winner = cols[0].find_all('p')
        if len(winner) == 2:
            winner = ""
        else:
            winner = names[0][0]
        fights.append([num, names, winner])
    return fights


def save_fights(filename, fights):
    for fight in fights:
        first_name = fight[1][0][0]
        second_name = fight[1][1][0]

        patterns = [re.compile('\d*;' + first_name), re.compile('\d*;' + second_name)]

        fighters = open('fighters.txt', 'r').read()

        fighter1_id = patterns[0].findall(fighters)
        fighter2_id = patterns[1].findall(fighters)
        if len(fighter1_id) > 1:
            nick = get_nickname(href=fight[1][0][1])
            full_name = re.compile('\d*;' + first_name + ";" + nick)
            fighter1_id = full_name.findall(fighters)
            fighter1_id = fighter1_id[0].split(';')[0]
        else:
            fighter1_id = (fighter1_id[0]).split(';')[0]

        if len(fighter2_id) > 1:
            nick = get_nickname(href=fight[1][1][1])
            full_name = re.compile('\d*;' + second_name + ";" + nick)
            fighter2_id = full_name.findall(fighters)
            fighter2_id = fighter2_id[0].split(';')[0]
        else:
            fighter2_id = (fighter2_id[0]).split(';')[0]

        info_str = ""
        names = first_name + ';' + second_name
        winner = fight[2]
        info_str = str(fight[0]) + ';' + str(fighter1_id) + ';' + str(fighter2_id) + ';' + names + ';' + str(winner)
        filename.write(info_str)
        filename.write('|\n')

def get_nickname(href):
    headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_5) \
    AppleWebKit/537.36 (KHTML, like Gecko) Chrome/61.0.3163.100 Safari/537.36',
    'Referer': 'http://www.fightmetric.com/statistics/events/completed'}

    html = get_html(href, headers)

    soup = BeautifulSoup(html.text)

    table = soup.find('section', class_="b-statistics__section")

    row = table.find('p', class_="b-content__Nickname")

    nick = row.text
    nick = nick.split()
    nick = nick[0]

    return nick


def remove_last_symbol(temp, file):
    str_temp = ""
    for line in temp:
        str_temp += line
    file.write(str_temp[:len(str_temp) - 1])

# Не все бойцы есть в таблице
# поэтому не у всех будут  id
# Если регулярка нашла двух бойцов с одинаковым именем то проверить ник
def main():
    headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_5) \
    AppleWebKit/537.36 (KHTML, like Gecko) Chrome/61.0.3163.100 Safari/537.36',
    'Referer': 'http://www.fightmetric.com/'}

    if (os.path.isfile('fights.txt')):
        os.remove('fights.txt')
    if (os.path.isfile('temp.txt')):
        os.remove('temp.txt')

    temp = open('temp.txt', 'w')
    file = open('fights.txt', 'w')
    parse(get_html("http://www.fightmetric.com/statistics/events/completed?page=all", headers), temp)
    temp.close()

    temp = open('temp.txt', 'r')

    remove_last_symbol(temp, file)

    file.close()
    temp.close()
    if (os.path.isfile('temp.txt')):
        os.remove('temp.txt')


main()
