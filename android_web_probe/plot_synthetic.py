#! /usr/bin/env python

import os
import sys
import logging
import argparse
import numpy

sys.path.append('../myplot/')
import myplot

from analyze import PowerMonitorLog





def main():
    # will replace file paths with Log object
    http_bytes_to_log = {
        1000:'1kb-http.csv',
        10000:'10kb-http.csv',
        100000:'100kb-http.csv',
        1000000:'1mb-http.csv',
        10000000:'10mb-http.csv',
    }
    https_bytes_to_log = {
        1000:'1kb-https.csv',
        10000:'10kb-https.csv',
        100000:'100kb-https.csv',
        1000000:'1mb-https.csv',
        10000000:'10mb-https.csv',
    }

    # load files and make log objects
    for size in http_bytes_to_log:
        path = os.path.join(args.logdir, http_bytes_to_log[size])
        log = PowerMonitorLog(path)
        http_bytes_to_log[size] = log
    
    for size in https_bytes_to_log:
        path = os.path.join(args.logdir, https_bytes_to_log[size])
        log = PowerMonitorLog(path)
        https_bytes_to_log[size] = log

    # plot stuff
    sizes = sorted(http_bytes_to_log.keys())
    xsizes = numpy.array(sizes)/1000.0

    # energy consumed
    http_extra_energy = []
    https_extra_energy = []
    http_duration = []
    https_duration = []
    for size in sizes:
        http_log = http_bytes_to_log[size]
        http_extra_energy.append(http_log.above_baseline_energy_uAh)
        http_duration.append(http_log.duration_seconds)

        https_log = https_bytes_to_log[size]
        https_extra_energy.append(https_log.above_baseline_energy_uAh)
        https_duration.append(https_log.duration_seconds)

    myplot.plot([xsizes, xsizes, xsizes, xsizes],
        [http_extra_energy, https_extra_energy, http_duration, https_duration],
        labels=['HTTP Energy', 'HTTPS Energy', 'HTTP Time', 'HTTPS Time'],
        xlabel='File Size (KB)', ylabel='Energy Consumed (uAh)',
        num_series_on_addl_y_axis=2, additional_ylabels=['Time (s)'],
        xscale='log',
        filename=os.path.join(args.logdir, 'energy_consumption.pdf'))

    # average current
    http_mean_current = []
    https_mean_current = []
    http_stddev = []
    https_stddev = []
    for size in sizes:
        http_log = http_bytes_to_log[size]
        http_mean_current.append(http_log.mean_current - http_log.baseline)
        http_stddev.append(http_log.stddev_current)
        https_log = https_bytes_to_log[size]
        https_mean_current.append(https_log.mean_current - https_log.baseline)
        https_stddev.append(https_log.stddev_current)
    
    myplot.plot([xsizes, xsizes], [http_mean_current, https_mean_current],
        labels=['HTTP', 'HTTPS'], yerrs=[http_stddev, https_stddev],
        xlabel='File Size (KB)', ylabel='Mean Current (mA)',
        xscale='log',
        filename=os.path.join(args.logdir, 'mean_current.pdf'))
    

if __name__ == "__main__":
    # set up command line args
    parser = argparse.ArgumentParser(formatter_class=argparse.ArgumentDefaultsHelpFormatter,\
                                     description='Plot power results from synthetic benchmarks.')
    parser.add_argument('logdir', default='.', help='Directory of power monitor files.')
    parser.add_argument('-q', '--quiet', action='store_true', default=False, help='only print errors')
    parser.add_argument('-v', '--verbose', action='store_true', default=False, help='print debug info. --quiet wins if both are present')
    args = parser.parse_args()

    # set up logging
    if args.quiet:
        level = logging.WARNING
    elif args.verbose:
        level = logging.DEBUG
    else:
        level = logging.INFO
    logging.basicConfig(
        format = "%(levelname) -10s %(asctime)s %(module)s:%(lineno) -7s %(message)s",
        level = level
    )

    main()
