from flask import Flask,render_template,request,redirect,session,send_file
from knowledgebase import diseases
from semantic_network import show_network
from neo4j_connection import get_diseases
import os
import joblib
import pandas as pd
import numpy as np
import joblib
import time

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

model_path = os.path.join(BASE_DIR, "model.pkl")
encoder_path = os.path.join(BASE_DIR, "encoder.pkl")

model = joblib.load(model_path)
encoder = joblib.load(encoder_path)

app=Flask(__name__)
app.secret_key="medical123"

# -------------------
# Register Page
# -------------------

@app.route('/register',methods=['GET','POST'])
def register():

    if request.method=="POST":

        user=request.form['username']
        pwd=request.form['password']

        file=open("users.txt","a")
        file.write(user+","+pwd+"\n")
        file.close()

        return render_template("register.html",
                               msg="Registration Successful")

    return render_template("register.html")


# -------------------
# Login Page
# -------------------

@app.route('/',methods=['GET','POST'])
def login():

    if request.method=="POST":

        user=request.form['username']
        pwd=request.form['password']

        file=open("users.txt","r")
        users=file.readlines()
        file.close()

        valid=False

        for u in users:

            data=u.strip().split(",")

            if len(data)==2:

                if user==data[0] and pwd==data[1]:
                    valid=True

        if valid:

            session['user']=user
            return redirect("/home")

        else:

            return render_template("login.html",
                                   error="Invalid Login")

    return render_template("login.html")


# -------------------
# User Profile
# -------------------

@app.route('/profile')
def profile():

    if 'user' not in session:
        return redirect("/")

    username=session['user']

    count=0
    history_data=[]

    try:

        file=open("history.txt","r")
        lines=file.readlines()
        file.close()

        for line in lines:

            if username in line:

                history_data.append(line)
                count+=1

    except:
        pass

    return render_template("profile.html",
                           user=username,
                           total=count,
                           history=history_data)


# -------------------
# Search Disease
# -------------------

@app.route('/search',methods=['GET','POST'])
def search():

    if 'user' not in session:
        return redirect("/")

    result=None

    if request.method=="POST":

        keyword=request.form['keyword']

        for d in diseases:

            if keyword.lower() in d.lower():

                result=(d,diseases[d])
                break

    return render_template("search.html",
                           result=result)


# -------------------
# Home Page
# -------------------

@app.route('/home')
def home():

    if 'user' not in session:
        return redirect("/")

    return render_template("index.html")


# -------------------
# Admin Panel
# -------------------

@app.route('/admin',methods=['GET','POST'])
def admin():

    if 'user' not in session:
        return redirect("/")

    if request.method=="POST":

        disease=request.form['disease']
        symptoms=request.form['symptoms']

        sym_list=symptoms.split(",")

        diseases[disease]={

        "Symptoms":sym_list,
        "Description":"New disease",
        "Treatment":"Consult doctor"

        }

        return redirect("/home")

    return render_template("admin.html")


# -------------------
# Doctor Recommendation
# -------------------

def recommend_doctor(symptom_list,severity):

    text=" ".join(symptom_list).lower()

    if "fever" in text or "cold" in text:
        doctor="General Physician"

    elif "heart" in text or "chest" in text:
        doctor="Cardiologist"

    elif "skin" in text or "rash" in text:
        doctor="Dermatologist"

    elif "stomach" in text:
        doctor="Gastroenterologist"

    elif "headache" in text:
        doctor="Neurologist"

    else:
        doctor="General Physician"

    if "Severe" in severity:
        doctor="Emergency Specialist"

    return doctor

import math

# -------------------
# Activation Functions
# -------------------

def relu(x):
    return max(0, x)

def sigmoid(x):
    return 1 / (1 + math.exp(-x))


# -------------------
# ANN MODEL (with Activation)
# -------------------
def ann_predict(selected):

    # Load symptom names from dataset
    all_symptoms = list(pd.read_csv("cleaned_dataset.csv").columns[:-1])

    # Convert input to binary
    input_data = [1 if s in selected else 0 for s in all_symptoms]
    input_array = np.array([input_data])

    # Predict probabilities
    prediction = model.predict_proba(input_array)

    index = np.argmax(prediction)
    disease = encoder.inverse_transform([index])[0]
    confidence = round(np.max(prediction) * 100, 2)

    return disease, confidence

