from flask import Flask, request, jsonify
from flask_cors import CORS
import mysql.connector
from werkzeug.utils import secure_filename
import os

app = Flask(__name__)
CORS(app)

class Catalogo:
    def __init__(self, host, user, password, database):
        self.conn = mysql.connector.connect(
            host=host,
            user=user,
            password=password,
            database=database
        )
        self.cursor = self.conn.cursor()

    def agregar_juego(self, titulo, descripcion, precio, imagen):
        sql = "INSERT INTO `juegos` (`titulo`, `descripcion`, `precio`, `imagen_url`) VALUES (%s, %s, %s, %s);"
        valores = (titulo, descripcion, precio, imagen)

        self.cursor.execute(sql, valores)
        self.conn.commit()
        return True

    def eliminar_juego(self, id):
        sql = f"DELETE FROM `juegos` WHERE (`idjuegos` = {id});"
        self.cursor.execute(sql)
        self.conn.commit()
        return True

    def traer_juego_por_id(self, id):
        sql = f"SELECT * FROM `juegos` WHERE (`idjuegos` = {id});"
        self.cursor.execute(sql)
        juego = self.cursor.fetchone()
        return juego

    def modificar_juego(self, id, titulo, descripcion, precio):
        sql = "UPDATE `juegos` SET `titulo` = %s, `descripcion` = %s, `precio` = %s WHERE (`idjuegos` = %s);"
        valores = (titulo, descripcion, precio, id)

        self.cursor.execute(sql, valores)
        self.conn.commit()
        return True

    def traer_juegos(self):
        sql = "SELECT * FROM `juegos`;"
        self.cursor.execute(sql)
        juegos = self.cursor.fetchall()
        return juegos

# Crear un objeto de la clase Catalogo con la configuración de tu base de datos
catalogo = Catalogo(host='localhost', user='root', password='Camidami2023', database='gaming')

RUTA_DESTINO = "./static/assets/"

@app.route("/juegos", methods=["POST"])
def agregar_juego():
    titulo = request.form['titulo']
    descripcion = request.form['descripcion']
    precio = request.form['precio']
    imagen = request.files['imagen']

    nombre_imagen = secure_filename(imagen.filename)
    nombre_base, extension = os.path.splitext(nombre_imagen)
    imagen_url = f"{nombre_base}{extension}"

    if catalogo.agregar_juego(titulo, descripcion, precio, imagen_url):
        imagen.save(os.path.join(RUTA_DESTINO, imagen_url))
        return jsonify({"mensaje": "juego agregado"}), 200
    else:
        return jsonify({"mensaje": "Error"}), 400

@app.route("/juegos", methods=["GET"])
def traer_juegos():
    juegos = catalogo.traer_juegos()

    juegos_json = []

    for juego in juegos:
        juego_json = {
            "id": juego[0],
            "imagen_url": juego[1],
            "titulo": juego[2],
            "descripcion": juego[3],
            "precio": juego[4],
            
        }
        juegos_json.append(juego_json)

    return jsonify(juegos_json), 200

@app.route("/juegos/<int:id>", methods=["DELETE"])
def eliminar_juego(id):
    if catalogo.eliminar_juego(id):
        return jsonify({"mensaje": "juego eliminado"}), 200
    else:
        return jsonify({"mensaje": "Error"}), 400

@app.route("/juegos/<int:id>", methods=["GET"])
def traer_juego_por_id(id):
    juego = catalogo.traer_juego_por_id(id)
    if juego:
        juego_json = {
            "id": juego[0],
            "titulo": juego[1],
            "descripcion": juego[2],
            "precio": juego[3],
            "imagen_url": juego[4]
        }
        return jsonify(juego_json), 200
    else:
        return jsonify({"mensaje": "Juego no encontrado"}), 400

@app.route("/juegos/<int:id>", methods=["PUT"])
def modificar_juego(id):
    titulo = request.form['titulo']
    descripcion = request.form['descripcion']
    precio = request.form['precio']

    if catalogo.modificar_juego(id, titulo, descripcion, precio):
        return jsonify({"mensaje": "juego modificado"}), 200
    else:
        return jsonify({"mensaje": "Error"}), 400

if __name__ == '__main__':
    app.run(port=5000, debug=True)