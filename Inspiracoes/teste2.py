import cv2 as cv
import numpy as np
from flask import Flask, render_template
from flask_sock import Sock

# Inicialize a aplicação Flask
app = Flask(__name__)
sock = Sock(app)

# Carregue o classificador de detecção de rosto do OpenCV
face_cascade = cv.CascadeClassifier(cv.data.haarcascades + 'haarcascade_frontalface_default.xml')

# Rota para renderizar o template HTML
@app.route("/")
def index():
    return render_template('example.html')

# Rota do socket para receber e processar a imagem
@sock.route('/socket')
def echo(socket):
    while True:
        input_data = socket.receive()
        # Transforme os dados em um vetor numpy
        input_array = np.frombuffer(input_data, np.uint8)
        # Decodifique a imagem
        input_image = cv.imdecode(input_array, cv.IMREAD_COLOR)
        # Realize a detecção de rostos na imagem
        output_image = detect_faces(input_image)
        # Codifique a imagem de saída em um formato compatível com envio pelo socket
        _, output_array = cv.imencode('.png', output_image)
        output_data = output_array.tobytes()
        socket.send(output_data)

def detect_faces(input_image):
    # Converta a imagem para escala de cinza
    gray = cv.cvtColor(input_image, cv.COLOR_BGR2GRAY)
    # Realize a detecção de rostos
    faces = face_cascade.detectMultiScale(gray, scaleFactor=1.1, minNeighbors=5, minSize=(30, 30))
    
    # Desenhe retângulos ao redor dos rostos detectados
    for (x, y, w, h) in faces:
        cv.rectangle(input_image, (x, y), (x + w, y + h), (0, 255, 0), 2)

    return input_image

if __name__ == "__main__":
    app.run()
