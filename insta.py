from flask import Flask, request, render_template_string, redirect, session, url_for
import random
import string
import secrets
import hashlib

app = Flask(__name__)

# =========================================================
# FLASK SECRET KEY
# =========================================================
# Server restart হলে এই key বদলাবে, তাই production-এ
# নিজের permanent random key এখানে বসিয়ে রাখা ভালো।
app.secret_key = secrets.token_hex(32)

# =========================================================
# SIMPLE IN-MEMORY USER STORAGE
# =========================================================

USERS = {}


# =========================================================
# GENERATED DATA
# =========================================================

FIRST_NAMES = [
    "Aarav", "Rohan", "Arjun", "Rahul", "Aditya",
    "Vikram", "Karan", "Ankit", "Sourav", "Raj",
    "Priya", "Riya", "Sneha", "Ananya", "Ishita","Purnandu"
]

LAST_NAMES = [
    "Sharma", "Das", "Roy", "Sen", "Gupta",
    "Singh", "Dutta", "Ghosh", "Patel", "Verma","Pramanik"
]

CITIES = [
    ("Kolkata", "West Bengal"),
    ("Mumbai", "Maharashtra"),
    ("Delhi", "Delhi"),
    ("Bengaluru", "Karnataka"),
    ("Hyderabad", "Telangana"),
    ("Chennai", "Tamil Nadu"),
    ("Pune", "Maharashtra")
]

BIOS = [
    "Technology enthusiast • Creator • Explorer",
    "Digital creator • Learning every day",
    "Photography • Technology • Travel",
    "Building things on the internet",
    "Tech lover • Coding • Innovation",
    "INDIVIDUAL"
]


def digits(length):
    return "".join(
        random.choices(string.digits, k=length)
    )


def hash_password(password):
    return hashlib.sha256(
        password.encode("utf-8")
    ).hexdigest()


def generate_profile(username):

    username = username.strip().lstrip("@")

    first = random.choice(FIRST_NAMES)
    last = random.choice(LAST_NAMES)

    city, state = random.choice(CITIES)

    followers = random.randint(120, 985000)
    following = random.randint(50, 2500)
    posts = random.randint(5, 850)

    email = (
        first.lower()
        + "."
        + last.lower()
        + str(random.randint(10, 999))
        + "@example.com"
    )

    phone = "+91 " + digits(10)

    address = (
        f"{random.randint(10, 999)}, "
        f"{random.choice(['Park Street', 'Lake Road', 'MG Road', 'College Road'])}, "
        f"{city}, {state}"
    )

    return {
        "username": username,
        "name": f"{first} {last}",
        "id": digits(15),
        "followers": f"{followers:,}",
        "following": f"{following:,}",
        "posts": f"{posts:,}",
        "bio": random.choice(BIOS),
        "phone": phone,
        "email": email,
        "address": address,
        "city": city,
        "state": state
    }


# =========================================================
# HTML
# =========================================================

