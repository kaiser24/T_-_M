from pyimagesearch.centroidtracker import CentroidTracker
from pyimagesearch.trackableobject import TrackableObject
from darknetfunctions import load_net, load_meta, detect
from pyimagesearch.functionaforos import *
import time, dlib, cv2, imutils, random, numpy as np, math, time
from shapely.geometry import Point
from shapely.geometry.polygon import Polygon
from scipy.spatial import distance

import os
import cProfile
import argparse
import pickle
'''
ap = argparse.ArgumentParser()
ap.add_argument('-v','--video', default='/home/pdi/Felipe_data/aforosDRON2/videos/test1.mp4', help='path to the video to process')
ap.add_argument('-m','--model', default='1', help='pick the model')
args = vars(ap.parse_args())
'''
pr = cProfile.Profile()
pr.enable()
IMSHOW = True
# Divisor de ancho del frame
WIDTHDIVIDER = 2
# Cargando video
#INPUTVIDEO = args['video']

INPUTVIDEO = '/home/pdi/Felipe_data/T&M_videos2process/Etiquetado20160301_090424/Etiquetado20160301_090424.mp4'


VIDEO_NAME = INPUTVIDEO.split('/')[-1].split('.')[0]
# Frames evitados en la deteccion
SKIPFRAMES = 1
#MAX_VEH = int(args['vehicles'])
# Cargando red

print("INCIANDO...")

path_to_tnm = "/home/pdi/Felipe_data/aforosDRON_mp/T_n_M/"

NET = load_net(b"/home/pdi/Felipe_data/aforosDRON_mp/T_n_M/cfg_files/yolov3.cfg",
               b"/home/pdi/Felipe_data/aforosDRON_mp/T_n_M/model/yolov3.weights", 0)
METADATA = load_meta(b"/home/pdi/Felipe_data/aforosDRON_mp/T_n_M/cfg_files/coco.data")

# Tipos de vehiculos entrenados en la red
vehiclesTypes = ["b'car'", "b'motorbyke'","b'bus'","b'truck'"]

# Inizializando trackers
totalFrames = 0
totalDown = 0
totalUp = 0
trackers = []
trackableObjects = {}
trace = 0
d = 60
ct = CentroidTracker(maxDisappeared=10, maxDistance=d)
W = None
H = None

path_count = path_to_tnm



try:
    os.mkdir(path_count + 'counting3/')
except:
    try:
        os.mkdir(path_count + 'counting3/' + 'cars')
    except:
        pass
    try:
        os.mkdir(path_count + 'counting3/' + 'motorbikes')
    except:
        pass
    try:
        os.mkdir(path_count + 'counting3/' + 'heavy')
    except:
        pass

# Seleccion de entradas y salidas
cap = cv2.VideoCapture(INPUTVIDEO)

det = 0

# Tamaño de video en # de frames
longVideo = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
# Inicio toma de tiempo
start = time.time()

old_boxes = []
maxDistance_2 = d
trackers = []
carTypesList = []
make_tracker = False
con = 0

#pts = np.array([ [234-60,203-60],[36-60,431-60],[612+60,401-60],[350+60,183-60] ], np.int32)
#polizone = Polygon( [(234-60,203-60),(36-60,431-60),(612+60,401-60),(350+60,183-60)] )

ret, frame = cap.read()
frame = imutils.resize(frame, width=704, height=480)
inputZones = selectPolygonZone(frame,'green')

inputZones = inputZones[0]

polizone = Polygon( [inputZones[0], inputZones[1], inputZones[2], inputZones[3]] )
pts = np.array([ [inputZones[0][0],inputZones[0][1]] ,[inputZones[1][0],inputZones[1][1]] , [inputZones[2][0],inputZones[2][1]], [inputZones[3][0],inputZones[3][1]] ])
#pts = np.array([ [300,203],[36,380],[640,380],[508,183] ], np.int32)
#polizone = Polygon( [(234,203),(36,380),(640,380),(508,183)] )

m = (pts[2][1] - pts[1][1] ) / (pts[2][0] - pts[1][0] )
b = pts[1][1] - m * pts[1][0]
limit = lambda x: b + m*x

m2 = (120-50)/(431-183)
radius = lambda y: m2*y

