from flask import Flask,render_template,request,jsonify
import requests
from bs4 import BeautifulSoup
import string
import json
import re
import networkx as nx
import plotly.graph_objs as go
import plotly.graph_objs as go
from pyvis.network import Network
import json
import pandas as pd
import plotly.graph_objs as go
from plotly.utils import PlotlyJSONEncoder
import plotly.express as px
import numpy as np
from soup import get_graph
from pyvis.network import Network
import plotly

app = Flask(__name__)
app.debug = True


# Part 1 Scraping, caching and reading cheese data

# S0 formatting functions
def turn_str_to_list(str):
    return re.split(', | and ', str)

# S1-1 functions to scrape cheese.com and get all urls for cheeses- get urls.json
def get_total_pages(letter):
    '''
    Doc string
    '''
    url = f'https://cheese.com/alphabetical/?per_page=100&i={letter}&page=1#top'
    response = requests.get(url)
    html_text = response.text
    soup = BeautifulSoup(html_text, 'html.parser')
    ul_tag = soup.find('ul', id='id_page')

    if ul_tag:
        li_tags = ul_tag.find_all('li')
        li_sum = len(li_tags)
        return li_sum
    else:
        return 1

def get_name_and_link(letter, page_sum, dictionary):
    '''
    Doc string
    '''
    for i in range(1, page_sum + 1):
        url = f'https://cheese.com/alphabetical/?per_page=100&i={letter}&page={i}#top'
        response = requests.get(url)
        html_text = response.text
        soup = BeautifulSoup(html_text, 'html.parser')
        div_tags = soup.find_all('div', class_='col-sm-6 col-md-4 cheese-item text-center')
        for div_tag in div_tags:
            a_tag = div_tag.find('h3').find('a')
            href = a_tag['href']
            text = a_tag.text.strip()
            dictionary[text] = href[1:-1]

def fetch_and_write_urls(dictionary):
    '''
    Doc string
    '''
    letters = list(string.ascii_lowercase)
    for letter in letters:
        sum = get_total_pages(letter)
        get_name_and_link(letter, sum, dictionary)

    with open('urls.json', 'w', encoding='utf-8') as f:
        json.dump(dictionary, f, indent=4, separators=(',', ': '), ensure_ascii=False)


# S1-2 functions to scrape and cache 1800+ cheese records from cheese.com - get cheese_cache.json
def fetch_and_write_cheese_data():
    '''
    Doc string
    '''
    cheese_data = []
    with open('urls.json', 'r') as f:
        urls = json.load(f)

    base_url = 'https://cheese.com/'
    # add try for this
    for value in urls.values():
        url = base_url + value
        info = {}
        response = requests.get(url)
        html_text = response.text
        soup = BeautifulSoup(html_text, 'html.parser')
        div_tag = soup.find('div', class_='unit')
        name_tag = div_tag.find('h1')
        info['name'] = name_tag.get_text().strip()
        info['url'] = url

        ul_tag = soup.find('ul', class_='summary-points')
        li_tags = ul_tag.find_all('li')
        milk_tag = li_tags[0].find('p')
        milk = milk_tag.get_text()[10:]
        info['milk'] = milk

        for li in li_tags[1:]:
            p_tag = li.find('p')
            p_content = p_tag.get_text()
            key, val = p_content.split(":", 1)
            val = val.strip()
            if key == 'Flavour':
                info['flavor'] = val
            elif key == 'Colour':
                info['color']  =val
            else:
                info[key.lower()] = val

        info['decription'] = ""
        div_des_tag = soup.find('div', class_='description')
        p_tag = div_des_tag.find('p')
        inner_p_tags = p_tag.find_all('p')
        for p in inner_p_tags:
            info['decription'] += (p.get_text() + ' ')
        info['decription'] = info['decription'][:-1]  # &bnp and the extra space it create
        cheese_data.append(info)

    with open('data/cheese_cache.json', 'w', encoding='utf-8') as f:
        json.dump(cheese_data, f, indent=4, separators=(',', ': '), ensure_ascii=False)

# S1-3 functions to load urls and cheese_cache
def load_urls():
    try:
        with open('data/urls.json', 'r') as f:
            urls = json.load(f)
    except:
        urls = {}

    if not urls:
        fetch_and_write_urls(urls)
        load_urls()
    else:
        return urls

def load_cheese_cache():
    try:
        with open('data/cheese_cache.json', 'r') as f:
            cheese_data = json.load(f)
    except:
        cheese_data = []

    if not cheese_data:
        fetch_and_write_cheese_data(cheese_data)
        load_cheese_cache()
    else:
        return cheese_data


