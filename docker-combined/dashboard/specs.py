# MIT LINCENCE. 2021
#
# This file is part of an academic capstone project,
# and it is made for AMD as part of efforts to automate
# the open source ROCM math libraries performance analytics.
# Contact The AMD rocm team for use and improvements on the project.
# The team: Victor Tuah Kumi, Aidan Forester, Javier Vite, Ahmed Iqbal
# Reach Victor Tuah Kumi on LinkedIn

"""Gets specifications for GPU/CPU on which rocm is run"""
import model

def get_specs(hardware_ids, rocm_versions):
    """Gets specification for all specified rocm hardwares"""
    specs_info = []
    for rocm in rocm_versions:
        for hardw_id in hardware_ids:
            specs = model.get_specs(hardw_id, rocm)  #returns dictionary
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
    return specs_info
