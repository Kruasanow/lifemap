# app.py
from flask import Flask, request, jsonify, render_template, redirect, url_for, flash, session

app = Flask(__name__)
app.secret_key = 'zalupa227' 

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/createdescription')
def createdescription():
    x = session['X']
    y = session['Y']
    return render_template('createdescription.html', x = x, y = y)

@app.route('/save_coordinates', methods=['POST'])
def save_coordinates():
    x = request.form.get('x')
    y = request.form.get('y')
    
    # Здесь вы можете обработать или сохранить координаты, как вам нужно
    print(f"X: {x}, Y: {y}")
    session['X'] = x
    session['Y'] = y
    return jsonify(status="success")

@app.route('/button_pressed', methods=['POST'])
def button_pressed():
    # Здесь выполняется обработка нажатия кнопки
    flash('Button was pressed!')
    return redirect(url_for('createdescription'))

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5555)