# Part 2: clean cheese data

# S2-1 Clean cheese_cache data and get filtered_cheese_data
def get_filtered_cheese_cache():
    with open('data/cheese_cache.json', 'r') as f:
        cheese_data = json.load(f)
    required_keys = ['name', 'url', 'decription', 'country of origin', 'region', 'type', 'milk', 'rind', 'texture', 'flavor', 'color', 'aroma']
    valid_cheese_data = [cheese for cheese in cheese_data if all(key in cheese for key in required_keys)]
    filtered_cheese_data = [{key: valid_cheese[key] for key in required_keys} for valid_cheese in valid_cheese_data]

    for data in filtered_cheese_data:
        country = data['country of origin']
        split_country = re.split(', | and ', country)
        type = data['type']
        milk = data['milk']
        texture = data['texture']
        flavor = data['flavor']
        aroma = data['aroma']

        uk = ['England', 'Great Britain', 'United Kingdom', 'Scotland', 'Wales']
        if any(item in split_country for item in uk):
            data['country of origin'] = 'United Kingdom'
        else:
            data['country of origin'] = split_country[0]

        data['type'] = turn_str_to_list(type)
        data['milk'] = turn_str_to_list(milk)
        data['texture'] = turn_str_to_list(texture)
        data['flavor'] = turn_str_to_list(flavor)
        data['aroma'] = turn_str_to_list(aroma)

    with open('data/filtered_cheese_cache.json', 'w', encoding='utf-8') as f:
        json.dump(filtered_cheese_data, f, indent=4, separators=(',', ': '), ensure_ascii=False)



# Part 3 cheese class, vertice class and graph class

# S3-1 cheese class
class Cheese:
    def __init__(self, json):
        self.name = json['name']
        self.url = json['url']
        self.description = json['decription']
        self.country = json['country of origin']
        self.region = json['region']
        self.moisture = json['type']
        self.milk = json['milk']
        self.texture = json['texture']
        self.rind = json['rind']
        self.flavor = json['flavor']
        self.color = json['color']
        self.aroma = json['aroma']

    def __str__(self):
        return f'{self.name} ({self.country}: {self.region})'

# S3-1 vertex class
class Vertex:
    def __init__(self, cheese):
        self.id = cheese.name
        self.name = cheese.name
        self.milk = cheese.milk
        self.texture = cheese.texture
        self.rind = cheese.rind
        self.flavor = cheese.flavor
        self.description = cheese.description
        self.aroma = cheese.aroma
        self.country = cheese.country
        self.region = cheese.region
        self.connectedTo = {}
        self.connection_sum = 0

    def addNeighbor(self, nbrVertex):
        weight = self.calSimilarity(nbrVertex)
        if weight != 0:
            self.connectedTo[nbrVertex.name] = weight

    def getId(self):
        return self.id

    def getWeight(self, nbrVertex):
        try:
            return self.connectedTo[nbrVertex.name]
        except:
            return 0

    def getConnections(self):
        return self.connectedTo.keys()

    def calcConnections(self):
        self.connection_sum = len(self.connectedTo.keys())

    def calSimilarity(self, nbrVertex):
        # Calculate Jaccard similarity between sets of milk, texture, rind, flavor, aroma
        milk_similarity = len(set(self.milk).intersection(set(nbrVertex.milk))) / len(set(self.milk).union(set(nbrVertex.milk)))
        texture_similarity = len(set(self.texture).intersection(set(nbrVertex.texture))) / len(set(self.texture).union(set(nbrVertex.texture)))
        flavor_similarity = len(set(self.flavor).intersection(set(nbrVertex.flavor))) / len(set(self.flavor).union(set(nbrVertex.flavor)))
        aroma_similarity = len(set(self.aroma).intersection(set(nbrVertex.aroma))) / len(set(set(self.aroma).union(set(nbrVertex.aroma))))
        general_similarity = milk_similarity*0 + texture_similarity*0 + flavor_similarity + aroma_similarity
        return round(general_similarity, 2)

