# app.py
from flask import Flask, request, jsonify, render_template

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/save_coordinates', methods=['POST'])
def save_coordinates():
    x = request.form.get('x')
    y = request.form.get('y')
    
    # Здесь вы можете обработать или сохранить координаты, как вам нужно
    print(f"X: {x}, Y: {y}")
    
    return jsonify(status="success")

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5555)
