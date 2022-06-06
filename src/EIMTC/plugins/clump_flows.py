import numpy as np
from runstats import *
from nfstream import NFPlugin




class Clump_Flow(NFPlugin):
    '''
    Clumps:
        Description:
            The plugin 'clumps' the packets of each flow by the direction src2dst or dst2src,
            for each clump in flow clump starts and end when the next packet change direction or last flow packet.
            The clumps then extracted stastical information from the clumps groups.
        INFO:
            The paper we used as refrence to the clumps is "The Challenge of Only One Flow Problem for Traffic Classification in Identity Obfuscation Environments":
            In the paper the authors call the clumps as 'subflows' such forward (src2dst) subflows and backward (dst2src) subflows.
            We used only the subflow features:
                -PACKET NUMBER (SIZE)
                -PACKET BYTES (LEN)
                -BYTES PER PACKET
            In addition we added few more statistical features to each one of the features above.

            the authors of the paper:
            HONG-YEN CHEN & TSUNG-NAN LIN

        Coded by Adi Lichy,
        Edited by Ofek Bader,
        Ariel University.
    '''

    def on_init(self, packet, flow):
        flow.udps.src2dst_clumps = Clumps()
        flow.udps.dst2src_clumps = Clumps()
        flow.udps.clumps = Clumps()
        flow.udps.direction = None
        flow.udps.clump = None
        self.on_update(packet,flow)

    def on_update(self, packet, flow):
        if flow.udps.direction is None or flow.udps.direction != packet.direction:#first packet direction or change of direction
            if flow.udps.clump is not None:#not the first clump
                if flow.udps.direction == 0:
                    flow.udps.clump.update_bytes_per_packet()
                    flow.udps.src2dst_clumps.add_clump(flow.udps.clump)
                    flow.udps.src2dst_clumps.update(flow.udps.clump.size,flow.udps.clump.len,flow.udps.clump.bytes_per_packet,flow.udps.clump.interarrival_time)
                    flow.udps.clumps.add_clump(flow.udps.clump)
                    flow.udps.clumps.update(flow.udps.clump.size,flow.udps.clump.len,flow.udps.clump.bytes_per_packet,flow.udps.clump.interarrival_time)
                else:
                    flow.udps.clump.update_bytes_per_packet()
                    flow.udps.dst2src_clumps.add_clump(flow.udps.clump)
                    flow.udps.dst2src_clumps.update(flow.udps.clump.size,flow.udps.clump.len,flow.udps.clump.bytes_per_packet,flow.udps.clump.interarrival_time)
                    flow.udps.clumps.add_clump(flow.udps.clump)
                    flow.udps.clumps.update(flow.udps.clump.size,flow.udps.clump.len,flow.udps.clump.bytes_per_packet,flow.udps.clump.interarrival_time)
            flow.udps.direction = packet.direction
            flow.udps.clump = Clump(flow.udps.direction)
            flow.udps.clump.update_size(1)
            flow.udps.clump.update_len(packet.raw_size)
            flow.udps.clump.update_clump_time_stats(packet.time)
            flow.udps.clump.update_time(packet.delta_time)
        else:
            flow.udps.clump.update_size(1)
            flow.udps.clump.update_clump_time_stats(packet.time)
            flow.udps.clump.update_len(packet.raw_size)

    def on_expire(self, flow):
        #end of flow closing last clump
        if flow.udps.direction == 0:
            flow.udps.clump.update_bytes_per_packet()
            flow.udps.src2dst_clumps.add_clump(flow.udps.clump)
            flow.udps.src2dst_clumps.update(flow.udps.clump.size,flow.udps.clump.len,flow.udps.clump.bytes_per_packet,flow.udps.clump.interarrival_time)
            flow.udps.clumps.add_clump(flow.udps.clump)
            flow.udps.clumps.update(flow.udps.clump.size,flow.udps.clump.len,flow.udps.clump.bytes_per_packet,flow.udps.clump.interarrival_time)
        else:
            flow.udps.clump.update_bytes_per_packet()
            flow.udps.dst2src_clumps.add_clump(flow.udps.clump)
            flow.udps.dst2src_clumps.update(flow.udps.clump.size,flow.udps.clump.len,flow.udps.clump.bytes_per_packet,flow.udps.clump.interarrival_time)
            flow.udps.clumps.add_clump(flow.udps.clump)
            flow.udps.clumps.update(flow.udps.clump.size,flow.udps.clump.len,flow.udps.clump.bytes_per_packet,flow.udps.clump.interarrival_time)
        #gathering clumps results
        len_stats_src2dst = flow.udps.src2dst_clumps.get_len_stats()
        len_stats_dst2src = flow.udps.dst2src_clumps.get_len_stats()
        len_stats = flow.udps.clumps.get_len_stats()
        size_stats_src2dst = flow.udps.src2dst_clumps.get_size_stats()
        size_stats_dst2src = flow.udps.dst2src_clumps.get_size_stats()
        size_stats = flow.udps.clumps.get_size_stats()
        bytes_per_packet_stats_src2dst = flow.udps.src2dst_clumps.get_bytes_per_packet_stats()
        bytes_per_packet_stats_dst2src = flow.udps.dst2src_clumps.get_bytes_per_packet_stats()
        bytes_per_packet_stats = flow.udps.clumps.get_bytes_per_packet_stats()
        interarrival_time_stats_src2dst = flow.udps.src2dst_clumps.get_time_stats()
        interarrival_time_stats_dst2src = flow.udps.dst2src_clumps.get_time_stats()
        interarrival_time_stats = flow.udps.clumps.get_time_stats()
        
        #gather clump results
        src2dst_clump = flow.udps.src2dst_clumps.get_clumps()
        dst2src_clump = flow.udps.dst2src_clumps.get_clumps()
        clump = flow.udps.clumps.get_clumps()
        len_stats_src2dst_clump_max = []
        len_stats_src2dst_clump_min = []
        len_stats_src2dst_clump_mean = []
        len_stats_src2dst_clump_stddev = []
        len_stats_src2dst_clump_skewness = []
        len_stats_src2dst_clump_variance = []
        len_stats_src2dst_clump_kurtosis = []
        len_stats_dst2src_clump_max = []
        len_stats_dst2src_clump_min = []
        len_stats_dst2src_clump_mean = []
        len_stats_dst2src_clump_stddev = []
        len_stats_dst2src_clump_skewness = []
        len_stats_dst2src_clump_variance = []
        len_stats_dst2src_clump_kurtosis = []
        len_stats_clump_max = []
        len_stats_clump_min = []
        len_stats_clump_mean = []
        len_stats_clump_stddev = []
        len_stats_clump_skewness = []
        len_stats_clump_variance = []
        len_stats_clump_kurtosis = []

        interarrival_time_stats_src2dst_clump_max = []
        interarrival_time_stats_src2dst_clump_min = []
        interarrival_time_stats_src2dst_clump_mean = []
        interarrival_time_stats_src2dst_clump_stddev = []
        interarrival_time_stats_src2dst_clump_skewness = []
        interarrival_time_stats_src2dst_clump_variance = []
        interarrival_time_stats_src2dst_clump_kurtosis = []
        interarrival_time_stats_dst2src_clump_max = []
        interarrival_time_stats_dst2src_clump_min = []
        interarrival_time_stats_dst2src_clump_mean = []
        interarrival_time_stats_dst2src_clump_stddev = []
        interarrival_time_stats_dst2src_clump_skewness = []
        interarrival_time_stats_dst2src_clump_variance = []
        interarrival_time_stats_dst2src_clump_kurtosis = []
        interarrival_time_stats_clump_max = []
        interarrival_time_stats_clump_min = []
        interarrival_time_stats_clump_mean = []
        interarrival_time_stats_clump_stddev = []
        interarrival_time_stats_clump_skewness = []
        interarrival_time_stats_clump_variance = []
        interarrival_time_stats_clump_kurtosis = []


        for clump_number in range(len(clump)):
            if clump_number < len(src2dst_clump):
                current_len = src2dst_clump[clump_number].get_len_stats()
                current_time = src2dst_clump[clump_number].get_time_stats()
                #len
                len_stats_src2dst_clump_max.append(current_len['maximum'])
                len_stats_src2dst_clump_min.append(current_len['minimum'])
                len_stats_src2dst_clump_mean.append(current_len['mean'])
                len_stats_src2dst_clump_stddev.append(current_len['stddev'])
                len_stats_src2dst_clump_skewness.append(current_len['skewness'])
                len_stats_src2dst_clump_variance.append(current_len['variance'])
                len_stats_src2dst_clump_kurtosis.append(current_len['kurtosis'])
                #time
                interarrival_time_stats_src2dst_clump_max.append(current_time['maximum'])
                interarrival_time_stats_src2dst_clump_min.append(current_time['minimum'])
                interarrival_time_stats_src2dst_clump_mean.append(current_time['mean'])
                interarrival_time_stats_src2dst_clump_stddev.append(current_time['stddev'])
                interarrival_time_stats_src2dst_clump_skewness.append(current_time['skewness'])
                interarrival_time_stats_src2dst_clump_variance.append(current_time['variance'])
                interarrival_time_stats_src2dst_clump_kurtosis.append(current_time['kurtosis'])
            if clump_number < len(dst2src_clump):
                current_len = dst2src_clump[clump_number].get_len_stats()
                current_time = dst2src_clump[clump_number].get_time_stats()
                #len
                len_stats_dst2src_clump_max.append(current_len['maximum'])
                len_stats_dst2src_clump_min.append(current_len['minimum'])
                len_stats_dst2src_clump_mean.append(current_len['mean'])
                len_stats_dst2src_clump_stddev.append(current_len['stddev'])
                len_stats_dst2src_clump_skewness.append(current_len['skewness'])
                len_stats_dst2src_clump_variance.append(current_len['variance'])
                len_stats_dst2src_clump_kurtosis.append(current_len['kurtosis'])
                #time
                interarrival_time_stats_dst2src_clump_max.append(current_time['maximum'])
                interarrival_time_stats_dst2src_clump_min.append(current_time['minimum'])
                interarrival_time_stats_dst2src_clump_mean.append(current_time['mean'])
                interarrival_time_stats_dst2src_clump_stddev.append(current_time['stddev'])
                interarrival_time_stats_dst2src_clump_skewness.append(current_time['skewness'])
                interarrival_time_stats_dst2src_clump_variance.append(current_time['variance'])
                interarrival_time_stats_dst2src_clump_kurtosis.append(current_time['kurtosis'])

            current_len = clump[clump_number].get_len_stats()
            current_time = clump[clump_number].get_time_stats()
            #len
            len_stats_clump_max.append(current_len['maximum'])
            len_stats_clump_min.append(current_len['minimum'])
            len_stats_clump_mean.append(current_len['mean'])
            len_stats_clump_stddev.append(current_len['stddev'])
            len_stats_clump_skewness.append(current_len['skewness'])
            len_stats_clump_variance.append(current_len['variance'])
            len_stats_clump_kurtosis.append(current_len['kurtosis'])
            #time
            interarrival_time_stats_clump_max.append(current_time['maximum'])
            interarrival_time_stats_clump_min.append(current_time['minimum'])
            interarrival_time_stats_clump_mean.append(current_time['mean'])
            interarrival_time_stats_clump_stddev.append(current_time['stddev'])
            interarrival_time_stats_clump_skewness.append(current_time['skewness'])
            interarrival_time_stats_clump_variance.append(current_time['variance'])
            interarrival_time_stats_clump_kurtosis.append(current_time['kurtosis'])

        #src2dst
        #len
        flow.udps.src2dst_max_clumps_len =      len_stats_src2dst['maximum']
        flow.udps.src2dst_min_clumps_len =      len_stats_src2dst['minimum']
        flow.udps.src2dst_mean_clumps_len =     len_stats_src2dst['mean']
        flow.udps.src2dst_stddev_clumps_len =   len_stats_src2dst['stddev']
        flow.udps.src2dst_skewness_clumps_len = len_stats_src2dst['skewness']
        flow.udps.src2dst_variance_clumps_len = len_stats_src2dst['variance']
        flow.udps.src2dst_kurtosis_clumps_len = len_stats_src2dst['kurtosis']

        #size
        flow.udps.src2dst_max_clumps_size =      size_stats_src2dst['maximum']
        flow.udps.src2dst_min_clumps_size =      size_stats_src2dst['minimum']
        flow.udps.src2dst_mean_clumps_size =     size_stats_src2dst['mean']
        flow.udps.src2dst_stddev_clumps_size =   size_stats_src2dst['stddev']
        flow.udps.src2dst_skewness_clumps_size = size_stats_src2dst['skewness']
        flow.udps.src2dst_variance_clumps_size = size_stats_src2dst['variance']
        flow.udps.src2dst_kurtosis_clumps_size = size_stats_src2dst['kurtosis']

        #bytes_per_packet
        flow.udps.src2dst_max_clumps_bytes_per_packet =       bytes_per_packet_stats_src2dst['maximum']
        flow.udps.src2dst_min_clumps_bytes_per_packet =       bytes_per_packet_stats_src2dst['minimum']
        flow.udps.src2dst_mean_clumps_bytes_per_packet =      bytes_per_packet_stats_src2dst['mean']
        flow.udps.src2dst_stddev_clumps_bytes_per_packet =    bytes_per_packet_stats_src2dst['stddev']
        flow.udps.src2dst_skewness_clumps_bytes_per_packet =  bytes_per_packet_stats_src2dst['skewness']
        flow.udps.src2dst_variance_clumps_bytes_per_packet =  bytes_per_packet_stats_src2dst['variance']
        flow.udps.src2dst_kurtosis_clumps_bytes_per_packet =  bytes_per_packet_stats_src2dst['kurtosis']

        #interarrival_time
        flow.udps.src2dst_max_clumps_interarrival_time =       interarrival_time_stats_src2dst['maximum']
        flow.udps.src2dst_min_clumps_interarrival_time =       interarrival_time_stats_src2dst['minimum']
        flow.udps.src2dst_mean_clumps_interarrival_time =      interarrival_time_stats_src2dst['mean']
        flow.udps.src2dst_stddev_clumps_interarrival_time =    interarrival_time_stats_src2dst['stddev']
        flow.udps.src2dst_skewness_clumps_interarrival_time =  interarrival_time_stats_src2dst['skewness']
        flow.udps.src2dst_variance_clumps_interarrival_time =  interarrival_time_stats_src2dst['variance']
        flow.udps.src2dst_kurtosis_clumps_interarrival_time =  interarrival_time_stats_src2dst['kurtosis']

        #dst2src
        #len
        flow.udps.dst2src_max_clumps_len =      len_stats_dst2src['maximum']
        flow.udps.dst2src_min_clumps_len =      len_stats_dst2src['minimum']
        flow.udps.dst2src_mean_clumps_len =     len_stats_dst2src['mean']
        flow.udps.dst2src_stddev_clumps_len =   len_stats_dst2src['stddev']
        flow.udps.dst2src_skewness_clumps_len = len_stats_dst2src['skewness']
        flow.udps.dst2src_variance_clumps_len = len_stats_dst2src['variance']
        flow.udps.dst2src_kurtosis_clumps_len = len_stats_dst2src['kurtosis']

        #size
        flow.udps.dst2src_max_clumps_size =      size_stats_dst2src['maximum']
        flow.udps.dst2src_min_clumps_size =      size_stats_dst2src['minimum']
        flow.udps.dst2src_mean_clumps_size =     size_stats_dst2src['mean']
        flow.udps.dst2src_stddev_clumps_size =   size_stats_dst2src['stddev']
        flow.udps.dst2src_skewness_clumps_size = size_stats_dst2src['skewness']
        flow.udps.dst2src_variance_clumps_size = size_stats_dst2src['variance']
        flow.udps.dst2src_kurtosis_clumps_size = size_stats_dst2src['kurtosis']

        #bytes_per_packet
        flow.udps.dst2src_max_clumps_bytes_per_packet =       bytes_per_packet_stats_dst2src['maximum']
        flow.udps.dst2src_min_clumps_bytes_per_packet =       bytes_per_packet_stats_dst2src['minimum']
        flow.udps.dst2src_mean_clumps_bytes_per_packet =      bytes_per_packet_stats_dst2src['mean']
        flow.udps.dst2src_stddev_clumps_bytes_per_packet =    bytes_per_packet_stats_dst2src['stddev']
        flow.udps.dst2src_skewness_clumps_bytes_per_packet =  bytes_per_packet_stats_dst2src['skewness']
        flow.udps.dst2src_variance_clumps_bytes_per_packet =  bytes_per_packet_stats_dst2src['variance']
        flow.udps.dst2src_kurtosis_clumps_bytes_per_packet =  bytes_per_packet_stats_dst2src['kurtosis']

        #interarrival_time
        flow.udps.dst2src_max_clumps_interarrival_time =       interarrival_time_stats_dst2src['maximum']
        flow.udps.dst2src_min_clumps_interarrival_time =       interarrival_time_stats_dst2src['minimum']
        flow.udps.dst2src_mean_clumps_interarrival_time =      interarrival_time_stats_dst2src['mean']
        flow.udps.dst2src_stddev_clumps_interarrival_time =    interarrival_time_stats_dst2src['stddev']
        flow.udps.dst2src_skewness_clumps_interarrival_time =  interarrival_time_stats_dst2src['skewness']
        flow.udps.dst2src_variance_clumps_interarrival_time =  interarrival_time_stats_dst2src['variance']
        flow.udps.dst2src_kurtosis_clumps_interarrival_time =  interarrival_time_stats_dst2src['kurtosis']

        #bidirectional clumps
        #len
        flow.udps.max_clumps_len =      len_stats['maximum']
        flow.udps.min_clumps_len =      len_stats['minimum']
        flow.udps.mean_clumps_len =     len_stats['mean']
        flow.udps.stddev_clumps_len =   len_stats['stddev']
        flow.udps.skewness_clumps_len = len_stats['skewness']
        flow.udps.variance_clumps_len = len_stats['variance']
        flow.udps.kurtosis_clumps_len = len_stats['kurtosis']

        #size
        flow.udps.max_clumps_size =      size_stats['maximum']
        flow.udps.min_clumps_size =      size_stats['minimum']
        flow.udps.mean_clumps_size =     size_stats['mean']
        flow.udps.stddev_clumps_size =   size_stats['stddev']
        flow.udps.skewness_clumps_size = size_stats['skewness']
        flow.udps.variance_clumps_size = size_stats['variance']
        flow.udps.kurtosis_clumps_size = size_stats['kurtosis']

        #bytes_per_packet
        flow.udps.max_clumps_bytes_per_packet =       bytes_per_packet_stats['maximum']
        flow.udps.min_clumps_bytes_per_packet =       bytes_per_packet_stats['minimum']
        flow.udps.mean_clumps_bytes_per_packet =      bytes_per_packet_stats['mean']
        flow.udps.stddev_clumps_bytes_per_packet =    bytes_per_packet_stats['stddev']
        flow.udps.skewness_clumps_bytes_per_packet =  bytes_per_packet_stats['skewness']
        flow.udps.variance_clumps_bytes_per_packet =  bytes_per_packet_stats['variance']
        flow.udps.kurtosis_clumps_bytes_per_packet =  bytes_per_packet_stats['kurtosis']

        #interarrival_time
        flow.udps.max_clumps_interarrival_time =       interarrival_time_stats['maximum']
        flow.udps.min_clumps_interarrival_time =       interarrival_time_stats['minimum']
        flow.udps.mean_clumps_interarrival_time =      interarrival_time_stats['mean']
        flow.udps.stddev_clumps_interarrival_time =    interarrival_time_stats['stddev']
        flow.udps.skewness_clumps_interarrival_time =  interarrival_time_stats['skewness']
        flow.udps.variance_clumps_interarrival_time =  interarrival_time_stats['variance']
        flow.udps.kurtosis_clumps_interarrival_time =  interarrival_time_stats['kurtosis']
        
        #Clump
        #src2dst
        #len
        flow.udps.src2dst_max_clump_len =       len_stats_src2dst_clump_max
        flow.udps.src2dst_min_clump_len =       len_stats_src2dst_clump_min
        flow.udps.src2dst_mean_clump_len =      len_stats_src2dst_clump_mean 
        flow.udps.src2dst_stddev_clump_len =    len_stats_src2dst_clump_stddev
        flow.udps.src2dst_skewness_clump_len =  len_stats_src2dst_clump_skewness
        flow.udps.src2dst_variance_clump_len =  len_stats_src2dst_clump_variance
        flow.udps.src2dst_kurtosis_clump_len =  len_stats_src2dst_clump_kurtosis

        #interarrival_time
        flow.udps.src2dst_max_clump_interarrival_time =       interarrival_time_stats_src2dst_clump_max
        flow.udps.src2dst_min_clump_interarrival_time =       interarrival_time_stats_src2dst_clump_min
        flow.udps.src2dst_mean_clump_interarrival_time =      interarrival_time_stats_src2dst_clump_mean 
        flow.udps.src2dst_stddev_clump_interarrival_time =    interarrival_time_stats_src2dst_clump_stddev
        flow.udps.src2dst_skewness_clump_interarrival_time =  interarrival_time_stats_src2dst_clump_skewness
        flow.udps.src2dst_variance_clump_interarrival_time =  interarrival_time_stats_src2dst_clump_variance
        flow.udps.src2dst_kurtosis_clump_interarrival_time =  interarrival_time_stats_src2dst_clump_kurtosis


        #dst2src
        #len
        flow.udps.dst2src_max_clump_len =       len_stats_dst2src_clump_max
        flow.udps.dst2src_min_clump_len =       len_stats_dst2src_clump_min
        flow.udps.dst2src_mean_clump_len =      len_stats_dst2src_clump_mean 
        flow.udps.dst2src_stddev_clump_len =    len_stats_dst2src_clump_stddev
        flow.udps.dst2src_skewness_clump_len =  len_stats_dst2src_clump_skewness
        flow.udps.dst2src_variance_clump_len =  len_stats_dst2src_clump_variance
        flow.udps.dst2src_kurtosis_clump_len =  len_stats_dst2src_clump_kurtosis

        #interarrival_time
        flow.udps.dst2src_max_clump_interarrival_time =       interarrival_time_stats_dst2src_clump_max
        flow.udps.dst2src_min_clump_interarrival_time =       interarrival_time_stats_dst2src_clump_min
        flow.udps.dst2src_mean_clump_interarrival_time =      interarrival_time_stats_dst2src_clump_mean 
        flow.udps.dst2src_stddev_clump_interarrival_time =    interarrival_time_stats_dst2src_clump_stddev
        flow.udps.dst2src_skewness_clump_interarrival_time =  interarrival_time_stats_dst2src_clump_skewness
        flow.udps.dst2src_variance_clump_interarrival_time =  interarrival_time_stats_dst2src_clump_variance
        flow.udps.dst2src_kurtosis_clump_interarrival_time =  interarrival_time_stats_dst2src_clump_kurtosis

        #bidirectional
        #len
        flow.udps.max_clump_len =       len_stats_clump_max
        flow.udps.min_clump_len =       len_stats_clump_min
        flow.udps.mean_clump_len =      len_stats_clump_mean 
        flow.udps.stddev_clump_len =    len_stats_clump_stddev
        flow.udps.skewness_clump_len =  len_stats_clump_skewness
        flow.udps.variance_clump_len =  len_stats_clump_variance
        flow.udps.kurtosis_clump_len =  len_stats_clump_kurtosis

        #interarrival_time
        flow.udps.max_clump_interarrival_time =       interarrival_time_stats_clump_max
        flow.udps.min_clump_interarrival_time =       interarrival_time_stats_clump_min
        flow.udps.mean_clump_interarrival_time =      interarrival_time_stats_clump_mean 
        flow.udps.stddev_clump_interarrival_time =    interarrival_time_stats_clump_stddev
        flow.udps.skewness_clump_interarrival_time =  interarrival_time_stats_clump_skewness
        flow.udps.variance_clump_interarrival_time =  interarrival_time_stats_clump_variance
        flow.udps.kurtosis_clump_interarrival_time =  interarrival_time_stats_clump_kurtosis

        #delete variables
        del flow.udps.direction
        del flow.udps.clump
        del flow.udps.src2dst_clumps
        del flow.udps.dst2src_clumps
        del flow.udps.clumps