# S3-3 graph class
class Graph:
    def __init__(self):
        self.vertList = {}
        self.numVertices = 0
        self.verts = []

    def addVertex(self, vertex):
        self.numVertices = self.numVertices + 1
        self.vertList[vertex.name] = vertex
        self.verts.append(vertex)
        return vertex

    def getVertex(self, name):
        if name in self.vertList:
            return self.vertList[name]
        else:
            return None

    def __contains__(self,name):
        return name in self.vertList

    def addEdge(self, startVertex, endVertex):
        if startVertex not in self.vertList.values():
            nv = self.addVertex(startVertex)
        if endVertex not in self.vertList.values():
            nv = self.addVertex(endVertex)
        self.vertList[startVertex.name].addNeighbor(self.vertList[endVertex.name])
        self.vertList[endVertex.name].addNeighbor(self.vertList[startVertex.name])


    def getVertices(self):
        return self.vertList.keys()

    def getSimilar(self, name, num=3):
        cur_vertex = self.getVertex(name)
        connections = cur_vertex.connectedTo
        similar_pairs = sorted(connections.items(), key=lambda item: item[1], reverse=True)
        similar_cheeses = [tuple[0] for tuple in similar_pairs]
        res = []
        for cheese in similar_cheeses:
          new_vertex = self.getVertex(cheese)
          res.append(new_vertex)
          print(type(new_vertex))
        return res[:num]
    
    def getDifferent(self, name, num=3):
        cur_vertex = self.getVertex(name)
        connections = cur_vertex.connectedTo
        vertex_connections = []
        for connection in connections:
            vertex = self.getVertex(connection)
            vertex_connections.append(vertex)
        different_pairs = sorted(connections.items(), key=lambda item: item[1])
        different_cheeses = [tuple[0] for tuple in different_pairs]
        res = []
        for cheese in different_cheeses:
          new_vertex = self.getVertex(cheese)
          res.append(new_vertex)
          print(type(new_vertex))
        return res[:num]

    def getMostCommon(self, num=3):
        connection_sum = []
        for vertex in self.vertList.values():
            connection_sum.append((vertex.name, vertex, len(vertex.connectedTo.keys())))
        most_common_pairs = sorted(connection_sum, key=lambda x: x[2], reverse=True)
        most_common = [tuple[1] for tuple in most_common_pairs]
        return most_common[:num]

    def getMostUnique(self, num=3):
        connection_sum = []
        for vertex in self.vertList.values():
            connection_sum.append((vertex.name, vertex, len(vertex.connectedTo.keys())))
        most_unique_pairs = sorted(connection_sum, key=lambda x: x[2])
        most_unique = [tuple[1] for tuple in most_unique_pairs]
        return most_unique[:num]
    
    def __iter__(self):
        return iter(self.vertList.values())


# 3-4 Populate graph
def get_graph():
    with open('data/filtered_cheese_cache.json', 'r') as f:
        filtered_cheese_data = json.load(f)

    cheeses = [Cheese(cheese) for cheese in filtered_cheese_data]
    graph = Graph()
    for cheese in cheeses:
        graph.addVertex(Vertex(cheese))

    vertex_sum = graph.numVertices
    verts = graph.verts
    for i in range(vertex_sum):
        for j in range(i+1, vertex_sum):
            graph.addEdge(verts[i], verts[j])
    return graph



# Part4: Data analysis and visualization

# S4-0 Get most common/unique cheeses among all cheeses and get most similar/different cheeses to a given cheese
def get_most_common_cheeses():
    g = get_graph()
    res  = g.getMostCommon()
    return res

def get_most_unique_cheeses():
    g = get_graph()
    res  = g.getMostUnique()
    return res

def get_most_similar_cheeses(cheese_name):
    g = get_graph()
    res  = g.getSimilar(cheese_name)
    return res

def get_most_similar_cheeses(cheese_name):
    g = get_graph()
    res  = g.getDifferent(cheese_name)
    return res


# S4-1 similarity network @https://towardsdatascience.com/pyvis-visualize-interactive-network-graphs-in-python-77e059791f01
def get_similarity_network():
    net = Network(height="950px", width="100%", bgcolor="white", font_color="black")
    net.repulsion()

    with open('data/filtered_cheese_cache.json', 'r') as f:
            filtered_cheese_data = json.load(f)

    cheeses = [Cheese(cheese) for cheese in filtered_cheese_data]
    vertices = [Vertex(cheese) for cheese in cheeses if cheese.country == 'United States'][:200]
    for i in range(len(vertices)):
        for j in range(i+1, len(vertices)):
            src=vertices[i].name
            dst=vertices[j].name
            w=vertices[i].calSimilarity(vertices[j])
            net.add_node(src, src, title=src)
            net.add_node(dst, dst, title=dst)
            # net.add_edge(src, dst, value=w)
            if w > 1.2:
                net.add_edge(src, dst, value=5, color="#3D8361")
            elif 0.8 < w < 1.2:
                net.add_edge(src, dst, value=3, color="#DAE2B6")
            elif 0.4 < w < 0.8:
                net.add_edge(src, dst, value=1, color="#DAE2B6")
    neighbor_map = net.get_adj_list()

    for node in net.nodes:
        if node["id"] in neighbor_map and len(neighbor_map[node["id"]]) > 50:
            node["size"] = 40
            node["color"] = "#3D8361"
        elif node["id"] in neighbor_map and len(neighbor_map[node["id"]]) > 30:
            node["size"] = 25
            node["color"] = "#90B77D"
        else:
            node["size"] = 5
            node["color"] = "#CFE8A9"
    # net.show_buttons()
    # net.show('similarity_network.html')
    net.save_graph("templates/network.html")

