const FPS = 5;

const inputCanvas = document.createElement('canvas'); // Para desenhar objetos
const inputContext = inputCanvas.getContext('2d');  // Dar comandos para desenhar coisas no Canvas

const outputCanvas = document.querySelector('canvas');
const outputContext = outputCanvas.getContext('2d');

const video = document.querySelector('video'); // Tag vídeo

const socket = new WebSocket('ws://localhost:5000/socket'); // Criando a coneccão 

async function getBlob() {
    return new Promise((resolve, reject) => {
        try {
            // Serve para obter Blob (objeto java para bytes puros), que é a imagem que está no canvas
            // mas na forma png. Chama blob e funcione na forma de "promise"
            inputCanvas.toBlob(resolve, 'image/png');
        } catch (error) {
            reject(error);
        }
    });
}

async function main() {
    const stream = await navigator.mediaDevices.getUserMedia({ video: true }); // Acesso a câmera
    const tracks = stream.getVideoTracks(); // Capta áudio e imagem. Mas só queremos imagem
    const { width, height } = tracks[0].getSettings(); // Capturando o vídeo e tamanho do vídeo.

    inputCanvas.width = width;
    inputCanvas.height = height;
    // Largura e altura dos vídeos (talvez não seja uma boa ideia, getusermedia passa restricoes tbm..)
    outputCanvas.width = width;
    outputCanvas.height = height;

    // Ver o objeto da TAG vídeo. Fonte vai ser a WEBCAM (stream)
    video.srcObject = stream; 

    // O que fazer quando o servidor mandar alguma coisa. Pega o blob.
    socket.addEventListener('message', async (event) => {
        const outputData = event.data;
        // Cria bitmap
        const bitmap = await createImageBitmap(outputData);
        // Desenha no canvas que já estava na página. 
        outputContext.drawImage(bitmap, 0, 0);
    });

    // setInterval usa-se quando se quer um loop infinito mas com um tempo específico entre uma iteracao
    // e outra. Chama async a funcao regularmente e deixa o tempo 1000 / FPS passar. 
    setInterval(async () => {
        // Pega o conteúdo do vídeo e desenha no Canvas, depois é coordenadas. "Screenschot da webcam" e 
        // salvar no canvas, para pegar os bytes do vídeo. 
        inputContext.drawImage(video, 0, 0);
        const blob = await getBlob();
        // Manda para o servidor.
        socket.send(blob);
    }, 1000 / FPS);
}

main();
