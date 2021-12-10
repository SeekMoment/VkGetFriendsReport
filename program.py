#!/usr/bin/env python

import argparse
import os
import vk
import csv
import json
import datetime

try:
    TOKEN = open(f"access_token.txt").read().strip()
    API_V = 5.135

    def parse():
        parser = argparse.ArgumentParser()

        parser.add_argument('-id',
                            type=int,
                            default=None,
                            help='VK ID of target. Default = None')
        parser.add_argument('-extension',
                            type=str,
                            default='.csv',
                            help="Extension of the output report. Default = csv")
        parser.add_argument('-path',
                            type=str,
                            default=os.getcwd(),
                            help="The path to the output report. Default = current directory")

        return parser.parse_args()

    # convert date of birth to iso format
    def get_birthdays(*args):
        if args[0][0] == '':
            a = str(datetime.datetime.strptime(f"{'01'}/{'01'}/{'0001'}", "%d/%m/%Y").isoformat()).split(
                '-')
            a[2] = a[2].split('T')
            a[0] = '0000'
            a[1] = '00'
            a[2][0] = '00'
            return f"{a[0]}-{a[1]}-{a[2][0]}T{a[2][1]}"

        elif len(args[0]) == 2:
            a = str(datetime.datetime.strptime(f"{args[0][0]}/{args[0][1]}/{'0001'}", "%d/%m/%Y").isoformat()).split(
                '-')
            a[0] = '0000'
            return f"{a[0]}-{a[1]}-{a[2]}"
        elif len(args[0]) == 3:
            return str(datetime.datetime.strptime(f"{args[0][0]}/{args[0][1]}/{args[0][2]}", "%d/%m/%Y").isoformat())


    def get_friends(target_id: int, extension: str, path: str):
        arr = []
        session = vk.Session(access_token=TOKEN)
        api = vk.API(session, lang='ru', v=API_V)
        try:
            friends_ids = api.friends.get(user_id=target_id, fields=['sex', 'bdate', 'city', 'country'])['items']
            friends_ids = sorted(friends_ids, key=lambda k: k['first_name'])
        except vk.exceptions.VkAPIError as e:
            print(f'Something went wrong with https://vk.com/id{target_id}\n'
                  f'{e.code} - {e.message}')
            return 1

        if not friends_ids:
            print(f'https://vk.com/id{target_id} has no friends :(')
            return 1
        if extension in ['.csv', '.json', '.tsv']:
            if os.path.exists(path):
                for friend_id in friends_ids:
                    first_name = friend_id.get('first_name', '-')
                    last_name = friend_id.get('last_name', '-')
                    country = dict(friend_id.get('country', '')).get('title', '-')
                    city = dict(friend_id.get('city', '')).get('title', '-')
                    bdate = friend_id.get('bdate', '').split('.')
                    bdate = get_birthdays(bdate)
                    sex = friend_id.get('sex')
                    sex = 'male' if sex == 2 else 'female'
                    if extension == '.csv':
                        with open(f"{path}/{target_id}.csv", 'a') as myfile:
                            wr = csv.writer(myfile, quoting=csv.QUOTE_ALL)
                            wr.writerow([first_name, last_name, country, city, bdate, sex])
                    elif extension == '.json':
                        arr.append({'first_name': first_name,
                                    'last_name': last_name,
                                    'country': country,
                                    'city': city,
                                    'bdate': bdate,
                                    'sex': sex})
                    elif extension == '.tsv':
                        with open(f"{path}/{target_id}.tsv", 'a') as myfile:
                            wr = csv.writer(myfile, delimiter='\t')
                            wr.writerow([first_name, last_name, country, city, bdate, sex])

                if extension == '.json':
                    with open(f"{path}/{target_id}.json", 'w') as myfile:
                        myfile.write(json.dumps({'friends': arr}))
                        del arr
            else:
                print('Invalid file path specified.')
                return 1
        else:
            print('Invalid file extension specified.')
            return 1


    def main():
        args = parse()
        if not args.id:
            print("No argument passed! Specify ID.")
            return 1
        get_friends(args.id, args.extension, args.path)


    if __name__ == "__main__":
        main()

except Exception as e:
    print(f'Something went wrong with access_token: {e}')
    print(f'Create access_token.txt file in the current directory and put your token there')


