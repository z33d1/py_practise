import urllib.request
from bs4 import BeautifulSoup
import string
from pathlib import Path
import os

fighter_id = 1


def get_html(url):
    response = urllib.request.urlopen(url)
    return response.read()


def parse_fighters(html, filename):
    soup = BeautifulSoup(html)
    table = soup.find('table', class_="b-statistics__table")

    fighters = []

    for row in table.find_all('tr')[2:]:
        cols = row.find_all('td')

        fighter_name = cols[0].a.text

        fighter_surname = cols[1].a.text

        fighter_nickname = cols[2].a.text
        if fighter_nickname == "":
            fighter_nickname = ""

        fighter_height = cols[3].text
        table = fighter_height.maketrans("'", ' ', '\n')
        fighter_height = fighter_height.translate(table)
        table = fighter_height.maketrans('"', ' ')
        fighter_height = fighter_height.translate(table)
        fighter_height = fighter_height.split()
        if fighter_height[0] != '--':
            temp = []
            fighter_height = round(float(fighter_height[0]) * 0.3048 + (
                10**(-1) * float(fighter_height[1]) * 0.254), 2)
            temp.append(fighter_height)
            fighter_height = temp
        else:
            fighter_height[0] = ''

        fighter_weight = cols[4].text
        fighter_weight = fighter_weight.split()
        if fighter_weight[0] != '--':
            fighter_weight[0] = round(int(fighter_weight[0]) * 0.453592)
        else:
            fighter_weight[0] = ""

        fighter_reach = cols[5].text
        table = fighter_reach.maketrans(".", ' ')
        fighter_reach = fighter_reach.translate(table)
        fighter_reach = fighter_reach.split()
        if fighter_reach[0] != '--':
            fighter_reach[0] = round(int(fighter_reach[0]) * 2.54)
        else:
            fighter_reach[0] = ''

        fighter_stance = cols[6].text
        fighter_stance = fighter_stance.split()
        if len(fighter_stance) == 0:
            fighter_stance = [""]

        fighter_wins = cols[7].text
        fighter_wins = fighter_wins.split()

        fighter_loses = cols[8].text
        fighter_loses = fighter_loses.split()

        fighter_draws = cols[9].text
        fighter_draws = fighter_draws.split()

        fighter_belt = cols[10].find("img")
        if fighter_belt is not None:
            fighter_belt = "Champion Belt"
        else:
            fighter_belt = ""

        fighters.append([
            fighter_name + ' ' + fighter_surname,
            fighter_nickname,
            str(fighter_height[0]),
            str(fighter_weight[0]),
            str(fighter_reach[0]),
            fighter_stance[0],
            fighter_wins[0],
            fighter_loses[0],
            fighter_draws[0],
            fighter_belt])

    save_fighters(fighters, filename)


def save_fighters(fighters, filename):
    global fighter_id

    for fighter in fighters:
        filename.write(str(fighter_id) + ';')
        filename.write(';'.join(fighter))
        filename.write('|\n')
        fighter_id = fighter_id + 1


def remove_last_symbol(temp, file):
    str_temp = ""
    for line in temp:
        str_temp += line
    file.write(str_temp[:len(str_temp) - 1])


def main():
    filename = "fighters.txt"
    temp_filename = 'temp.txt'

    if (os.path.isfile(filename)):
        os.remove(filename)
    if (os.path.isfile(temp_filename)):
        os.remove(temp_filename)

    file = open(filename, 'w')
    temp = open(temp_filename, 'w')
    for char in string.ascii_lowercase:
        parse_fighters(get_html("http://www.fightmetric.com/\
statistics/fighters?char={:s}&page=all".format(char)), temp)
    temp.close()
    temp = open(temp_filename, 'r')

    remove_last_symbol(temp, file)
    temp.close()
    file.close()
    os.remove(temp_filename)


main()
