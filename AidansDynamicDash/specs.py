import model

 #API to use 
def get_specs(hardware_ids, rocm_versions):   #hardware_id is a list
    specs_info = []
    for rocm in rocm_versions:
        for hardw_id in hardware_ids:
            specs = model.get_specs(hardw_id, rocm)  #//returns dictionary
            if specs is not None:
                title = f'{rocm} specs'
                info = f'''
                      
                ```
                    {title}

                    Host info:
                        hostname:       {specs['hostname']}
                        cpu info:       {specs['cpu_info']}
                        ram:            {specs['ram']}
                        distro:         {specs['distro']}
                        kernel version: {specs['kernel']}
                        rocm version:   {specs['rocm']}
                    Device info:
                        device:            {specs['device']} 
                        vbios version:     {specs['vbios']}
                        vram:              {specs['vram']}
                        performance level: {specs['performance']}
                        system clock:      {specs['sys_clock']}
                        memory clock:      {specs['mem_clock']}
                ```
                    '''    
                specs_info.append(info)
    return specs_info                        #list               