import subprocess
import csv
import glob
import os
from datetime import datetime



class spec:
    def __init__(self) -> None:
        pass
    
class spec_ip_address:
    def __init__(self, ip) -> None:
        self.ip = ip

    def __str__(self) -> str:
        return f'ip.addr=={self.ip}'
    
class spec_port:
    def __init__(self, port) -> None:
        self.port = port

    def __str__(self) -> str:
        return f'tcp.port=={self.port} or udp.port=={self.port}' 
    
class spec_protocol:
    def __init__(self, proto) -> None:
        self.proto = proto

    def __str__(self) -> str:
        return f'{self.proto}'
    
class spec_timestamp_larger_than:
    def __init__(self, epoch_time, units='nano') -> None:
        self.epoch_time = epoch_time
        if units == 'nano':
            self.epoch_time /= 1000

    def __str__(self) -> str:
        return f'frame.time_epoch>={self.epoch_time}'

class spec_timestamp_smaller_than:
    def __init__(self, epoch_time, units='nano') -> None:
        self.epoch_time = epoch_time +1
        if units == 'nano':
            self.epoch_time /= 1000

    def __str__(self) -> str:
        return f'frame.time_epoch<={self.epoch_time}'
    
class spec_timestamp_range:
    def __init__(self, start_epoch_time, end_epoch_time, units='nano') -> None:
        start = spec_timestamp_larger_than(start_epoch_time, units)
        end = spec_timestamp_smaller_than(end_epoch_time, units)
        self.spec = spec_and([start, end])

    def __str__(self) -> str:
        return str(self.spec)

class spec_and:
    def __init__(self, specs) -> None:
        self.specs = specs
        
    def __str__(self) -> str:
        return '('+' and '.join([str(spec) for spec in self.specs])+')'

class spec_or:
    def __init__(self, specs) -> None:
        self.specs = specs
        
    def __str__(self) -> str:
        return '('+' or '.join([str(spec) for spec in self.specs])+')'
    
class spec_5tuple:
    def __init__(self, ip1, port1, ip2, port2, protocol) -> None:
        self.specs = [
            spec_ip_address(ip1),
            spec_port(port1),
            spec_ip_address(ip2),
            spec_port(port2),
            spec_protocol(protocol)
        ]
    
    def __str__(self) -> str:
        return f'{self.protocol} and ip.addr=={self.ip1} and {self.protocol}.port=={self.port1} and ip.addr=={self.ip2} and {self.protocol}.port=={self.port2}'


def run_tshark_wspecs(input_filepath, output_filepath, tshark_location, filter, error_log_filepath='./tshark_error_log.txt', ):
    splitted_save = f'-w {output_filepath}'.split()
    command =  f'{tshark_location} -r {input_filepath} -2 -n -R'
    splitted_command = command.split() + [str(filter)] + splitted_save
    print(' '.join(splitted_command))
    with open(output_filepath, "w") as outfile:
        with open(error_log_filepath, "w") as error_log_file:
            proc = subprocess.run(
                splitted_command, 
                stdout = outfile, 
                stderr = error_log_file,
                check=True
            )
     


def current_time():
    now = datetime.now()
    current_time = now.strftime("%H:%M:%S")
    return current_time



if __name__ == '__main__':
    filepath = '../temp/DoH-Firefox84-NextDNS-1-pcap-format.pcap'
    output_path = '../temp/output_sess_ex.pcap'
    
    sess_1_spec = spec_and([
        spec_ip_address('192.168.1.105'),
        spec_port(61296),
        spec_ip_address('213.227.181.51'),
        spec_port(443),
        spec_protocol('tcp'),
        spec_timestamp_range(1610353294304, 1610353332681)
    ])
    sess_2_spec = spec_and([
        spec_ip_address('192.168.1.105'),
        spec_port(61393),
        spec_ip_address('213.227.181.51'),
        spec_port(443),
        spec_protocol('tcp'),
        spec_timestamp_larger_than(1610353294304),
        spec_timestamp_smaller_than(1610353758977),
    ])
    
    specs = spec_or([
       sess_1_spec, 
       sess_2_spec 
    ])
    
    # spec_5tuple('192.168.1.105', 61296, '213.227.181.51', 443, 'tcp')

    print(specs)
    
    run_tshark_wspecs(filepath, output_path, 'tshark', specs)