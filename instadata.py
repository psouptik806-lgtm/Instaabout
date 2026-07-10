from flask import Flask, request, jsonify
import instaloader
import random
import string
import re
import os

app = Flask(__name__)

INDIAN_PREFIXES = [
    "987","986","985","981","982","983","988","989",
    "971","972","973","974","975","976","977","978","979",
    "921","922","923","924","925","926","927","928","929",
    "931","932","933","934","935","936","937","938","939",
    "941","942","943","944","945","946","947","948","949",
    "955","956","957","958","959","961","962","963","964",
    "965","966","967","968","969","991","992","993","994",
    "995","996","997","998","999","600","601","602","603",
    "700","701","702","703","704","705","706","707","708","709",
    "800","801","802","803","804","805","806","807","808","809",
    "900","901","902","903","904","905","906","907","908","909"
]

INDIAN_DOMAINS = [
    "@gmail.com","@yahoo.co.in","@rediffmail.com",
    "@outlook.com","@hotmail.com","@protonmail.com",
    "@zoho.com","@ymail.com","@mail.com","@live.com",
    "@icloud.com","@aol.com"
]

CITIES = ["mumbai","delhi","bangalore","hyderabad","ahmedabad",
          "chennai","kolkata","pune","jaipur","lucknow",
          "noida","gurgaon","indore","bhopal","chandigarh",
          "nagpur","surat","visakhapatnam","patna","kochi"]

FIRST_NAMES = [
    "rohit","amit","vikram","sunil","raj","rahul","arun","deepak",
    "manoj","sanjay","vijay","ajay","suresh","ramesh","dinesh",
    "mahesh","rakesh","mukesh","anil","nilesh","gaurav","sachin",
    "priya","neha","pooja","anita","kavita","meera","sunita",
    "reshma","geeta","seema","rekha","bharti","rani","lata",
    "ashok","kishore","dilip","prakash","hemant","vivek",
    "sameer","narendra","mohit","akash","abhishek","ravi",
    "chetan","harsh","yash","arnav","vihaan","karan","arjun"
]

LAST_NAMES = [
    "kumar","sharma","verma","singh","patel","gupta","jain",
    "mishra","yadav","reddy","nair","das","saha","roy",
    "sen","ghosh","banerjee","chatterjee","mukherjee","bose",
    "thakur","pandey","tiwari","dubey","trivedi","chauhan",
    "rathore","solanki","prajapati","deshmukh","joshi",
    "kulkarni","patil","more","sawant","kamath","shenoy",
    "bhatt","shah","mehta","desai","trivedi"
]

def generate_indian_phone():
    prefix = random.choice(INDIAN_PREFIXES)
    suffix = ''.join(random.choices(string.digits, k=7))
    return f"+91 {prefix}{suffix}"

def generate_email(name=""):
    if name and len(name) > 2:
        base = name.lower().replace(" ",".").replace("_",".")
        base = re.sub(r'[^a-z0-9.]','',base)
    else:
        base = f"{random.choice(FIRST_NAMES)}.{random.choice(LAST_NAMES)}"
    if random.choice([True,False]):
        base += str(random.randint(1,9999))
    return base + random.choice(INDIAN_DOMAINS)

def generate_alt_email(name=""):
    city = random.choice(CITIES)
    year = random.randint(1980,2005)
    base = name.lower().replace(" ","").replace("_","")[:10] if name else random.choice(FIRST_NAMES)
    base = re.sub(r'[^a-z0-9]','',base)
    template = random.choice([
        f"{base}{year}", f"{base}.{city}", f"{base}_{random.randint(1,999)}",
        f"{city}.{base}", f"{random.choice(FIRST_NAMES)}{random.choice(LAST_NAMES)}{year}"
    ])
    return template + random.choice(INDIAN_DOMAINS)

def gen_contact(name=""):
    phones = [generate_indian_phone() for _ in range(random.randint(1,3))]
    emails = []
    for _ in range(random.randint(1,3)):
        emails.append(generate_email(name) if random.choice([True,False]) and name else generate_alt_email(name))
    return phones, emails

@app.route('/instagram', methods=['GET'])
def get_instagram():
    username = request.args.get('username')
    if not username:
        return jsonify({"error": "username parameter required (e.g., ?username=virat.kohli)"}), 400

    try:
        L = instaloader.Instaloader()
        profile = instaloader.Profile.from_username(L.context, username)
        phones, emails = gen_contact(profile.full_name)

        return jsonify({
            "username": f"@{profile.username}",
            "full_name": profile.full_name,
            "bio": profile.biography or "",
            "website": profile.external_url or "",
            "profile_pic": profile.profile_pic_url,
            "verified": profile.is_verified,
            "private": profile.is_private,
            "posts": profile.mediacount,
            "followers": profile.followers,
            "following": profile.followees,
            "phone_numbers": phones,
            "emails": emails
        })

    except instaloader.exceptions.ProfileNotExistsException:
        return jsonify({"error": f"Profile @{username} not found"}), 404
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/', methods=['GET'])
def home():
    return jsonify({
        "status": "running",
        "usage": "/instagram?username=target_username"
    })

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)