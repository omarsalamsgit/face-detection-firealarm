# import packages
from imutils.video import VideoStream
from firebase import firebase
import firebase_admin
from firebase_admin import credentials 
from firebase_admin import firestore 
from google.cloud import firestore
import os
import numpy as np
import argparse
import imutils
import time
import datetime
import cv2
import mysql.connector as mysql
from sense_hat import SenseHat


# Build argument parsing
ap = argparse.ArgumentParser()
ap.add_argument("-p", "--prototxt", default="deploy.prototxt.txt",
    help="path to Caffe 'deploy' prototxt file")
ap.add_argument("-m", "--model", default="res10_300x300_ssd_iter_140000.caffemodel",
    help="path to Caffe pre-trained model")
ap.add_argument("-i", "--input", type=str,
    help="path to optional input video")
ap.add_argument("-o", "--output", type=str,
    help="path to optional output video")
ap.add_argument("-l", "--lag", type=float, default=0,
    help="setup loop lag time to reduce scans")
ap.add_argument("-c", "--confidence", type=float, default=0.5,
    help="minimum probability to filter weak detections")
ap.add_argument("-d","--debug", action='store_true',
    help="No argument needed")
args = vars(ap.parse_args())



#initiate sensehat (for sensors/LEDs)
sense = SenseHat()

# Connect to MySQL database
#print connection object if connected
dbsql = mysql.connect (
    host = "localhost",
    user = "user",
    passwd = "password",
    database = "facedetection"
)
print(dbsql)

# Create cursor instance for executing SQL statements
cursor = dbsql.cursor()

# Authenticate google firebase
# Init Firestore DB
credential_path = "/path/to/service-account-file.json"
os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = credential_path
firebase_admin.initialize_app()
db = firestore.Client()

# Load openCV serialised model
print("[INFO] Loading model...")
net = cv2.dnn.readNetFromCaffe(args["prototxt"], args["model"])

# Print set lag time 
print("[INFO] Setting " + str(args["lag"]) + " second lag...")

# Check if input is detected
# initialize the video stream and allow the camera sensor to warm up
# If input used grab file reference
if not args.get("input",False):
    print("[INFO] Starting live video stream...")
    vs = VideoStream(usePiCamera=True).start()
    time.sleep(2.0)    
else:
    print("[INFO] Opening sample video...")
    vs = cv2.VideoCapture(args["input"])
    time.sleep(1.0)

# Setup timestamp
ts = time.time()
st = datetime.datetime.fromtimestamp(ts).strftime('%Y-%m-%d %H:%M:%S')

# Init colours for LEDs
red = (255, 0, 0)
white = (200,200,200)
green = (0,255,0)

# Init writer for output video file
writer = None


#frame_rate = 10
#prev = 0 

# loop over the frames from the video stream
while True:
    
    #time_elapsed = time.time() - prev
    frame = vs.read()
    # grab the frame from the threaded video stream and resize it
    # to have a maximum width of 400 pixels 
    
    frame = frame[1] if args.get("input", False) else frame
    if args["input"] is not None and frame is None:   
        break
   
 
    frame = imutils.resize(frame, width=400)
 
    # grab the frame dimensions and convert it to a blob
    (h, w) = frame.shape[:2]
    blob = cv2.dnn.blobFromImage(cv2.resize(frame, (300, 300)), 1.0,
        (300, 300), (104.0, 177.0, 123.0))
    
    # Detect temperature
    # Format Temp
    temp = sense.get_temperature()
    tempf = "{:.2f}".format(temp)


        
    
    # Setup inputted lag time
    time.sleep(args["lag"])


    # pass the blob through the network and obtain the detections and
    # predictions
    net.setInput(blob)
    detections = net.forward()

    data = {}
    
# loop over the detections
    count = 0
    for i in range(0, detections.shape[2]):
        

        # extract the confidence (i.e., probability) associated with the
        # prediction
        confidence = detections[0, 0, i, 2]

        # filter out weak detections by ensuring the `confidence` is
        # greater than the minimum confidence
        # counts detected faces
        if confidence > args["confidence"]:
            count += 1
        else: 
            continue
       
       #Write video if requested
        if args["output"] is not None and writer is None:
            fourcc = cv2.VideoWriter_fourcc(*"MJPG")
            writer = cv2.VideoWriter(args["output"], fourcc, 30, (w, h), True)

        # compute the (x, y)-coordinates of the bounding box for the
        # object
        box = detections[0, 0, i, 3:7] * np.array([w, h, w, h])
        (startX, startY, endX, endY) = box.astype("int")
     
        # draw the bounding box of the face along with the associated
        # probability
        text = "{:.2f}%".format(confidence * 100)
        y = startY - 10 if startY - 10 > 10 else startY + 10
        cv2.rectangle(frame, (startX, startY), (endX, endY),
            (0, 0, 255), 2)

        cv2.putText(frame, text, (startX, y),
            cv2.FONT_HERSHEY_SIMPLEX, 0.45, (0, 0, 255), 2)
        
        #faces = "#"+str(count)
        #cv2.putText(frame, faces, (endX, y),
        #    cv2.FONT_HERSHEY_SIMPLEX, 0.45, (0, 0, 255), 2)       
        
        # Check to see if can write to disk
        if writer is not None:
           writer.write(frame)

        # Print face count in console
        print("Number of Faces " + str(count))

        # Connect to firebase live server
        app = firebase.FirebaseApplication('https://yourfirebase.firebaseio.com')
        data= {'Timestamp':st,'Faces':count, 'Confidence':text}
        app.put('https://yourfirebase.firebaseio.com','/count',data)
      
        doc_ref = db.collection(u'fullcount')
        doc_ref.add({
            u'time': firestore.SERVER_TIMESTAMP,
            u'Faces': count,
            u'confidence': text 
        })

        #query db (debug)
        # Then query for documents
        #users_ref = db.collection(u'fullcount')

        #for doc in users_ref.stream():
        #    print(u'{} => {}'.format(doc.id, doc.to_dict()))
        
   
        ## defining the Query
        query = "INSERT INTO detections (time,location, count, confidence, temperature) VALUES (%s,%s, %s, %s, %s)"
        ## storing values in a variable
        values = (st,'CB11-NW-LV1-DOOR1',count,text,tempf)

        ## executing the query with values
        cursor.execute(query, values)

        ## to make final output we have to run the 'commit()' method of the database object
        dbsql.commit()

        #test for added records (debug)
        if args["debug"] is True: print(cursor.rowcount, "record inserted")


    # show the output frame
    cv2.imshow("Frame", frame)
    key = cv2.waitKey(1) & 0xFF
    
    #tempf = "{:.2f}".format(temp)
    time.sleep(1.0)
    print("Temp: %s C" % tempf)

    # if the `q` key was pressed, break from the loop
    if key == ord("q"):
        break




#check if writer needs to be released
if writer is not None:
    writer.release()
# if we are not using a video file, stop the camera video stream
if not args.get("input", False):
	vs.stop()

# otherwise, release the video file pointer
else:
	vs.release()

# do a bit of cleanup
cv2.destroyAllWindows()
vs.stop()

