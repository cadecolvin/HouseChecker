from websites import Zillow, Google, CityOfFargo, CassCounty
from websites import Home, Address


max_price = 350000

# Find a list of all homes
all_homes = Zillow.get_homes()

# Remove any homes that have a price about the threshold
filtered_homes = [home for home in all_homes if home.price <= max_price]

# Pull addresses for all homes
for home in filtered_homes:
    home.address = Google.get_address(home.coordinates)

# Remove homes that didn't get an address successfully
# and add pacel numbers
filtered_homes = [home for home in filtered_homes if home.address is not None]
for home in all_homes:
    home.parcel_no = CityOfFargo.get_parcel_no(home.address)

print(filtered_homes)
