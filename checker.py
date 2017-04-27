import time
from websites import Zillow, Google, CityOfFargo, CassCounty
from websites import Home, Address


max_price = 350000

# Find a list of all homes
all_homes = Zillow.get_homes()
print(f'Found {len(all_homes)} on zillow')

# Remove any homes that have a price about the threshold
filtered_homes = [home for home in all_homes if home.price <= max_price]
filtered_homes = all_homes
print(f'Filtered out {len(all_homes) - len(filtered_homes)}')

# Pull addresses for all homes
for home in filtered_homes:
    print(f'Searching with coordinates {home.coordinates[0]},{home.coordinates[1]}')
    address = Google.get_address(home.coordinates[0],home.coordinates[1])
    home.address = address

# Remove homes that didn't get an address successfully
# and add pacel numbers
filtered_homes = [home for home in filtered_homes if home.address is not None]
for home in filtered_homes:
    home.parcel_no = CityOfFargo.get_parcel_no(home.address)
    print(f'Found parcel number {home.parcel_no}')
    time.sleep(1)

with open('homes.csv', 'wt') as f:
    f.write('Price,House Number,Street,City\n')
    for home in filtered_homes:
        f.write(f'{home.price},{home.address.house_no},{home.address.street},{home.address.city}\n')
