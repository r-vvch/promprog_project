# promprog_project

Project for industrial programming course

## classification

Classifiers and data preparation

```
usage:

python3 data_praparation.py

python3 classifier.py

```

## plots

PACP streams visualising tool

Required packages: tshark, matplotlib

```
usage: python3 plotter.py [-h] path [protocol] [mode] [streams] [time_unit]

Build graphs for network streams

positional arguments:
  path        Path to pcap file or directory with pcap files
  protocol    Protocol in interest: TCP, QUIC, UDP or "any"
  mode        Graph type: grid or united plot
  streams     Streams to be plotted, space-separated
  time_unit   Time unit on the plot

optional arguments:
  -h, --help  show this help message and exit
```

Work examples:

![grid](plots/streams_graph_grid_test.png)

![united](plots/streams_graph_united_test.png)
