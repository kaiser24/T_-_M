<?php 
$name= $_FILES['file1']['name'];

$tmp_name= $_FILES['file1']['tmp_name'];

$file_size = $_FILES["file1"]["size"];

$position= strpos($name, ".");

$fileextension= substr($name, $position + 1);

$fileextension= strtolower($fileextension);


if (isset($name)) {

    if (empty($name))
        {
            echo "Please choose a file";
        } 
        if($file_size > 3221225472){
            $errors[]='El archivo debe ser inferior a 3 GB';
            echo ($errors);
        }
            else if (!empty($name)){
                if (($fileextension !== "mp4") && ($fileextension !== "avi") && ($fileextension !== "webm"))
            {
                echo "The file extension must be .mp4, .avi, or .webm in order to be uploaded";
            }

                else if (($fileextension == "mp4") || ($fileextension == "ogg") || ($fileextension == "webm"))
                {
                    if (move_uploaded_file($tmp_name, "archivos/$name")) {
                    echo 'Subida completada';
                }
             
            }
        }
    }
?>