#Clump class
class Clump:

    def __init__(self,direction):
        self.direction = direction
        self.size = 0
        self.len = 0
        self.len_stats = Statistics()
        self.bytes_per_packet = 0
        self.interarrival_time = 0
        self.interarrival_time_stats = Statistics()
        self.previous_time = 0

    def get_time_stats(self):
        stats = {}
        stats['maximum'] = self.interarrival_time_stats.maximum() if self.interarrival_time_stats._count > 0 else 0
        stats['minimum'] = self.interarrival_time_stats.minimum() if self.interarrival_time_stats._count > 0 else 0
        stats['mean'] = self.interarrival_time_stats.mean()
        stats['stddev'] = self.interarrival_time_stats.stddev() if self.interarrival_time_stats._count >= 2 else 0
        stats['skewness'] = self.interarrival_time_stats.skewness() if stats['stddev'] != 0 else 0
        stats['variance'] = self.interarrival_time_stats.variance() if self.interarrival_time_stats._count >= 2 else 0
        stats['kurtosis'] = self.interarrival_time_stats.kurtosis() if stats['stddev'] != 0 else 0
        return stats
    
    def get_len_stats(self):
        stats = {}
        stats['maximum'] = self.len_stats.maximum() if self.len_stats._count > 0 else 0
        stats['minimum'] = self.len_stats.minimum() if self.len_stats._count > 0 else 0
        stats['mean'] = self.len_stats.mean()
        stats['stddev'] = self.len_stats.stddev() if self.len_stats._count >= 2 else 0
        stats['skewness'] = self.len_stats.skewness() if stats['stddev'] != 0 else 0
        stats['variance'] = self.len_stats.variance() if self.len_stats._count >= 2 else 0
        stats['kurtosis'] = self.len_stats.kurtosis() if stats['stddev'] != 0 else 0
        return stats


    def update(self,size,time,len,bytes_per_packet):
        self.update_size(size)
        self.update_time(time)
        self.update_len(len)
        self.update_bytes_per_packet(bytes_per_packet)

    def update_size(self,value):
        self.size += value

    def update_time(self,value):
        self.interarrival_time = value

    def update_clump_time_stats(self,value):
        if self.previous_time == 0:
            self.previous_time = value
            value = 0.0
        else:
            temp = value - self.previous_time
            self.previous_time = value
            value = temp
        self.interarrival_time_stats.push(value)

    def update_len(self,value):
        self.len_stats.push(value)
        self.len += value

    def update_bytes_per_packet(self):
        self.bytes_per_packet = self.len_stats.mean()
    
    def get_size(self):
        return self.size

    def get_time(self):
        return self.interarrival_time

    def get_len(self):
        return self.len

    def get_bytes_per_packet(self):
        return self.bytes_per_packet

    #Clump class END

