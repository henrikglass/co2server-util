import sys, getopt
import requests
import json
import time
from datetime import datetime

eu_contry_codes = """AT BE BG CY CZ DK-DK1 EE FI FR DE HR GR HU IE IT-CNO EL LV LT LU MT 
    NL PL PT RO SK SI ES SE GB IS NO-NO1 CH ME MK AL RS TR BA AZ MD UA BY GE
    AM""".split()

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
    for country in eu_contry_codes:
        time.sleep(5)
        r = requests.get(request_prefix + country, headers=request_headers)
        json_data = json.loads(r.text)
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S") 
        if 'data' in json_data:
            json_data['data'].update({'time' : timestamp})
            print(country + "=" + json.dumps(json_data['data']))
        else:
            print(country + "={\"time\": \"" + timestamp + "\"}")
        if int(r.headers['X-RateLimit-Remaining-hour']) < 1:
            time.sleep(3600) # sleep 1 hour

if __name__ == '__main__':
    main(sys.argv[1:])
