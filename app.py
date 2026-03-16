import os
from flask import Flask,request,jsonify,render_template
from openai import OpenAI
from dotenv import load_dotenv

from database import init_db,save,history
from tools_google import google_search
from tools_pdf import read_pdf
from tools_image import create_image

load_dotenv()

app=Flask(__name__)

client=OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

init_db()


@app.route("/")
def home():
    return render_template("index.html")


@app.route("/chat",methods=["POST"])
def chat():

    msg=request.json["message"]

    save("user",msg)

    # imagem
    if msg.startswith("imagem:"):

        prompt=msg.replace("imagem:","")

        url=create_image(prompt)

        reply=f"<img src='{url}' width='300'>"

        save("assistant",reply)

        return jsonify({"response":reply})


    # google
    if msg.startswith("google:"):

        q=msg.replace("google:","")

        res=google_search(q)

        msg=f"Resultados da web:\n{res}"


    hist=history()

    response=client.responses.create(
        model="gpt-4.1-mini",
        input=hist+[{"role":"user","content":msg}]
    )

    reply=response.output_text

    save("assistant",reply)

    return jsonify({"response":reply})


@app.route("/upload",methods=["POST"])
def upload():

    file=request.files["file"]

    text=read_pdf(file)

    return jsonify({"text":text})


if __name__=="__main__":
    app.run(host="0.0.0.0",port=5000)