#Clumps class
class Clumps:
    
    def __init__(self):
        self.clumps = []
        self.size = Statistics() # number of packets
        self.len = Statistics() # bytes
        self.bytes_per_packet = Statistics()
        self.interarrival_time = Statistics()# interarrival_time

    def add_clump(self,clump):
        self.clumps.append(clump)

    def update(self,size,len,bytes_per_packet,time):
        self.update_size(size)
        self.update_len(len)
        self.update_bytes_per_packet(bytes_per_packet)
        self.update_time(time)

    def update_size(self,value):
        self.size.push(value)

    def update_time(self,value):
        self.interarrival_time.push(value)

    def update_len(self,value):
        self.len.push(value)

    def update_bytes_per_packet(self,value):
        self.bytes_per_packet.push(value)

    def get_clumps(self):
        return self.clumps

    def get_size_stats(self):
        stats = {}
        stats['maximum'] = self.size.maximum() if self.size._count > 0 else 0
        stats['minimum'] = self.size.minimum() if self.size._count > 0 else 0
        stats['mean'] = self.size.mean()
        stats['stddev'] = self.size.stddev() if self.size._count >= 2 else 0
        stats['skewness'] = self.size.skewness() if stats['stddev'] != 0 else 0
        stats['variance'] = self.size.variance() if self.size._count >= 2 else 0
        stats['kurtosis'] = self.size.kurtosis() if stats['stddev'] != 0 else 0
        return stats

  
    def get_time_stats(self):
        stats = {}
        stats['maximum'] = self.interarrival_time.maximum() if self.interarrival_time._count > 0 else 0
        stats['minimum'] = self.interarrival_time.minimum() if self.interarrival_time._count > 0 else 0
        stats['mean'] = self.interarrival_time.mean()
        stats['stddev'] = self.interarrival_time.stddev() if self.interarrival_time._count >= 2 else 0
        stats['skewness'] = self.interarrival_time.skewness() if stats['stddev'] != 0 else 0
        stats['variance'] = self.interarrival_time.variance() if self.interarrival_time._count >= 2 else 0
        stats['kurtosis'] = self.interarrival_time.kurtosis() if stats['stddev'] != 0 else 0
        return stats

    def get_len_stats(self):
        stats = {}
        stats['maximum'] = self.len.maximum() if self.len._count > 0 else 0
        stats['minimum'] = self.len.minimum() if self.len._count > 0 else 0
        stats['mean'] = self.len.mean()
        stats['stddev'] = self.len.stddev() if self.len._count >= 2 else 0
        stats['skewness'] = self.len.skewness() if stats['stddev'] != 0 else 0
        stats['variance'] = self.len.variance() if self.len._count >= 2 else 0
        stats['kurtosis'] = self.len.kurtosis() if stats['stddev'] != 0 else 0
        return stats

    def get_bytes_per_packet_stats(self):
        stats = {}
        stats['maximum'] = self.bytes_per_packet.maximum() if self.bytes_per_packet._count > 0 else 0
        stats['minimum'] = self.bytes_per_packet.minimum() if self.bytes_per_packet._count > 0 else 0
        stats['mean'] = self.bytes_per_packet.mean()
        stats['stddev'] = self.bytes_per_packet.stddev() if self.bytes_per_packet._count >= 2 else 0
        stats['skewness'] = self.bytes_per_packet.skewness() if stats['stddev'] != 0 else 0
        stats['variance'] = self.bytes_per_packet.variance() if self.bytes_per_packet._count >= 2 else 0
        stats['kurtosis'] = self.bytes_per_packet.kurtosis() if stats['stddev'] != 0 else 0
        return stats
#Clumps class END