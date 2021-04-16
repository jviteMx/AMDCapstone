from template import LibraryProcessor
class RANDProcessor(LibraryProcessor):
    def __init__(self):
        self.library_name = 'rocRAND'
        self.CLIENT_IP = 'localhost'
        self.CLIENT_PORT = 27017
        LibraryProcessor.__init__(self, self.CLIENT_IP, self.CLIENT_PORT, self.library_name)

    def process_data(self, list_data, file_path_object):
        data = list_data
        file_name = data[0]
        self.suite_name = self.process_suite_name(file_name, file_path_object)
        grouped_data = [('xorwow', data[2:25]),('mrg32k3a', data[26:49]),('mtgp32', data[50:73]),
                        ('philox', data[74:97]),('sobol32', data[98:121])]
        keys, values = [], []
        dict_data_combined = {}
        for algo in grouped_data:
            ALGO = algo[0]
            data = algo[1]
            sub_data = data[1:]
            for i in range(len(sub_data)):
                if 'Throughput' not in sub_data[i]:
                    ALGO = ALGO + '@' + sub_data[i].strip().strip(':')
                    continue
                else:
                    process_a = [i.strip() for i in sub_data[i].split(',')]
                    process_b = [i.split('=') for i in process_a]  
                    process_c = [[i.strip(), j.strip()] for [i, j] in process_b]
                    temp = process_c[-1]
                    process_d = [[i.strip(' ') + '-' + j.split(' ')[1], j.split(' ')[0]] for [i, j] in process_c[:-1]]
                    process_d.append(temp)
                    for pair in process_d:
                        key = pair[0]
                        value = pair[1]
                        key = ALGO + '@' + key
                        keys.append(key)
                        values.append(value)
                    dict_data = dict(zip(keys, values))  
                    dict_data_combined = dict_data_combined | dict_data
                    
                    keys, values = [], []
                    ALGO = algo[0]   
        # print(dict_data_combined)         

        self.suite_data = [dict_data_combined]

        self.run(self.suite_name, self.suite_data)

    def process_suite_name(self, info, file_path_object): 
        renamed = info.split(':')
        renamed = [i.strip() for i in renamed]
        renamed = ''.join(renamed)
        renamed = file_path_object.name.rstrip('.dat') + renamed
        return renamed.lower()

if __name__ == '__main__':
    axis_titles = ['uniform-unit', 'uniform-float', 'uniform-double', 'normal-float', 'normal-double', 'log-normal-float', 
                'log-normal-double', 'poisson lambda 10.0', 'discrete-poisson lambda 10.0', 'discrete-custom']

    added_fields = {'Algorithm': ['xorwow', 'mrg32k3a', 'mtgp32', 'philox', 'sobol32']}

    rand = RANDProcessor()
    rand.activate_process(platform='GPU-Server2', dat_file='assets/test.dat', version='rocm4.0', specs_file='assets/specs.txt', 
                        axis_titles=axis_titles, added_fields=added_fields, plots=['bar'])