#!/usr/bin/env python
# coding: utf-8

# In[7]:


import torch
import torch.nn as nn
from torchvision import datasets, models, transforms
import os


# In[8]:


# Load the test data.
data_transforms = {
    'test': transforms.Compose([
        transforms.Resize([224, 224]),
        transforms.ToTensor()
    ])
}

data_dir = 'D:\data (augmented, 4 classes, tif)'
image_datasets = {x: datasets.ImageFolder(os.path.join(data_dir, x),
                                          data_transforms[x])
                  for x in ['test']}

batch_size = 128
dataloaders = {x: torch.utils.data.DataLoader(image_datasets[x], batch_size=batch_size,
                                             shuffle=True, num_workers=4)
              for x in ['test']}
dataset_sizes = {x: len(image_datasets[x]) for x in ['test']}
class_names = image_datasets['test'].classes

device = torch.device("cuda" if torch.cuda.is_available() else "cpu")


# In[9]:


# Load the saved model state_dict for inference (done later to keep len(class_names) after the dataloader dynamic).
model_ft = models.alexnet(pretrained=True)
model_ft.classifier[6] = nn.Linear(4096, len(class_names))
model_ft.classifier.add_module("7", nn.Dropout())           # Comment this out if the AlexNet model did not include the last dropout layer.

PATH = "D:\Models\model_20190411-093358.pth"
model_ft.load_state_dict(torch.load(PATH))

model_ft = model_ft.to(device)


# In[10]:


was_training = model_ft.training

model_ft.eval()

all_labels = []
all_preds = []
    
with torch.no_grad():
    for inputs, labels in dataloaders['test']:    # The labels will correspond to the alphabetical order of the class names (https://discuss.pytorch.org/t/how-to-get-the-class-names-to-class-label-mapping/470).
        inputs = inputs.to(device)
        labels = labels.to(device)
        labels_list = labels.tolist()
        all_labels.extend(labels_list)
            
        outputs = model_ft(inputs)
        _, preds = torch.max(outputs, 1)
        preds_list = preds.tolist()
        all_preds.extend(preds_list)
            
    model_ft.train(mode=was_training)


# In[11]:


from pandas_ml import ConfusionMatrix
cm = ConfusionMatrix(all_labels, all_preds)
cm.print_stats()

