import os
import pandas as pd

from flask import Flask, render_template, redirect, url_for


dummy_data = {
    'name': ['John', 'Jane', 'Doe'],
    'age': [25, 30, 35],
}

dummy_data = pd.DataFrame(dummy_data)


def main():
    app = Flask(__name__)

    # default route
    @app.route('/')
    def index():
        return render_template('index.html')
    
    @app.route('/showcase')
    def showcase():
        return render_template('showcase.html', data=dummy_data.to_html())
    
    @app.errorhandler(404)
    def not_found(e):
        return render_template('404.html'), 404
    


    
    # run the app
    app.run(host='localhost', port=5000, debug=True)
    

if __name__ == '__main__':
    main()