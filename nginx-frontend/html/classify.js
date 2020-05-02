let url = "https://dog-or-hotdog.meansqua.red/api/analyze:predict";

function dropHandler(ev) {
  
    // Prevent default behavior (Prevent file from being opened)
    ev.preventDefault();
  
    if (ev.dataTransfer.items) {
      // Use DataTransferItemList interface to access the file(s)

      // clear images
      reset();

      for (var i = 0; i < ev.dataTransfer.items.length; i++) {
        // If dropped items aren't files, reject them
        if (ev.dataTransfer.items[i].kind === 'file') {
          
          var file = ev.dataTransfer.items[i].getAsFile();
          //console.log('... file[' + i + '].name = ' + file.name);
          showImage(file);
          var promise = getBase64(ev.dataTransfer.files[i]);
          promise.then(function(result) {
            // remove data prefix of base64 encoded string
            base64Img = result.split(/,(.+)/)[1]
            apicall(base64Img);
          });
          
        }
      }
    } 
  }

function showImage(file) {
  //console.log('showimage')
  var urlCreator = window.URL || window.webkitURL;
  var imageUrl = urlCreator.createObjectURL(file);
  let img = document.createElement('img')
  img.classList.add('h-100')
  img.classList.add('d-inline-block')
  img.src = imageUrl
  document.getElementById('images').appendChild(img)
}

function showLabel(text) {
  document.getElementById('label').innerHTML = text;
}

function dragOverHandler(ev) {
    //console.log('File(s) in drop zone'); 
    // Prevent default behavior (Prevent file from being opened)
    ev.preventDefault();
}


function getBase64(file, onLoadCallback) {
  return new Promise(function(resolve, reject) {
      var reader = new FileReader();
      reader.onload = function() { resolve(reader.result); };
      reader.onerror = reject;
      reader.readAsDataURL(file);
  });
}

function apicall(b64) {
    // Sending and receiving data in JSON format using POST method
    var xhr = new XMLHttpRequest();
    xhr.open("POST", url, true);
    xhr.onreadystatechange = function () {
        if (xhr.readyState === 4 && xhr.status === 200) {
            var json = JSON.parse(xhr.responseText);
            //console.log(JSON.stringify(json));
            label = json['predictions'][0]['label'];
            proba = json['predictions'][0]['probability'] * 100;
            let promise = fetch('classes.json');
            promise.then(result => result.json())
            .then(function(classes) {
              showLabel("That's a " + classes[label] + "! I am " + proba.toFixed(2) + " % sure :)");
            });
            
            
        }
    }
    var data = JSON.stringify({"images": [b64], "tta": false});
    xhr.send(data);
}

function reset() {
  images = document.getElementById('images');
  images.innerHTML = "";
  showLabel('');
}

function useExample() {
  reset();
  let promise = fetch('examples.json');
  promise.then(result => result.json())
  .then(function(examples) {
    images = examples['images'];
    b64img = images[getRandomInt(images.length)];
    apicall(b64img);
    b64img = `data:image/png;base64,${b64img}`;
    let img = document.createElement('img');
    img.classList.add('h-100');
    img.classList.add('img-fluid');
    img.src = b64img;
    document.getElementById('images').appendChild(img);
  });
}

function getRandomInt(max) {
  return Math.floor(Math.random() * Math.floor(max));
}