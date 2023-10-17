import cv2 as cv
import numpy as np
from flask import Flask, render_template
from flask_sock import Sock

# Inicialize a aplicação Flask
app = Flask(__name__)
sock = Sock(app)

# Carregue o modelo YOLO
net = cv.dnn.readNet('yolov3.weights', 'yolov3.cfg')
classes = []

with open('coco.names', 'r') as f:
    classes = f.read().strip().split('\n')

layer_names = net.getLayerNames()
output_layers = [layer_names[i - 1] for i in net.getUnconnectedOutLayers()]
detected_object_coordinates = []

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
        # Realize a detecção de objetos na imagem
        output_image = detect_objects(input_image)
        # Codifique a imagem de saída em um formato compatível com envio pelo socket
        _, output_array = cv.imencode('.png', output_image)
        output_data = output_array.tobytes()
        socket.send(output_data)
        # Envie também as coordenadas para a lista
        send_detected_object_coordinates()

def detect_objects(input_image):
    height, width, channels = input_image.shape

    # Preparando a imagem para ser jogada para o modelo do YOLO
    blob = cv.dnn.blobFromImage(input_image, 0.00392, (416, 416), (0, 0, 0), True, crop=False)
    net.setInput(blob)
    outs = net.forward(output_layers)

    class_ids = []
    confidences = []
    boxes = []

    for out in outs:
        for detection in out:
            scores = detection[5:]
            class_id = np.argmax(scores)
            confidence = scores[class_id]

            if confidence > 0.5:
                # Coordenadas do objeto detectado
                center_x = int(detection[0] * width)
                center_y = int(detection[1] * height)
                w = int(detection[2] * width)
                h = int(detection[3] * height)

                # Pontos de canto do retângulo
                x = int(center_x - w / 2)
                y = int(center_y - h / 2)

                boxes.append([x, y, w, h])
                confidences.append(float(confidence))
                class_ids.append(class_id)

    indexes = cv.dnn.NMSBoxes(boxes, confidences, 0.5, 0.4)

    for i in range(len(boxes)):
        if i in indexes:
            x, y, w, h = boxes[i]
            label = str(classes[class_ids[i]])
            confidence = confidences[i]

            # Desenhe o retângulo e rotulando o objeto detectado
            cv.rectangle(input_image, (x, y), (x + w, y + h), (0, 255, 0), 2)
            cv.putText(input_image, f'{label} {confidence:.2f}', (x, y - 10), cv.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)

            # Armazene as coordenadas do objeto detectado na lista
            detected_object_coordinates.append((x, y, label))

    return input_image


def send_detected_object_coordinates():
    # Envie as coordenadas dos objetos detectados ao cliente ou utilize-as conforme necessário
    for coordinate in detected_object_coordinates:
        x, y, label = coordinate
        print(f'Objeto: {label}, Coordenadas: ({x}, {y})')



if __name__ == "__main__":
    app.run()


