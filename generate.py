import random
import string
from datetime import datetime, timedelta

def generate_name():
    first_names = ["John", "Emma", "Michael", "Sophia", "William", "Olivia", "James", "Ava", "Benjamin", "Isabella",
                   "Ethan", "Mia", "Alexander", "Charlotte", "Daniel", "Amelia", "Matthew", "Harper", "Joseph", "Evelyn",
                   "David", "Abigail", "Jackson", "Emily", "Samuel", "Elizabeth", "Henry", "Sofia", "Andrew", "Avery",
                   "Jacob", "Ella", "Joshua", "Scarlett", "Christopher", "Grace", "Nicholas", "Chloe", "Tyler", "Victoria"]
    last_names = ["Smith", "Johnson", "Brown", "Taylor", "Miller", "Davis", "Garcia", "Wilson", "Martinez", "Anderson",
                  "Thomas", "Jackson", "White", "Harris", "Martin", "Thompson", "Moore", "Young", "Allen", "King",
                  "Wright", "Scott", "Green", "Baker", "Adams", "Nelson", "Carter", "Mitchell", "Perez", "Roberts",
                  "Turner", "Phillips", "Campbell", "Parker", "Evans", "Edwards", "Collins", "Stewart", "Sanchez", "Morris"]
    return f"{random.choice(first_names)} {random.choice(last_names)}"

# Function to generate random addresses
def generate_address():
    street_names = ["Main St", "Oak Ave", "Maple Rd", "Cedar Ln", "Elm St", "Pine Ave", "Birch Rd", "Walnut Ln", "Spruce St", "Ash Ave",
                    "Willow Dr", "Cypress Ct", "Sycamore Ter", "Magnolia Blvd", "Chestnut Way", "Hickory Pl", "Beech Cir", "Poplar Trl", "Aspen Hts", "Cottonwood Pkwy",
                    "Mulberry Sq", "Hawthorn Cres", "Redwood Grove", "Juniper Hills", "Linden Meadow", "Laurel Valley", "Dogwood Ridge", "Fir Glen", "Hemlock Brook", "Olive Garden",
                    "Myrtle Island", "Rosewood Estates", "Tamarack Crossing", "Sage Meadows", "Lilac Fields", "Lavender Lane", "Jasmine Court", "Daisy Drive", "Orchid Avenue", "Tulip Road"]
    cities = ["New York", "Los Angeles", "Chicago", "Houston", "Phoenix", "Philadelphia", "San Antonio", "San Diego", "Dallas", "San Jose",
              "Austin", "Jacksonville", "Fort Worth", "Columbus", "San Francisco", "Charlotte", "Indianapolis", "Seattle", "Denver", "Washington",
              "Boston", "Nashville", "El Paso", "Detroit", "Memphis", "Portland", "Oklahoma City", "Las Vegas", "Louisville", "Baltimore",
              "Milwaukee", "Albuquerque", "Tucson", "Fresno", "Sacramento", "Mesa", "Atlanta", "Kansas City", "Colorado Springs", "Miami"]
    states = ["NY", "CA", "IL", "TX", "AZ", "PA", "TX", "CA", "TX", "CA",
              "TX", "FL", "TX", "OH", "CA", "NC", "IN", "WA", "CO", "DC",
              "MA", "TN", "TX", "MI", "TN", "OR", "OK", "NV", "KY", "MD",
              "WI", "NM", "AZ", "CA", "CA", "AZ", "GA", "MO", "CO", "FL"]
    return f"{random.randint(100, 999)} {random.choice(street_names)}", random.choice(cities), random.choice(states), str(random.randint(10000, 99999)).zfill(5)
# Function to generate random phone numbers
def generate_phone_number():
    return ''.join(random.choices(string.digits, k=10))

# Function to generate random dates
def generate_date(start_date, end_date):
    time_between_dates = end_date - start_date
    days_between_dates = time_between_dates.days
    random_number_of_days = random.randrange(days_between_dates)
    random_date = start_date + timedelta(days=random_number_of_days)
    return random_date

# Generate data for the "criminals" table
def generate_criminals_data(file, num_records):
    for i in range(num_records):
        criminal_id = i + 1
        violent_stat = random.choice([True, False])
        probation_stat = random.choice([True, False])
        name = generate_name()
        file.write(f"INSERT INTO criminals (Criminal_ID, Violent_Stat, Probation_Stat, Name) VALUES ({criminal_id}, {violent_stat}, {probation_stat}, '{name}');\n")

# Generate data for the "address" table
def generate_address_data(file, num_records):
    for i in range(num_records):
        criminal_id = i + 1
        addr, city, state, zip_code = generate_address()
        file.write(f"INSERT INTO address (Criminal_ID, Addr, City, State, Zip_Code) VALUES ({criminal_id}, '{addr}', '{city}', '{state}', '{zip_code}');\n")


# Generate data for the "aliases" table
def generate_aliases_data(file, num_records):
    for i in range(num_records):
        criminal_id = i + 1
        num_aliases = random.randint(0, 3)
        for j in range(num_aliases):
            alias = generate_name()
            file.write(f"INSERT INTO aliases (Criminal_ID, Alias) VALUES ({criminal_id}, '{alias}');\n")

# Generate data for the "crimes" table
def generate_crimes_data(file, num_records):
    crime_codes = ["A100", "B200", "C300", "D400", "E500"]
    classifications = ["Felony", "Misdemeanor", "Infraction"]
    for i in range(num_records):
        crime_id = i + 1
        criminal_id = random.randint(1, num_records)
        crime_code = random.choice(crime_codes)
        classification = random.choice(classifications)
        file.write(f"INSERT INTO crimes (Crime_ID, Criminal_ID, Crime_Code, Classification) VALUES ({crime_id}, {criminal_id}, '{crime_code}', '{classification}');")

