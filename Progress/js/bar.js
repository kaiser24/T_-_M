  function _(el){
      return document.getElementById(el);
  }
  
  
function uploadFile(formulario, archivo){
    extensiones_permitidas = new Array(".mp4",".avi",".webm");
    mierror="";
      if (!archivo){
          mierror = "Debes selecionar un archivo";
          alert(mierror);
      }else{
          extension=(archivo.substring(archivo.lastIndexOf("."))).toLowerCase();
          permitida = false;
          if (extension == extensiones_permitidas[0]) {
              permitida = true;
          }
      }
      if (!permitida) {
          mierror = "Comprueba la extension de los archivos a subir, Solo se pueden subir con extenciones: " +extensiones_permitidas.join();
          alert (mierror);
      }else {
        texto1 = "archivos";
        namearchivo=(archivo.substring(archivo.lastIndexOf("\\")));
        texto = texto1.concat(namearchivo);
        //alert (texto);
        document.getElementById("cuadro_video").src=texto;
        var mediaElement = document.getElementById("cuadro_video");
        mediaElement.currentTime = 5;
        window. open("../Progress/img/ejemplo.png", "Cambiando", "width=500, height=389, top=100px, left=500px");
        var file = _("file1").files[0];
          //alert(file.name+" | "+file.size+" | "+file.type);
        var formdata = new FormData();
        formdata.append("file1", file);
        var ajax = new XMLHttpRequest();
        ajax.upload.addEventListener("progress", progressHandler, false);
        ajax.addEventListener("load", completeHandler, false);
        ajax.addEventListener("error", errorHandler, false);
        ajax.addEventListener("abort", abortHandler, false);
        ajax.open("POST", "subir.php");
        ajax.send(formdata);           
      }
    
  }
  
        function progressHandler(event){
                var percent = (event.loaded / event.total) * 100;
                _("progressBar").value = Math.round(percent);
                _("status").innerHTML = Math.round(percent)+"%";
            }
            function completeHandler(event){
                _("status").innerHTML = event.target.responseText;
                _("progressBar").value = 0;
            }
            function errorHandler(event){
                _("status").innerHTML = "Upload Failed";
            }
            function abortHandler(event){
                _("status").innerHTML = "Upload Aborted";
            }