#S4-2-1 Cheese origins by country - map
def get_cheese_origin_by_country_map():
    with open('data/filtered_cheese_cache.json', 'r') as f:
        filtered_cheese_data = json.load(f)

    cheese_list = [Cheese(cheese) for cheese in filtered_cheese_data]
    cheese_data = pd.DataFrame([vars(cheese) for cheese in cheese_list])
    cheese_data = cheese_data.groupby('country').agg({'name': 'count'}).reset_index()
    cheese_data.columns = ['Country', 'Number of Cheeses Originated']

    fig = px.choropleth(
        cheese_data,
        locations='Country',
        locationmode='country names',
        color='Number of Cheeses Originated',
        hover_name='Country',
        color_continuous_scale=px.colors.sequential.YlOrRd,
        # px.colors.sequential.Blues,
        color_continuous_midpoint=100,
        width=1000,
        height=800
    )

    fig.update_layout(
        template='plotly_white',
        geo=dict(
            showframe=True,
            showcoastlines=True,
            projection_type='equirectangular'
        )
    )
    return fig
    # fig.show()


#S4-2-2 Cheese origins by country - bar chart
def get_cheese_origin_by_country_barchart():
    with open('data/filtered_cheese_cache.json', 'r') as f:
        filtered_cheese_data = json.load(f)

    cheese_list = [Cheese(cheese) for cheese in filtered_cheese_data]
    cheese_data = pd.DataFrame([vars(cheese) for cheese in cheese_list])
    cheese_data_group = cheese_data.groupby('country').agg({'name': 'count'}).reset_index()
    cheese_data_group.columns = ['Country', 'Number of Cheeses Originated here']
    cheese_data_sort = cheese_data_group.sort_values('Number of Cheeses Originated here', ascending=False)

    trace = go.Bar(x=cheese_data_sort['Country'], y=cheese_data_sort['Number of Cheeses Originated here'])

    layout = go.Layout(title='',
                    xaxis=dict(title='Country'),
                    yaxis=dict(title='Number of Cheeses Originated here'))

    fig = go.Figure(data=[trace], layout=layout)
    # fig.show()
    return fig


#S4-3-1 US Cheese origins by state - barcahrt
def get_cheese_origin_by_state_barchart():
    with open('data/filtered_cheese_cache.json', 'r') as f:
        filtered_cheese_data = json.load(f)

    cheese_list = [Cheese(cheese) for cheese in filtered_cheese_data]
    us_cheese_list = [cheese for cheese in cheese_list if cheese.country == 'United States' and cheese.region != 'Unity']

    with open("data/us_state_name_dict.json", "r") as f:
        us_state_name_dict = json.load(f)

    for cheese in us_cheese_list:
        cheese.region = us_state_name_dict[cheese.region]

    cheese_data = pd.DataFrame([vars(cheese) for cheese in us_cheese_list])
    cheese_data_group = cheese_data.groupby('region').agg({'name': 'count'}).reset_index()
    cheese_data_group.columns = ['State', 'Number of Cheeses Originated']
    cheese_data_sort = cheese_data_group.sort_values('Number of Cheeses Originated', ascending=False)    
    trace = go.Bar(x=cheese_data_sort['State'], y=cheese_data_sort['Number of Cheeses Originated'], marker=dict(color='#655DBB'))
    layout = go.Layout(title=' ',
                    xaxis=dict(title='State'),
                    yaxis=dict(title='Number of Cheeses Originated'))

    fig = go.Figure(data=[trace], layout=layout)
    return fig
    # fig.show()


