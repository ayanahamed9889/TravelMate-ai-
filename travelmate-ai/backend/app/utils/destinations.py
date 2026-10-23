"""Curated destinations for Explore / Dashboard: India + the rest of the world.

`avg_daily` is a rough per-person daily budget in INR (stay + food + local transport),
meant for comparison between places, not a quote. `image` is None: the frontend looks a
photo up from Wikipedia (see /api/images) and draws a gradient while it loads.
"""

REGIONS = ["India", "Asia", "Middle East", "Europe", "Africa", "Americas", "Oceania"]
INDIA_ZONES = ["North India", "South India", "West", "East", "Northeast"]

# Shown first on the dashboard (a mix of India and the world)
FEATURED_ORDER = ["bali", "jaipur", "paris", "goa", "dubai", "tokyo", "interlaken", "new-york", "leh-ladakh"]


def _d(id_, name, state, region, tagline, avg_daily, best_time, tags, featured=False,
       country="India", cc="IN", zone=""):
    return {
        "id": id_, "name": name, "state": state, "country": country, "cc": cc,
        "region": region, "zone": zone, "tagline": tagline, "avg_daily": avg_daily,
        "best_time": best_time, "tags": tags, "image": None, "featured": featured,
    }


DESTINATIONS = [
    _d('jaipur', 'Jaipur', 'Rajasthan', "India", 'Pink City palaces & bazaars', 5500, 'Oct - Mar', ['Heritage', 'Culture', 'Shopping'], True, zone='North India'),
    _d('udaipur', 'Udaipur', 'Rajasthan', "India", 'City of Lakes & royal stays', 6500, 'Sep - Mar', ['Heritage', 'Romantic', 'Lakes'], False, zone='North India'),
    _d('agra', 'Agra', 'Uttar Pradesh', "India", 'Taj Mahal & Mughal heritage', 4500, 'Oct - Mar', ['Heritage', 'History'], False, zone='North India'),
    _d('varanasi', 'Varanasi', 'Uttar Pradesh', "India", 'Ganga ghats & living spirituality', 3500, 'Oct - Mar', ['Spiritual', 'Culture', 'Food'], False, zone='North India'),
    _d('amritsar', 'Amritsar', 'Punjab', "India", 'Golden Temple & Punjabi food', 3000, 'Oct - Mar', ['Spiritual', 'Food'], False, zone='North India'),
    _d('rishikesh', 'Rishikesh', 'Uttarakhand', "India", 'Yoga, rafting & the Ganga', 3500, 'Sep - Jun', ['Adventure', 'Wellness', 'Spiritual'], False, zone='North India'),
    _d('manali', 'Manali', 'Himachal Pradesh', "India", 'Snow peaks & adventure sports', 4500, 'Mar - Jun, Dec - Feb', ['Adventure', 'Nature', 'Snow'], False, zone='North India'),
    _d('leh-ladakh', 'Leh-Ladakh', 'Ladakh', "India", 'High passes, lakes & monasteries', 7000, 'May - Sep', ['Adventure', 'Nature', 'Road trip'], False, zone='North India'),
    _d('alleppey', 'Alleppey', 'Kerala', "India", 'Houseboats on the backwaters', 6000, 'Oct - Mar', ['Relaxation', 'Nature', 'Romantic'], False, zone='South India'),
    _d('munnar', 'Munnar', 'Kerala', "India", 'Tea gardens & misty hills', 5000, 'Sep - Mar', ['Nature', 'Relaxation'], False, zone='South India'),
    _d('hampi', 'Hampi', 'Karnataka', "India", 'Ruins of the Vijayanagara empire', 3000, 'Oct - Feb', ['History', 'Heritage', 'Backpacking'], False, zone='South India'),
    _d('mysuru', 'Mysuru', 'Karnataka', "India", 'Palaces, silk & sandalwood', 3500, 'Oct - Feb', ['Heritage', 'Culture'], False, zone='South India'),
    _d('pondicherry', 'Pondicherry', 'Puducherry', "India", 'French quarter & calm beaches', 4500, 'Oct - Mar', ['Beaches', 'Culture', 'Food'], False, zone='South India'),
    _d('goa', 'Goa', 'Goa', "India", 'Beaches, cafes & nightlife', 6500, 'Nov - Feb', ['Beaches', 'Nightlife', 'Relaxation'], True, zone='West'),
    _d('mumbai', 'Mumbai', 'Maharashtra', "India", 'City that never sleeps', 7500, 'Nov - Feb', ['Food', 'Shopping', 'Nightlife'], False, zone='West'),
    _d('jaisalmer', 'Jaisalmer', 'Rajasthan', "India", 'Golden fort & desert camps', 5000, 'Oct - Mar', ['Adventure', 'Heritage', 'Desert'], False, zone='West'),
    _d('rann-of-kutch', 'Rann of Kutch', 'Gujarat', "India", 'White salt desert festival', 5000, 'Nov - Feb', ['Nature', 'Culture', 'Photography'], False, zone='West'),
    _d('kolkata', 'Kolkata', 'West Bengal', "India", 'City of joy, art & sweets', 4000, 'Oct - Feb', ['Culture', 'Food', 'History'], False, zone='East'),
    _d('darjeeling', 'Darjeeling', 'West Bengal', "India", 'Tea estates & Kanchenjunga views', 4500, 'Mar - May, Oct - Nov', ['Nature', 'Relaxation'], False, zone='East'),
    _d('puri', 'Puri', 'Odisha', "India", 'Jagannath Temple & beaches', 3000, 'Oct - Mar', ['Spiritual', 'Beaches'], False, zone='East'),
    _d('andaman', 'Andaman Islands', 'Andaman & Nicobar', "India", 'Clear water, diving & islands', 8000, 'Oct - May', ['Beaches', 'Adventure', 'Relaxation'], False, zone='East'),
    _d('gangtok', 'Gangtok', 'Sikkim', "India", 'Monasteries & Himalayan views', 5000, 'Mar - Jun, Oct - Dec', ['Nature', 'Culture'], False, zone='Northeast'),
    _d('shillong', 'Shillong', 'Meghalaya', "India", 'Living-root bridges & waterfalls', 4500, 'Oct - May', ['Nature', 'Adventure'], False, zone='Northeast'),
    _d('kaziranga', 'Kaziranga', 'Assam', "India", 'One-horned rhino safaris', 5500, 'Nov - Apr', ['Nature', 'Wildlife'], False, zone='Northeast'),
    _d('bangkok', 'Bangkok', 'Thailand', 'Asia', 'Temples, street food & nightlife', 4500, 'Nov - Feb', ['Food', 'Culture', 'Nightlife'], False, country='Thailand', cc='TH'),
    _d('phuket', 'Phuket', 'Thailand', 'Asia', 'Island beaches & boat trips', 6000, 'Nov - Apr', ['Beaches', 'Adventure', 'Nightlife'], False, country='Thailand', cc='TH'),
    _d('bali', 'Bali', 'Indonesia', 'Asia', 'Rice terraces, temples & surf', 5500, 'Apr - Oct', ['Beaches', 'Wellness', 'Culture'], True, country='Indonesia', cc='ID'),
    _d('singapore', 'Singapore', 'Singapore', 'Asia', 'Gardens, skyline & hawker food', 11000, 'Feb - Apr', ['Food', 'Family', 'Shopping'], False, country='Singapore', cc='SG'),
    _d('kuala-lumpur', 'Kuala Lumpur', 'Malaysia', 'Asia', 'Twin Towers, food & easy day trips', 4500, 'May - Jul', ['Food', 'Shopping', 'City'], False, country='Malaysia', cc='MY'),
    _d('hanoi', 'Hanoi', 'Vietnam', 'Asia', 'Old Quarter, pho & Ha Long Bay', 3500, 'Oct - Apr', ['Food', 'Culture', 'History'], False, country='Vietnam', cc='VN'),
    _d('siem-reap', 'Siem Reap', 'Cambodia', 'Asia', 'Angkor Wat sunrise', 3500, 'Nov - Mar', ['History', 'Heritage', 'Backpacking'], False, country='Cambodia', cc='KH'),
    _d('tokyo', 'Tokyo', 'Japan', 'Asia', 'Neon city, sushi & anime culture', 11000, 'Mar - May, Oct - Nov', ['Food', 'Culture', 'Shopping'], True, country='Japan', cc='JP'),
    _d('kyoto', 'Kyoto', 'Japan', 'Asia', 'Temples, geisha lanes & autumn leaves', 10000, 'Mar - May, Oct - Nov', ['Culture', 'Heritage', 'Photography'], False, country='Japan', cc='JP'),
    _d('seoul', 'Seoul', 'South Korea', 'Asia', 'K-culture, palaces & street snacks', 9000, 'Apr - Jun, Sep - Nov', ['Food', 'Shopping', 'Culture'], False, country='South Korea', cc='KR'),
    _d('hong-kong', 'Hong Kong', 'Hong Kong', 'Asia', 'Skyline, dim sum & harbour views', 11000, 'Oct - Dec', ['Food', 'Shopping', 'City'], False, country='Hong Kong', cc='HK'),
    _d('kathmandu', 'Kathmandu', 'Nepal', 'Asia', 'Stupas, Himalaya & trekking base', 3500, 'Oct - Nov, Mar - Apr', ['Adventure', 'Spiritual', 'Culture'], False, country='Nepal', cc='NP'),
    _d('maldives', 'Maldives', 'Maldives', 'Asia', 'Overwater villas & coral reefs', 18000, 'Nov - Apr', ['Beaches', 'Romantic', 'Relaxation'], False, country='Maldives', cc='MV'),
    _d('colombo', 'Colombo', 'Sri Lanka', 'Asia', 'Beaches, tea country & ancient cities', 4000, 'Dec - Mar', ['Beaches', 'Culture', 'Nature'], False, country='Sri Lanka', cc='LK'),
    _d('dubai', 'Dubai', 'United Arab Emirates', 'Middle East', 'Skyscrapers, desert safaris & malls', 12000, 'Nov - Mar', ['Shopping', 'Luxury', 'Family'], True, country='United Arab Emirates', cc='AE'),
    _d('abu-dhabi', 'Abu Dhabi', 'United Arab Emirates', 'Middle East', 'Grand Mosque & Louvre', 11000, 'Nov - Mar', ['Culture', 'Luxury', 'Family'], False, country='United Arab Emirates', cc='AE'),
    _d('istanbul', 'Istanbul', 'Turkey', 'Middle East', 'Where Europe meets Asia', 6500, 'Apr - Jun, Sep - Nov', ['History', 'Food', 'Culture'], False, country='Turkey', cc='TR'),
    _d('doha', 'Doha', 'Qatar', 'Middle East', 'Souq Waqif & modern museums', 11000, 'Nov - Mar', ['Culture', 'Luxury', 'City'], False, country='Qatar', cc='QA'),
    _d('amman', 'Amman', 'Jordan', 'Middle East', 'Petra & the Dead Sea', 7000, 'Mar - May, Sep - Nov', ['History', 'Adventure', 'Nature'], False, country='Jordan', cc='JO'),
    _d('muscat', 'Muscat', 'Oman', 'Middle East', 'Forts, wadis & calm beaches', 8000, 'Oct - Apr', ['Nature', 'Culture', 'Relaxation'], False, country='Oman', cc='OM'),
    _d('paris', 'Paris', 'France', 'Europe', 'Eiffel Tower, museums & cafes', 14000, 'Apr - Jun, Sep - Oct', ['Romantic', 'Culture', 'Food'], True, country='France', cc='FR'),
    _d('london', 'London', 'United Kingdom', 'Europe', 'Royal sights, theatre & pubs', 15000, 'May - Sep', ['History', 'Culture', 'Shopping'], False, country='United Kingdom', cc='GB'),
    _d('rome', 'Rome', 'Italy', 'Europe', 'Colosseum, Vatican & pasta', 11000, 'Apr - Jun, Sep - Oct', ['History', 'Food', 'Culture'], False, country='Italy', cc='IT'),
    _d('barcelona', 'Barcelona', 'Spain', 'Europe', 'Gaudi, beaches & tapas', 10000, 'May - Jun, Sep', ['Beaches', 'Culture', 'Food'], False, country='Spain', cc='ES'),
    _d('amsterdam', 'Amsterdam', 'Netherlands', 'Europe', 'Canals, bikes & museums', 13000, 'Apr - May', ['Culture', 'City', 'Photography'], False, country='Netherlands', cc='NL'),
    _d('prague', 'Prague', 'Czechia', 'Europe', 'Fairytale old town & castle', 7500, 'Apr - Jun, Sep - Oct', ['History', 'Culture', 'Nightlife'], False, country='Czechia', cc='CZ'),
    _d('vienna', 'Vienna', 'Austria', 'Europe', 'Palaces, music & coffeehouses', 11500, 'Apr - Jun, Sep - Oct', ['Culture', 'History', 'Food'], False, country='Austria', cc='AT'),
    _d('budapest', 'Budapest', 'Hungary', 'Europe', 'Thermal baths & Danube nights', 7000, 'Apr - Jun, Sep - Oct', ['Relaxation', 'Nightlife', 'History'], False, country='Hungary', cc='HU'),
    _d('interlaken', 'Interlaken', 'Switzerland', 'Europe', 'Alps, lakes & scenic trains', 20000, 'Jun - Sep, Dec - Feb', ['Nature', 'Adventure', 'Snow'], True, country='Switzerland', cc='CH'),
    _d('santorini', 'Santorini', 'Greece', 'Europe', 'White villages & caldera sunsets', 12000, 'May - Oct', ['Romantic', 'Beaches', 'Photography'], False, country='Greece', cc='GR'),
    _d('lisbon', 'Lisbon', 'Portugal', 'Europe', 'Trams, tiles & pastel de nata', 8500, 'Mar - Oct', ['Food', 'Culture', 'City'], False, country='Portugal', cc='PT'),
    _d('reykjavik', 'Reykjavik', 'Iceland', 'Europe', 'Northern lights & glaciers', 16000, 'Sep - Mar', ['Nature', 'Adventure', 'Photography'], False, country='Iceland', cc='IS'),
    _d('berlin', 'Berlin', 'Germany', 'Europe', 'History, art & nightlife', 10000, 'May - Sep', ['History', 'Nightlife', 'Culture'], False, country='Germany', cc='DE'),
    _d('cairo', 'Cairo', 'Egypt', 'Africa', 'Pyramids & the Nile', 4500, 'Oct - Apr', ['History', 'Culture', 'Heritage'], False, country='Egypt', cc='EG'),
    _d('cape-town', 'Cape Town', 'South Africa', 'Africa', 'Table Mountain, wine & coast', 6500, 'Nov - Mar', ['Nature', 'Adventure', 'Food'], False, country='South Africa', cc='ZA'),
    _d('marrakech', 'Marrakech', 'Morocco', 'Africa', 'Souks, riads & Sahara trips', 5000, 'Mar - May, Sep - Nov', ['Culture', 'Shopping', 'Desert'], False, country='Morocco', cc='MA'),
    _d('masai-mara', 'Masai Mara', 'Kenya', 'Africa', 'Big-five safaris & the migration', 9000, 'Jul - Oct', ['Wildlife', 'Nature', 'Adventure'], False, country='Kenya', cc='KE'),
    _d('zanzibar', 'Zanzibar', 'Tanzania', 'Africa', 'Spice island & turquoise beaches', 6000, 'Jun - Oct', ['Beaches', 'Culture', 'Relaxation'], False, country='Tanzania', cc='TZ'),
    _d('mauritius', 'Mauritius', 'Mauritius', 'Africa', 'Lagoons, waterfalls & resorts', 11000, 'May - Dec', ['Beaches', 'Romantic', 'Relaxation'], False, country='Mauritius', cc='MU'),
    _d('new-york', 'New York', 'United States', 'Americas', 'Skyline, Broadway & museums', 18000, 'Apr - Jun, Sep - Nov', ['City', 'Culture', 'Shopping'], True, country='United States', cc='US'),
    _d('los-angeles', 'Los Angeles', 'United States', 'Americas', 'Hollywood, beaches & theme parks', 16000, 'Mar - May, Sep - Nov', ['Family', 'Beaches', 'City'], False, country='United States', cc='US'),
    _d('toronto', 'Toronto', 'Canada', 'Americas', 'CN Tower & Niagara day trip', 13000, 'Jun - Sep', ['City', 'Family', 'Nature'], False, country='Canada', cc='CA'),
    _d('cancun', 'Cancun', 'Mexico', 'Americas', 'Caribbean beaches & Mayan ruins', 9000, 'Dec - Apr', ['Beaches', 'History', 'Nightlife'], False, country='Mexico', cc='MX'),
    _d('rio-de-janeiro', 'Rio de Janeiro', 'Brazil', 'Americas', 'Christ the Redeemer & Copacabana', 7000, 'Dec - Mar', ['Beaches', 'Nightlife', 'Nature'], False, country='Brazil', cc='BR'),
    _d('buenos-aires', 'Buenos Aires', 'Argentina', 'Americas', 'Tango, steak & grand boulevards', 6500, 'Mar - May, Sep - Nov', ['Culture', 'Food', 'Nightlife'], False, country='Argentina', cc='AR'),
    _d('cusco', 'Cusco', 'Peru', 'Americas', 'Gateway to Machu Picchu', 6000, 'May - Sep', ['History', 'Adventure', 'Heritage'], False, country='Peru', cc='PE'),
    _d('sydney', 'Sydney', 'Australia', 'Oceania', 'Opera House, harbour & beaches', 14000, 'Sep - Nov, Mar - May', ['City', 'Beaches', 'Family'], False, country='Australia', cc='AU'),
    _d('queenstown', 'Queenstown', 'New Zealand', 'Oceania', 'Adventure capital among the Alps', 13000, 'Dec - Mar', ['Adventure', 'Nature', 'Snow'], False, country='New Zealand', cc='NZ'),
    _d('fiji', 'Fiji', 'Fiji', 'Oceania', 'Island resorts & coral reefs', 12000, 'May - Oct', ['Beaches', 'Romantic', 'Relaxation'], False, country='Fiji', cc='FJ'),
]

_BY_ID = {d["id"]: d for d in DESTINATIONS}


def get_destination(dest_id: str):
    return _BY_ID.get(dest_id)


def find_by_name(name: str):
    key = (name or "").strip().lower()
    for d in DESTINATIONS:
        if key in (d["name"].lower(), d["id"]):
            return d
    return None


def search_destinations(q: str = "", region: str = "", limit: int = 100):
    q = (q or "").strip().lower()
    region = (region or "").strip().lower()
    out = []
    for d in DESTINATIONS:
        if region and d["region"].lower() != region:
            continue
        if q:
            hay = " ".join([d["name"], d["state"], d["country"], d["tagline"], d["region"], d["zone"], *d["tags"]]).lower()
            if q not in hay:
                continue
        out.append(d)
    return out[:limit]


def recommended(limit: int = 6):
    order = {i: n for n, i in enumerate(FEATURED_ORDER)}
    featured = sorted((d for d in DESTINATIONS if d["id"] in order), key=lambda d: order[d["id"]])
    rest = [d for d in DESTINATIONS if d["id"] not in order]
    return (featured + rest)[:limit]
