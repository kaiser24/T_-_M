<!DOCTYPE html>
<html>
<head>
    <title>Datos </title>
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <link rel="stylesheet" href="https://maxcdn.bootstrapcdn.com/bootstrap/3.4.1/css/bootstrap.min.css">
    <link rel="stylesheet" href="https://stackpath.bootstrapcdn.com/bootstrap/4.4.1/css/bootstrap.min.css">
    <link rel="stylesheet" href="css/style.css">
    <script src="https://ajax.googleapis.com/ajax/libs/jquery/3.4.1/jquery.min.js"></script>
    <script src="https://kit.fontawesome.com/cb4ab753a2.js" crossorigin="anonymous"></script>
    
</head>
<body>
	<section id="circleBar">
        <div class="container">
            <div class="row">
                <div class="col-md-6">                                       
                    <div id="coordiv" onmousemove="myFunction(event)" onmouseout="clearCoor()">
                            <canvas id="canvas_video" width="500px" height="350px">Tu navegador no admite el elemento &lt;canvas&gt;.</canvas>
                            <video src="" id="cuadro_video" poster=""></video> 
                    </div>
                    <p id="demo1"></p> 
                    <button type="button" class="btn btn-outline-primary btn-lg" onclick="javascript:clearArea();return false;">Limpiar Area</button> 
                </div>
                <div class="col-md-6">
                    <div class="round_bar" data-value="0.99" data-size="200" data-thickness="12">
                        <strong></strong>
                        <span>#</span>
                    </div>
                    <button id="procesar" type="button" onclick="WriteToFile();" class="btn btn-primary btn-lg">Procesar</button>
                </div>
            </div>
        </div>
    </section>

    <div class="container">
            <div class="row">
                <div class="col-md-6">
                    <!-- RELLENO -->
                </div>
                <div class="col-md-6">    
                    <div class="list-group-item active">
                        <h3 class="list-group-item-heading" style="text-align:center;">Resultados</h3>
                    </div>
                </div>
                <br>
                <div class="col-md-6">
                    <div class="card border-secondary mb-6" style="max-width: 60rem; margin-top:2.5%;">
                        <form action="" id="upload_form" method="post" enctype="multipart/form-data">  
                            <div class="card-header" style="font-size:15px;">Subir archivo</div>
                                <input type="file" name="file1" id="file1" style="margin-top:2%; margin-left:3%;"> 
                                 <progress id="progressBar" value="0" max="100" style="width:300px; margin-top:1%; margin-left:3%;"> </progress> <span id="status"></span>
                                    <div class="card-body text-dark">
                                        <button type="button" class="btn btn-outline-primary btn-lg" value="Upload File" onclick="uploadFile(this.form, this.form.file1.value)" style="margin-top:1%;">Subir Video</button>
                                        <button type="submit" class="btn btn-outline-danger btn-lg" id="cancel" acesskey="62"  style="margin-top:1%;">Cancelar</button>
                                    </div>
                            </div> 
                            
                        </form>    
                </div>
               
                <div class="col-md-3">
                    <div class="list-group" style="margin-top:5%; text-align:center;">
                        <a class="list-group-item">
                            <h4 class="list-group-item-heading">Automoviles</h4>
                            <p class="list-group-item-text">Cantidad:</p>
                        </a>
                        <a class="list-group-item">
                            <h4 class="list-group-item-heading">Pesados</h4>
                            <p class="list-group-item-text">Cantidad:</p>
                        </a>
                        <a class="list-group-item">
                            <h4 class="list-group-item-heading">Motocicletas</h4>
                            <p class="list-group-item-text">Cantidad:</p>
                        </a>
                        <!-- <a href="#" class="list-group-item">
                        <h4 class="list-group-item-heading">Motocicletas</h4>
                        <p class="list-group-item-text">Cqantidad:</p>
                        </a> -->
                    </div>
                </div>
                <div class="col-md-3">
                    <div class="list-group" style="margin-top:5%; text-align:center;">
                        <a class="list-group-item">
                            <h3 class="list-group-item-heading" style="margin-top:2%;">50</h3>
                            <p class="list-group-item-text"></p>
                        </a>
                    </div>
                    <div class="list-group" style="margin-top:2.5%; text-align:center;">
                        <a class="list-group-item">
                            <h3 class="list-group-item-heading" style="margin-top:2%;">40</h3>
                            <p class="list-group-item-text"></p>
                        </a>
                    </div>
                    <div class="list-group" style="margin-top:2.5%; text-align:center;">
                        <a class="list-group-item">
                            <h3 class="list-group-item-heading" style="margin-top:2%;">20</h3>
                            <p class="list-group-item-text"></p>
                        </a>
                    </div>
                </div>
            </div>

    <script src="https://code.jquery.com/jquery-3.4.1.js"></script> 
    <script src="https://ajax.googleapis.com/ajax/libs/d3js/5.15.0/d3.min.js"></script>
    <script src="https://cdnjs.cloudflare.com/ajax/libs/jquery-circle-progress/1.2.2/circle-progress.min.js"></script>
    <script src="js/bar.js"></script>  
    <script src="js/progress.js"></script>
    <script src="js/canvas.js"></script>
     
</body>
