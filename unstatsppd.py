#!/usr/bin/env python
# coding: utf-8
#
# Copyright (c) 2011 Xavier Santolaria <xavier@santolaria.net>
#
# Permission to use, copy, modify, and distribute this software for any
# purpose with or without fee is hereby granted, provided that the above
# copyright notice and this permission notice appear in all copies.
#
# THE SOFTWARE IS PROVIDED "AS IS" AND THE AUTHOR DISCLAIMS ALL WARRANTIES
# WITH REGARD TO THIS SOFTWARE INCLUDING ALL IMPLIED WARRANTIES OF
# MERCHANTABILITY AND FITNESS. IN NO EVENT SHALL THE AUTHOR BE LIABLE FOR
# ANY SPECIAL, DIRECT, INDIRECT, OR CONSEQUENTIAL DAMAGES OR ANY DAMAGES
# WHATSOEVER RESULTING FROM LOSS OF USE, DATA OR PROFITS, WHETHER IN AN
# ACTION OF CONTRACT, NEGLIGENCE OR OTHER TORTIOUS ACTION, ARISING OUT OF
# OR IN CONNECTION WITH THE USE OR PERFORMANCE OF THIS SOFTWARE.

import getpass
import time
import untappd

from optparse import OptionParser
from pygooglechart import PieChart2D


MY_UNTAPPD_API_KEY = ""
UNTAPPD_DFLT_OFFSET = 25

PIECHART_OUTFILE = 'unstatsppd-pie.png'

dayofWeek = ('Monday', 'Tuesday', 'Wednesday', 'Thursday',
             'Friday', 'Saturday', 'Sunday')


def main():
    parser = OptionParser(usage="usage: %prog [options]", version="%prog 0.1")
    parser.add_option("-a", "--auth",
                      action="store_true",
                      dest="auth",
                      help="use authenticated mechanism")
    parser.add_option("-u", "--user",
                      action="store",
                      dest="username",
                      help="specify username to query data from")
    (options, args) = parser.parse_args()

    if options.username is None:   # Username is required
        parser.error('Username not given')

    user = options.username
    passwd = None

    if options.auth is not None:
        passwd = getpass.getpass()
        if not passwd:
            sys.exit("Error: no password entered.")

    c = count = 0

    u = untappd.Api(MY_UNTAPPD_API_KEY, user, passwd)

    # Get the days from the beers checkins
    days = get_user_days(u, user)

    # Create a chart object of 400x200 pixels
    chart = PieChart2D(400, 200)

    pie_labels = [] ; pie_data = []

    for k, v in days.iteritems():
        pie_data.append(v)
        label = "%s (%dX)" % (dayofWeek[k], v)
        pie_labels.append(label)
        
    # Add data
    chart.add_data(pie_data)
    # Add the labels to the pie data
    chart.set_pie_labels(pie_labels)

    #print chart.get_url()

    chart.download(PIECHART_OUTFILE)



def get_user_days(u, user):
    days = {}
    offset = 0 ; i = 0

    while True:
        data = u.get_user_feed(**{'user': user, 'offset': offset})

        for result in data['results']:
            tstamp = result.get('created_at')

            # Format: Mon, 06 Jun 2011 22:30:24 +0000
            struct_time = time.strptime(tstamp, "%a, %d %b %Y %H:%M:%S +0000")
            days[struct_time.tm_wday] = days.get(struct_time.tm_wday, 0) + 1

        if data.get('next_page'):
            offset = offset + UNTAPPD_DFLT_OFFSET
        else:
            break 

    return days


if __name__ == "__main__":
    main()
