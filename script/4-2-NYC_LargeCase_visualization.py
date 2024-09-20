import numpy as np
import time
import sys
import math
import random
import networkx as nx
import matplotlib.pyplot as plt
import csv

def distance_sphere(row,row1):
    (lat1,lng1,lat2,lng2)=(row[0],row[1],row1[0],row1[1])
    degrees_to_radians = math.pi/180.0
    # phi = 90 - latitude
    phi1 = (90.0 - lat1)*degrees_to_radians
    phi2 = (90.0 - lat2)*degrees_to_radians
    # theta = longitude
    theta1 = lng1*degrees_to_radians
    theta2 = lng2*degrees_to_radians
    cos = (math.sin(phi1)*math.sin(phi2)*math.cos(theta1 - theta2) +
           math.cos(phi1)*math.cos(phi2))
    if cos>=1:
        arc=0
    else:
        arc = math.acos( cos )
    return arc*3960 #return mile


# Euclidean distance between two points

def distance(points, i, j):
    dx = points[i][0] - points[j][0]
    dy = points[i][1] - points[j][1]
    return math.sqrt(dx*dx + dy*dy)



problem_size=[]
time_cost=[]
# Parse argument
#
# if len(sys.argv) < 2:
#     print('Usage: tsp.py npoints')
#     exit(1)
# n = int(sys.argv[1])

# Create n random points
c=1
G=nx.Graph()
file_source='../data/4-LargeCase/new615_2019_varying_penalty_balanced_assign.csv'
color_list=['aqua','aquamarine','black','blue','brown','chartreuse','chocolate','coral','crimson','darkblue','darkgreen','fuchsia','gold','green','grey','indigo','khaki','lavender','lightgreen','lime','magenta','maroon','navy','olive','orange','orchid','plum','purple','red','salmon','teal','violet','yellowgreen','orangered','sienna','maroon','aqua','aquamarine','black','blue','brown','chartreuse','chocolate','coral','crimson','darkblue','darkgreen','fuchsia','gold','green','grey','indigo','khaki','lavender','lightgreen','lime','magenta','maroon','navy','olive','orange','orchid','plum','purple','red','salmon','teal','violet','yellowgreen','orangered','sienna','maroon']
station=np.loadtxt(file_source,delimiter=',',skiprows=1)
added=[]
visiting_frequency={}
for row in station:
    i=row[0]
    if i not in added:
        visiting_frequency[i]=0
        G.add_node(i)
        G.nodes[i]['id']=i
        G.nodes[i]['lat']=row[3]
        G.nodes[i]['lng']=row[4]
        G.nodes[i]['target']=row[2]
        G.nodes[i]['class']=row[c]
        G.nodes[i]['next']=[]
    else:
        G.nodes[i]['target']=G.nodes[i]['target']+row[2]

print('Total number of stations: %g' %len(G.nodes()))


print('##########')
unique_class=np.unique(station[:,c])
if -1 in unique_class:
    class_num=len(unique_class)-1
else:
    class_num=len(unique_class)

fig = plt.figure(figsize=(6, 10), dpi=900)
print(class_num, 'number of classes')
classes={}
complete_class=[]
for row in unique_class:
    classes[row]=[]

for row in G.nodes():
    # if G.nodes[row]['class']!=-10 and G.nodes[row]['target']!=0:
    classes[G.nodes[row]['class']].append(G.nodes[row])
    complete_class.append(row)
jj=1
ff=0

balanced=[]

balan=0
outl=0
split=0

