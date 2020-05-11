# Image-Captioning-for-Chest-X-ray-Images
I have made a Deep Learning model to generate Radiology Reports from a given Chest X-Ray Image.

Project ID: PW20PRD01

Project Type : Research Project

Project Title: Image Captioning for Chest X-Ray images

Team Members: Krishna Khurana(01FB16ECS482) , Manmath Sahoo(01FB16ECS488) , Shrey Jain(01FB16ECS490)

Project Guide: Prof. P. Ramadevi

Project Abstract: For medical images, radiologists have to write a description completely for the medical reports. Understanding these reports is a complex and tedious task which requires a lot of experience and time. Diagnosis done by inexperienced radiologists in rural areas can sometimes be error-prone and fatal. To have a less number of bugs and for saving the radiologist’s time we need a system which is computer-aided for the generation of medical reports, which can further be used by radiologists to refer and diagnose better. So we propose an Encoder-Decoder architecture to annotate medical images.The input to the encoder is the medical image which we have to caption.The encoder consist of the Inception V3 model, in which we have removed the last layer of the model to encode the X-ray image.The encoded image from the CNN layer is used as the input to the RNN model, which consist of the Attention mechanism.The decoder will provide us with the caption for the images. We use various evaluation metrics to compare our model with other base models.



Code Execution : 

A.) For downloading dataset

Our project consists of two python files (get_iu_xray.py , xray.py). Get_iu_xray.py is the python code to scrape images from Indiana University Open-I search engine. So we first execute this python code first.

Command-1: python get_iu_xray.py  




B.) For training the model


Now we have to execute the python code xray.py which trains our model on the images downloaded from the above python script.

Command-2: python xray.py



C.) For demo of our project

If anyone wants to just use the model and see a demo of our model, 

Command-3: python demo.py

It has a dictionary with the results of our model for a validation set of images saved in a dictionary and we serve it with the help of flask. 


D.) For evaluation of our project

If anyone wants to just see the evaluation score of our model , there is a python notebook file with name Evaluation_Metrics(recommended to use in Google Colab) or the python file

Command-3: python Evaluation_Metrics.py

A file results.txt is required to run the evaluation code. The file is present along with other items in the folder.
