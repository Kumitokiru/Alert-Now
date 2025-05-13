import os
import time
import pandas as pd
import googlemaps
from dotenv import load_dotenv

# Load environment variables from a .env file
load_dotenv()

# Retrieve the API key from environment variables
api_key = os.getenv("GOOGLE_API_KEY")
if not api_key:
    raise RuntimeError("Please set the GOOGLE_API_KEY environment variable.")

# Initialize the Google Maps client
gmaps = googlemaps.Client(key=api_key)

# Dictionary mapping cities to their respective barangays
barangays_by_city = {
    "San Pablo City": [
        "Atisan", "Bagong Bayan II-A", "Bagong Pook VI-C", "Barangay I-A",
        "Barangay I-B", "Barangay II-A", "Barangay II-B", "Barangay II-C",
        "Barangay II-D", "Barangay II-E", "Barangay II-F", "Barangay III-A",
        "Barangay III-B", "Barangay III-C", "Barangay III-D", "Barangay III-E",
        "Barangay III-F", "Barangay IV-A", "Barangay IV-B", "Barangay IV-C",
        "Barangay V-A", "Barangay V-B", "Barangay V-C", "Barangay V-D",
        "Barangay VI-A", "Barangay VI-B", "Barangay VI-D", "Barangay VI-E",
        "Barangay VII-A", "Barangay VII-B", "Barangay VII-C", "Barangay VII-D",
        "Barangay VII-E", "Bautista", "Concepcion", "Del Remedio", "Dolores",
        "San Antonio 1", "San Antonio 2", "San Bartolome",
        "San Buenaventura", "San Crispin", "San Cristobal", "San Diego",
        "San Francisco", "San Gabriel", "San Gregorio", "San Ignacio",
        "San Isidro", "San Joaquin", "San Jose", "San Juan", "San Lorenzo",
        "San Lucas 1", "San Lucas 2", "San Marcos", "San Mateo", "San Miguel",
        "San Nicolas", "San Pedro", "San Rafael", "San Roque", "San Vicente",
        "Sta. Ana", "Sta. Catalina", "Sta. Cruz", "Sta. Felomina",
        "Sta. Isabel", "Sta. Maria", "Sta. Maria Magdalena", "Sta. Monica",
        "Sta. Veronica I", "Sta. Veronica II", "Santiago I", "Santiago II",
        "Santisimo Rosario", "Santo Angel", "Santo Cristo", "Santo Niño",
        "Soledad"
    ],
    "Quezon Province": [
        "Anastacia", "Aquino", "Ayusan I", "Ayusan II", "Behia", "Bukal", "Bula",
        "Bulakin", "Cabatang", "Cabay", "Del Rosario", "Lagalag", "Lalig",
        "Lumingon", "Lusacan", "Paiisa", "Palagaran", "Poblacion I",
        "Poblacion II", "Poblacion III", "Poblacion IV", "Quipot",
        "San Agustin", "San Francisco", "San Isidro", "San Jose", "San Juan",
        "San Pedro", "Tagbakin", "Talisay", "Tamisian"
    ]
}

# Function to geocode a barangay and return its latitude and longitude
def geocode_barangay(barangay: str, city: str) -> (float, float):
    """Return (lat, lng) for 'barangay, city, Philippines' or (None, None) if not found."""
    query = f"{barangay}, {city}, Philippines"
    try:
        result = gmaps.geocode(query)
        if not result:
            print(f"Geocoding failed for: {query}")
            return None, None
        loc = result[0]["geometry"]["location"]
        return loc["lat"], loc["lng"]
    except Exception as e:
        print(f"Error geocoding {query}: {e}")
        return None, None

# Iterate through each barangay and collect their coordinates
rows = []
for city, barangays in barangays_by_city.items():
    for brgy in barangays:
        lat, lng = geocode_barangay(brgy, city)
        rows.append({
            "city": city,
            "barangay": brgy,
            "latitude": lat,
            "longitude": lng
        })
        # Delay to respect API rate limits
        time.sleep(0.1)

# Create a DataFrame and save to CSV
df = pd.DataFrame(rows, columns=["city", "barangay", "latitude", "longitude"])
output_file = "barangay_locations.csv"
df.to_csv(output_file, index=False, encoding="utf-8-sig")
print(f"Saved {len(df)} rows to {output_file}")
