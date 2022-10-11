import csv, io
from datetime import datetime, timedelta
from .encrypt_util import *
from django.shortcuts import render, redirect
from django.conf import settings
from django.http import HttpResponse
from django.forms import formset_factory
from .forms import generateForm, uploadCSV, cargoForm
from .models import Cargo, cargoList
import numpy as np
np.set_printoptions(suppress=True)

def index(request):
    x = datetime.utcnow()
    print("Time now:",x)
    cargo = Cargo.objects.filter(creation_time__lte=datetime.utcnow()-timedelta(minutes=30))
    for i in cargo:
        print(i.creation_time,"is deleted!")
        i.delete()
        cl = cargoList.objects.filter(cargo=i.id)
        cl.delete()
    return render(request, 'index.html', {})

def generate(request):
    error_message = " "

    x = datetime.utcnow()
    print("Time now:",x)
    cargo = Cargo.objects.filter(creation_time__lte=datetime.utcnow()-timedelta(minutes=30))
    for i in cargo:
        print(i.creation_time,"is deleted!")
        i.delete()
        cl = cargoList.objects.filter(cargo=i.id)
        cl.delete()

    if request.method == 'POST':
        form = generateForm(request.POST)
        csvform = uploadCSV(request.POST, request.FILES)
        
        if form.is_valid():
            d = form.cleaned_data
            boxes = d.get('num_box')

            cargo = Cargo(
                num_box = d.get('num_box'), 
                capacity = d.get('capacity'),
                ini_rate = d.get('ini_rate'),
            )

            cargo.save()

            id = encrypt(cargo.id)
            return redirect(table, pk=id)

        if csvform.is_valid():

            #Initial List
            box = []
            description = []
            height = []
            length = []
            width = []
            weight = []
            cbm = []
            chargeable_weight = []
            value = [] 
            i = 0
            rate = csvform.cleaned_data['ini_rate']

            file = request.FILES['csvFile']
            data_set = file.read().decode('utf-8')
            data = io.StringIO(data_set)

            try:
                for c in csv.reader(data):
                    if len(c) == 5:
                        if c[0].lower() == "description" and c[1].lower() == "height" and c[2].lower() == "length" and c[3].lower() == "width" and c[4].lower() == "weight":
                            break
                        else:
                            error_message = "Please follow the sample format!"
                            raise ValueError
                    else:
                        error_message = "Unnecessary field is detected!"
                        raise ValueError

                for d in csv.reader(data):
                    i = i + 1
                    if i > 500:
                        error_message = "You have exceed the limit of 500 items!"
                        box = []
                        description = []
                        height = []
                        length = []
                        width = []
                        weight = []
                        cbm = []
                        chargeable_weight = []
                        value = [] 
                        raise ValueError

                    if len(d) != 5:
                        error_message = "Unnecessary field is detected!"
                        raise ValueError

                    description.append(d[0])
                    if type(d[1]) == " " or d[2] == " " or d[3] == " " or d[4] == " ":
                        error_message = "Missing data in required fields!"
                        raise ValueError

                    try:
                        h = float(d[1])
                        l = float(d[2])
                        wdth = float(d[3])
                        wght = float(d[4])
                    except:
                        error_message = "Invalid data!"
                        raise ValueError

                    hl = h * l #height_length
                    prod = (hl * wdth) / 1000000 #prod
                    c = float(prod) * 333 #cbm_charge

                    height.append(int(h))
                    length.append(int(l))
                    width.append(int(wdth))
                    weight.append(int(wght))
                    cbm.append(int(c))
                    
                boxes = len(cbm)

                #add box number
                for i in range(int(boxes)+1):
                    if i != 0:
                        box.append(i)

                #charge_list
                for i in range(0,int(boxes)):
                    if (weight[i] > cbm[i]):
                        chargeable_weight.append(weight[i])
                    elif (cbm[i] > weight[i]):
                        chargeable_weight.append(cbm[i])
                    elif (weight[i] == cbm[i]):
                        chargeable_weight.append(weight[i])

                #profi_list
                for i in range(0,int(boxes)):
                    profit = chargeable_weight[i] * int(rate)
                    value.append(int(profit))

                cargo = Cargo(
                    num_box = boxes, 
                    capacity = csvform.cleaned_data['capacity'],
                    ini_rate = rate,
                )

                cargo.save()
                id = encrypt(cargo.id)

                table_list = zip(box,description,height,length,width,weight,cbm,chargeable_weight,value)
                for b, d, h, l, wd, we, cb, chW, v in table_list:
                    _, create = cargoList.objects.update_or_create(
                        cargo = Cargo.objects.get(id=cargo.id),
                        box = b,
                        description = d,
                        height = h,
                        length = l,
                        width = wd,
                        weight = we,
                        cbm = cb,
                        chargeable_weight = chW,
                        profit = v,
                    )

                return redirect(result, pk=id)

            except:
                form = generateForm(request.POST)
                csvform = uploadCSV(request.POST, request.FILES)
                
    else:
        form = generateForm(request.POST)
        csvform = uploadCSV(request.POST, request.FILES)

    context = {
        'form':form,
        'csv':csvform,
        'error':error_message,
        }

    return render(request, 'generate.html', context)

