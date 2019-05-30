import numpy as np
import torch
import torch.nn as nn
import torch.optim as optim
import torch.nn.functional as F
import torchvision.transforms as T

class Residual(nn.Module):
    expansion = 4
    def __init__(self, planes, Norm):
        super(Residual, self).__init__()
        self.fc1    = nn.Linear(planes, planes)
        self.nm1    = Norm(planes)
        self.fc2    = nn.Linear(planes, planes)
        self.nm2    = Norm(planes)
        self.fc3    = nn.Linear(planes, planes*4)
        self.nm3    = Norm(planes*4)
        self.relu   = nn.ReLU(inplace=True)
    def forward(self, x):
#        residual = x
#        print("x", x.shape)
        out = self.fc1(x)
#        print("fc1", out.shape)
#        out = self.nm1(out)
#        print("nm1", out.shape)
        out = self.relu(out)
        out = self.fc2(out)
#        out = self.nm2(out)
        out = self.relu(out)
        out = self.fc3(out)
#        out = self.nm3(out)
#        out += residual
        out = self.relu(out)
        return out

class DNN(nn.Module):
    '''
        Given
        Release time(RT),
        Deadline(DD),
        Priority(PR),
        Processing time(PT),
        Avg. Release time(ART),
        Avg. Deadline(ADD),
        Avg. Priority(APR),
        Avg. Processing time(APT),
        Current time(CT)
        Using fully connected acrhitecture as MNIST, it defines a state.
    '''
    def __init__(self, block, Norm):
        super(DNN, self).__init__()
        self.R1 = block(1*9, Norm)
        self.R2 = block(4*9, Norm)
        self.R3 = block(16*9, Norm)
        self.last = F.Linear(576, 1)

    def forward(self, x):
        '''
            x: n * 9 shaped tensor
        '''
        x = self.R1(x)
        x = self.R2(x)
        x = self.R3(x)
        print(x.shape)
        return x

def FC10(Norm):
    model = DNN(Residual, Norm)
    return model
