# Facial Detection Fire Alarm 

## UTS 2019


This project is based of research on the application of faical recognition for building safety. 

The follow repository contains the proof of concept files, including the flows requires for Node-Red (with credentials removed)


# Running The Script

```sh
mm 
```

# Current Functionality 

1)	Facial Recognition (Counting, Graphing, Live Count & Confidence detection)
2)	Argument Parsing (Debug Mode, input sample video, output detection, set confidence, set analyses lag)
3)	Database storage and logging (Cloudant, Firestore & MySQL)
4)	Alarm trigger (Start physical and software alerts)
5)	Dashboard (View live charts and statistics, view database of sensors, view location of alarm on an interactive map)

# Future Development Recommendations

-	Heat map: That involves analysing count data, location of the alarm and a visual depiction of crowds on a building floor map. 
-	Live camera feed: Streaming of the camera feed with face detection to the dashboard for live viewing
-	Liveliness & Tracking: Check if detections are people through liveliness and tracking already counted people.
-	Efficient Input Video: Improved threading and buffering for inputted demo videos
-	Frame Skip: Improve efficiency and decrease workload by reducing the amount of frame that are being analysed
-	Recognition and Training: Training the model to learn the names of people, this will allow it to recognise the faces detected.
-	Better Visual Aid: For locations of alarms on the map, 3D models of the buildings can be used to pinpoint positions along with images.
-	Data visualisation: Implementing powerful tools such a Tableau and Power BI to analyse data and produce much more details charts with more interactivity and control.
-	Gas Sensor: Using a hardware gas sensor (MQ Sensors) for detecting various gases that could cause a fire or create by a fire.
-	Temperature Accuracy: The SenseHat tends to be inaccurate as it seems to be effected by the CPU
-	Reduce Databases: This solution can be clunky and ineffecient as it implements 3 databases
-	Detailed Historical Charting: Simple Node-Red functionality and inexperience limited this


# Requirements

- Raspberry Pi
- Pi Compatbile Cam
- SenseHat
- Piezo Buzzer
- Node-Red Starter Kit for IBM Cloud (BlueMix + Cloudant)
- Firebase
- Twilio Trial Account