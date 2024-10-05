from flask import Flask, render_template
app = Flask(__name__)

@app.route("/")
def main():
    return "Welcome!"

if __name__ == "__main__":
    app.run()

def main():
    return render_template('main_panel.html')