def table(request, pk):
    x = datetime.utcnow()
    print("Time now:",x)
    cargo = Cargo.objects.filter(creation_time__lte=datetime.utcnow()-timedelta(minutes=30))
    for i in cargo:
        print(i.creation_time,"is deleted!")
        i.delete()
        cl = cargoList.objects.filter(cargo=i.id)
        cl.delete()

    id = decrypt(pk)
    try: 
        cargo = Cargo.objects.get(id=id)
    except:
        return redirect(index)

    boxes = int(cargo.num_box)
    capacity = int(cargo.capacity)
    rate = float(cargo.ini_rate)
    
    #Initial List
    box = []
    description = []
    height = []
    length = []
    width = []
    weight = []
    cbm = []
    chargeable_weight = []
    value = []

    cargoFormSet = formset_factory(cargoForm,extra=int(boxes)-1, min_num=1, validate_min=True)

    if request.method == 'POST':
        formset = cargoFormSet(request.POST)

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

                try:
                    height.append(int(h))
                    description.append(desc)
                    length.append(int(l))
                    width.append(int(wdth))
                    weight.append(int(wght))
                    cbm.append(int(c))
                except:
                    description.clear
                    formset = cargoFormSet(request.POST)

            for i in range(int(boxes)+1):
                if i != 0:
                    box.append(i)

            #charge_list
            for i in range(0,int(boxes)):
                if (weight[i] > cbm[i]):
                    chargeable_weight.append(weight[i])
                elif (cbm[i] > weight[i]):
                    chargeable_weight.append(cbm[i])
                elif (weight[i] == cbm[i]):
                    chargeable_weight.append(weight[i])

            #profi_list
            for i in range(0,int(boxes)):
                profit = chargeable_weight[i] * int(rate)
                value.append(round(float(profit)))

            table_list = zip(box,description,height,length,width,weight,cbm,chargeable_weight,value)

            for b, d, h, l, wd, we, cb, chW, v in table_list:
                _, create = cargoList.objects.update_or_create(
                    cargo = Cargo.objects.get(id=id),
                    box = b,
                    description = d,
                    height = h,
                    length = l,
                    width = wd,
                    weight = we,
                    cbm = cb,
                    chargeable_weight = chW,
                    profit = v,
                )

            id = encrypt(id)

            return redirect(result, pk=id)

        else:
            print(formset.errors)

    else:
        formset = cargoFormSet()

    context = {
        "box":boxes,
        "capacity":capacity,
        "rate":rate,
        'formset':formset,
    }

    return render(request, 'table.html', context)

#List of not included items
xboxList = []
xwghtList = []
xcbmList = []
xvalList = []

#Final Optimal List
boxList = []
wghtList = []
cbmList = []
valList = []

