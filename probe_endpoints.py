import requests, time, os

base = "https://na.gov.pk/en/includes/getpartlimentyears.php"
headers = {"User-Agent": "nigran-sandbox (student project; hamzakhattak188@gmail.com)"}

calls = [
    ("1_years",    {"tenure_id": 21}),
    ("2_sessions", {"Tenure_ID": 21, "ParYear_id": 73}),
    ("3_list",     {"tenureid": 21, "py_id": 73, "session_id": ""}),
]

os.makedirs("responses", exist_ok=True)
for name, params in calls:
    r = requests.get(base, params=params, headers=headers, timeout=30)
    print("=====", name, "| status:", r.status_code, "| length:", len(r.text))
    print(r.text[:1500])
    with open(f"responses/{name}.html", "w", encoding="utf-8") as f:
        f.write(r.text)
    time.sleep(10)