# Generate data for the "appeals" table
def generate_appeals_data(file, num_records):
    appeal_statuses = ["Filed", "Pending", "Granted", "Denied"]
    for i in range(num_records):
        crime_id = i + 1
        filing_date = generate_date(datetime(2020, 1, 1), datetime(2023, 12, 31))
        hearing_date = filing_date + timedelta(days=random.randint(30, 180))
        appeal_status = random.choice(appeal_statuses)
        file.write(f"INSERT INTO appeals (Crime_ID, Filing_Date, Hearing_Date, Appeal_Status) VALUES ({crime_id}, '{filing_date}', '{hearing_date}', '{appeal_status}');")

# Generate data for the "charges" table
def generate_charges_data(file, num_records):
    for i in range(num_records):
        crime_id = i + 1
        charge_date = generate_date(datetime(2020, 1, 1), datetime(2023, 12, 31))
        charge_status = charge_date + timedelta(days=random.randint(30, 180))
        file.write(f"INSERT INTO charges (Crime_ID, Charge_Status, Charge_Date) VALUES ({crime_id}, '{charge_status}', '{charge_date}');")

# Generate data for the "officer" table
def generate_officer_data(file, num_records):
    precincts = ["1st Precinct", "2nd Precinct", "3rd Precinct", "4th Precinct", "5th Precinct"]
    officer_statuses = ["Active", "Inactive", "Suspended", "Retired"]
    for i in range(num_records):
        badge_number = i + 1
        name = generate_name()
        precinct = random.choice(precincts)
        officer_status = random.choice(officer_statuses)
        file.write(f"INSERT INTO officer (Badge_Number, Name, Precinct, Officer_Status) VALUES ({badge_number}, '{name}', '{precinct}', '{officer_status}');")

# Generate data for the "arresting_officers" table
def generate_arresting_officers_data(file, num_records):
    for i in range(num_records):
        crime_id = i + 1
        badge_id = random.randint(1, num_records)
        file.write(f"INSERT INTO arresting_officers (Crime_ID, Badge_ID) VALUES ({crime_id}, {badge_id});")

# Generate data for the "hearing" table
def generate_hearing_data(file, num_records):
    for i in range(num_records):
        crime_id = i + 1
        hearing_date = generate_date(datetime(2020, 1, 1), datetime(2023, 12, 31))
        appeal_cutoff_date = hearing_date + timedelta(days=random.randint(30, 180))
        file.write(f"INSERT INTO hearing (Crime_ID, Hearing_Date, Appeal_Cutoff_Date) VALUES ({crime_id}, '{hearing_date}', '{appeal_cutoff_date}');")

# Generate data for the "sentencing" table
def generate_sentencing_data(file, num_records):
    sentence_types = ["Incarceration", "Probation", "Community Service", "Fine"]
    for i in range(num_records):
        crime_id = i + 1
        start_date = generate_date(datetime(2020, 1, 1), datetime(2023, 12, 31))
        end_date = start_date + timedelta(days=random.randint(30, 1000))
        violation_num = random.randint(0, 5)
        sentence_type = random.choice(sentence_types)
        file.write(f"INSERT INTO sentencing (Crime_ID, Start_Date, End_Date, Violation_Num, Sentence_Type) VALUES ({crime_id}, '{start_date}', '{end_date}', {violation_num}, '{sentence_type}');")

# Generate data for the "monetary" table
def generate_monetary_data(file, num_records):
    for i in range(num_records):
        crime_id = i + 1
        amount_fined = round(random.uniform(100, 10000), 2)
        amount_paid = round(random.uniform(0, amount_fined), 2)
        court_fee = round(random.uniform(50, 1000), 2)
        due_date = generate_date(datetime(2020, 1, 1), datetime(2023, 12, 31))
        file.write(f"INSERT INTO monetary (Crime_ID, Amount_Fined, Amount_Paid, Court_Fee, Due_Date) VALUES ({crime_id}, {amount_fined}, {amount_paid}, {court_fee}, '{due_date}');")

# Generate data for the "criminal_phone" table
def generate_criminal_phone_data(file, num_records):
    for i in range(num_records):
        criminal_id = i + 1
        num_phones = random.randint(0, 3)
        for j in range(num_phones):
            number = generate_phone_number()
            file.write(f"INSERT INTO criminal_phone (Criminal_ID, Number) VALUES ({criminal_id}, '{number}');")

# Generate data for the "officer_phone" table
def generate_officer_phone_data(file, num_records):
    for i in range(num_records):
        badge_number = i + 1
        num_phones = random.randint(0, 2)
        for j in range(num_phones):
            number = generate_phone_number()
            file.write(f"INSERT INTO officer_phone (Badge_Number, Number) VALUES ({badge_number}, '{number}');")

with open("insert_statements.sql", "w") as file:
    num_records = 1000
    generate_criminals_data(file, num_records)
    generate_address_data(file, num_records)
    generate_aliases_data(file, num_records)
    generate_crimes_data(file, num_records)
    generate_appeals_data(file, num_records)
    generate_charges_data(file, num_records)
    generate_officer_data(file, num_records)
    generate_arresting_officers_data(file, num_records)
    generate_hearing_data(file, num_records)
    generate_sentencing_data(file, num_records)
    generate_monetary_data(file, num_records)
    generate_criminal_phone_data(file, num_records)
    generate_officer_phone_data(file, num_records)