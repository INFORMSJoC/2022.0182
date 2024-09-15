import numpy as np
import time
import sys
import math
import random
from gurobipy import *
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

# Callback - use lazy constraints to eliminate sub-tours
def subtourelim(model, where):
    if where == GRB.Callback.MIPSOL:
        selected_length=[0 for v in range(veh_n)]
        selected = [[] for v in range(veh_n)]
        # make a list of edges selected in the solution

        for v in range(veh_n):
            selected[v] += [(i,j) for i in range(-2,n) for j in range(-2,n) if i!=j and model.cbGetSolution(model._vars[v,i,j]) > 0.5]

        nodes=[[] for v in range(veh_n)]
        for v in range(veh_n):
            for (i,j) in selected[v]:
                if i not in nodes[v]:
                    nodes[v].append(i)
                if j not in nodes[v]:
                    nodes[v].append(j)
        for v in range(veh_n):
            selected_length[v]=len(nodes[v])

            # find the shortest cycle in the selected edge list
        for v in range(veh_n):
            if len(selected[v])>0:

                tours = subtour(selected[v],selected_length[v])

                for tour in tours:
                    if -1 not in tour:
                        if len(tour) < selected_length[v]:
                            print(v,'I am adding SEC######################################################')
                            # add a subtour elimination constraint
                            expr = 0
                            for i in range(len(tour)-1):
                                expr += model._vars[v,tour[i], tour[i+1]]
                            expr += model._vars[v,tour[-1], tour[0]]
                                    # print 'expr',expr
                            model.cbLazy(expr <= len(tour)-1)


# Euclidean distance between two points

def distance(points, i, j):
    dx = points[i][0] - points[j][0]
    dy = points[i][1] - points[j][1]
    return math.sqrt(dx*dx + dy*dy)


# Given a list of edges, finds the shortest subtour

def subtour(edges,n1):
    # print 'n1',n1
    visited = {}
    for i,j in edges:
        if i not in visited:
            visited[i]=False
        if j not in visited:
            visited[j]=False
    cycles = []
    lengths = []
    selected = {}
    for x, y in edges:
        selected[x]=y
    # print 'subtour',selected
    while True:
        if visited[-1]==False:
            current=-1
        else:
            for nod in visited:
                if visited[nod]==False:
                    current=nod
                    break

        thiscycle = [current]
        while True:
            visited[current] = True
            neighbors = [selected[current]]
            # print 'neighbors',current,neighbors
            if visited[neighbors[0]] == True:
                break
            current = neighbors[0]
            thiscycle.append(current)

        cycles.append(thiscycle)
        lengths.append(len(thiscycle))
        if sum(lengths) == n1:
            break

    if len(cycles)>1:
        return cycles
    else:
        return cycles

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
overal_file=open('../results/LargeCase/overall_complete_server.csv','a',newline='')
writeroverall=csv.writer(overal_file)
writeroverall.writerow(['class', 'Number of Stations', 'Number of Visited Stations','Total Targets', 'Rebalanced Bikes' , 'Demand Loss', 'Total Distance' , 'CT','obj'])

file_source='../data/4-LargeCase/new615_2019_varying_penalty_balanced_assign.csv'
color_list=['black','blue','red','green','gray','lime','purple','pink','orange','plum','tomato','silver','brown','springgreen','yellowgreen']
station=np.loadtxt(file_source,delimiter=',',skiprows=1)
for row in station:
    i=row[1]
    G.add_node(i)
    G.nodes[i]['id']=i
    G.nodes[i]['lat']=row[3]
    G.nodes[i]['lng']=row[4]
    G.nodes[i]['target']=row[2]
    G.nodes[i]['class']=row[c]
    G.nodes[i]['next']=[]
    G.nodes[i]['loss']=row[8]


unique_class=np.unique(station[:,c])
if -1 in unique_class:
    class_num=len(unique_class)-1
else:
    class_num=len(unique_class)


print(class_num, 'number of classes')
classes={}
complete_class=[]
for row in unique_class:
    if row!=-1:
        classes[row]=[]

for row in G.nodes():
    if G.nodes[row]['class']!=-1 and G.nodes[row]['target']!=0:
        classes[G.nodes[row]['class']].append(G.nodes[row])
        complete_class.append(row)
jj=1
ff=0

