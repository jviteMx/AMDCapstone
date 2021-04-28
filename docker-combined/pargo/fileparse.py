from pargo.template import FFTSuiteProcessor, RANDSuiteProcessor, BLASSuiteProcessor

def parse_and_write():
    fft = FFTSuiteProcessor()
    fft.activate_process(strict_dir_path='fft-assets')

    blas = BLASSuiteProcessor()
    blas.activate_process(strict_dir_path='blas-assets')

    rand = RANDSuiteProcessor()
    rand.activate_process(strict_dir_path='rand-assets')

if __name__ == '__main__':
    parse_and_write()    
