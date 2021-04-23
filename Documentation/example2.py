from pargo.rand import RANDSuiteProcessor

rand = RANDSuiteProcessor()

rand.activate_process(platform='GPU-Server-1', specs_file_path='path_to_specs.txt', dat_file_path='path_to_test_suite.dat', version='rocm4.0')


#If rand was a new library being added, after overriding process_data, it could be as shown below.

if __name__ == '__main__':
    axis_titles = ['uniform-unit', 'uniform-float', 'uniform-double', 'normal-float', 'normal-double', 'log-normal-float', 
                'log-normal-double', 'poisson lambda 10.0', 'discrete-poisson lambda 10.0', 'discrete-custom']
    added_fields = {'Algorithm': ['xorwow', 'mrg32k3a', 'mtgp32', 'philox', 'sobol32']}

    rand = RANDSuiteProcessor()
    rand.activate_process(platform='GPU-Server-2', dat_file_path='assets/test.dat', version='rocm4.0', specs_file_path='assets/specs.txt', 
                        axis_titles=axis_titles, added_fields=added_fields, plots=['bar'])
