import cv2 as cv
import numpy as np

# from mtcnn.mtcnn import MTCNN
from flask import Flask, render_template
from flask_sock import Sock

# detector = MTCNN(), criando aplicacao flask específica. 
app = Flask(__name__)
sock = Sock(app)

# Decoradores
@app.route("/")
def index():
    return render_template('example.html')

# Transformacao de dados para o formato certo. Esperando algum dado vir do socket. 
# A partir de bytes, tranforma em um vetor numpy "frombuffer". 
@sock.route('/socket')
def echo(socket):
    while True:
        input_data = socket.receive()
        # passa para vetor numpy (bits to numpy vector)
        input_array = np.frombuffer(input_data, np.uint8)
        # imagem a cores...
        input_image = cv.imdecode(input_array, cv.IMREAD_COLOR)
        output_image = process(input_image)
        _, output_array = cv.imencode('.png', output_image)
        output_data = output_array.tobytes()
        socket.send(output_data)


def process(input_image):
    output_image = cv.Canny(input_image, 100, 200)
    # output_image = input_image.copy()
    # for face in detector.detect_faces(input_image):
    #    x, y, width, height = face['box']
    #    cv.rectangle(output_image, (x, y), (x + width, y + height), (0, 255, 0), 2)
    return output_image
