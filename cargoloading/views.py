from xml.etree.ElementInclude import include
from django.shortcuts import render, redirect
from django.forms import formset_factory
from .forms import generateForm, tableForm
import numpy as np
np.set_printoptions(suppress=True)

def index(request):
    return render(request, 'index.html', {})

def generate(request):
    if request.method == 'POST':
        form = generateForm(request.POST)
        if form.is_valid():
            request.session['num_box'] = request.POST['num_box']
            request.session['cargo_type'] = request.POST['cargo_type']
            request.session['capacity'] = request.POST['capacity']
            request.session['ini_rate'] = request.POST['ini_rate']
            box = form.cleaned_data['num_box']
            print(box)
            return redirect(table)         
    else:
        form = generateForm()

    context = {"form":form, }
    return render(request, 'generate.html', context)

description = []
height = []
length = []
width = []
weight = []
cbm = []
chargeable_weight = []
value = []
box = []

def table(request):
    box = request.session.get('num_box')
    type = request.session.get('cargo_type')
    capacity = request.session.get('capacity')
    rate = request.session.get('ini_rate')

    tableFormSet = formset_factory(tableForm,extra=int(box)-1, min_num=1, validate_min=True)
    
    if request.method == 'POST':
        formset = tableFormSet(request.POST)
        height.clear()
        description.clear()
        length.clear()
        width.clear()
        weight.clear()
        cbm.clear()
        chargeable_weight.clear()
        value.clear()
        
        if formset.is_valid():
            for d in formset:
                data = d.cleaned_data
                desc = data.get('description')
                h = data.get('height')
                l = data.get('length')
                wdth = data.get('width')
                wght = data.get('weight')
                hl = h * l #height_length
                prod = (hl * wdth) / 1000000 #prod
                c = prod * 333 #cbm_charge
                print(d.cleaned_data)
                
                try:
                    height.append(round(float(h)))
                    description.append(desc)
                    length.append(round(float(l)))
                    width.append(round(float(wdth)))
                    weight.append(int(wght))
                    cbm.append(round(c))
                except:
                    description.clear
                    formset = tableFormSet(request.POST)
            
            #charge_list
            for i in range(0,int(box)):
                if (weight[i] > cbm[i]):
                    chargeable_weight.append(weight[i])
                elif (cbm[i] > weight[i]):
                    chargeable_weight.append(cbm[i])
                elif (weight[i] == cbm[i]):
                    chargeable_weight.append(weight[i])

            #profi_list
            for i in range(0,int(box)):
                profit = chargeable_weight[i] * int(rate) 
                value.append(round(float(profit)))
                    
            return redirect(result)

        else:
            print(formset.errors)
        
    else:
        formset = tableFormSet()
    
    context = {
        "box":box, 
        "type":type,
        "capacity":capacity, 
        "rate":rate,
        'formset':formset,
    }

    return render(request, 'table.html', context)

#Optimal List
boxList = []
dscList = []
hghtList = []
lenList = []
wdthList = []
wghtList = []
cbmList = []
chrge_wghtList = []
valList = []

def result(request):
    capacity = request.session.get('capacity')
    boxes = request.session.get('num_box')
    volume = 666 if int(capacity) == 600 else 999 if int(capacity) == 1000 else 3330

   
    for i in range(int(boxes)+1):
        if i != 0:
            box.append(i)
    
    dynamic_Prog(weight, value, int(capacity), int(boxes), int(volume), cbm)
    print(boxList)
    table_list = zip(box,description,height,length,width,weight,cbm,chargeable_weight,value)
    final_list = zip(boxList,wghtList,valList,cbmList)
    total_cost = sum(valList)
    total_cbm = sum(cbmList)

    context = {
        'total_cbm':total_cbm,
        'total_cost':total_cost,
        'bl':boxList,
        'tl':table_list,
        'fl':final_list,
    }
    return render(request, 'result.html', context)

