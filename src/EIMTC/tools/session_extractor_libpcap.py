from pypacker import ppcap
from pypacker.layer12 import ethernet
from pypacker.layer3 import ip
from pypacker.layer4 import tcp



def main():
    filepath = '../temp/DoH-Firefox84-NextDNS-1-pcap-format.pcap'
    output_path = '../temp/output_sess_ex.pcap'
    
    preader = ppcap.Reader(filename=filepath)
    pwriter = ppcap.Writer(filename=output_path, linktype=ppcap.DLT_EN10MB)

    for ts, buf in preader:
        eth = ethernet.Ethernet(buf)

        if eth[ip.IP] is not None:
            if eth[tcp.TCP] is not None:
                '192.168.1.105', 61296, '213.227.181.51', 443, 'tcp'
                if (eth[ip.IP].src_s == '192.168.1.105' or eth[ip.IP].dst_s == '192.168.1.105'
                    ) and (eth[ip.IP].src_s == '213.227.181.51' or eth[ip.IP].dst_s == '213.227.181.51'
                    ) and (eth[tcp.TCP].sport == 61296 or eth[tcp.TCP].sport == 443
                    ) and (eth[tcp.TCP].dport == 61296 or eth[tcp.TCP].dport == 443):
                    
                #print("%d: %s:%s -> %s:" % (ts, eth[ip.IP].src_s, eth[ip.IP].dst_s, eth[tcp.TCP].sport))
                    pwriter.write(eth.bin())

    pwriter.close()



if __name__ == '__main__':
    main()