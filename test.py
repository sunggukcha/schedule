import torch
from models import dnn
model = dnn.FC10(lambda x:x)
x = torch.tensor([ 1.0, 2.0, 3.0, 4.0, 5.0, 6.0, 7.0, 8.0, 9.0 ])
model(x)