for row in classes:
    if row !=-1:
        print('current cluster ID is: %d' %row)
        i=0
        points={}
        target={}
        available={}
        dock={}
        status={}
        station_index={}
        for rows in station:
            if rows[c]==row:
                station_index[i]=rows[0]
                points[i]=([rows[3],rows[4]])
                target[i]=rows[2]
                available[i]=rows[5]
                dock[i]=rows[6]
                status[i]=rows[7]
                i+=1
        n=len(points)
        # start=time.clock()

        ff=0
        lamb=0.5
        veh_n=1
        mm=1000000

        depots=[[40.7292,-74.0113],[40.750739,-73.9921],[40.716629, -73.982616]]
        ll=np.average([points[kk][0] for kk in points])
        lonlong=np.average([points[kk][1] for kk in points])
        distance_list=[distance_sphere((ll,lonlong),(depots[kk][0],depots[kk][1])) for kk in range(3)]
        inde=distance_list.index(min(distance_list))
        depot=depots[inde]
        print(row,n,inde)
        n = len(points)

        points[-1]=depot
        points[-2]=depot

        # m = Model()
        # Create variables
        y={}
        vars = {}
        U={}
        s={}
        U[-1]=0
        U[-2]=0

        # selected = [(v,i,j) for i in range(-2,n) for j in range(-2,n) for v in range(veh_n) if i!=j and solution[v,i,j] > 0.5]
        selected=[]
        ffile=open('../results/LargeCase/Log//'+str(row)+'.csv','r')
        readder=csv.reader(ffile)
        selected1=[]
        for row in readder:
            selected.append((int(row[0]),int(row[1]),int(row[2])))
            if int(row[1])>=0:
                selected1.append(int(row[1]))
                visiting_frequency[station_index[int(row[1])]]=visiting_frequency[station_index[int(row[1])]]+1
        # for v,i,j in selected:
        #     writer.writerow([v,i,j,solution[v,i,j]])
        ffile.close()

            # print subtour[i][row][0],points[row][1]
        # print(jj)
        plt.scatter(depot[1],depot[0],s=70,c=color_list[jj],marker='*')

        for rows in selected:
            if rows[1]==-1:
                plt.arrow(points[rows[1]][1],points[rows[1]][0],0.8*(points[rows[2]][1]-points[rows[1]][1]),0.8*(points[rows[2]][0]-points[rows[1]][0]),head_width=0.001,head_length=0.001,width=0.0002,fc='k',ec='k',zorder=10)
            plt.plot([points[rows[1]][1],points[rows[2]][1]],[points[rows[1]][0],points[rows[2]][0]],color=color_list[jj],linewidth=2)
        for rows in points:
            if rows not in selected1:
                plt.scatter(points[rows][1],points[rows][0],c='black',marker='x')
            else:
                plt.scatter(points[rows][1], points[rows][0], s=50, c=color_list[jj], marker='o')
            # print subtour[i][row][0],points[row][1]
        # print('Optimal cost: %g' % m.objVal)
        print('')

        for rowss in points:
            if rowss==-1 or rowss==-2:
                plt.scatter(points[rowss][1],points[rowss][0],s=50,c=color_list[0],marker='s')
            # else:
            #     plt.scatter(points[rowss][1],points[rowss][0],s=50,c=color_list[jj],marker='o')


        jj += 1
    for rows in station:
        # if rows[1]==0:
        #     plt.scatter(float(rows[4]),float(rows[3]),s=50,c='black',marker='x')
        if rows[2]==0:
            plt.scatter(float(rows[4]),float(rows[3]),s=50,c='black',marker='s')

    for rows in station:
        if rows[7] == 1:
            plt.scatter(float(rows[4]),float(rows[3]),s=50,c='black',marker='D')
            split+=1


print(balan,outl,split)

plt.xlabel("Longitude",fontsize=12)
plt.ylabel("Latitude",fontsize=12)
# plt.xticks([-74.03,-74.01,-73.99,-73.97,-73.92])
plt.title("New York City Station Map",fontsize=14)
plt.ticklabel_format(useOffset=False)
plt.xlim(-74.02,-73.92)
plt.ylim(40.655,40.81)
# plt.xticks(fontsize=12)
# plt.yticks(fontsize=12)
start_marker=plt.scatter([],[],marker='*',s=70,facecolors='none',edgecolors='black',label='Depot')
optimized_stations=plt.scatter([],[],marker='o',facecolors='none',s=50,edgecolors='black',label='Optimized Station')
splitted_station=plt.scatter([],[],marker='D',facecolors='none',s=50,edgecolors='black',label='Split Station')
outlier=plt.scatter([],[],marker='x',s=50,facecolors='black',edgecolors='black',label='Outlier Station')
balanced=plt.scatter([],[],marker='s',s=50,facecolors='none',edgecolors='black',label='Balanced Station')
plt.legend(handles=[start_marker,optimized_stations,splitted_station,outlier,balanced],bbox_to_anchor=(0.965, 0.155))
fig.tight_layout()
# plt.show()
plt.savefig('../results/LargeCase/day_1_1_12clusters.png',format='png',figsize=(2,6),dpi=900)

for row in visiting_frequency:
    print(row,visiting_frequency[row])
