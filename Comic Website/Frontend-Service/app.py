from flask import Flask, render_template, request, session, redirect,send_from_directory,g
import requests
import os

ITEM_FOLDER = os.environ.get("ITEM_FOLDER", "/items")

app = Flask(__name__)
app.config.from_mapping(
    SECRET_KEY="it_is_secret",
    JWT_SECRET_KEY = "Pepsi max",
    JWT_TOKEN_LOCATION = "Header"        
    )

#bff base address
BFF_BADD = "http://bff-service:5001"

#This is the header that will be carried with bff calls whenever there's need for it. Previously on frontend-service, when logging in token is saved in the session
def bff_header():
    token = session.get("token")
    if token:
        return {"Authorization": f"Bearer {token}"}
    else:
        return {}

#get the proper user for the session. The navbar is dependent on this to switch to a logged in navbar
@app.before_request
def load_user():
    g.user = session.get("user_id")


#The comics are not in the same folder as frontend-service like it was in the monolithic structure. So this basically gets the files needed from items folder.
@app.route("/items/<path:path>")
def send_file(path):
    return send_from_directory(ITEM_FOLDER,path)

@app.route("/")
def index():
    return redirect("home")

'''
There's nothing better than being at home! |_| <- my attempt at a home. Missing the roof... Oh well, basically it calls bff's url that's used to receive all comics.
And then we check if there's a token in the session. if there is, the service knows somebody has logged in and sets the user to true
'''
@app.route("/home")
def home():
    received = requests.get(f'{BFF_BADD}/Comics')
    loggedIn = session.get("token")
    if received.status_code == 200:
        if loggedIn:
            return render_template('home.html',comics=received.json(),user=True)
        else:
            return render_template('home.html',comics=received.json(), user=False)
    else:
        return render_template('home.html',comics =[])

'''Basically the same like all others, but it has post and get. Get automatically happens since the if statement won't be accepted till there's a POST.
Then bff is called with the request form and if everything goes smoothly, the session parameters are filled and user is redirected to home.
'''
@app.route("/login", methods =["GET", "POST"])
def login():
    if request.method == "POST":
        received = requests.post(f'{BFF_BADD}/login',data=request.form)
        if received.status_code == 200:
            session["token"] = received.json().get("token")
            session["user_id"] = received.json().get("user_id")
            session["username"] = received.json().get("username")
            return redirect("home")
        else:
            return {},400
    
    return render_template('auth/login.html')

#SSame as login, but at success it just redirects to login
@app.route("/register", methods = ["GET","POST"])
def register():
    if request.method == "POST":
        received = requests.post(f'{BFF_BADD}/register', data=request.form)
        if received.status_code == 201:
            return redirect("login")
        
    return render_template('auth/register.html')

#gets the comic that's needed. Only get, because well it gets!
@app.route('/comic/<id>', methods=["GET"])
def comic(id):
    received = requests.get(f"{BFF_BADD}/Comic/{id}")
    if received.status_code == 200:
        return render_template('catalogue/comic.html', comic=received.json())
    else:
        return render_template('catalogue/comic.html')
    
@app.route('/comics')
def comics():
    received = requests.get(f'{BFF_BADD}/Comics',params={"publisher": request.args.get("publisher")})
    if received.status_code == 200:
        return render_template('catalogue/comics.html', comics=received.json())
    return render_template('catalogue/comics.html')

@app.route('/read/<int:series_id>/<int:issue_number>/<int:page>')
def read(series_id,issue_number,page):
    received = requests.get(f"{BFF_BADD}/Issue/read/{series_id}/{issue_number}/{page}")
    if received.status_code == 200:
        series_id = received.json().get("series_id")
        issue_number = received.json().get("issue_number")
        page = received.json().get("page")
        img_path = received.json().get("img_path")
        issues_count = received.json().get("issues_count")
        print(issues_count)
        return render_template('catalogue/read.html', series_id=series_id,issue_number=issue_number,page=page,img_path=img_path, issues_count=issues_count)
    else:
        return render_template('catalogue/read.html')

@app.route('/profile')
def profile():
    user_id = session.get("user_id")
    received = requests.get(f"{BFF_BADD}/profile/{user_id}")
    if received.status_code == 200:
        username = received.json().get("username")
        received = requests.get(f"{BFF_BADD}/profile/comics/{user_id}")
        if received.status_code == 200:
            return render_template('user/profile.html',username=username, comics=received.json())

#This is where bff_header() gets their run on the field! Since we need to make sure the uploaded comic gets its owner, 
#the headers parameter of post is filled using bff_header()
@app.route("/add_series",methods=["GET", "POST"])
def add_series():
    
    if request.method == "POST":
        
        file = request.files["front_page"]
        files = {'front_page': (file.filename, file.stream, file.mimetype)}
        received = requests.post(f"{BFF_BADD}/Upload/comic", data=request.form,files = files,headers=bff_header())
    
        if received.status_code == 200:
            return redirect("profile")
        else:
            return {},400
    
    return render_template('user/add_series.html')

@app.route('/add_issue', methods=["GET","POST"])
def add_issue():
    user_id = session.get("user_id")
    
    if request.method == "POST":
        
        file = request.files["issue"]
        files = {'issue': (file.filename, file.stream, file.mimetype)}
        received = requests.post(f"{BFF_BADD}/Upload/issue", data=request.form,files = files,headers=bff_header())
        if received.status_code == 201:
            return redirect("profile")
        else:
            return {},400
        
    received = requests.get(f"{BFF_BADD}/profile/comics/{user_id}")
    if received.status_code == 200:
        return render_template('user/add_issue.html', series = received.json())
    
    return render_template('user/add_issue.html')


@app.route('/logout')
def logout():
    session.clear()
    return redirect('home')

if __name__ == "__main__":
    app.run(host="0.0.0.0", port =5000)
