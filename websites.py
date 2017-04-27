import json
import re
import requests
import traceback


class Zillow:
    @staticmethod
    def get_homes():
        """
        Returns all homes for sale in the Fargo city limits.
        Homes will have the following fields populated
        coordinates,price,bed_no,bath_no
        :return: All homes for sale in Fargo
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
        homes = []
        for property in properties:
            home = Home()

            try:
                # Format the lat and lon properly
                lat = str(property[1])
                lon = str(property[2])
                lat = lat[:2] + '.' + lat[2:]
                lon = lon[:3] + '.' + lon[3:]
                home.coordinates = (lat, lon)

                price = property[3]
                price = price.replace('K', '000')
                price = price.replace('M', '000000')
                price = price.replace('$', '')
                home.price = int(price)

                home.bed_no = property[8][1]
                home.bath_no = property[8][2]

                homes.append(home)
            except:
                pass

        return homes


class Google:
    @staticmethod
    def get_address(lat, lon):
        """
        Returns a formatted address string from Google's API if the 
        latitude and longitute can be found
        :param lat: The latitude where the address is found
        :param lon: The longitute where the address is found
        :return: An address formatted as follows: 123 4th St N, City, State Zip, US
        """
        google_api = f'http://maps.googleapis.com/maps/api/geocode/json?latlng={lat},{lon}'

        response = requests.get(google_api)
        result = response.json()

        try:
            full_address = result['results'][0]['formatted_address']
            house_no = re.search(r'\d+(?=\s)', full_address)
            street = re.search(r'(?<=\s)\d.+?(?=,)', full_address)
            city = re.search(r'(?<=,\s)\w+(?=,)', full_address)
            state = re.search(r'(?<=,\s)\w\w(?=\s)', full_address)
            zip = re.search(r'(?<=\w\w\s)\d{5}(?=,)', full_address)

            # Format the street properly for Fargo searches
            street = re.sub(r'(\d+)(?:nd|st|th)', r'\1', street[0])

            return Address(house_no[0], street, city[0], state[0], zip[0])
        except:
            pass


class CityOfFargo:
    @staticmethod
    def get_parcel_and_seg(address):
        """
        Returns a Fargo Parcel number based on an address
        :param address: The address to search. Must be formatted as 123 1 St S
        :return: A tuple of (parcel_no, seg_no)
        """
        city_url = 'http://www.fargoparcels.com/index.asp'
        formatted_address = f'{address.house_no} {address.street}'
        payload = {'address':formatted_address,'process':'true'}
        response = requests.post(city_url, data=payload)
        page_text = response.content.decode('utf-8')
        try:
            match = re.search(r'\d{2}-\d{4}-\d{5}-\d{3}&seg=\d', page_text)[0]
            values = match.split('&')
            parcel_no = values[0]
            seg = values[1].replace('seg=', '')

            return (parcel_no, seg)
        except:
            return (0,0)

    @staticmethod
    def get_square_feet(parcel_no, seg_no):
        """
        Finds the assessment information for the given property
        :param parcel_no: The parcel number of the property
        :return: The property's assessment information
        """
        city_url = 'http://www.fargoparcels.com/index.asp'
        payload = {'dispaddr':parcel_no, 'seg':seg_no}
        response = requests.get(city_url, params=payload)
        page_text = response.content.decode('utf-8')

        try:
            sq_ft = re.findall(r'\d{3,4}(?=\sSq. Ft.)', page_text)
            if sq_ft is not None:
                return sq_ft[-1]
            else:
                return 0
        except:
            return 0


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


class Home:
    @property
    def address(self):
        return self._address
    @address.setter
    def address(self, value):
        self._address = value

    @property
    def coordinates(self):
        return self._coordinates
    @coordinates.setter
    def coordinates(self, value):
        self._coordinates = value

    @property
    def parcel_no(self):
        return self._parcel_no
    @parcel_no.setter
    def parcel_no(self, value):
        self._parcel_no = value

    @property
    def seg_no(self):
        return self._seg_no
    @seg_no.setter
    def seg_no(self, value):
        self._seg_no = value

    @property
    def price(self):
        return self._price
    @price.setter
    def price(self, value):
        self._price = value

    @property
    def bed_no(self):
        return self._bed_no
    @bed_no.setter
    def bed_no(self, value):
        self._bed_no = value

    @property
    def bath_no(self):
        return self._bath_no
    @bath_no.setter
    def bath_no(self, value):
        self._bath_no = value

    @property
    def sq_ft(self):
        return self._sq_ft
    @sq_ft.setter
    def sq_ft(self, value):
        self._sq_ft = value


class Address:
    def __init__(self, house_no, street, city, state, zip):
        self.house_no = house_no
        self.street = street
        self.city = city
        self.state = state
        self.zip = zip