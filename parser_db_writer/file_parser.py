from mongo_writer import DBInserter

def parse_data (dat_file):
    with open(dat_file) as file:
        data = file.readlines() #open(dat_file).readlines()
        del data[0]
    return data   

data = parse_data ('radix2_dim1_double_n1_c2c_inplace.dat')
list_of_dicts = []
keys = data[0].split()[1:]

for i in range(1, len(data)):
    values = data[i].split()[0:4] 
    values.append(data[i].split()[4:])
    dict_data = dict(zip(keys, values))
    list_of_dicts.append(dict_data)


#Insert to mongo
writer = DBInserter()
collection = writer.write_to_db(list_of_dicts)


#Test read from mongo
example_read = collection.find_one({'xlength': '2048'})
print(example_read)