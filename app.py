from flask import Flask, render_template, jsonify, request, Response
import pandas as pd
import pickle
from datetime import datetime
from sqlalchemy import create_engine, text
import matplotlib.pyplot as plt 
from matplotlib.backends.backend_agg import FigureCanvasAgg as FigureCanvas
from matplotlib.figure import Figure
import io


app = Flask(__name__)

messages = [{'title': 'Bienvenidos a mi predicción de Propinas',
             'content': 'Vamos a ver como predicir las propinas'}]


@app.route('/')
def index():
    return render_template('index.html', messages=messages)


@app.route('/create/', methods=('GET', 'POST'))
def create():
    return render_template('create.html')




@app.route('/procesar_formulario', methods=['POST'])
def procesar_formulario():
    if request.method == 'POST':
        total = float(request.form['numero_decimal'])
        sex = int(request.form['genero'])
        smoker = int(request.form['fumador'])
        day = int(request.form['dia'])
        food = int(request.form['comida'])
        size = int(request.form['numero_entero'])
    x = [[total, sex, smoker, day, food, size]]
    X = total, sex, smoker, day, food, size

    predi = modelo_cargado.predict(x)


    df = pd.DataFrame({
    'Predi': [str(predi[0])],
    'input':[str(X)],
    'fecha' : [datetime.now()]
    }
    )
    df.to_sql('logs', con=engine, if_exists='append')

    message_predi = [{
    'title':f'Te dejaran una Propina aproximada de {round(float(predi), 2)}€'
    }]

    return render_template('index_predi.html', messages=message_predi)



@app.route('/importance', methods=['GET'])
def importance():
    datos_graph = pd.DataFrame(modelo_cargado.feature_importances_, columns=["importance"], index=["Total comida", "Genero", "Fumador", "Dia", "Comida", "Comensales"]).sort_values("importance", ascending=False)
    
    fig = Figure()
    axis = fig.add_subplot(1, 1, 1)
    axis.bar([x for x in datos_graph.index], [x[0] for x in datos_graph.values])
    output = io.BytesIO()
    FigureCanvas(fig).print_png(output)


    return Response(output.getvalue(), mimetype='image/png')



@app.route('/create_log', methods=('GET', 'POST'))
def create_log():
    return render_template('create_log.html')


@app.route('/procesar_log', methods=['POST'])
def pros_logs():
    start = request.form['fechaHora_start']
    end = request.form['fechaHora_end']
    query = f"""
        SELECT * FROM logs
        WHERE fecha < '{end}'
        AND fecha > '{start}';
    """

    dfs = pd.DataFrame(pd.read_sql(query, con=engine))
    tabla_html = dfs.to_html(index=False)


    return render_template('tabla_log.html', tabla_html=tabla_html)







if __name__ == "__main__":

    engine = create_engine("postgresql://fl0user:UtmRka5rZVI1@ep-holy-queen-16258744.eu-central-1.aws.neon.fl0.io:5432/database?sslmode=require")

    with open('modelo_propinas.pkl', 'rb') as archivo:
    modelo_cargado = pickle.load(archivo)
    
    app.run(debug=True, port=8080)
