# NurtiVision


# The Problem

I (Archita) have tried countless ways to count my calories, but every time, I ended up giving up—it was just too much work. Manually adding up numbers everyday became overwhelming. Yes, iPhone apps exist that let you take pictures of your food, but they aren’t live, or capable of tracking your daily caloric intake–-I would have to end up writing down and adding my total calories myself by hand, and existing iPhone applications do not already do this for me. They also don’t tell you whether you’re actually working toward your food-intake goals and making progress.

![Microsoft Edge](https://github.com/user-attachments/assets/c2880a2f-6faf-43aa-a1bb-b3c2e8bc06e4)



The bottom line problem: I want to lose weight, but I need a live assistant to watch what I eat and count my calories because I am too busy to manually add up the numbers. While iPhone applications make you take a picture of your food, and tell you the calories for a particular meal, users want a truly effortless experience. I (Archita) have always dreamed of someone to watch what I eat, and give me a notification whenever I binge eat chocolates, or when I cross my daily caloric intake. 


# The Solution


The report below follows the assumption that we are deploying our application in the Ray-Ban Meta Glasses—a sleek pair of glasses. In our demo, our application runs on Meta Quest 2.
We assume that these glasses will be as common as a smartphone in the future. 
Our AI-powered VR application will automatically track what you eat, logging calories, protein, fat, potassium, and carbs in real time. If a user is binge-eating unhealthy foods, the system sends a live notification, telling them to stop and helping them work towards their goals.


![Built-in Retina Display](https://github.com/user-attachments/assets/9c2b9db9-4bf4-43a1-8761-0b1f2349ad5a)



## User Experience Workflow

1. The user first enters their weight loss goal: for example, lose 5 pounds by the next month. 
2. The app will calculate how many calories they need to consume everyday to reach this weight loss goal. 
3. The VR headset detects when the person is eating and will log in the calories, potassium, protein, carbs, and fat of that meal. 
4. The user will get a live notification—as they are eating—if they reach above their daily caloric limit. 
5. The UI displays overall results/trends about the user's daily food intake. 

## What we are proud of, and how we built it

It’s incredible that we created a novel application with the potential to revolutionize the future of health tracking! Wow! We will most definitely use this app to track our calories when VR/AR glasses become more common. 

We developed an object detection model based on YOLOv11 to perform initial food detection and integrated our application with the OpenAI API for calorie counting. Since the original YOLO model was trained on the COCO dataset, which lacks class labels corresponding to different kinds of food, we scraped food images from online datasets and used the Grounding DINO model to annotate them with bounding boxes for YOLO finetuning. The model was fine tuned on a Jetson Orin Nano. The model is deployed on a web app on a Meta Quest 2 using the onnxruntime JS library and accesses the live video feed to make predictions. Specifically, the model detects when food is in the frame (future support will be added for detecting when a person is eating) and the web app automatically captures a picture to be used as input for a query to the OpenAI API (the YOLO model makes this process less expensive by reducing the number of queries). The OpenAI API call allows us to determine what food the user is eating, its weight, and the approximate nutrient content. We make a further API call to the USDA caloric food database to ensure that our nutrient predictions are more accurate. This nutrient information is sent to an SQL database and stored for future reference. If the user exceeds their daily calorie intake goal, they will receive a notification from the app. 



## Business Model

$10 Billion Dollar Market Cap estimation. 
We expect our app to be used on the Meta Ray-Ban Glasses, and aggressive AI/VR adoption in the next 5-10 years. 
As if they aren’t already becoming common, the Meta Ray-Ban Glasses are rapidly gaining traction and will soon be ubiquitous.
![20250215_124717](https://github.com/user-attachments/assets/ed376d44-4669-4feb-9ad8-6b02b8e81739)

We solve the core calorie-tracking pain point better than any other app, and this could be the next MyFitnessPal but smarter, faster, and fully automated. 

Our app assumes aggressive AI/VR adoption, seamless integration into daily life, and solving the core calorie-tracking pain point better than any other app. If executed well, this could be the next MyFitnessPal but smarter, faster, and fully automated. 

# The Team (4 people, 4 schools represented)

- **Inky** - De Anza, Specializes in VR Frontend and Backend Development
- **Susan** - Stanford, specializes in Hardware Camera Integration and ML/AI
- **Archita** - Cornell, specializes in Backend Development and ML/AI
- **Akaash** - Georgia Tech, specializes in Vision and Backend Development

  
![20250215_094915](https://github.com/user-attachments/assets/619972d8-a6f1-4e4a-87c1-d462a183149d)

# Next Steps

- Regularly watching when the user is consuming addictive substances, such as nicotine, alcohol, marijuana, etc, and giving a notification to say “that’s enough substance for today”. We plan to expand it to an overall live health monitoring assistant. 
- Integrate with technology such as Meta AR glasses, which is a much more natural item to wear on a daily basis.

# Challenges we ran into

The Meta Quest has privacy issues with live streaming. We are not allowed to live stream on the Meta Quest, and we would need to submit a petition to get our use-case approved. 

It is possible to get our livestream purpose approved, but the approval process takes a very long time and is too long for the duration of this hackathon. 

So, to demonstrate a proof of concept, we quickly pivoted to using a web-cam that can stream onto MetaQuest. The Webcam connects to our local computer for the server, and streams to the MetaQuest via RTSP protocol. The webcam is mounted on top of the Meta Quest, and we behave as if the Meta Quest itself is live-streaming data. 

# What we learned

A ton! Live Streaming a peripheral hardware webcam using RTSP protocol, programming VR and AR on the Meta Quest 2, and training YOLOv11 to detect when a person is eating food! Our pipeline is built ground up and novel—we figured it out along the way with little documentation to lean on!

# Built With

- **OpenAI API**: to retrieve nutrition information about food
- **NVIDIA Jetson Orin Nano**: to train the YOLOv11 model
- **Perplexity Sonar**: to display eating habits insights. 
- **Other Technologies**: Unity, React, Node.js, Flask, SQLAlchemy, YOLOv11, USDA Food API, hardware camera webcam 

# Side Note

In the future, we plan to integrate this application with Terra API as it is very easy to retrieve other health data from the user, such as daily calories burnt. We were looking forward to integrating with TerraAPI. 

# Try it Out!

- Insert a public github link. 
- Insert Youtube video link.