def result(request, pk):
    x = datetime.utcnow()
    print("Time now:",x)
    cargo = Cargo.objects.filter(creation_time__lte=datetime.utcnow()-timedelta(minutes=30))
    for i in cargo:
        print(i.creation_time,"is deleted!")
        i.delete()
        cl = cargoList.objects.filter(cargo=i.id)
        cl.delete()

    id = decrypt(pk)
    try: 
        cargo = Cargo.objects.get(id=id)
    except:
        return redirect(index)

    boxes = int(cargo.num_box)
    capacity = cargo.capacity
    rate = float(cargo.ini_rate)
    
    cargolist = cargoList.objects.filter(cargo=id)

    #Initial List
    box = []
    description = []
    height = []
    length = []
    width = []
    weight = []
    cbm = []
    chargeable_weight = []
    value = []

    for l in cargolist:
        box.append(l.box)
        description.append(l.description)
        height.append(round(float(l.height)))
        length.append(round(float(l.length)))
        width.append(round(float(l.width)))
        weight.append(round(float(l.weight)))
        cbm.append(round(float(l.cbm)))
        chargeable_weight.append(round(float(l.chargeable_weight)))
        value.append(round(float(l.profit)))


    volume = 666 if int(capacity) == 600 else 999 if int(capacity) == 1000 else 3330

    if sum(weight) >= sum(cbm):
        dynamic_Prog_Weight(weight, value, int(capacity), int(boxes), int(volume), cbm)
    elif sum(weight) < sum(cbm):
        dynamic_Prog_Volume(weight, value, int(capacity), int(boxes), int(volume), cbm)

    table_list = zip(box,description,height,length,width,weight,cbm,chargeable_weight,value)
    #Summary of inputs
    total_cost = sum(value)
    total_weight = sum(weight)
    total_box = len(box)
    total_cbm = sum(cbm)

    final_list = zip(boxList,wghtList,valList,cbmList)
    #Summary of final solution
    final_cost = sum(valList)
    final_weight = sum(wghtList)
    final_box = len(boxList)
    final_cbm = sum(cbmList)

    drop_list = zip(xboxList,xwghtList,xvalList,xcbmList)
    #Summary of drop list
    drop_cost = sum(xvalList)
    drop_weight = sum(xwghtList)
    drop_box = len(xboxList)
    drop_cbm = sum(xcbmList)

    if drop_weight == 0 and drop_cbm == 0:
        recommendation = "No recommendations needed."
    elif (drop_weight <= 600 or drop_weight != 0) and (drop_cbm <= 666 or drop_cbm != 0):
        recommendation = "The recommended vehicle to load the remaining box/es is a light van with a maximum capacity of 600 kg in terms of weight and a maximum capacity of 666 kg in terms of volume."
    elif (drop_weight > 600 or drop_weight <= 1000) and (drop_cbm > 666 or drop_cbm <= 999):
        recommendation = "The recommended vehicle to load the remaining box/es is an L300 van with a maximum capacity of 1000 kg in terms of weight and a maximum capacity of 999 kg in terms of volume."
    elif (drop_weight > 1000 or drop_weight <= 2000) and (drop_cbm > 999 or drop_cbm <= 3330):
        recommendation = "The recommended vehicle to load the remaining box/es is a closed van with a maximum capacity of 2000 kg in terms of weight and a maximum capacity of 3330 kg in terms of volume."
    else:
        recommendation = "It is better to use big trucks in loading the remaining items"
    
    id = encrypt(id)
    
    context = {
        'boxes':boxes,
        'capacity':capacity,
        'rate':rate,
        'pk':id,
        'bl':boxList,
        'tl':table_list,
        'dl':drop_list,
        'fl':final_list,
        'total_cbm':total_cbm,
        'total_cost':total_cost,
        'total_weight':total_weight,
        'total_box':total_box,
        'final_cost':final_cost,
        'final_weight':final_weight,
        'final_box':final_box,
        'final_cbm':final_cbm,
        'drop_cost':drop_cost,
        'drop_weight':drop_weight,
        'drop_box':drop_box,
        'drop_cbm':drop_cbm,
        'recom':recommendation,
    }

    return render(request, 'result.html', context)