while cap.isOpened():
    startImage = time.time()
    # Capture frame-by-frame
    ret, frame = cap.read()
    frame = imutils.resize(frame, width=704, height=480)
    frame_height, frame_width,_ = frame.shape
    frame_toshow = frame.copy()
    #print(frame_toshow.shape)
    

    cv2.polylines(frame_toshow, [pts], True, (80,180,23), 3)
    rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    
    temp_trace = trace
    trace = np.zeros(frame.shape)
    trace = np.uint8((trace)+(temp_trace))

    if W is None or H is None:
        (H, W) = frame.shape[:2]
    status = "Waiting"
    
    rects = []
    carTypesList_l = []

    if trackers:

        old_boxes = []
        to_del = []
        # loop over the trackers
        for i, tracker in enumerate(trackers):

            # set the status of our system to be 'tracking' rather
            # than 'waiting' or 'detecting'
            status = "Tracking"

            # update the tracker and grab the updated position
            ok,pos = tracker.update(frame)

            #pos = tracker.get_position()
            
            # unpack the position object
            startX = int(pos[0])
            startY = int(pos[1])
            endX = int(pos[0] + pos[2])
            endY = int(pos[1] + pos[3])

            if(endX > frame_width):
                endX = frame_width
            if(endY > frame_height):
                endY = frame_height
            
            #print((startX, startY, endX, endY))
            cv2.rectangle(frame_toshow, (startX-int(startX*0.02),startY-int(startY*0.05)),(endX+int(endX*0.02),endY+int(endY*0.05)), (0, 255, 0), 2)

            # add the bounding box coordinates to the rectangles list
            #rects.append((startX, startY, endX, endY))

            #print(ok)
            if(not ok):
                to_del.append(i)
            else:
                rects.append((startX, startY, endX, endY))
                old_boxes.append((startX, startY, endX, endY))
        
        for i in range(len(to_del)):
            del trackers[to_del[-i -1]]
            del carTypesList[to_del[-i-1]]

    if( (totalFrames % SKIPFRAMES == 0) or (not trackers) ):
        # set the status and initialize our new set of object trackers
        status = "Detecting"

        rects = []
        carTypesList_l = []
        

        cv2.imwrite('cam.jpg', frame)
        detections = detect(NET, METADATA,  b'cam.jpg', thresh=0.7)
        for detection in detections:
            if((str(detection[0]) == "b'car'") or (str(detection[0]) == "b'motorbike'") or (str(detection[0]) ==  "b'bus'") or (str(detection[0]) == "b'truck'")):
                pt1 = (int(detection[2][0]-detection[2][2]/WIDTHDIVIDER),
                    int(detection[2][1]-detection[2][3]/WIDTHDIVIDER))
                pt2 = (int(detection[2][0]+detection[2][2]/WIDTHDIVIDER),
                    int(detection[2][1]+detection[2][3]/WIDTHDIVIDER))

                
                #rect = dlib.rectangle(np.int64(pt1[0]), np.int64(
                #    pt1[1]), np.int64(pt2[0]), np.int64(pt2[1]))
                rect = (pt1[0],pt1[1],pt2[0]-pt1[0],pt2[1]-pt1[1])
                
                center = (int(detection[2][0]), int(detection[2][1]) )
                if(polizone.contains( Point( center)  ) ):
                    
                    #cv2.rectangle(frame_toshow, pt1, pt2, (0, 255, 0), 2)

                    rects.append( ( pt1[0],pt1[1],pt2[0],pt2[1] ) )
                    carTypesList_l.append(str(detection[0]))
                    
                    
                    #print(det,pt1[1],pt2[1], pt1[0],pt2[0])
                    #cv2.imwrite(path_count + 'counting2/' + 'dets/' + str(det) + str(detection[0]) + '.jpg',frame[ pt1[1]:pt2[1], pt1[0]:pt2[0],: ] )
                    #cv2.waitKey(200)
                    det += 1
                    #print(det)
                    #cv2.imshow('det', frame[ pt1[1]:pt2[1], pt1[0]:pt2[0],: ] )
                    #if(det == 150):
                    #    cv2.waitKey(0)
                    #if(str(detection[0]) == "b'motorbike'"):
                    #    cv2.imshow(str(detection[0]), frame[ pt1[1]:pt2[1], pt1[0]:pt2[0],: ] )
                    #    cv2.waitKey(0)
                    

                # loop over the trackers
        if(old_boxes):
            con += 1
            #print(con)
            centers = []
            areas = []
            for old_box in old_boxes:
                centers.append( ( int( (old_box[0] + old_box[2])/2 ),int( (old_box[1] + old_box[3])/2 ) ) )
                areas.append( (old_box[2] - old_box[0])*(old_box[3] - old_box[1]) )
                #print((old_box[2] - old_box[0])*(old_box[3] - old_box[1]))
                #cv2.circle(frame_todraw, ( int( (old_box[0] + old_box[2])/2 ),int( (old_box[1] + old_box[3])/2 ) ), 3, (0,0,255), -1)
        
            for rect, carType in zip(rects, carTypesList_l):
                ccenter = ( int( (rect[0] + rect[2])/2 ),int( (rect[1] + rect[3])/2 ) )
                carea = (rect[2] - rect[0])*(rect[3] - rect[1])
                #cv2.circle(frame_todraw, ccenter, 8, (0,255,0), -1)
                make_tracker = True
                
                for i,(center,area) in enumerate(zip(centers,areas)):
                    if(distance.euclidean(ccenter,center) < d ):
                        #print(area, carea)
                        if(area < carea*0.8):
                            #cv2.putText(frame_toshow, 'DANGER', (ccenter[0] - 10, ccenter[1] - 10),cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0,0,255), 2)
                            #print('B',len(trackers) )
                            trackers[i] = cv2.TrackerKCF_create()
                            trackers[i].init(frame, (rect[0],rect[1],rect[2]-rect[0],rect[3]-rect[1]) )
                            #print('A',len(trackers) )
                        make_tracker = False
                        break

                if(make_tracker):
                    tracker = cv2.TrackerKCF_create()
                    tracker.init(frame, (rect[0],rect[1],rect[2]-rect[0],rect[3]-rect[1]) )
                    trackers.append(tracker)
                    carTypesList.append(carType)
                    old_boxes.append( rect )
            #print('==',old_boxes)

        else:
            for rect, carType in zip(rects, carTypesList_l):
                tracker = cv2.TrackerKCF_create()
                tracker.init(frame, (rect[0],rect[1],rect[2]-rect[0],rect[3]-rect[1]) )
                
            # utilize it during skip frames
                trackers.append(tracker)
                carTypesList.append(carType)
                #make_trackers = False
            old_boxes = rects.copy()

    
    objects, carTypeObjects, boxes = ct.update(old_boxes, carTypesList, frame)
    # loop over the tracked objects
    '''
    for bbo, typ in zip(old_boxes, carTypesList):
        print( (bbo[3]-bbo[1])*(bbo[2]-bbo[0]) , typ)
        
        if(typ == "b'motorbike'" or typ == "b'motorbike'"):
            cv2.waitKey(0)'''

    
    for i, (objectID, centroid) in enumerate( objects.items() ):
            # check to see if a trackable object exists for the current
            # object ID
        to = trackableObjects.get(objectID, None)
    
        # if there is no existing trackable object, create one
        if to is None:

            to = TrackableObject(objectID, centroid, set_color(
                carTypeObjects[objectID]), carTypeObjects[objectID])
            
            #cv2.imshow(obj_tosave,frame[ obox[1]:obox[3],obox[0]:obox[2],: ])
            #cv2.waitKey(0)

        # store the trackable object in our dictionary
        trackableObjects[objectID] = to

        # draw both the ID of the object and the centroid of the
        # object on the output frame
        text = "{1}_{0} ".format(to.objectID,to.vehicle)
        
        
        if IMSHOW:
            #print(centroid,objectID)
            cv2.putText(frame_toshow, text, (centroid[0] - 10, centroid[1] - 10),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.5, to.color, 2)
            cv2.circle(frame_toshow, (centroid[0], centroid[1]), 2, to.color, -1)

            #cv2.circle(frame_toshow, (centroid[0], centroid[1]), int(radius(centroid[1])), (80,180,23), 2)

    if IMSHOW:
        #cv2.namedWindow('Frame')
        #cv2.moveWindow('Frame', 800, 0)
        cv2.imshow('Frame', frame_toshow)
        
        if cv2.waitKey(1) & 0xFF == ord('q'):
            cv2.destroyAllWindows()
            break

    endImage = time.time()
    #printProgressBar(totalFrames,longVideo-2,"Progeso: ",str(round(endImage - startImage,2)) + "s por imagen",2,100)
    totalFrames += 1
    if (totalFrames + 1) == longVideo:
        break
