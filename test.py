'''
After creating virtualenv
    cd virtualenvs
    virtualenv test
    source test/bin/activate
Install...
    pip install Flask
    pip install neo4j-driver
To run ...
    python test.py

'''

from flask import Flask, g, Response, request
from neo4j.v1 import GraphDatabase, basic_auth
from json import dumps

app = Flask(__name__)
app.debug = True

password = "L0wt3ch!"

driver = GraphDatabase.driver('bolt://localhost',auth=basic_auth("neo4j", password))


def get_db ():
    if not hasattr(g, 'neo4j_db'):
        g.neo4j_db = driver.session ()
    return g.neo4j_db

@app.teardown_appcontext
def close_db(error):
    if hasattr(g, 'neo4j_db'):
        g.neo4j_db.close()


@app.route("/")
def get_graph():
    db = get_db()
    results = db.run("MATCH (m:Movie)<-[:ACTED_IN]-(a:Person) "
             "RETURN m.title as movie, collect(a.name) as cast "
             "LIMIT {limit}", {"limit": request.args.get("limit", 100)})
    nodes = []
    rels = []
    i = 0
    for record in results:
        nodes.append({"title": record["movie"], "label": "movie"})
        target = i
        i += 1
        for name in record['cast']:
            actor = {"title": name, "label": "actor"}
            try:
                source = nodes.index(actor)
            except ValueError:
                nodes.append(actor)
                source = i
                i += 1
            rels.append({"source": source, "target": target})
    return Response(dumps({"nodes": nodes, "links": rels}), mimetype="application/json")

'''def hello():
    return "Hello World!"
'''

if (__name__ == "__main__"):
    app.run(port = 5000)