def op_csv(request, pk):
    id = decrypt(pk)
    cargo = Cargo.objects.get(id=id)
    boxes = int(cargo.num_box)
    capacity = cargo.capacity

    cargolist = cargoList.objects.filter(cargo=id)

    #Initial List
    box = []
    description = []
    height = []
    length = []
    width = []
    weight = []
    cbm = []
    chargeable_weight = []
    value = []

    for l in cargolist:
        box.append(l.box)
        description.append(l.description)
        height.append(round(float(l.height)))
        length.append(round(float(l.length)))
        width.append(round(float(l.width)))
        weight.append(round(float(l.weight)))
        cbm.append(round(float(l.cbm)))
        chargeable_weight.append(round(float(l.chargeable_weight)))
        value.append(round(float(l.profit)))


    volume = 666 if int(capacity) == 600 else 999 if int(capacity) == 1000 else 3330

    if sum(weight) >= sum(cbm):
        dynamic_Prog_Weight(weight, value, int(capacity), int(boxes), int(volume), cbm)
    elif sum(weight) < sum(cbm):
        dynamic_Prog_Volume(weight, value, int(capacity), int(boxes), int(volume), cbm)

    response = HttpResponse(
            content_type='text/csv',
            headers={'Content-Disposition': 'attachment; filename="optimal.csv"'},
    )

    write = csv.writer(response)
    header = ['Box No.','Weight','Volume','Profit']
    ly = zip(boxList, wghtList, cbmList, valList)
    write.writerow(header)
    for b, w, c, v in ly:
        write.writerow((b,w,c,v))

    return response

def dp_csv(request,pk):
    id = decrypt(pk)
    cargo = Cargo.objects.get(id=id)
    boxes = int(cargo.num_box)
    capacity = cargo.capacity

    cargolist = cargoList.objects.filter(cargo=id)

    #Initial List
    box = []
    description = []
    height = []
    length = []
    width = []
    weight = []
    cbm = []
    chargeable_weight = []
    value = []

    for l in cargolist:
        box.append(l.box)
        description.append(l.description)
        height.append(round(float(l.height)))
        length.append(round(float(l.length)))
        width.append(round(float(l.width)))
        weight.append(round(float(l.weight)))
        cbm.append(round(float(l.cbm)))
        chargeable_weight.append(round(float(l.chargeable_weight)))
        value.append(round(float(l.profit)))


    volume = 666 if int(capacity) == 600 else 999 if int(capacity) == 1000 else 3330

    if sum(weight) >= sum(cbm):
        dynamic_Prog_Weight(weight, value, int(capacity), int(boxes), int(volume), cbm)
    elif sum(weight) < sum(cbm):
        dynamic_Prog_Volume(weight, value, int(capacity), int(boxes), int(volume), cbm)

    response = HttpResponse(
            content_type='text/csv',
            headers={'Content-Disposition': 'attachment; filename="drop.csv"'},
    )

    write = csv.writer(response)
    header = ['Box No.','Weight','Volume','Profit']
    lz = zip(xboxList, xwghtList, xcbmList, xvalList)
    write.writerow(header)
    for b, w, c, v in lz:
        write.writerow((b,w,c,v))

    return response