PAGE = r"""
<!DOCTYPE html>
<html lang="en">

<head>

<meta charset="UTF-8">

<meta name="viewport"
      content="width=device-width,initial-scale=1.0">

<title>Instagram Lookup</title>

<style>

*{
    box-sizing:border-box;
    margin:0;
    padding:0;
    font-family:Arial,Helvetica,sans-serif;
}

body{
    min-height:100vh;

    background:
        radial-gradient(
            circle at 50% -20%,
            rgba(0,255,102,.13),
            transparent 40%
        ),
        #020603;

    color:#dffff0;

    padding:25px 15px;
}

.container{
    width:100%;
    max-width:1000px;
    margin:auto;
}

/* ======================================================
   LOGO
====================================================== */

.logo{
    text-align:center;
    padding:20px 0;
}

.logo h1{
    font-size:46px;
    letter-spacing:5px;

    color:#00ff66;

    text-shadow:
        0 0 6px #00ff66,
        0 0 18px #00ff66,
        0 0 35px rgba(0,255,102,.5);
}

.logo p{
    margin-top:9px;
    color:#70987c;
}

/* ======================================================
   AUTH
====================================================== */

.auth-card{

    max-width:480px;

    margin:30px auto;

    padding:25px;

    background:#031109;

    border:1px solid #087a38;

    border-radius:20px;

    box-shadow:
        0 0 30px rgba(0,255,102,.08);
}

.auth-title{

    text-align:center;

    color:#00ff66;

    font-size:25px;

    margin-bottom:20px;
}

.auth-form{

    display:grid;

    gap:12px;
}

.auth-form input{

    background:#010603;

    color:white;

    border:1px solid #155f35;

    border-radius:11px;

    padding:14px;

    outline:none;
}

.auth-form input:focus{

    border-color:#00ff66;

    box-shadow:
        0 0 12px rgba(0,255,102,.15);
}

.auth-button{

    padding:14px;

    border:0;

    border-radius:11px;

    background:#00ff66;

    color:#001b08;

    font-weight:900;

    cursor:pointer;
}

.switch{

    margin-top:15px;

    text-align:center;

    color:#688e73;

    font-size:13px;
}

.switch a{

    color:#00ff66;

    text-decoration:none;
}

.error{

    margin-bottom:15px;

    padding:12px;

    background:#250707;

    border:1px solid #ff3838;

    color:#ff9999;

    border-radius:10px;

    font-size:13px;
}

/* ======================================================
   DASHBOARD
====================================================== */

.topbar{

    display:flex;

    justify-content:space-between;

    align-items:center;

    margin-bottom:20px;
}

.user-label{

    color:#70987c;

    font-size:13px;
}

.logout{

    color:#ff7777;

    text-decoration:none;

    font-size:13px;
}

/* ======================================================
   SEARCH
====================================================== */

.search-card{

    padding:25px;

    background:#031109;

    border:1px solid #087a38;

    border-radius:20px;
}

.search-form{

    display:flex;

    gap:12px;
}

.search-form input{

    flex:1;

    background:#010603;

    color:white;

    border:1px solid #155f35;

    border-radius:12px;

    padding:16px;

    outline:none;
}

.search-form input:focus{

    border-color:#00ff66;

    box-shadow:
        0 0 12px rgba(0,255,102,.15);
}

.search-button{

    padding:0 28px;

    border:0;

    border-radius:12px;

    background:#00ff66;

    color:#001b08;

    font-weight:900;

    cursor:pointer;
}

.search-info{

    margin-top:12px;

    font-size:11px;

    color:#527b60;
}

/* ======================================================
   RESULT
====================================================== */

.result{

    margin-top:25px;

    padding:25px;

    background:#020d07;

    border:1px solid #0a7938;

    border-radius:20px;
}

.profile-head{

    display:flex;

    align-items:center;

    gap:18px;

    padding-bottom:20px;

    border-bottom:
        1px solid #0c3020;
}

.avatar{

    width:82px;

    height:82px;

    border-radius:50%;

    display:flex;

    align-items:center;

    justify-content:center;

    background:
        linear-gradient(
            135deg,
            #00ff66,
            #063d1d
        );

    color:#001b08;

    font-size:26px;

    font-weight:900;

    border:2px solid #00ff66;

    box-shadow:
        0 0 20px rgba(0,255,102,.35);
}

.name{

    color:#00ff66;

    font-size:27px;

    font-weight:900;
}

.username{

    margin-top:5px;

    color:#628c6e;
}

.generated{

    display:inline-block;

    margin-top:7px;

    color:#79d894;

    font-size:10px;
}

.bio{

    margin-top:9px;

    color:#b6d9c0;

    font-size:13px;
}

/* ======================================================
   STATS
====================================================== */

.stats{

    display:grid;

    grid-template-columns:
        repeat(3,1fr);

    gap:10px;

    margin-top:20px;
}

.stat{

    text-align:center;

    padding:14px;

    background:#03140a;

    border-radius:10px;

    border:1px solid #0a3d20;
}

.stat strong{

    display:block;

    color:#00ff66;

    font-size:19px;
}

.stat span{

    color:#557d62;

    font-size:10px;
}

/* ======================================================
   INFO
====================================================== */

.info-grid{

    display:grid;

    grid-template-columns:
        repeat(2,1fr);

    gap:12px;

    margin-top:18px;
}

.info{

    padding:15px;

    background:#031109;

    border-left:
        3px solid #00ff66;

    border-radius:10px;
}

.info label{

    color:#527b60;

    font-size:10px;

    text-transform:uppercase;

    letter-spacing:1px;
}

.info div{

    margin-top:6px;

    color:#e7ffed;

    word-break:break-word;
}

/* ======================================================
   AD
====================================================== */

.ad-area{

    margin-top:30px;

    display:none;
}

.ad-area.visible{

    display:block;
}

.ad-card{

    background:#fff;

    color:#111;

    border-radius:10px;

    overflow:hidden;

    box-shadow:
        0 5px 30px rgba(0,255,102,.12);
}

.ad-header{

    display:flex;

    align-items:center;

    padding:13px;
}

.ad-avatar{

    width:42px;

    height:42px;

    border-radius:50%;

    background:#071d11;

    border:2px solid #00ff66;

    color:#00ff66;

    display:flex;

    align-items:center;

    justify-content:center;

    font-weight:900;

    margin-right:10px;
}

.ad-brand{

    font-weight:700;
}

.ad-sponsored{

    color:#777;

    font-size:11px;

    margin-top:2px;
}

.ad-text{

    padding:
        0 13px 14px;

    line-height:1.5;

    font-size:14px;
}

.ad-banner{

    min-height:220px;

    display:flex;

    align-items:center;

    justify-content:center;

    text-align:center;

    background:
        radial-gradient(
            circle,
            #063e20,
            #010604
        );

    color:#00ff66;
}

.ad-banner h2{

    font-size:30px;

    text-shadow:
        0 0 15px #00ff66;
}

.ad-banner p{

    margin-top:9px;

    color:#a5ffc0;
}

.ad-footer{

    display:flex;

    justify-content:space-between;

    align-items:center;

    padding:13px;

    background:#f0f2f5;
}

.ad-url{

    font-size:10px;

    color:#777;
}

.ad-title{

    margin-top:4px;

    font-size:14px;

    font-weight:700;
}

.ad-button{

    border:0;

    border-radius:6px;

    background:#1877f2;

    color:white;

    padding:9px 18px;

    font-weight:700;

    cursor:pointer;
}

.ad-timer{

    margin-top:8px;

    text-align:center;

    color:#557b61;

    font-size:11px;
}

/* ======================================================
   MOBILE
====================================================== */

@media(max-width:650px){

    .logo h1{
        font-size:34px;
    }

    .search-form{
        flex-direction:column;
    }

    .search-button{
        height:50px;
    }

    .info-grid{
        grid-template-columns:1fr;
    }

    .profile-head{
        flex-direction:column;
        text-align:center;
    }

}

</style>

</head>

<body>

<div class="container">

{% if not logged_in %}

<!-- ======================================================
     LOGIN / SIGNUP
====================================================== -->

<div class="logo">

<h1>INSTAGRAM LOOKUP</h1>

<p>
Secure Profile Lookup Interface
</p>

</div>

<div class="auth-card">

<div class="auth-title">

{% if mode == "signup" %}
Create Account
{% else %}
Welcome Back
{% endif %}

</div>

{% if error %}

<div class="error">
{{ error }}
</div>

{% endif %}

<form
    method="POST"
    action="{{ url_for('signup' if mode == 'signup' else 'login') }}"
    class="auth-form"
>

<input
    type="text"
    name="username"
    placeholder="Username"
    required
>

<input
    type="password"
    name="password"
    placeholder="Password"
    required
>

<button
    class="auth-button"
    type="submit"
>
{% if mode == "signup" %}
SIGN UP
{% else %}
LOGIN
{% endif %}
</button>

</form>

<div class="switch">

{% if mode == "signup" %}

Already have an account?
<a href="{{ url_for('login') }}">Login</a>

{% else %}

Don't have an account?
<a href="{{ url_for('signup') }}">Create Account</a>

{% endif %}

</div>

</div>

{% else %}

<!-- ======================================================
     LOGGED-IN DASHBOARD
====================================================== -->

<div class="logo">

<h1>INSTAGRAM LOOKUP</h1>

<p>
Profile Search Interface
</p>

</div>

<div class="topbar">

<div class="user-label">
Logged in as <b>{{ current_user }}</b>
</div>

<a
    class="logout"
    href="{{ url_for('logout') }}"
>
Logout
</a>

</div>


<div class="search-card">

<form
    method="POST"
    action="{{ url_for('lookup') }}"
    class="search-form"
>

<input
    type="text"
    name="target"
    placeholder="Enter Instagram username"
    value="{{ target }}"
    required
>

<button
    class="search-button"
    type="submit"
>
LOOKUP
</button>

</form>

<div class="search-info">

Enter a username such as @example_user.

</div>

</div>


{% if error %}

<div class="error">
{{ error }}
</div>

{% endif %}


{% if profile %}

<!-- ======================================================
     PROFILE RESULT
====================================================== -->

<div class="result">

<div class="profile-head">

<div class="avatar">
{{ profile.name[0] }}
</div>

<div>

<div class="name">
{{ profile.name }}
</div>

<div class="username">
@{{ profile.username }}
</div>

<span class="generated">
Generated information
</span>

<div class="bio">
{{ profile.bio }}
</div>

</div>

</div>


<div class="stats">

<div class="stat">

<strong>
{{ profile.posts }}
</strong>

<span>
POSTS
</span>

</div>

<div class="stat">

<strong>
{{ profile.followers }}
</strong>

<span>
FOLLOWERS
</span>

</div>

<div class="stat">

<strong>
{{ profile.following }}
</strong>

<span>
FOLLOWING
</span>

</div>

</div>


<div class="info-grid">

<div class="info">

<label>
Instagram ID
</label>

<div>
{{ profile.id }}
</div>

</div>


<div class="info">

<label>
Mobile
</label>

<div>
{{ profile.phone }}
</div>

</div>


<div class="info">

<label>
Email
</label>

<div>
{{ profile.email }}
</div>

</div>


<div class="info">

<label>
Address
</label>

<div>
{{ profile.address }}
</div>

</div>


<div class="info">

<label>
City
</label>

<div>
{{ profile.city }}
</div>

</div>


<div class="info">

<label>
State
</label>

<div>
{{ profile.state }}
</div>

</div>

</div>

</div>

{% endif %}


<!-- ======================================================
     ADVERTISEMENT
====================================================== -->

<div
    id="adArea"
    class="ad-area"
>

<div class="ad-card">

<div class="ad-header">

<div class="ad-avatar">
CO
</div>

<div>

<div class="ad-brand">
CYBER ORION TIPS
</div>

<div class="ad-sponsored">
Sponsored · Paid Promotion
</div>

</div>

</div>


<div class="ad-text">

💻 Ready to master technology?

Explore premium technology strategies,
network learning resources and cybersecurity
educational content.

</div>


<div class="ad-banner">

<div>

<h2>
CYBER ORION TIPS
</h2>

<p>
Premium Cybersecurity Learning
</p>

</div>

</div>


<div class="ad-footer">

<div>

<div class="ad-url">
youtube.com
</div>

<div class="ad-title">
Unlock Premium Cyber Strategies 🚀
</div>

</div>

<button
    class="ad-button"
    onclick="window.open(
        'https://youtube.com',
        '_blank'
    )"
>
Visit
</button>

</div>

</div>

<div class="ad-timer">

Next advertisement in
<span id="timer">5</span>s

</div>

</div>


<script>

/* =====================================================
   5 SECOND AD ROTATION
===================================================== */

let remaining = 5;

const adArea =
    document.getElementById("adArea");

const timer =
    document.getElementById("timer");


function showAd(){

    adArea.classList.add("visible");

    remaining = 5;

}


setInterval(function(){

    remaining--;

    if(timer){

        timer.textContent =
            remaining;

    }

    if(remaining <= 0){

        showAd();

    }

}, 1000);

</script>

{% endif %}

</div>

</body>
</html>
"""


