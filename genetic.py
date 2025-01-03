#Inputs to the algorithm 

#Bird Velocity --> bird_velocity
#Difference between bird and gap(horizontal) --> bird_x - pipes[0][0].x
#Difference between bird and gap(vertical) --> bird_y - pipes[0][0].height

from torch import nn
import torch.nn.functional as F
import copy
import torch

population = 350    # Total Population

class network(nn.Module):
    def __init__(self, M):
        # M is the dimension of input feature
        super(network, self).__init__()
        self.layer1 = nn.Linear(M, 5)
        self.layer2 = nn.Linear(5, 5)
        self.out = nn.Linear(5,1)

    def forward(self,x):
        return F.sigmoid(self.out(self.layer2(self.layer1(x))))
    
def mutate_model(model, mutation_strength=0.1):
    # Clone the model to avoid altering the original
    new_model = copy.deepcopy(model)
    
    # Apply mutations to the weights and biases
    for param in new_model.parameters():
        if param.requires_grad:  # Only mutate trainable parameters
            noise = torch.randn_like(param) * mutation_strength
            param.data += noise  # Add random noise to parameters
    
    return new_model

# model = network(3)
# new_model = mutate_model(model)
# for name, param in model.named_parameters():
#     print(f"Parameter name: {name}, Shape: {param}")
   
# for name, param in new_model.named_parameters():
#     print(f"Parameter name: {name}, Shape: {param}")