@app.route('/diagnose', methods=['POST'])
def diagnose():

    if 'user' not in session:
        return redirect("/")

    selected = request.form.getlist('symptom')

    results = []

    # Default values (IMPORTANT)
    best = "No Disease Found"

    suggestion = {
        "Description": "No disease detected",
        "Treatment": "Stay healthy"
    }

    doctor = "General Physician"


    # Smart Diagnosis
    for disease in diseases:

        symptoms = diseases[disease]["Symptoms"]

        match = len(set(selected) & set(symptoms))

        if match > 0:

            percent = (match / len(symptoms)) * 100


            # Severity
            if percent > 70:
                severity = "High"
            elif percent > 40:
                severity = "Medium"
            else:
                severity = "Low"


            # Advice
            if severity == "High":
                advice = "Visit doctor immediately"
            elif severity == "Medium":
                advice = "Take rest and monitor symptoms"
            else:
                advice = "Normal care is enough"


            # Doctor Recommendation
            doctor_type = recommend_doctor(selected,severity)


            results.append(
                (disease,
                 round(percent,2),
                 severity,
                 advice,
                 doctor_type)
            )


    # Sort Results
    results.sort(key=lambda x:x[1],reverse=True)


    # Best Disease (AI Suggestion)
    if results:

        best = results[0][0]

        suggestion = diseases[best]

        doctor = results[0][4]


    # Save History
    file=open("history.txt","a")
    file.write(session['user']+","+str(selected)+"\n")
    file.close()

    ann_disease, ann_confidence = ann_predict(selected)

    return render_template(
"result.html",

symptoms=selected,
results=results,
best=best,
suggestion=suggestion,
ann_disease=ann_disease,
ann_confidence=ann_confidence
)




# -------------------
# History
# -------------------

@app.route('/history')
def history():

    if 'user' not in session:
        return redirect("/")

    try:

        file=open("history.txt","r")
        data=file.readlines()
        file.close()

    except:

        data=[]

    return render_template("history.html",
                           data=data)


# -------------------
# Delete History
# -------------------

@app.route('/delete_history')
def delete_history():

    if 'user' not in session:
        return redirect("/")

    file=open("history.txt","w")
    file.close()

    return redirect("/history")


# -------------------
# Disease Details
# -------------------

@app.route('/disease/<name>')
def disease_details(name):

    if 'user' not in session:
        return redirect("/")

    info=diseases[name]

    return render_template("disease.html",
                           name=name,
                           info=info)

# -------------------
# Semantic Network
# -------------------



@app.route('/network')
@app.route('/network/<category>')
def network(category="All"):
    if 'user' not in session:
        return redirect("/")

    # Clean category name to prevent errors
    valid_categories = ["All", "Respiratory", "Digestive", "Skin", "Infectious", "Chronic"]
    if category not in valid_categories:
        category = "All"

    show_network(category)

    return render_template("network.html",
                           current=category,
                           menu=valid_categories,
                           now=time.time())
# -------------------
# Dashboard
# -------------------

@app.route('/dashboard')
def dashboard():

    if 'user' not in session:
        return redirect("/")

    try:

        file=open("users.txt","r")
        users=file.readlines()
        file.close()

        total_users=len(users)

    except:

        total_users=0


    total_diseases=len(diseases)


    try:

        file=open("history.txt","r")
        history=file.readlines()
        file.close()

        total_history=len(history)

    except:

        total_history=0


    return render_template("dashboard.html",
                           users=total_users,
                           diseases=total_diseases,
                           history=total_history)

# -------------------
# About Page
# -------------------

@app.route('/about')
def about():

    if 'user' not in session:
        return redirect("/")

    return render_template("about.html")


# -------------------
# Download PDF Report
# -------------------

@app.route('/download_report')
def download_report():

    if 'user' not in session:
        return redirect("/")

    from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
    from reportlab.lib.styles import getSampleStyleSheet

    file_path = "report.pdf"

    doc = SimpleDocTemplate(file_path)
    styles = getSampleStyleSheet()

    content = []

    content.append(Paragraph("AI Medical Diagnosis Report", styles['Title']))
    content.append(Spacer(1, 20))

    content.append(Paragraph("User: " + session['user'], styles['Normal']))
    content.append(Spacer(1, 10))

    try:
        file = open("history.txt","r")
        lines = file.readlines()
        file.close()

        if lines:
            last = lines[-1]
            content.append(Paragraph("Symptoms: " + last, styles['Normal']))

    except:
        content.append(Paragraph("No history found", styles['Normal']))

    content.append(Spacer(1, 20))
    content.append(Paragraph("Generated by AI Medical System", styles['Normal']))

    doc.build(content)

    return send_file(file_path, as_attachment=True)
# -------------------
# Logout
# -------------------

@app.route('/logout')
def logout():

    session.clear()

    return redirect("/")

#port = int(os.environ.get("PORT", 10000))
#app.run(host="0.0.0.0", port=10000)