# start_time=time.clock()
balanced=[]
optimized=[]
# optimized=[0,1,2,4,6,8,12,14,26,27,399,559,560,797,798,1260,1385,1757,1758,1759,2095,2096,2228,2229,2416,2417,2620,2686,2725,2867,3027,3028]
for row in classes:
    # if row in [1]:
    # if row !=-1 and row not in optimized:
    # if row==0:
    optimized.append(row)
    claa=row
    ffile = open('../results/LargeCase/Log/'+str(row) + '.csv','w', newline='')
    writer = csv.writer(ffile)
    print('current cluster ID is: %d' %row)
    i=0
    points={}
    target={}
    available={}
    dock={}
    unitloss={}
    for rows in station:
        if rows[c]==row:
            points[i]=([rows[3],rows[4]])
            target[i]=rows[2]
            available[i]=rows[5]
            dock[i]=rows[6]
            unitloss[i]=rows[8]

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
    n = len(points)
    print(len(target), target)
    target[-1]=0
    target[-2]=0
    points[-1]=depot
    points[-2]=depot
    m = Model()
    # Create variables
    y={}
    vars = {}
    U={}
    s={}
    U[-1]=0
    U[-2]=0
    for i in range(-2,n):
        for v in range(veh_n):
            y[v,i] = m.addVar(obj=0, vtype=GRB.CONTINUOUS, name="Y"+str(v)+str(i))
            U[i]= m.addVar(obj=0,vtype=GRB.CONTINUOUS,name="U"+str(i))
            s[v,i]=m.addVar(obj=0,vtype=GRB.CONTINUOUS,lb=-26.0,name="S"+str(v)+str(i))
            for j in range(-2,n):
                vars[v,i,j] = m.addVar(obj=0, vtype=GRB.BINARY,
                                             name='e'+str(i)+'_'+str(j))

    m.update()

    for v in range(v):
        for i in range(-2,n):
            m.addConstr(vars[v,i,i]==0)


    expr=LinExpr()
    for v in range(veh_n):
        for i in range(-2,n):
            for j in range(-2,n):
                if i!=j:
                    expr.addTerms(distance_sphere(points[i], points[j]),vars[v,i,j])

    for i in range(n):
        expr.addTerms(lamb*unitloss[i],U[i])

    m.setObjective(expr,GRB.MINIMIZE)

    m.update()

    ###constrain U[i] (4)(5)
    for i in range(n):
        m.addConstr(quicksum(s[v,i] for v in range(veh_n))-target[i], GRB.LESS_EQUAL,U[i])
        m.addConstr(target[i]-quicksum(s[v,i] for v in range(veh_n)),GRB.LESS_EQUAL,U[i])

    ###constrain flow, (6),(7)
    for v in range(veh_n):
        for i in range(-2,n):
            for j in range(-2,n):
                # if i!=j:
                m.addConstr(y[v,i]+s[v,j]-y[v,j]+(1-vars[v,i,j])*mm,GRB.GREATER_EQUAL,0)
                m.addConstr(y[v,i]+s[v,j]-y[v,j]-(1-vars[v,i,j])*mm,GRB.LESS_EQUAL,0)

    for v in range(veh_n):
        for i in range(n):
            m.addConstr(s[v, i] + mm * quicksum(vars[v, i, j] for j in range(n)), GRB.GREATER_EQUAL, 0)
            m.addConstr(s[v, i] - mm * quicksum(vars[v, i, j] for j in range(n)), GRB.LESS_EQUAL, 0)

    ###constrain vehicle capacity (8)
    for i in range(-2,n):
        for v in range(veh_n):
            m.addConstr(y[v,i],GRB.LESS_EQUAL,25)
            m.addConstr(y[v,i],GRB.GREATER_EQUAL,0)

    ###constrain continuity (9)
    for i in range(n):
        m.addConstr(quicksum(vars[v,i,j] for v in range(veh_n) for j in range(-2,n) if i!=j),GRB.LESS_EQUAL,1)
        m.addConstr(quicksum(vars[v,j,i] for v in range(veh_n) for j in range(-2,n) if i != j),GRB.LESS_EQUAL,1)
    ###constrain 1 visit (10)
    # for j in range(n):
    #     m.addConstr(quicksum(vars[v,i,j] for v in range(veh_n) for i in range(-2,n))==1)

    ###constrain Inventory (11)
    for i in range(n):
        for v in range(veh_n):
            m.addConstr(s[v,i], GRB.LESS_EQUAL, available[i])
            m.addConstr(s[v,i],GRB.GREATER_EQUAL,(available[i]-dock[i]))


    for v in range(veh_n):
        for i in range(n):
            m.addConstr(quicksum(vars[v,i,j] for j in range(-2,n) if j!=i and j!=-1)==quicksum(vars[v,j,i] for j in range(-2,n) if j!=i))

    for v in range(veh_n):
        m.addConstr(quicksum(vars[v,-1,j] for j in range(n))==1)
        m.addConstr(quicksum(vars[v,j,-2] for j in range(n))==1)
        # m.addConstr(quicksum(vars[v,-2,j] for j in range(n))==0)
        m.addConstr(vars[v,-2,-1]==1)

    # m.addConstr(quicksum(vars[0,i,j] for i in range(-2,n) for j in range(-2,n) if i!=j)==7)
    ff+=1
    m.update()


    # Optimize model

    m._vars = vars
    m.params.LazyConstraints = 1
    m.optimize(subtourelim)
    # end=time.clock()
    solution = m.getAttr('x', vars)
    # time_cost.append(end-start)
    problem_size.append(n)
    selected = [(v,i,j) for i in range(-2,n) for j in range(-2,n) for v in range(veh_n) if i!=j and solution[v,i,j] > 0.5]

    for v,i,j in selected:
        writer.writerow([v,i,j,solution[v,i,j]])
    ffile.close()

    fig = plt.figure(figsize=(6, 10), dpi=900)
        # print subtour[i][row][0],points[row][1]
    plt.scatter(depot[1],depot[0],s=70,c=color_list[3],marker='*')

    for rows in selected:
        if rows[1]==-1:
            plt.arrow(points[rows[1]][1],points[rows[1]][0],0.8*(points[rows[2]][1]-points[rows[1]][1]),0.8*(points[rows[2]][0]-points[rows[1]][0]),head_width=0.001,head_length=0.001,width=0.0002,fc='k',ec='k',zorder=10)
        plt.plot([points[rows[1]][1],points[rows[2]][1]],[points[rows[1]][0],points[rows[2]][0]],color=color_list[2],linewidth=2)

        # print subtour[i][row][0],points[row][1]
    print('Optimal cost: %g' % m.objVal)
    print('')

    for rowss in points:
        if rowss==-1 or rowss==-2:
            plt.scatter(points[rowss][1],points[rowss][0],s=50,c=color_list[0],marker='s')
        else:
            plt.scatter(points[rowss][1],points[rowss][0],s=50,c=color_list[1],marker='o')
    jj += 1

    plt.xlabel("Longitude")
    plt.ylabel("Latitude")
    # plt.xticks([-74.03,-74.01,-73.99,-73.97,-73.92])
    plt.title("Inner Cluster Optimal Rebalancing Route")
    plt.ticklabel_format(useOffset=False)
    plt.xlim(-74.02,-73.92)
    plt.ylim(40.66,40.81)
    start_marker=plt.scatter([],[],marker='*',s=70,facecolors='none',edgecolors='black',label='Depot')
    optimized_stations=plt.scatter([],[],marker='o',facecolors='none',s=50,edgecolors='black',label='Optimized Station')
    splitted_station=plt.scatter([],[],marker='D',facecolors='none',s=50,edgecolors='black',label='Split Station')
    outlier=plt.scatter([],[],marker='x',s=50,facecolors='black',edgecolors='black',label='Outlier Station')
    balanced=plt.scatter([],[],marker='s',s=50,facecolors='none',edgecolors='black',label='Balanced Station')
    plt.legend(handles=[start_marker,optimized_stations,splitted_station,outlier,balanced],bbox_to_anchor=(0.97, 0.14))

    total_dis=0
    for v in range(veh_n):
        for i in range(-2,n):
            for j in range(-2,n):
                if i!=j:
                    total_dis=total_dis+distance_sphere(points[i], points[j])*vars[v,i,j].x

    plt.title(str(n)+'\n'+str(sum([abs(target[i]) for i in range(n)]))+'\n'+str(sum([lamb*unitloss[i]*U[i].x for i in range(n)]))+'\n'+str(total_dis)+'\n'+str(m.Runtime)+'\n'+str(m.objVal))
    # plt.show()
    plt.savefig('../results/LargeCase/Figure//'+str(claa)+'.png',format='png',figsize=(2,6),dpi=900)
    plt.clf()
    for i in range(n):
        print(s[v,i].x)
    writeroverall.writerow([claa,n,sum([1 for i in range(-2,n) for j in range(-2,n) if solution[v,i,j]>0.5])-2,sum([abs(target[i]) for i in range(n)]),sum([abs(target[i]) for i in range(n)])-sum([U[i].x for i in range(n)]),sum([unitloss[i]*U[i].x for i in range(n)]),total_dis,m.Runtime,m.objVal])