# =========================================================
# LOGIN
# =========================================================

@app.route("/login", methods=["GET", "POST"])
def login():

    error = None

    if request.method == "POST":

        username = request.form.get(
            "username", ""
        ).strip().lower()

        password = request.form.get(
            "password", ""
        )

        if username not in USERS:

            error = "Account not found."

        elif USERS[username] != hash_password(password):

            error = "Incorrect password."

        else:

            session["user"] = username

            return redirect(
                url_for("home")
            )

    return render_template_string(
        PAGE,
        logged_in=False,
        mode="login",
        error=error
    )


# =========================================================
# SIGNUP
# =========================================================

@app.route("/signup", methods=["GET", "POST"])
def signup():

    error = None

    if request.method == "POST":

        username = request.form.get(
            "username", ""
        ).strip().lower()

        password = request.form.get(
            "password", ""
        )

        if len(username) < 3:

            error = "Username must contain at least 3 characters."

        elif len(password) < 6:

            error = "Password must contain at least 6 characters."

        elif username in USERS:

            error = "Username already exists."

        else:

            USERS[username] = hash_password(
                password
            )

            session["user"] = username

            return redirect(
                url_for("home")
            )

    return render_template_string(
        PAGE,
        logged_in=False,
        mode="signup",
        error=error
    )


