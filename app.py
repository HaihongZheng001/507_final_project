from flask import Flask,render_template,request
import networkx as nx
import plotly.graph_objs as go
import plotly.graph_objs as go
from pyvis.network import Network
import json
import pandas as pd
import plotly.graph_objs as go
import plotly.express as px
import numpy as np
from pyvis.network import Network
import plotly
import helpers

app = Flask(__name__)
app.debug = True



@app.route('/')
def home():
    return render_template('index.html')

@app.route('/network')
def network():
    helpers.get_similarity_network()
    return render_template('network.html')


@app.route('/network_image')
def network_image():
    return render_template('network_image.html')

@app.route('/common_and_unique_cheese', methods=['GET', 'POST'])
def common_and_unique_cheese():
    if request.method == 'POST':
        g = helpers.get_graph()
        button_value = request.form['button']
        if button_value == 'most_common':
            result = 'Most common'
            cheeses = g.getMostCommon()
        elif button_value == 'most_unique':
            result = 'Most unique'
            cheeses = g.getMostUnique()
        return render_template('common_and_unique_cheese.html', result=result, cheeses=cheeses)
    else:
        return render_template('common_and_unique_cheese.html')


@app.route("/similar_and_different_cheese", methods=["GET", "POST"])
def similar_and_different_cheese():
    if request.method == "POST":
        g = helpers.get_graph()
        cheese_name = request.form["cheese_name"]
        button = request.form["button"]
        if button == "get_similar":
            result = g.getSimilar(cheese_name)
        elif button == "get_different":
            result = g.getDifferent(cheese_name)
        else:
            result = []
    else:
        result = []

    return render_template("similar_and_different_cheese.html", result=result)


@app.route('/cheese_origin_by_country_map')
def cheese_origin_by_country_map():
    fig = helpers.get_cheese_origin_by_country_map()
    fig_json = fig.to_json()
    return render_template('cheese_origin_by_country_map.html', fig_json=fig_json)

@app.route('/cheese_origin_by_country_barchart')
def cheese_origin_by_country_barchart():
    fig = helpers.get_cheese_origin_by_country_barchart()
    plot_div = fig.to_html(full_html=False)
    return render_template('cheese_origin_by_country_barchart.html', plot_div=plot_div)

@app.route("/cheese_origin_by_state_map")
def cheese_origin_by_state_map():
    fig = helpers.get_cheese_origin_by_state_map()
    fig_json = fig.to_json()
    return render_template('cheese_origin_by_state_map.html', fig_json=fig_json)

@app.route('/cheese_origin_by_state_barchart')
def cheese_origin_by_state_barchart():
    fig = helpers.get_cheese_origin_by_state_barchart()
    plot_div = fig.to_html(full_html=False)
    return render_template('cheese_origin_by_state_barchart.html', plot_div=plot_div)


@app.route('/us_cheese_rind_piechart')
def us_cheese_rind_piechart():
    fig = helpers.get_us_cheese_rind_piechart()
    plot_div = fig.to_html(full_html=False)
    return render_template('us_cheese_rind_piechart.html', plot_div=plot_div)


if __name__ == '__main__':
    app.run()
