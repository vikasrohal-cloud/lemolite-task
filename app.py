from flask import Flask,render_template,redirect,url_for
import pymongo


app = Flask(__name__)
app.secret_key = "testing"
client = pymongo.MongoClient("mongodb://localhost:27017/total_record")

@app.route("/", methods=['POST', 'GET'])
def index():
    return render_template("index.html")

if __name__ == "__main__":
    app.run(debug=True)