# Function for Dynamic Programming
# dynamic_Prog(weight, value, vehicle_capacity, num_box, vehicle_volume, cbm)
def dynamic_Prog(W, V, M, n, C, Z):

    optimal_set = np.array([[0, 0, 0, 0]])

    bin_Table = [[0 for x in range(M + 1)] for x in range(n + 1)]
    for i in range(n + 1):
        for j in range(M + 1):
            if i == 0 or j == 0:
                bin_Table[i][j] = 0
            elif j >= W[i-1]:
                bin_Table[i][j] = max(
                    V[i-1] + bin_Table[i-1][j-W[i-1]], bin_Table[i-1][j])
            else:
                bin_Table[i][j] = bin_Table[i-1][j]
    print("Max Profit: ", bin_Table[n][M])
    print("Maximum Capacity (Weight): ", M)
    print("Maximum Capacity (Volume): ", C)
    print("\nSelected Packs: ")
    print("Box No.\tWeight\tProfit/Value\tCBM")
    while (n != 0):
        if (bin_Table[n][M] != bin_Table[n-1][M]):
            print(n, "\t", W[n-1], "\t", V[n-1], "\t\t", Z[n-1])
            row = np.array([n, W[n-1],  V[n-1], Z[n-1]])
            optimal_set = np.append(optimal_set, [row], axis=0)

            M = M - W[n-1]
        n -= 1

    # DESCENDING ORDER FOR PROFIT/VALUE
    optimal_set = optimal_set[optimal_set[:, 2].argsort()[::-1]]

    print("\n\n******INITIAL OPTIMAL SOLUTION (Weight Constraint Only)******")
    print("Box No.\tWeight\tProfit/Value\tCBM")
    optimal_set = np.delete(optimal_set, -1, axis=0)
    print(optimal_set)

    print('\n***CBM SUM***')
    cbmSum = sum(optimal_set[:, -1])
    print("{:.2f}".format(cbmSum))

    # INITIAL optimal_set VALUES (weight constraint only)
    numOfBoxes_init = int(len(optimal_set[:, 0]))
    numbox_list = optimal_set[:, 0] # BAGONG LIST

    weightList_init = optimal_set[:, 1]

    profitList_init = optimal_set[:, 2]  

    a = optimal_set[:, 3]
    a1 = a.tolist()
    volumeList_init = list(map(round, a1)) 

    # BKP DP ALGO - APPLY TO INITIAL optimal_set VALUES
    Final_optimal_set = np.array([[0, 0, 0, 0]])


    volume_Table = [[0 for x in range(C + 1)]
                    for x in range(numOfBoxes_init + 1)]
    for i in range(numOfBoxes_init + 1):
        for j in range(C + 1):
            if i == 0 or j == 0:
                volume_Table[i][j] = 0
            elif j >= volumeList_init[i-1]:
                volume_Table[i][j] = max(
                    profitList_init[i-1] + volume_Table[i-1][j-volumeList_init[i-1]], volume_Table[i-1][j])
            else:
                volume_Table[i][j] = volume_Table[i-1][j]

    # print optimal volume
    while (numOfBoxes_init != 0):
        if (volume_Table[numOfBoxes_init][C] != volume_Table[numOfBoxes_init-1][C]):
            row = np.array([numbox_list[numOfBoxes_init-1],  weightList_init[numOfBoxes_init-1],
                           profitList_init[numOfBoxes_init-1], volumeList_init[numOfBoxes_init-1]])
            Final_optimal_set = np.append(Final_optimal_set, [row], axis=0)

            C = C - volumeList_init[numOfBoxes_init-1]
        numOfBoxes_init -= 1
        #BAGONG WAY PAG-KAAPPEND: numbox_list[numOfBoxes_init-1]

    # DESCENDING ORDER FOR PROFIT/VALUE
    
    Final_optimal_set = Final_optimal_set[Final_optimal_set[:, 2].argsort()[
        ::-1]]

    print("\n\n******FINAL OPTIMAL SOLUTION (Weight Constraint and Volume Constraint)******")
    print("Box No.\tWeight\tProfit/Value\tCBM")
    Final_optimal_set = np.delete(Final_optimal_set, -1, axis=0)
    print(Final_optimal_set)
    boxList.clear()
    dscList.clear()
    hghtList.clear()
    lenList.clear()
    wdthList.clear()
    wghtList.clear()
    cbmList.clear()
    chrge_wghtList.clear()
    valList.clear()

    for i in Final_optimal_set:
        boxList.append(i[0])
        wghtList.append(i[1])
        valList.append(i[2])
        cbmList.append(i[3]) 

    
    

    
          