#S4-3-2 US Cheese origins by state - map
def get_cheese_origin_by_state_map():
    with open('data/filtered_cheese_cache.json', 'r') as f:
        filtered_cheese_data = json.load(f)

    cheese_list = [Cheese(cheese) for cheese in filtered_cheese_data]
    us_cheese_list = [cheese for cheese in cheese_list if cheese.country == 'United States' and cheese.region != 'Unity']

    with open("data/us_state_code_dict.json", "r") as f:
        us_state_code_dict = json.load(f)

    for cheese in us_cheese_list:
        cheese.state_code = us_state_code_dict[cheese.region]

    cheese_data = pd.DataFrame([vars(cheese) for cheese in us_cheese_list])
    cheese_data_group = cheese_data.groupby('state_code').agg({'name': 'count'}).reset_index()
    cheese_data_group.columns = ['State', 'Count']

    fig = px.choropleth(locations=cheese_data_group['State'],
                        locationmode="USA-states",
                        color=cheese_data_group['Count'],
                        scope="usa",
                        color_continuous_scale='Bluyl',
                        width=1200,
                        height=700,
                        title='')
    # fig.show()
    return fig


# S4-4 US Cheese rind by pirchart
def get_us_cheese_rind_piechart():
    with open('data/filtered_cheese_cache.json', 'r') as f:
        filtered_cheese_data = json.load(f)

    cheese_list = [Cheese(cheese) for cheese in filtered_cheese_data]
    cheese_dict = {"country": [], "cheese_rind": []}
    for cheese in cheese_list:
        cheese_dict["country"].append(cheese.country)
        cheese_dict["cheese_rind"].append(cheese.rind)

    data = pd.DataFrame(cheese_dict)
    us_cheeses = data[data["country"] == "United States"]
    rind_counts = us_cheeses["cheese_rind"].value_counts()

    # fig = px.pie(values=rind_counts.values, names=rind_counts.index, title="Cheese Rind Distribution in the US")
    # fig.show()
    fig = px.pie(values=rind_counts.values, names=rind_counts.index, title=" ", width=1200, height=700)
    return fig


@app.route('/')
def home():
    return render_template('index.html')

@app.route('/network')
def network():
    get_similarity_network()
    return render_template('network.html')


@app.route('/network_image')
def network_image():
    return render_template('network_image.html')

@app.route('/common_and_unique_cheese', methods=['GET', 'POST'])
def common_and_unique_cheese():
    if request.method == 'POST':
        g = get_graph()
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
# @app.route('/common_and_unique_cheese', methods=['GET', 'POST'])
# def common_and_unique_cheese():
#     if request.method == 'POST':
#         g = get_graph()
#         button_value = request.form['button']
#         if button_value == 'most_common':
#             result = g.getMostCommon()
#             message = "🏆 Top three most common cheeses:"
#         elif button_value == 'most_unique':
#             result = g.getMostUnique()
#             message = "🥇 Top three most unique cheeses:"
#         else:
#             result = []
#             message = ""
#         return render_template('common_and_unique_cheese.html', result=result, message=message)
#     else:
#         return render_template('common_and_unique_cheese.html', message="")

@app.route("/similar_and_different_cheese", methods=["GET", "POST"])
def similar_and_different_cheese():
    if request.method == "POST":
        g = get_graph()
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
    fig = get_cheese_origin_by_country_map()
    fig_json = fig.to_json()
    return render_template('cheese_origin_by_country_map.html', fig_json=fig_json)

@app.route('/cheese_origin_by_country_barchart')
def cheese_origin_by_country_barchart():
    fig = get_cheese_origin_by_country_barchart()
    plot_div = fig.to_html(full_html=False)
    return render_template('cheese_origin_by_country_barchart.html', plot_div=plot_div)

@app.route("/cheese_origin_by_state_map")
def cheese_origin_by_state_map():
    fig = get_cheese_origin_by_state_map()
    fig_json = fig.to_json()
    return render_template('cheese_origin_by_state_map.html', fig_json=fig_json)

@app.route('/cheese_origin_by_state_barchart')
def cheese_origin_by_state_barchart():
    fig = get_cheese_origin_by_state_barchart()
    plot_div = fig.to_html(full_html=False)
    return render_template('cheese_origin_by_state_barchart.html', plot_div=plot_div)


@app.route('/us_cheese_rind_piechart')
def us_cheese_rind_piechart():
    fig = get_us_cheese_rind_piechart()
    plot_div = fig.to_html(full_html=False)
    return render_template('us_cheese_rind_piechart.html', plot_div=plot_div)


if __name__ == '__main__':
    app.run()
