import sys, getopt
import requests
import json
import time
from datetime import datetime

request_prefix = "https://api.co2signal.com/v1/latest?countryCode="
#request_headers = {"auth-token":"XXXXXXXXXXXXXX"}

# parse args
def parse_args(argv):
    global request_headers
    try:
        opts, args = getopt.getopt(argv, "a:")
    except:
        print("Error parsing input arguments")
        sys.exit()
    for opt, arg in opts:
        if opt == '-a': request_headers = {"auth-token":arg}

def main(argv): 
    parse_args(argv)
    co2_table = dict()
    while True:
        # clear table
        co2_table.clear()
        
        # read table file
        file = open("co2_table.txt", "r")
        for entry in file:
            split = entry.split('=')
            co2_table[split[0]] = json.loads(split[1])
        file.close()
   
        # update local table copy
        for key in co2_table:
            print(key)
            time.sleep(5)
            r = requests.get(request_prefix + key, headers=request_headers)
            json_data = json.loads(r.text)
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            
            if 'data' in json_data and 'carbonIntensity' in json_data['data']:
                if (json_data['data']['carbonIntensity'] == 'null'):
                    print(key + " was null")
                    continue

                json_data['data'].update({'time' : timestamp})
                print(key + "=" + json.dumps(json_data['data']))
                co2_table[key] = json_data['data']
            
            if int(r.headers['X-RateLimit-Remaining-hour']) < 1:
                print("rate limited at " + timestamp)
                time.sleep(3600) # sleep 1 hour

        # update table file
        file = open("co2_table.txt", "r+")
        file.seek(0)
        for key in co2_table:
            file.write(key + "=" + json.dumps(co2_table[key]) + "\n")
        file.truncate()
        file.close()

        # debug print
        print("file written to.")
        #for key in co2_table:
        #    print(key + "=" + str(co2_table[key]))


if __name__ == '__main__':
    main(sys.argv[1:])
