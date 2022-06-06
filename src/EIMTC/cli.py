#!/usr/bin/env python3
'''
CLI module
'''
from extractor import Extractor
import click


@click.command()
@click.option('--input', type=click.Path(exists=True, readable=True), help='Input PCAP file.')
@click.option('--output', type=click.Path(writable=True), default='./extracted_features', help='Output directory of extracted features.')
def entry(input, output):
    print(
        """ Parameters received: 
        Input PCAP file: {}
        Output directory: {}
        """.format(input, output))
    
    print('Starting to extract features...')
    
    Extractor(input, output).extract()
    

if __name__ == '__main__':
    entry()