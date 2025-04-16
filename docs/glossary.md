# Glossary

### **AI Model**
A trained set of values that can be input into an AI model Architecture to classify a provided image into the correct class. It results from training an AI and is unique to the values provided during the training phase.

### **AI Model Architecture**
The structural design of an artificial intelligence model. It is the blueprint that defines how data flows through the model. For most cases, this will be YOLOv5.

### **Dataset**
The images and annotations that will be used to train the AI model.

### **Epoch**
One complete pass through the entire training dataset during the train AI process. When training, it is important to have a good-sized epoch to ensure the AI learns effectively from the provided training data.

### **Box Loss**
A measure of how accurately a model predicts the bounding box around an object. It is calculated from the difference between the predicted box and the ground truth (the box provided in the training data).

### **CLS Loss**
Classification loss. The loss is calculated based on how well the model classifies an object into the correct category.

### **IoU**
Intersection over Union. A measure of how well the predicted bounding box overlaps with the ground truth (the box provided during training.) An IoU of 1 is a perfect overlap, and zero means there is no overlap.

### **Mean Average Precision IoU**
Precision and recall are calculated for a range of IoU thresholds. These values are then plotted on a graph with precision on the Y-axis and recall on the X-axis. This allows comparison between having a high precision and a high recall. Average precision is then derived as the area under the precision-recall curve.

### **Mean Average Precision IoU (0.5-0.95)**
The same as mean average precision IoU, but with different threshold values.

### **Precision**
Precision measures how well a model can make accurate positive predictions. It measures how many positive instances are correct. Precision is a valuable tool when the cost of false positives is also high.

### **Recall**
The recall statistic focuses on identifying results that contain a defect but are labelled correctly and those that contain a defect but were incorrectly labelled as not containing one. It emphasises the model’s ability to identify positive cases and penalises the model for failing to detect positives.

### **Overfitting**
Overfitting is a concern in developing AI models. It occurs when a model performs well with its training and test data but fails to generalise unseen data. This can happen when the model learns incorrect features, such as background noise or image rotation, instead of actual relevant features.