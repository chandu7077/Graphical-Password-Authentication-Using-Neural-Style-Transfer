from flask import Flask,render_template,request,url_for,redirect,session
from flask_sqlalchemy import SQLAlchemy
from flask_session import Session
import json
import requests
import os
import random,time
from flask_cors import CORS
UPLOAD_FOLDER = 'images/'
app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
cors = CORS(app)
app.config['CORS_HEADERS'] = 'Content-Type'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///users.sqlite3'
db = SQLAlchemy(app)
Session(app)

#pname=""
checkurl1=""
prevno=""
def apply_style(nsty,ncon,name=""):
    con="/root/Documents/app/images/"
    sty="/root/Documents/app/styles/"
    sty=sty+"style_"+str(nsty)+".jpg"
    con=con+name+str(ncon)+".jpg"
    r = requests.post(
        "https://api.deepai.org/api/fast-style-transfer",
        files={
            'content': open(con, 'rb'),
            'style': open(sty, 'rb'),
        },
        headers={'api-key': '17dbd89a-4fd6-4057-abf6-b3ddbc519b3c'}
    )
    dic=dict(r.json())
    url=dic["output_url"]
    return url

class User(db.Model):
    name=db.Column(db.String, primary_key = True)
    style=db.Column(db.Integer)

    def __init__(self,name,style):
        self.name=name
        self.style=style

@app.route('/')
def index():
    return render_template("index.html")

@app.route("/upload", methods=["POST"])
def upload():
    if request.method=="POST":
        dic={}
        dic["upload successful GO BACK"]="l"
        uploaded_files = request.files.getlist("images")
        for i,file in zip(range(1,len(uploaded_files)+1),uploaded_files):
            file.save(os.path.join(app.config['UPLOAD_FOLDER'],request.form["username"]+str(i)+".jpg"))
        return json.dumps(dic)

@app.route("/style",methods=["POST","GET"])
def style():
    print("style")
    if request.method=="POST":
        data=request.json
        name,style=data["name"],data["index"]
        session["name"]=name
        print(name,style)
        user=User(name,int(style))
        db.session.add(user)
        db.session.commit()
    return redirect(url_for("foo"))

@app.route("/foo")
def foo():
    pname=session["name"]
    time.sleep(5)
    user=User.query.filter_by(name=pname).all()[0]
    style=str(user.style)
    url1=apply_style(style,'1',pname)
    url2=apply_style(style,'2',pname)
    url3=apply_style(style,'3',pname)
    save_image(pname,url1,'1')
    save_image(pname,url2,'2')
    save_image(pname,url3,'3')
    return render_template("view.html",url1=url1,url2=url2,url3=url3)

def save_image(name,url,no):
    r = requests.get(url)
    fname="/root/Documents/app/styled/"
    fname=fname+name+"_styled_"+no+".jpg"
    with open(fname,'wb') as f:
        f.write(r.content)

@app.route("/login/step1",methods=["POST","GET"])
def login():
    global checkurl1,prevno
    if request.method=="POST":
        root="/root/Documents/app/images/"
        name=request.form.get("username")
        style=random.randrange(1,10)
        no=random.randrange(1,4)
        prevno=no
        try:
            ansurl=apply_style(str(style),str(no),name)
        except:
            return "<html><body><p>Error Occured</p></body></html>"
        session["checkurl1"]=ansurl
        cnt=1
        dic={}
        users=User.query.all()
        for user in users:
            if len(user.name)>0:
                dic[user.name]=[1,2,3]
        dic.pop(name)
        ansdic={}
        while cnt<9:
            user=random.choice(list(dic.keys()))
            if user in ansdic:
                if len(dic[user])>0:
                    no=random.choice(dic[user])
                    ansdic[user].append(no)
                    dic[user].remove(no)
                    cnt+=1
            else:
                no=random.randrange(1,4)
                ansdic[user]=[no]
                dic[user].remove(no)
                cnt+=1
        urls=[]
        urls.append(ansurl)
        for u in ansdic:
            for no in ansdic[u]:
                url=apply_style(str(style),str(no),u)
                urls.append(url)
        return render_template("step1.html",url=urls,name=name)


@app.route("/login/check1",methods=["POST","GET"])
def check1():
    if request.method=="POST":
        data=request.json
        url=data["url"]
        if url==checkurl1:
            return "ok"
    return "no"

furls=[]
@app.route("/login/step2",methods=["POST","GET"])
def login2():
    global checkurl2,checkurl3,prevno,furls
    if request.method=="GET":
        urls=[]
        name=request.args.get("nam")
        sli=[1,2,3,4,5,6,7,8,9]
        style=User.query.filter_by(name=name)[0].style
        sli.remove(style)
        li=[1,2,3]
        li.remove(prevno)
        n1,n2=li[0],li[1]
        ansurl2=apply_style(str(style),str(li[0]),name)
        ansurl3=apply_style(str(style),str(li[1]),name)
        style2=random.choice(sli)
        sli.remove(style2)
        url4,url5="",""
        url4=apply_style(str(style2),str(li[0]),name)
        url5=apply_style(str(style2),str(li[1]),name)
        checkurl2=ansurl2
        checkurl3=ansurl3
        urls.extend([ansurl2,ansurl3,url4,url5])
        cnt=4
        dic={}
        users=User.query.all()
        names=[]
        for user in users:
            names.append(user.name)
        chosen=[]
        name=random.choice(names)
        names.remove(name)
        urls.append(apply_style(str(style),str(n1),name))
        urls.append(apply_style(str(style),str(n2),name))
        urls.append(apply_style(str(style2),str(n1),name))
        urls.append(apply_style(str(style2),str(n2),name))
        name=random.choice(names)
        names.remove(name)
        style3=random.choice(sli)
        sli.remove(style3)
        style4=random.choice(sli)
        sli.remove(style4)
        urls.append(apply_style(str(style3),str(n1),name))
        urls.append(apply_style(str(style3),str(n2),name))
        urls.append(apply_style(str(style4),str(n1),name))
        urls.append(apply_style(str(style4),str(n2),name))
        name=random.choice(names)
        names.remove(name)
        urls.append(apply_style(str(style3),str(n1),name))
        urls.append(apply_style(str(style3),str(n2),name))
        urls.append(apply_style(str(style4),str(n1),name))
        urls.append(apply_style(str(style4),str(n2),name))
        print(urls)
        print(len(urls))
        furls=urls
        print(style,style2,style3,style4)
        return render_template("step2.html",url=furls)

@app.route("/final")
def final():
    return render_template("chandu.html")

checkcnt=0
@app.route("/login/check2",methods=["POST","GET"])
def check2():
    global checkcnt
    if request.method=="POST":
        data=request.json
        url=data["url"]
        if url in [checkurl2,checkurl3]:
            checkcnt+=1
        if checkcnt==2:
            return "ok"

    return "wrong password"






if __name__ == '__main__':
    db.create_all()
    app.run()
