import re
import numpy as np
import matplotlib.pyplot as plt

data = r'C:\Users\Elton\documents\github\nao_play\data.txt'
# thanks gpt!!!!! <3
pattern =r'[-+]?\d+(?:\.\d+)?(?:[eE][-+]?\d+)?'

with open(data, 'r') as file:
    count = 0
    data_list = []
    local_list = []
    for i, line in enumerate(file):
        if count < 3:

            numbers = re.findall(pattern,line)
            numbers = [float(number) for number in numbers]
            local_list.append(np.array(numbers))
            print(numbers)
        
        if count == 3:
            data_list.append(np.concatenate(local_list))
            local_list = []
        
        if count == 4:
            count = -1
            print()
        count += 1

data = np.vstack(data_list)
np.savetxt('formated_data.txt',data,delimiter=',')

rotX = data[:,[0,4,8]]
rotY = data[:,[1,5,9]]
rotZ = data[:,[2,6,10]]
pos = data[:,[3,7,11]]

min_val = min(np.min(rotX),np.min(rotY),np.min(rotZ),np.min(pos))
max_val = max(np.max(rotX),np.max(rotY),np.max(rotZ),np.min(pos))
print(min_val, max_val)


def graph_comp(comp, name):
    plt.plot(comp[:,0],label='1')
    plt.plot(comp[:,1],label='2')
    plt.plot(comp[:,2],label='3')
    plt.title(name)
    plt.xlabel('time')
    plt.ylim(min_val-1,max_val+1)
    plt.legend()

    plt.savefig(f'{name}.png')
    plt.clf()

graph_comp(rotX, 'wX component')
graph_comp(rotY, 'wY component')
graph_comp(rotZ, 'wZ component')
graph_comp(pos, 'pV component')