/**
 * This function captures an image from the webcam, resizes it to the preferred
 * dimensions of the selected model, and represents it in a format suitable for
 * input to the network.
 */

function predictSaliency(image, model, networkInputSize) {
  return tf.tidy(() => {
    // Fetch input image
    loadedImage = tf.browser.fromPixels(image);
    const batchedImage = loadedImage.toFloat().expandDims();
    const resizedImage = tf.image.resizeBilinear(batchedImage, networkInputSize, true);
    const clippedImage = tf.clipByValue(resizedImage, 0.0, 255.0);  // TODO: Does this actually do anything?
    const reversedImage = tf.reverse(clippedImage, 2);

    // Make a prediction
    const modelOutput = model.predict(reversedImage);
    const resizedOutput = tf.image.resizeBilinear(modelOutput, [image.height, image.width], true);
    const clippedOutput = tf.clipByValue(resizedOutput, 0.0, 255.0);  // TODO: Does this actually do anything?
    return clippedOutput.squeeze();
  });
}

function injectCanvas(query, width, height) {
    // Generate a new canvas element with the target size and put it into the dom under the queried element
    var cropContainer = document.querySelector(query);
    const newCanvas = document.createElement("canvas");
    newCanvas.width = width;
    newCanvas.height = height;
    cropContainer.appendChild(newCanvas);
    return newCanvas;
}

function brightestRect(tensor, rectSize, ctx) {
    console.log("Calculating brightest rect...");
    // How roughly are we guessing. If this is bigger, it will run faster
    const stepSize = rectSize / 5;

    var maxWidth = tensor.shape[0];
    var maxHeight = tensor.shape[1];

    var bestValue = 0;
    var bestPosition = undefined;
    // Iterate over chunks by stepSize, limited by bounds
    for (var col = 0; col < maxWidth - rectSize + 1; col += stepSize) {
        for (var row = 0; row < maxHeight - rectSize + 1; row += stepSize) {

            // Slice the tensor to get the submatrix of [rectSize, rectSize] starting at this chunk.
            var submatrix = tf.slice(tensor, [col, row], [rectSize, rectSize]);
            // Calculate the sum of the submatrix
            var value = submatrix.mean().dataSync()[0];
            if (value > bestValue) {
                bestValue = value;
                bestPosition = [row, col];
            }

            // Draw selected bounding box
            ctx.globalCompositeOperation = "source-over";
            ctx.beginPath();
            ctx.rect(row, col, rectSize, rectSize);
            ctx.strokeStyle = "#ffff0011";
            ctx.stroke();

            ctx.font = "6px Arial";
            ctx.fillStyle = "#ffff00";
            ctx.fillText("" + Math.round(value * 100), row, col + 12);
        }
    }
    return bestPosition;
}


function cropRotateAndScale(img, targetSize) {
    var newCanvas = injectCanvas("#cropped", targetSize, targetSize);

    // Determine the portion of the panel we want to target
    var sourceRect = [0, 0, img.naturalWidth, img.naturalHeight];

    // If we're very wide, take the leftmost quarter (it's probably a single row strip)
    if (img.naturalWidth > 2*img.naturalHeight) {
        sourceRect = [0, 0, Math.floor(img.naturalWidth/4), img.naturalHeight];
    // If we're very tall, take the topmost quarter (it's probably a very long page)
    } else if (img.naturalHeight > 2*img.naturalWidth) {
        sourceRect = [0, 0, img.naturalWidth, Math.floor(img.naturalHeight/4)];
    } else {
        sourceRect = [0, 0, Math.floor(img.naturalWidth/2), Math.floor(img.naturalHeight/2)];
    }

    // Make sure the aspect ratio stays correct for the targetSize
    var targetRect = [0, 0, targetSize, targetSize];
    if (sourceRect[2] > sourceRect[3]) {
        let size = targetSize / sourceRect[2] * sourceRect[3];
        targetRect = [0, (targetSize - size) / 2, targetSize, size];
    } else if (sourceRect[3] > sourceRect[2]) {
        let size = targetSize / sourceRect[3] * sourceRect[2];
        targetRect = [(targetSize - size) / 2, 0, size, targetSize];
    }

    // TODO: Try shaving a tiny bit off the top and left, since those are probably panel borders

    // Draw the target part of the image onto the canvas, and fill the rest of the area with black
    const ctx = newCanvas.getContext("2d");
    ctx.fillStyle = 'black';
    ctx.fillRect(0, 0, targetSize, targetSize);
    ctx.drawImage(img, ...sourceRect, ...targetRect);

    // TODO: try applying a vignette to block out some comic border spam?
//    var grd = ctx.createRadialGradient(targetSize / 2, targetSize / 2, targetSize / 3, targetSize / 2, targetSize / 2, targetSize / 2);
//    grd.addColorStop(0, "#00000000");
//    grd.addColorStop(1, "#000000ff");
//    ctx.fillStyle = grd;
//    ctx.fillRect(0, 0, targetSize, targetSize);

    return newCanvas;
}


async function predictSaliencyAndRender(image, model, networkSize) {
    console.log("Predicting saliency...");
    // Calculate the saliency
    var saliencyMap = predictSaliency(image, model, [networkSize, networkSize]);
//    var dropLow = 0.25;
//    saliencyMap = saliencyMap.clipByValue(dropLow, 1.0);
//    saliencyMap = saliencyMap.sub(tf.scalar(dropLow)).mul(tf.scalar(1 / (1-dropLow)));

    // Initialize random trash
    const canvas = injectCanvas("#saliency", networkSize, networkSize);
    const ctx = canvas.getContext("2d");

    // Draw saliency map
    await tf.browser.toPixels(saliencyMap, canvas);

    // Multiply in the original image
    ctx.globalCompositeOperation = "multiply";
    ctx.drawImage(image, 0, 0);

    return saliencyMap;
}


function getThumbnailOptions(croppedImage, saliencyMap) {
    thumbSize = Math.floor(croppedImage.width / 1.75);
    const canvas = injectCanvas("#thumbnails", thumbSize, thumbSize);
    const ctx = canvas.getContext("2d");

    // Calculate the row/col of the center of the rectangle. Most effective solution, currently.
    var corner = brightestRect(saliencyMap, thumbSize, ctx);

    // Calculate the most salient point as the center instead. Not as effective.
//    var i = tf.argMax(saliencyMap.flatten()).dataSync()[0]
//    var row = Math.floor(i / saliencyMap.shape[1]);
//    var col = i % saliencyMap.shape[1];
//    corner = [col - (thumbSize / 2), row - (thumbSize / 2)];

    // TODO: Calculate the size of the blob originating around the most salient point, and capture that in a square?

    // Draw selected bounding box
    ctx.drawImage(croppedImage, corner[0], corner[1], thumbSize, thumbSize, 0, 0, thumbSize, thumbSize);
}



async function runModel() {
    // Load model
    console.log("Loading model...");
    var networkSize = 128;
    const modelURL = "https://storage.googleapis.com/msi-net/model/high/model.json";
    const model = await tf.loadGraphModel(modelURL);
    console.log("Model loaded!");

    document.querySelectorAll("#inputs img").forEach(async function (img) {
        // Capture the portion of the image we're interested in
        var croppedImage = cropRotateAndScale(img, networkSize);
        // Calculate the saliency map and render it
        var saliencyMap = await predictSaliencyAndRender(croppedImage, model, networkSize);
        // Render thumbnails using different possible algorithms
        getThumbnailOptions(croppedImage, saliencyMap);
        // TODO: Make this return from the original source, if possible.

        // Cleanup
        saliencyMap.dispose();
    });

    model.dispose();
}
