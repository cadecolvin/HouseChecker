import time
from websites import Zillow, Google, CityOfFargo, CassCounty
from websites import Home, Address


max_price = 350000

# Find a list of all homes
all_homes = Zillow.get_homes()
print(f'Found {len(all_homes)} on zillow')

# Remove any homes that have a price about the threshold
filtered_homes = [home for home in all_homes if home.price <= max_price]
print(f'Filtered out {len(all_homes) - len(filtered_homes)}')

# Pull addresses for all homes
for home in filtered_homes:
    print(f'Searching with coordinates {home.coordinates[0]},{home.coordinates[1]}')
    address = Google.get_address(home.coordinates[0],home.coordinates[1])
    home.address = address

# Remove homes that didn't get an address successfully
# and add pacel numbers and sqare footage
filtered_homes = [home for home in filtered_homes if home.address is not None]
for home in filtered_homes:
    parcel_seg = CityOfFargo.get_parcel_and_seg(home.address)
    home.parcel_no = parcel_seg[0]
    home.seg_no = parcel_seg[1]
    home.sq_ft = CityOfFargo.get_square_feet(home.parcel_no, home.seg_no)
    print(f'Found parcel number {home.parcel_no}')
    print(f'Sq. Ft: {home.sq_ft}')
    time.sleep(1)

with open('homes.csv', 'wt') as f:
    f.write('Price,House Number,Street,City\n')
    for home in filtered_homes:
        f.write(f'{home.price},{home.address.house_no},{home.address.street},{home.address.city}'\
                f'{home.parcel_no},{home.seg_no},{home.sq_ft},{home.bed_no},{home.bath_no}\n')
