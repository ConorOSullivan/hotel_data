import random
import credentials
import requests
import json
import time
import md5
import psycopg2

session_id = ''.join(random.choice('0123456789ABCDEF') for i in range(16))
my_ip = '73.15.131.191'
my_user_agent = 'Mozilla/5.0(Macintosh;IntelMacOSX10_9_5)AppleWebKit/537.36(KHTML,likeGecko)Chrome/41.0.2272.76Safari/537.36'
minor_rev = '4'

def generate_sig(apiKey, secret):
    m = md5.new()
    m.update(apiKey)
    m.update(secret)
    m.update(str(int(time.time())))
    return m.hexdigest()

sig = generate_sig(credentials.creds['apiKey'],credentials.creds['shared_secret'])

base_request = ''.join(("http://api.ean.com/ean-services/rs/hotel/v3/list?apiKey=%s" % (credentials.creds['apiKey']),
            "&cid=%s" % (credentials.creds['cid']),
            "&customerIpAddress=%s" % (my_ip),
            "&customerUserAgent=%s" % (my_user_agent),
            "&customerSessionId=%s" % (session_id),
            "&minorRev=%s" % (minor_rev),
            "&sig=%s" % (sig),
            "&locale=en_US&currencyCode=USD"))

class Request():
    def __init__(self):
        self.request_string = ""
        self.cache_request_string = ""

    def compose_first_request(self, city, state, countryCode, arrivalDate, departureDate, numAdults):
        self.request_string = base_request+''.join(('&xml=<HotelListRequest>',
                    '<city>%s</city>' % (city),
                    '<stateProvinceCode>%s</stateProvinceCode>' % (state),
                    '<countryCode>%s</countryCode>' % (countryCode),
                    '<arrivalDate>%s</arrivalDate>' % (arrivalDate),
                    '<departureDate>%s</departureDate>' % (departureDate),
                    '<RoomGroup>',
                      '<Room>',
                        '<numberOfAdults>%s</numberOfAdults>' % numAdults,
                      '</Room>',
                    '</RoomGroup>',
                    '</HotelListRequest>'))

    def compose_cache_request(self, cacheKey, cacheLocation):
        self.cache_request_string = base_request+''.join(('&xml=<HotelListRequest>',
                    '<cacheKey>%s</cacheKey>' % cacheKey,
                    '<cacheLocation>%s</cacheLocation>' % cacheLocation,
                    '</HotelListRequest>'))

                    
def compose_insert(resp):
    hotels = resp
    inserts = []
    for hotel in hotels:
        inserts.append('('+','.join(("'%s','%s','%s',%f" % (hotel['name'],hotel['postalCode'],hotel['countryCode'],hotel['hotelRating']),
                            "%f,%f,'%s',%d" % (hotel['highRate'],hotel['lowRate'],hotel['locationDescription'],hotel['confidenceRating']),
                            "'%s'" % (hotel['city']))) + ')')
    insert_statement = 'insert into sf_hotels values '+','.join(inserts)+';'
    print 'string formatted'
    conn = psycopg2.connect("dbname=expedia user=power_user password=q1w2e3")
    print 'connected to database'
    cursor = conn.cursor()
    cursor.execute(insert_statement)
    print 'sql executed'
    conn.commit()

def main():
    new_request = Request()
    new_request.compose_first_request('San Francisco','CA','US','07/04/2015','07/06/2015','3')

    response = requests.get(new_request.request_string)
    print 'get response'
    json_data = json.loads(response.content)
    print 'parse response'
    compose_insert(json_data['HotelListResponse']['HotelList']['HotelSummary'])
    print 'main done'
    # while json_data['moreResultsAvailable'] = 'true':
    #     print 'continuing cache at',
    #     print time.time()
    #     cacheKey = json_data['cacheKey']
    #     cacheLocation = json_data['cacheLocation']
    #     cache_request = Request()
    #     cache_request.compose_cache_request(cacheKey, cacheLocation)

    #     cache_response = request.get(cache_request.cache_request_string)
    #     json_data = json.loads(cache_response.content)

    #     compose_insert(json_data['HotelListResponse']['HotelList']['HotelSummary'])

main()    


