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
import json

def crateTracker(tracker_type):
    if(tracker_type == 'KCF'):
        tracker = cv2.TrackerKCF_create()
    elif(tracker_type == 'TLD'):
        tracker = cv2.TrackerKCF_create()
    elif(tracker_type == 'MEDIANFLOW'):
        tracker = cv2.TrackerKCF_create()
    elif(tracker_type == 'MOSSE'):
        tracker = cv2.TrackerKCF_create()
    elif(tracker_type == 'Dlib'):
        tracker = dlib.correlation_tracker()
    return tracker
       


def updateCountDict(DICT, count_array):
    DICT['count']['cars'] = count_array[0]
    DICT['count']['motorbikes'] = count_array[1]
    DICT['count']['heavy'] = count_array[2] + count_array[3]
    
    return DICT

def loadNet():
    #==================================== Loading The Darknet model and the YOLO metadata ===================================
    print("INCIANDO...")
    NET = load_net(b"/home/pdi/darknet/cfg/yolov3.cfg",
                b"/home/pdi/Felipe_data/yolov3.weights", 0)
    METADATA = load_meta(b"/home/pdi/darknet/cfg/coco.data")
    #========================================================================================================================
    return NET, METADATA


def executeTnM(INFO, NET, METADATA, IMSHOW = False, DRAW_ZONE = False, SAVE_DETS = False):

    tracker_types = ['KCF'      , 'TLD' , 'MEDIANFLOW' , 'MOSSE', 'Dlib']
    tracker_type = tracker_types[4]
    dir_n = os.path.dirname(__file__)

    
    #=============================================CONFIGURATION CONSTANTS====================================================
    # Display the video
    IMSHOW = IMSHOW
    # Draw zone in this code. Wont work through the service.
    DRAW_ZONE = DRAW_ZONE
    # Save detections
    SAVE_DETS = SAVE_DETS
    # Shape divider
    WIDTHDIVIDER = 2
    DLIB_TOLERANCE = 10  # Threshold to dlib decide whether the tracked object was lost of not
    CENTROID_DIST = 60      #distance between centroids

    # Json object
    jsonpath = dir_n + "/TM_DATA/JSON/DATA_OUTPUT.json"
    #=======================================================================================================================
    #json2save = "/home/pdi/Felipe_data/TM_DATA/JSON/" + os.path.splitext( os.path.basename(INFO['video']) )[0]

    try:
        os.mknod(jsonpath)
    except:
        pass

    #========================================================DATA dICTIONARY================================================
    DATA_OUTPUT = {
        'state' : 'processing',
        'video' : INFO['video'],
        'poly': INFO['poly'],
        'count' : {
            'cars' : 0,
            'motorbikes' : 0,
            'heavy' : 0
        },
        'progress' : 0,
        'errors' : None,
        'Warnings' : None

    }  
    #========================================================================================================================

    # Reading the video to process
    INPUTVIDEO = INFO['video']
    POLY = INFO['poly']

    # Getting zone corners
    inputZones = []
    for i in range(4):
        inputZones.append( (POLY[i]['x'], POLY[i]['y']) )

    ok= True

    # Path to the video to process
    #INPUTVIDEO = '/home/pdi/Felipe_data/T&M_videos2process/Etiquetado20160301_090424/Etiquetado20160301_090424.mp4'
    #INPUTVIDEO = args['video']

    #================================================== Handling file errors============================================
    if( not (os.path.exists(INPUTVIDEO)) ):
        print('Error')
        error = 'File not found.'
        print(error)

        # Updates output data with the error before exiting
        DATA_OUTPUT['errors'] = error
        with open(jsonpath, 'w') as DATA_OUTPUTjson:
            json.dump(DATA_OUTPUT, DATA_OUTPUTjson)
        exit()

    # Validating video format
    VALID_EXT = ['.mp4','.avi','.flv','.mov']
    _, VIDEO_EXT = os.path.splitext(INPUTVIDEO)
    if( not (VIDEO_EXT in VALID_EXT) ):
        print('Error')
        error = '{} format not supported. Allowed formats {}'.format(VIDEO_EXT,VALID_EXT) 
        print(error)

        # Updates output data with the error before exiting
        DATA_OUTPUT['errors'] = error
        with open(jsonpath, 'w') as DATA_OUTPUTjson:
            json.dump(DATA_OUTPUT, DATA_OUTPUTjson)
        exit()

    #==================================================================================================================


    # Frames evitados en la deteccion
    SKIPFRAMES = 1
    # Types of vehicles to detect
    vehiclesTypes = ["b'car'", "b'motorbike'","b'bus'","b'truck'"]

    # Inizializando trackers
    totalFrames = 0
    trackers = []
    trackableObjects = {}

    # Centroid tracker
    d = CENTROID_DIST
    ct = CentroidTracker(maxDisappeared=10, maxDistance=d, vehiclesTypes=vehiclesTypes, SAVE_DETS = SAVE_DETS,SAVE_PATH = dir_n)


    if SAVE_DETS:
        # Making directories to save the detections. For checking the behavior of the detector.
        #path_count = os.path.join(dir_n, '/data/')
        try:
            os.mkdir(dir_n + '/counting3/')
            os.mkdir(dir_n + '/counting3/' + 'cars')
            os.mkdir(dir_n + '/counting3/' + 'motorbikes')
            os.mkdir(dir_n + '/counting3/' + 'heavy')
        except:
            try:
                os.mkdir(dir_n + '/counting3/' + 'cars')
            except:
                pass
            try:
                os.mkdir(dir_n + '/counting3/' + 'motorbikes')
            except:
                pass
            try:
                os.mkdir(dir_n + '/counting3/' + 'heavy')
            except:
                pass

    # Creating the video object
    cap = cv2.VideoCapture(INPUTVIDEO)
    det = 0

    # FPS of the video
    videoFPS = cap.get(cv2.CAP_PROP_FPS)

    # Lenght of the video
    longVideo = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))

    # Inicio toma de tiempo
    start = time.time()

    # Initializing some variables
    old_boxes = []
    maxDistance_2 = d
    trackers = []
    carTypesList = []
    make_tracker = False
    con = 0

    # Reads the first frame of the video to draw the boz where to do the detections
    ret, frame = cap.read()
    frame = imutils.resize(frame, width=704, height=480)


    # gets the corner points of the drawn box
    if DRAW_ZONE:
        inputZones = []
        inputZones = selectPolygonZone(frame,'green')
        inputZones = inputZones[0]
        #inputZones = [(237, 195), (163, 404), (666, 395), (491, 163), (237, 195)]
    polizone = Polygon( [inputZones[0], inputZones[1], inputZones[2], inputZones[3]] )
    pts = np.array([ [inputZones[0][0],inputZones[0][1]] ,[inputZones[1][0],inputZones[1][1]] , [inputZones[2][0],inputZones[2][1]], [inputZones[3][0],inputZones[3][1]] ])


    # Some functions
    m = (pts[2][1] - pts[1][1] ) / (pts[2][0] - pts[1][0] )
    b = pts[1][1] - m * pts[1][0]
    limit = lambda x: b + m*x

    m2 = (120-50)/(431-183)
    radius = lambda y: m2*y


    #========================================================Video Processing============================================
    while cap.isOpened():

        # Capture frame-by-frame
        ret, frame = cap.read()
        frame = imutils.resize(frame, width=704, height=480)
        frame_height, frame_width,_ = frame.shape
        if IMSHOW:
            frame_toshow = frame.copy()    # this is just for drawing and displaying

            # Draws the detection area on the frame to display
            cv2.polylines(frame_toshow, [pts], True, (80,180,23), 3)
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        
        rects = []
        carTypesList_l = []

        # If there are objects being tracked then we process them first else just continue to the detections
        if trackers:
            #print(len(trackers))

            old_boxes = []
            to_del = []
            # loop over the trackers
            for i, tracker in enumerate(trackers):

                # set the status of our system to be 'tracking' rather
                # than 'waiting' or 'detecting'
                status = "Tracking"

                # update the tracker and grab the updated position
                if(tracker_type == 'Dlib'):
                    ok = True
                    pos_conf = tracker.update(frame)
                    pos = tracker.get_position()
                    startX = int(pos.left())
                    startY = int(pos.top())
                    endX = int(pos.right())
                    endY = int(pos.bottom())
                    #print(pos_conf)
                    if(pos_conf < DLIB_TOLERANCE ):
                        ok = False

                else:
                    ok,pos = tracker.update(frame)
                
                    # unpack the position object
                    startX = int(pos[0])
                    startY = int(pos[1])
                    endX = int(pos[0] + pos[2])
                    endY = int(pos[1] + pos[3])

                # if the box of the tracker has a part outside of our frame then crops it
                # This helps to keep the centroid close to the detection
                if(endX > frame_width):
                    endX = frame_width
                if(endY > frame_height):
                    endY = frame_height
                
                if IMSHOW:
                    cv2.rectangle(frame_toshow, (startX-int(startX*0.02),startY-int(startY*0.05)),(endX+int(endX*0.02),endY+int(endY*0.05)), (0, 255, 0), 2)

                #print(ok)
                if(not ok):
                    # list of the trackers that have been lost
                    to_del.append(i)
                else:
                    # Trackers that are still ok are passed to our "current boxes"
                    rects.append((startX, startY, endX, endY))
                    old_boxes.append((startX, startY, endX, endY))
            
            for i in range(len(to_del)):
                # Removes Lost trackers
                del trackers[to_del[-i -1]]
                del carTypesList[to_del[-i-1]]

        # time for detections. SKIPFRAMES tells which frames to detect. 1 is detection every frame. 2 every 2 frames and so on.
        # If there are not trackers we need to do detections.
        if( (totalFrames % SKIPFRAMES == 0) or (not trackers) ):
            # set the status and initialize our new set of object trackers
            status = "Detecting"

            rects = []
            carTypesList_l = []
            
            # For yolo to do detections has to read the img from a place on the disk for some reason
            cv2.imwrite('cam.jpg', frame)
            detections = detect(NET, METADATA,  b'cam.jpg', thresh=0.7)

            # Iterates the detections
            for detection in detections:
                # The model was trained on COCO which has 80 classes. We only care for this 4.
                if((str(detection[0]) == "b'car'") or (str(detection[0]) == "b'motorbike'") or (str(detection[0]) ==  "b'bus'") or (str(detection[0]) == "b'truck'")):
                    pt1 = (int(detection[2][0]-detection[2][2]/WIDTHDIVIDER),
                        int(detection[2][1]-detection[2][3]/WIDTHDIVIDER))
                    pt2 = (int(detection[2][0]+detection[2][2]/WIDTHDIVIDER),
                        int(detection[2][1]+detection[2][3]/WIDTHDIVIDER))

                    
                    #rect = dlib.rectangle(np.int64(pt1[0]), np.int64(
                    #    pt1[1]), np.int64(pt2[0]), np.int64(pt2[1]))

                    center = (int(detection[2][0]), int(detection[2][1]) )
                    if(polizone.contains( Point( center)  ) ):
                        
                        # then appends it to our current boxes, xi,yi,xf,yf
                        rects.append( ( pt1[0],pt1[1],pt2[0],pt2[1] ) )
                        carTypesList_l.append(str(detection[0]))
                        det += 1

            # We need to check if the new objects (From detections) is already being tracked to not create another tracker object.
            if(old_boxes):
                con += 1

                centers = []
                areas = []

                # Centers of the old boxes (The ones currently tracked)
                for old_box in old_boxes:
                    centers.append( ( int( (old_box[0] + old_box[2])/2 ),int( (old_box[1] + old_box[3])/2 ) ) )
                    areas.append( (old_box[2] - old_box[0])*(old_box[3] - old_box[1]) )

                # Iterate the new boxes (The detected ones)
                for rect, carType in zip(rects, carTypesList_l):

                    # Gets the new boxes centers
                    ccenter = ( int( (rect[0] + rect[2])/2 ),int( (rect[1] + rect[3])/2 ) )
                    carea = (rect[2] - rect[0])*(rect[3] - rect[1])

                    # We will create the new tracker unless it already exist
                    make_tracker = True
                    
                    # Iterate old centers
                    for i,(center,area) in enumerate(zip(centers,areas)):
                        
                        # Distance between the new center and the old
                        if(distance.euclidean(ccenter,center) < d ):
                            
                            # If is less than a threshold then its the same and sets to not make a new tracker.
                            if(area < carea*0.8):

                                # The vehicles approach the camera, so they become bigger, but the trackers (at least the opencv ones)
                                # do change the size of the box and gets to a point where the tracker box and the detection box are too different
                                # that their centroids are too apart and another object is created. To solve this we have to re-initialize
                                # the tracker when their size its too different from the detection. 
                                trackers[i] = crateTracker(tracker_type)
                                if( tracker_type == 'Dlib'):
                                    drect = dlib.rectangle(rect[0], rect[1], rect[2], rect[3])
                                    trackers[i].start_track(frame, drect)
                                else:
                                    trackers[i].init(frame, (rect[0],rect[1],rect[2]-rect[0],rect[3]-rect[1]) )
                            make_tracker = False
                            break
                    
                    # If there are not matches, then create a new tracker object
                    if(make_tracker):
                        tracker = crateTracker(tracker_type)
                        if( tracker_type == 'Dlib'):
                            drect = dlib.rectangle(rect[0], rect[1], rect[2], rect[3])
                            tracker.start_track(frame, drect)
                        else:
                            tracker.init(frame, (rect[0],rect[1],rect[2]-rect[0],rect[3]-rect[1]) )
                        trackers.append(tracker)
                        carTypesList.append(carType)
                        old_boxes.append( rect )

            # If there are not a single object then every detection is a new object.
            else:
                for rect, carType in zip(rects, carTypesList_l):
                    tracker = crateTracker(tracker_type)
                    if( tracker_type == 'Dlib'):
                        drect = dlib.rectangle( rect[0], rect[1], rect[2], rect[3] )
                        tracker.start_track(frame, drect)
                    else:
                        tracker.init(frame, (rect[0],rect[1],rect[2]-rect[0],rect[3]-rect[1]) )
                    trackers.append(tracker)
                    carTypesList.append(carType)
                old_boxes = rects.copy()

        # old_boxes are the boxes of the objects on the current frame
        # Passing them to our centroid tracker to create an id for each object if new.    
        objects, carTypeObjects, boxes = ct.update(old_boxes, carTypesList, frame)
        # loop over the tracked objects
        
        for i, (objectID, centroid) in enumerate( objects.items() ):
                # check to see if a trackable object exists for the current
                # object ID
            to = trackableObjects.get(objectID, None)
        
            # if there is no existing trackable object, create one
            if to is None:

                to = TrackableObject(objectID, centroid, set_color(
                    carTypeObjects[objectID]), carTypeObjects[objectID])


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


        if IMSHOW:

            cv2.imshow('Frame', frame_toshow)   
            if cv2.waitKey(1) & 0xFF == ord('q'):
                cv2.destroyAllWindows()
                break

        
        # Updating data processing
        #printProgressBar(totalFrames,longVideo-2,"Progeso: ",str(round(endImage - startImage,2)) + "s por imagen",2,100)
        DATA_OUTPUT = updateCountDict(DATA_OUTPUT, ct.get_vehicleCount())
        DATA_OUTPUT['progress'] = str( round( (totalFrames * 100)/(longVideo - 2),1 ) )  + "%"

        # Writing the json with the current info
        with open(jsonpath, 'w') as DATA_OUTPUTjson:
            json.dump(DATA_OUTPUT, DATA_OUTPUTjson)

        totalFrames += 1
        if (totalFrames + 1) == longVideo:

            # Writing the json with the output info and saving the info of the process to a new json
            DATA_OUTPUT['state'] = 'free'
            with open(jsonpath, 'w') as DATA_OUTPUTjson:
                json.dump(DATA_OUTPUT, DATA_OUTPUTjson)
            
            break
    cv2.destroyAllWindows()
    return ct.get_vehicleCount()

if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument('-v','--video', required=True, help='path to the video to process')
    args = vars(ap.parse_args())

    datas = {'video': args['video'],
        'poly':[
            {'x':237,'y':195},
            {'x':163,'y':404},
            {'x':666,'y':395},
            {'x':491,'y':163}
        ]
        
    }
    
    NET, METADATA = loadNet()
    res = executeTnM(datas, NET, METADATA, IMSHOW = True, DRAW_ZONE = True,SAVE_DETS= True)
    print(res)


