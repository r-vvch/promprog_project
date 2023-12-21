import argparse
import math
import pyshark
import matplotlib.pyplot as plt
from datetime import datetime
import os
import subprocess


class PacketInfo:
    def __init__(self, stream, length, time_relative):
        self.stream = int(stream)
        self.length = float(length)
        self.time_relative = float(time_relative)

    def __str__(self):
        return "% s % s % s" % (self.stream, self.length, self.time_relative)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Build graphs for network streams')
    parser.add_argument('path', type=str, help='Path to pcap file or directory with pcap files')
    parser.add_argument('protocol', nargs='?', type=str, default='TCP',
                        help='Protocol in interest: TCP, QUIC, UDP or \"any\" ')
    parser.add_argument('mode', nargs='?', type=str, default='grid', help='Graph type: grid or united plot')
    parser.add_argument('streams', nargs='?', type=str, default='all', help='Streams to be plotted, space-separated')
    parser.add_argument('time_unit', nargs='?', type=float, default=1.0, help='Time unit on the plot')
    args = parser.parse_args()

    time_unit = args.time_unit

    if os.path.isdir(args.path):
        for file in os.listdir(args.path):
            if os.path.splitext(file)[1] == ".pcap":
                subprocess.run(["python3", "netplt.py",
                                args.path + file, args.protocol, args.mode, args.streams, str(time_unit)])
            elif not os.path.isdir(args.path + "/" + file):
                print(file + " is not .pcap file")

    elif os.path.isfile(args.path):

        protocol = args.protocol

        if protocol == 'TCP' or protocol == 'tcp':
            pcap = pyshark.FileCapture(args.path, display_filter="tcp")
        elif protocol == 'QUIC' or protocol == 'quic':
            pcap = pyshark.FileCapture(args.path, display_filter="quic")
        elif protocol == 'UDP' or protocol == 'udp':
            pcap = pyshark.FileCapture(args.path, display_filter="udp")
        elif protocol == 'any':
            if args.mode == 'united':
                pcap = pyshark.FileCapture(args.path)
            else:
                print("Protocol option \"any\" can only be used with \"united\" plot mode")
                exit()
        else:
            print("Protocol not considered, using TCP")
            pcap = pyshark.FileCapture(args.path, display_filter="tcp")

        selected_streams = []
        selected_streams_str = args.streams
        if selected_streams_str != 'all':
            selected_streams = sorted([int(x) for x in selected_streams_str.split()])

        packet_storage = {}

        max_stream = 0
        max_time = 0.0
        min_time = float(pcap[0].sniff_timestamp)
        for packet in pcap:
            if float(packet.sniff_timestamp) < min_time:
                min_time = packet.sniff_timestamp
        for packet in pcap:
            packet_time = float(packet.sniff_timestamp) - min_time
            if protocol == 'TCP' or protocol == 'tcp':
                stream_num = int(packet.tcp.stream)
            elif protocol == 'QUIC' or protocol == 'quic' or protocol == 'UDP' or protocol == 'udp':
                stream_num = int(packet.udp.stream)
            else:
                if packet.transport_layer == 'UDP':
                    stream_num = int(packet.udp.stream)
                elif packet.transport_layer == 'TCP':
                    stream_num = int(packet.tcp.stream)
                else:
                    stream_num = -1

            if stream_num > max_stream:
                max_stream = stream_num
            if packet_time > max_time:
                max_time = packet_time
            if selected_streams_str == 'all' or stream_num in selected_streams:
                if stream_num not in packet_storage.keys():
                    packet_storage[stream_num] = []
                if protocol == 'TCP' or protocol == 'tcp':
                    packet_storage[stream_num].append(PacketInfo(stream_num, packet.tcp.len, packet_time))
                elif protocol == 'QUIC' or protocol == 'quic' or protocol == 'UDP' or protocol == 'udp':
                    packet_storage[stream_num].append(PacketInfo(stream_num, packet.udp.length, packet_time))
                else:
                    packet_storage[stream_num].append(PacketInfo(stream_num, packet.length, packet_time))

        if args.mode == "grid":

            all_streams = []
            for stream, stream_packets in packet_storage.items():
                all_streams.append(stream)

            if len(packet_storage) == 1:
                plt.rcParams["figure.figsize"] = (3, 3)
            elif len(packet_storage) == 2:
                plt.rcParams["figure.figsize"] = (6, 3)
            else:
                plt.rcParams["figure.figsize"] = (9, math.ceil(len(all_streams) / 3) * 3)

            x = args.path.split("/")
            plt.title(x[len(x) - 1].split(".")[0])

            pos = 1
            for stream, stream_packets in packet_storage.items():
                times = []
                lengths = []
                current_time = 0.0
                while current_time < max_time:
                    interval_length = 0.0
                    for packet in stream_packets:
                        if current_time < packet.time_relative < current_time + time_unit:
                            interval_length += packet.length
                    times.append(current_time)
                    lengths.append(interval_length)
                    current_time += time_unit
                if len(packet_storage) == 2:
                    plt.subplot(1, 2, pos)
                elif len(packet_storage) > 2:
                    plt.subplot(math.ceil(len(all_streams) / 3), 3, pos)

                times.append(max_time)
                plt.stairs(lengths, times, fill=True)
                plt.title(stream)
                plt.xlabel('time')
                if time_unit == 1:
                    plt.ylabel('bits/sec')
                else:
                    plt.ylabel('bits/' + str(time_unit) + 'sec')
                pos += 1

            plt.tight_layout()

            now = datetime.now()
            now.replace(microsecond=0)

            plt.savefig('streams_graph_grid_' + x[len(x) - 1].split(".")[0] + '.png')

        elif args.mode == "united":
            plt.rcParams["figure.figsize"] = (6, 6)

            pos = 1
            for stream, stream_packets in packet_storage.items():
                times = []
                lengths = []
                current_time = 0
                while current_time < max_time:
                    interval_length = 0
                    for packet in stream_packets:
                        if current_time < packet.time_relative < current_time + time_unit:
                            interval_length += packet.length
                    times.append(current_time)
                    lengths.append(interval_length)
                    current_time += time_unit
                times.append(max_time)
                if stream != -1:
                    plt.stairs(lengths, times, fill=True, label=stream)
                else:
                    plt.stairs(lengths, times, fill=True, label="undefined")
                pos += 1

            if (selected_streams_str == 'all' and max_stream < 22) or (0 < len(selected_streams) < 22):
                lgd = plt.legend(bbox_to_anchor=(1, 1), loc='upper left')
            else:
                lgd = plt.legend(ncol=math.ceil((max_stream + 1) / 21), bbox_to_anchor=(1, 1), loc='upper left')
            plt.xlabel('time')
            if time_unit == 1:
                plt.ylabel('bits/sec')
            else:
                plt.ylabel('bits/' + str(time_unit) + 'sec')
            now = datetime.now()
            now.replace(microsecond=0)
            x = args.path.split("/")
            plt.title(x[len(x) - 1].split(".")[0])

            plt.savefig('streams_graph_united_' + x[len(x) - 1].split(".")[0] + '.png', bbox_extra_artists=(lgd,),
                        bbox_inches='tight')

        else:
            print("Wrong input, specify mode")

    else:
        print("Wrong path")
