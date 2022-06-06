import subprocess
import pandas as pd
import numpy as np

def run_tshark_tls(input_filepath, output_filepath, tshark_location, error_log_filepath='./tshark_error_log.txt'):
    command =  f'{tshark_location} -r {input_filepath} -E header=y -E separator=, -E quote=d -T fields -e frame.time -e ip.src -e tcp.srcport -e ip.dst -e tcp.dstport -e ip.proto -e tls.record.version -e tls.record.length -e tls.connection_id -e tls.handshake -Y tls -2 -n'
    splitted_command = command.split()
    with open(output_filepath, "w") as outfile:
        with open(error_log_filepath, "w") as error_log_file:
            proc = subprocess.run(
                splitted_command, 
                stdout = outfile, 
                stderr = error_log_file,
                check=True
            )
    