from flask import Flask
from flask import request, render_template 
import json
from TM_Service import loadNet, executeTnM

NET = None
METADATA = None
#======================================================Requests============================================================
app = Flask(__name__)
@app.route('/',methods=['GET'])                                 
def hello_world():                                              
    return 'Hello World!'                                       

@app.route('/getinfo',methods=['POST'])            
def customerupdate():
    
    # From Python    
    #data = request.files.get('datas').read().decode('UTF-8')
    #info = json.loads( data )                  
    #print(info)                                          

    # from PHP
    #data = request.json
    #info = json.load( data )
    #print(info)

    data = '/home/pdi/Felipe_data/aforosDRON_mp/T_n_M/TM_DATA/JSON/DATA_OUTPUT.json'
    with open(data) as data:
        info = json.load(data)

    print('Processing')
    result = executeTnM(info, NET, METADATA)
    print(result)

    return "Finished"
#==========================================================================================================================

if __name__ == "__main__":
    
    NET, METADATA = loadNet()
    
    app.run(host='0.0.0.0')