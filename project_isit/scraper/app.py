from flask import Flask, request, jsonify, render_template
from image_scraper import parse

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/parser', methods=['GET'])
def scrape():
    url = request.args.get('url')
    if not url:
        return jsonify({'error': 'Не задан URL'}), 400

    parse(url)
    
    return jsonify({'message': 'Скрапинг запущен'})



if __name__ == '__main__':
    app.run(debug=True)