# =========================================================
# HOME
# =========================================================

@app.route("/")
def home():

    if "user" not in session:

        return redirect(
            url_for("login")
        )

    return render_template_string(
        PAGE,
        logged_in=True,
        current_user=session["user"],
        profile=None,
        error=None,
        target=""
    )


# =========================================================
# LOOKUP
# =========================================================

@app.route("/lookup", methods=["POST"])
def lookup():

    if "user" not in session:

        return redirect(
            url_for("login")
        )

    target = request.form.get(
        "target", ""
    ).strip()

    error = None
    profile = None

    if not target:

        error = "Please enter an Instagram username."

    elif len(target) > 100:

        error = "Username is too long."

    else:

        profile = generate_profile(
            target
        )

    return render_template_string(
        PAGE,
        logged_in=True,
        current_user=session["user"],
        profile=profile,
        error=error,
        target=target
    )


# =========================================================
# LOGOUT
# =========================================================

@app.route("/logout")
def logout():

    session.clear()

    return redirect(
        url_for("login")
    )


# =========================================================
# HEALTH CHECK
# =========================================================

@app.route("/health")
def health():

    return {
        "status": "online",
        "service": "Instagram Lookup"
    }


# =========================================================
# START SERVER
# =========================================================

if __name__ == "__main__":

    app.run(
        host="0.0.0.0",
        port=5000,
        debug=False
    )
