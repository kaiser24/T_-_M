var cvs,
    context,
    dragging = false,
    dragStartLocation,
    snapshot;
    contador = 0;


function getCanvasCoordinates(event) {
    var x = event.clientX - cvs.getBoundingClientRect().left,
        y = event.clientY - cvs.getBoundingClientRect().top;

    return {x: x, y: y};
}

function myFunction(event) {
    if(contador  <=3){
    x = event.clientX - cvs.getBoundingClientRect().left,
    y = event.clientY - cvs.getBoundingClientRect().top;
    }
  }
  
  function clearCoor() {
    document.getElementById("demo1").innerHTML = "";
  }

function takeSnapshot() {
    snapshot = context.getImageData(0, 0, cvs.width, cvs.height);
}

function restoreSnapshot() {
    context.putImageData(snapshot, 0, 0);
}


function drawLine(position) {
    if (contador <= 4){
    context.beginPath();
    context.moveTo(dragStartLocation.x, dragStartLocation.y);
    context.lineTo(position.x, position.y);
    context.stroke();
    }
}

function dragStart(event) {
    if (contador <= 4){
    dragging = true;
    dragStartLocation = getCanvasCoordinates(event);
    takeSnapshot();
    coor = "Coordinates: (" + ("X: ") + x + " , " + ("Y: ") + y + ")";
    document.getElementById("demo1").innerHTML = coor
    console.log(getCanvasCoordinates(event));
    }contador++;
}

function drag(event) {
    var position;
    if (dragging === true) {
        restoreSnapshot();
        position = getCanvasCoordinates(event);
        drawLine(position);
    }
}

    function dragStop(event) {
    restoreSnapshot(); var position = getCanvasCoordinates(event);
    drawLine(position);
    if (contador <= 4){
        dragging = true;
    }else{
        dragging = false;
    }if(contador == 5){
        document.getElementById("procesar").style.visibility= 'visible';
    }
}
function init() {
    cvs = document.getElementById("canvas_video");
    context = cvs.getContext('2d');
    context.strokeStyle = '#1DE615';
    context.lineWidth = 4;
    // context.lineCap = 'round';

    cvs.addEventListener('mousedown', dragStart, false);
    cvs.addEventListener('mousemove', drag, false);
    cvs.addEventListener('mouseup', dragStop, false);
}

window.addEventListener('load', init, false);

function clearArea() {
    contador = 0;
    context.setTransform(1, 0, 0, 1, 0, 0);
    context.clearRect(0, 0, cvs.width, cvs.height);
}

// function EscribirJson() {
//     myObj = {name: "John", age: 31, city: "New York"};
//     myJSON = JSON.stringify(myObj);
//     localStorage.setItem("testJSON", myJSON);
//     alert(myObj);
// }

function WriteToFile1() {
    var ajax = new XMLHttpRequest();
    ajax.open("POST", "subir.php");
    alert("Completado");
}