# Function for Dynamic Programming
# dynamic_Prog(weight, value, vehicle_capacity, num_box, vehicle_volume, cbm)
def dynamic_Prog_Weight(W, V, M, n, C, Z):

    not_included = np.array([[0, 0, 0, 0]])

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

    while (n != 0):
        if (bin_Table[n][M] != bin_Table[n-1][M]):
            row = np.array([n, W[n-1],  V[n-1], Z[n-1]])
            optimal_set = np.append(optimal_set, [row], axis=0)

            M = M - W[n-1]
        else:
            row = np.array([n, W[n-1],  V[n-1], Z[n-1]])
            not_included = np.append(not_included, [row], axis=0)

        n -= 1

    # YUNG DITO GAWING 0 YUNG -1
    optimal_set = np.delete(optimal_set, 0, axis=0)
    
    cbmSum = sum(optimal_set[:, -1])

    # INITIAL optimal_set VALUES (weight constraint only)
    numOfBoxes_init = int(len(optimal_set[:, 0]))
    numbox_list = optimal_set[:, 0]  # BAGONG LIST

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

                # The second conditional statement (elif) contains the code block for when
                # the VOLUME of the i(th) box is less than the total VOLUME permissible for that cell (j).
                # In this code block, the profit when the box is included versus the profit when the box is excluded are compared.
                # Whichever of the values is the highest is the one assigned to that cell.
            else:
                volume_Table[i][j] = volume_Table[i-1][j]

    # print optimal volume
    while (numOfBoxes_init != 0):
        if (volume_Table[numOfBoxes_init][C] != volume_Table[numOfBoxes_init-1][C]):
            row = np.array([numbox_list[numOfBoxes_init-1],  weightList_init[numOfBoxes_init-1],
                           profitList_init[numOfBoxes_init-1], volumeList_init[numOfBoxes_init-1]])
            Final_optimal_set = np.append(Final_optimal_set, [row], axis=0)

            C = C - volumeList_init[numOfBoxes_init-1]

        else:  # ELSE STATEMENT PARA SA MGA BOX NA DI MASASAMA SA FINAL OPTIMAL SOLUTION
            row = np.array([numbox_list[numOfBoxes_init-1],  weightList_init[numOfBoxes_init-1],
                           profitList_init[numOfBoxes_init-1], volumeList_init[numOfBoxes_init-1]])
            not_included = np.append(not_included, [row], axis=0)

        numOfBoxes_init -= 1
        # BAGONG WAY PAG-KAAPPEND: numbox_list[numOfBoxes_init-1]

    # DESCENDING ORDER FOR PROFIT/VALUE

    Final_optimal_set = Final_optimal_set[Final_optimal_set[:, 2].argsort()[
        ::-1]]

    print("\n\n******FINAL OPTIMAL SOLUTION (Weight Constraint and Volume Constraint)******")
    print("Box No.\tWeight\tProfit/Value\tCBM")
    Final_optimal_set = np.delete(Final_optimal_set, -1, axis=0)
    print(Final_optimal_set)

    boxList.clear()
    wghtList.clear()
    cbmList.clear()
    valList.clear()

    for i in Final_optimal_set:
        boxList.append(i[0])
        wghtList.append(i[1])
        valList.append(i[2])
        cbmList.append(i[3])

    finalcbmSum = sum(Final_optimal_set[:, -1])

    # DESCENDING ORDER FOR PROFIT/VALUE NG ITEMS NA DI MAIINCLUDE SA FINAL OPTIMAL SOLUTION
    not_included = not_included[not_included[:, 2].argsort()[::-1]]
    not_included = np.delete(not_included, -1, axis=0)

    xboxList.clear()
    xwghtList.clear()
    xcbmList.clear()
    xvalList.clear()

    for i in not_included:
        xboxList.append(i[0])
        xwghtList.append(i[1])
        xvalList.append(i[2])
        xcbmList.append(i[3])

    not_includedcbmSum = sum(not_included[:, -1])
    notincluded_numBox = int(len(not_included[:, 0]))


