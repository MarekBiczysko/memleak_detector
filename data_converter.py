import csv

def returnLinesFromDataFile(data_filename):

    with open(data_filename, 'rb') as f:
        reader = csv.reader(f)
        full_data = list(reader)
        full_data[0] = full_data[0][7:]
        full_data[1] = full_data[1][7:]
        return full_data

def rearangeData(data):
    new_data = [[]]

    for i in range(9):
        new_data[0].append(data[0][i])

    tmp_iter = 0
    tmp_list = []
    for i in range(len(data[0])):
        if tmp_iter == 10:
            new_data.append(tmp_list)
            tmp_iter = 0
            tmp_list = []
        try:
            tmp_list.append(int(data[1][i]))
        except ValueError:
            tmp_list.append(data[1][i])
        tmp_iter += 1

    return new_data

def writeAllFieldsToCSV(CSVfilename, data_list):
    bts_name = data_list[0][6]
    with open(bts_name + CSVfilename, "wb") as f:
        writer = csv.writer(f)
        writer.writerows(data_list)

def returnListOfuniqueBTSdata(data):
    sorted_data = sortDataByField(data, 6)
    inverted = map(list, zip(*sorted_data))
    no_of_BTS = len(set(inverted[6]))-1
    data_sorted_btsid = [[] for x in range(no_of_BTS)]
    temp_btsid = sorted_data[0][6]
    id_iter = 0
    for i in range(no_of_BTS):
        temp_btsid = sorted_data[id_iter][6]
        while sorted_data[id_iter][6] == temp_btsid:
            data_sorted_btsid[i].append(sorted_data[id_iter])
            temp_btsid = sorted_data[id_iter][6]
            id_iter += 1
        data_sorted_btsid[i] = sortDataByField(data_sorted_btsid[i], 8)

    return data_sorted_btsid

def sortDataByField(data, field):
    #uptime 8
    #btsid 6
    return sorted(data, key=lambda l: l[field])

def rearangeAllFiles(filenames):

    for filename in filenames:
        data = returnLinesFromDataFile(filename)
        new_data = rearangeData(data)
        data_sorted_btsid = returnListOfuniqueBTSdata(new_data)
        for i in data_sorted_btsid:
            writeAllFieldsToCSV(filename, i)



data_filenames = ['MRBTS.csv']

rearangeAllFiles(data_filenames)



