/**
 * This script is adapted from the two tensorflowjs examples hosted at
 * https://github.com/tensorflow/tfjs-examples/tree/master/webcam-transfer-learning
 * and https://github.com/tensorflow/tfjs-models/tree/master/posenet/demos
 */

const image = document.getElementById("swordsImage");
const webcam = document.getElementById("webcam");
const canvas = document.getElementById("canvas");
const ctx = canvas.getContext("2d");

let model;
let modelURL;
let imageDims;
let canvasDims = [image.height, image.width];
let modelChange;

/**
 * This function captures an image from the webcam, resizes it to the preferred
 * dimensions of the selected model, and represents it in a format suitable for
 * input to the network.
 */
function fetchInputImage() {
  return tf.tidy(() => {
    loadedImage = tf.browser.fromPixels(image);
    const batchedImage = loadedImage.toFloat().expandDims();
    const resizedImage = tf.image.resizeBilinear(batchedImage, imageDims, true);
    const clippedImage = tf.clipByValue(resizedImage, 0.0, 255.0);
    const reversedImage = tf.reverse(clippedImage, 2);
    return reversedImage;
  });
}

function predictSaliency() {
  return tf.tidy(() => {
    const modelOutput = model.predict(fetchInputImage());
    const resizedOutput = tf.image.resizeBilinear(modelOutput, canvasDims, true);
    const clippedOutput = tf.clipByValue(resizedOutput, 0.0, 255.0);
    return clippedOutput.squeeze();
  });
}

function getMax(arr) {
    let len = arr.length;
    let max = -Infinity;

    while (len--) {
        max = arr[len] > max ? arr[len] : max;
    }
    return max;
}

/**
 * Here the model is loaded and fed with an initial image to warm up the
 * graph execution such that the next prediction will run faster. Afterwards,
 * the network keeps on predicting saliency as long as no other model is
 * selected. The results are automatically drawn to the canvas.
 */
async function runModel() {
    showLoadingScreen();

    model = await tf.loadGraphModel(modelURL);
    const saliencyMap = predictSaliency();

    var i = tf.argMax(saliencyMap.flatten()).dataSync()[0]
    var row = Math.floor(i / saliencyMap.shape[1]);
    var col = i % saliencyMap.shape[1];

    console.log("yolo " + i + " " + row + "," + col);

    // Draw
    await tf.browser.toPixels(saliencyMap, canvas);

    const ctx = canvas.getContext("2d");
    ctx.globalCompositeOperation = "multiply";
    ctx.drawImage(image, 0, 0);

    const clipSize = Math.floor(Math.min(...canvasDims) / 3);
    ctx.globalCompositeOperation = "source-over";
    ctx.beginPath();
    ctx.rect(col-Math.floor(clipSize/2), row-Math.floor(clipSize/2), clipSize, clipSize);
    ctx.strokeStyle = "#ff0000";
    ctx.stroke();
    saliencyMap.dispose();

    model.dispose();
}

/**
 * When a new model is currently loading, the canvas signals a message
 * to the user.
 */
function showLoadingScreen() {
  ctx.fillStyle = "white";
  ctx.textAlign = "center";
  ctx.font = "1.7em Alegreya Sans SC", "1.7em sans-serif";
  ctx.fillText("loading model...", canvas.width / 2, canvas.height / 2);
}

/**
 * The main function that first defines the default model, adds mouse click
 * listeners that interrupt the current prediction loop and invoke the loading
 * of a different model, and tries to set up a webcam stream for input to the
 * model.
 */
async function app() {
  modelURL = "https://storage.googleapis.com/msi-net/model/very_low/model.json";
  // Keep aspect ratio, but have a maximum size
  const maxSize = 128;
  var scaleFactor;
  if (canvasDims[0] > canvasDims[1]) {
    scaleFactor = maxSize / canvasDims[0];
  } else {
    scaleFactor = maxSize / canvasDims[1];
  }
  imageDims = [Math.floor(canvasDims[0] * scaleFactor), Math.floor(canvasDims[1] * scaleFactor)];
  console.log(imageDims);
  runModel();
}

app();