def dynamic_Prog_Volume(W, V, M, n, C, Z):

    not_included = np.array([[0, 0, 0, 0]])

    optimal_set = np.array([[0, 0, 0, 0]])

    bin_Table = [[0 for x in range(C + 1)] for x in range(n + 1)]
    for i in range(n + 1):
        for j in range(C + 1):
            if i == 0 or j == 0:
                bin_Table[i][j] = 0
            elif j >= Z[i-1]:
                bin_Table[i][j] = max(
                    V[i-1] + bin_Table[i-1][j-Z[i-1]], bin_Table[i-1][j])
            else:
                bin_Table[i][j] = bin_Table[i-1][j]

    while (n != 0):
        if (bin_Table[n][C] != bin_Table[n-1][C]):
            row = np.array([n, W[n-1],  V[n-1], Z[n-1]])
            optimal_set = np.append(optimal_set, [row], axis=0)

            C = C - Z[n-1]
        else:
            row = np.array([n, W[n-1],  V[n-1], Z[n-1]])
            not_included = np.append(not_included, [row], axis=0)

        n -= 1

    # DESCENDING ORDER FOR PROFIT/VALUE
    # YUNG DITO GAWING 0 YUNG -1
    optimal_set = np.delete(optimal_set, 0, axis=0)
    cbmSum = sum(optimal_set[:, -1])



    # INITIAL optimal_set VALUES (weight constraint only)
    numOfBoxes_init = int(len(optimal_set[:, 0]))
    numbox_list = optimal_set[:, 0]  # BAGONG LIST

    weightList_init = optimal_set[:, 1]

    profitList_init = optimal_set[:, 2]

    a = optimal_set[:, 3]
    a1 = a.tolist()
    volumeList_init = list(map(round, a1))

    # BKP DP ALGO - APPLY TO INITIAL optimal_set VALUES
    Final_optimal_set = np.array([[0, 0, 0, 0]])

    weight_Table = [[0 for x in range(M + 1)]
                    for x in range(numOfBoxes_init + 1)]
    for i in range(numOfBoxes_init + 1):
        for j in range(M + 1):
            if i == 0 or j == 0:
                weight_Table[i][j] = 0
            elif j >= weightList_init[i-1]:
                weight_Table[i][j] = max(
                    profitList_init[i-1] + weight_Table[i-1][j-weightList_init[i-1]], weight_Table[i-1][j])

                # The second conditional statement (elif) contains the code block for when
                # the VOLUME of the i(th) box is less than the total VOLUME permissible for that cell (j).
                # In this code block, the profit when the box is included versus the profit when the box is excluded are compared.
                # Whichever of the values is the highest is the one assigned to that cell.
            else:
                weight_Table[i][j] = weight_Table[i-1][j]

    # print optimal volume
    while (numOfBoxes_init != 0):
        if (weight_Table[numOfBoxes_init][M] != weight_Table[numOfBoxes_init-1][M]):
            row = np.array([numbox_list[numOfBoxes_init-1],  weightList_init[numOfBoxes_init-1],
                           profitList_init[numOfBoxes_init-1], volumeList_init[numOfBoxes_init-1]])
            Final_optimal_set = np.append(Final_optimal_set, [row], axis=0)

            M = M - weightList_init[numOfBoxes_init-1]

        else:  # ELSE STATEMENT PARA SA MGA BOX NA DI MASASAMA SA FINAL OPTIMAL SOLUTION
            row = np.array([numbox_list[numOfBoxes_init-1],  weightList_init[numOfBoxes_init-1],
                           profitList_init[numOfBoxes_init-1], volumeList_init[numOfBoxes_init-1]])
            not_included = np.append(not_included, [row], axis=0)

        numOfBoxes_init -= 1
        # BAGONG WAY PAG-KAAPPEND: numbox_list[numOfBoxes_init-1]

    # DESCENDING ORDER FOR PROFIT/VALUE

    Final_optimal_set = Final_optimal_set[Final_optimal_set[:, 2].argsort()[
        ::-1]]

    print("\n\n******FINAL OPTIMAL SOLUTION (Weight Constraint and Volume Constraint)******")
    print("Box No.\tWeight\tProfit/Value\tCBM")
    Final_optimal_set = np.delete(Final_optimal_set, -1, axis=0)
    print(Final_optimal_set)

    boxList.clear()
    wghtList.clear()
    cbmList.clear()
    valList.clear()

    for i in Final_optimal_set:
        boxList.append(i[0])
        wghtList.append(i[1])
        valList.append(i[2])
        cbmList.append(i[3])

    finalcbmSum = sum(Final_optimal_set[:, -1])

    # DESCENDING ORDER FOR PROFIT/VALUE NG ITEMS NA DI MAIINCLUDE SA FINAL OPTIMAL SOLUTION
    not_included = not_included[not_included[:, 2].argsort()[
        ::-1]]
    print("\n\n******ITEMS NOT INCLUDED IN THE OPTIMAL SOLUTION******")
    print("Box No.\tWeight\tProfit/Value\tCBM")
    not_included = np.delete(not_included, -1, axis=0)
    print(not_included)

    xboxList.clear()
    xwghtList.clear()
    xcbmList.clear()
    xvalList.clear()

    for i in not_included:
        xboxList.append(i[0])
        xwghtList.append(i[1])
        xvalList.append(i[2])
        xcbmList.append(i[3])

    not_includedcbmSum = sum(not_included[:, -1])
    notincluded_numBox = int(len(not_included[:, 0]))

