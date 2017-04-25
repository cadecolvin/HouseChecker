import json
import re
import requests


class Zillow:
    @staticmethod
    def get_coordinates():
        """
        Coordinates will be returned as a list of Tuples of lenght 2
        Tuple[0] = latitude
        Tuple[1] = longitude
        """
        url = 'https://www.zillow.com/search/GetResults.htm?spt=homes&status=110001&'\
                'lt=111101&ht=100000&pr=,&mp=,&ba=0%2C&sf=,&lot=0%2C&yr=,&'\
                'singlestory=0&hoa=0%2C&pho=0&pets=0&parking=0&laundry=0&income-restricted=0&'\
                'pnd=0&red=0&zso=0&days=any&ds=all&pmf=1&pf=1&sch=100111&zoom=10&'\
                'rect=-97219391,46746918,-96481247,46955886&p=1&sort=globalrelevanceex&search=map&'\
                'rid=18073&rt=6&listright=true&isMapSearch=1&zoom=10'

        response = requests.get(url)
        results = response.json()
        properties = results['map']['properties']
        coords = []
        for property in properties:
            lat = str(property[1])
            lon = str(property[2])

            # Format the lat and lon properly
            lat = lat[:2] + '.' + lat[2:]
            lon = lon[:3] + '.' + lon[3:]

            coords.append((lat, lon))

        return coords


class Google:
    @staticmethod
    def get_address(lat, lon):
        """
        Returns a formatted address string from Google's API if the 
        latitude and longitute can be found
        :param lat: The latitude where the address is found
        :param lon: The longitute where the address is found
        :return: A address formatted as follows: 123 14th St N, City, State, Zip, US
        """
        google_api = f'http://maps.googleapis.com/maps/api/geocode/json?latlng={lat},{lon}'

        response = requests.get(google_api)
        result = response.json()

        try:
            full_address = result['results'][0]['formatted_address']
            return full_address
        except:
            print(f'{lat},{lon}')


class CityOfFargo:
    @staticmethod
    def get_parcel_no(address):
        """
        Returns a Fargo Parcel number based on an address
        :param address: The address to search. Must be formatted as 123 1 St S
        :return: The parcel number
        """
        city_url = 'http://www.fargoparcels.com/index.asp'
        payload = {'address':address,'process':'true'}
        response = requests.post(city_url, data=payload)
        page_text = response.content.decode('utf-8')
        parcel_no = re.search(r'\d{2}-\d{4}-\d{5}-\d{3}', page_text)

        return parcel_no[0]

    @staticmethod
    def get_assessment_info(parcel_no):
        """
        Finds the assessment information for the given property
        :param parcel_no: The parcel number of the property
        :return: The property's assessment information
        """
        city_url = 'http://www.fargoparcels.com/index.asp'
        payload = {'dispaddr':parcel_no, 'seg':'1'}
        response = requests.get(city_url, params=payload)

        return response.content.decode('utf-8')


class CassCounty:
    @staticmethod
    def get_latest_tax_amount(parcel_no):
        """
        Finds the latest property tax due on the property
        :param parcel_no: The parcel number of the property
        :return: The latest tax amount due as an integer
        """
        url = 'https://www.casscountynd.gov/_wcf/PropertyTaxService.svc/GetPropertyByParcelNumber'
        payload = {'parcelNumber':parcel_no}
        headers = {'content-type':'application/json'}

        response = requests.post(url,data=json.dumps(payload), headers=headers)
        data = response.json()

        tax_amount = data['d']['LatestStatement']['Tax']
        tax_amount = tax_amount.replace('$', '')
        tax_amount = tax_amount.replace(',', '')
        return int(float(tax_amount))
