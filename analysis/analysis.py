#!/usr/bin/env python3

import os
import sys
import glob
import pprint

from statistics import mean, stdev

import radical.analytics as ra

data = dict()
base = os.getcwd().split('/')[-1]

with open('results_%s_weak.dat'   % base, 'w') as f_weak, \
     open('results_%s_strong.dat' % base, 'w') as f_strong:

    header  = '# n_serv n_cli  n_req'
    header += '     comm_1      stdev'
    header += '       recv      stdev'
    header += '      parse      stdev'
    header += '      reply      stdev'
    header += '     comm_2      stdev'
    header += '      total      stdev'
    header += '\n'

    f_weak.write(header)
    f_strong.write(header)

    for f in sorted(list(glob.glob('*.prof'))):

        print(f)
        elems = f.split('.')

        n_services = int(elems[1][1:])
        n_clients  = int(elems[2][1:])
        n_requests = int(elems[3][1:])

        print(n_services, n_clients, n_requests)

        entities = dict()

        with open(f, 'r') as fin:
            for line in fin:
                if line[0] == '#':
                    continue
                elems = line.split(',')
                uid   = elems[4]

                if not uid.startswith('reg'):
                    continue

                if uid not in entities:
                    entities[uid] = dict()

                ts = float(elems[0])
                ev = elems[1]
                entities[uid][ev] = ts

        t_comm_1 = list()
        t_recv   = list()
        t_parse  = list()
        t_reply  = list()
        t_comm_2 = list()
        t_total  = list()

        missing = 0

        for uid, times in entities.items():

            try:
                t_comm_1.append(times['req_start']    - times['request_start'])
                t_recv.append  (times['req_received'] - times['req_start'])
                t_parse.append (times['req_parsed']   - times['req_received'])
                t_reply.append (times['rep_stop']     - times['req_parsed'])
                t_comm_2.append(times['request_stop'] - times['rep_stop'])
                t_total.append(times['request_stop']  - times['request_start'])

            except KeyError:
                missing += 1
                print(f, uid)
                pprint.pprint(times)

        print('Missing: %6d'   % missing)
        print('comm_1 : %10.6f +/- %10.6f' % (mean(t_comm_1), stdev(t_comm_1)))
        print('recv   : %10.6f +/- %10.6f' % (mean(t_recv  ), stdev(t_recv  )))
        print('parse  : %10.6f +/- %10.6f' % (mean(t_parse ), stdev(t_parse )))
        print('reply  : %10.6f +/- %10.6f' % (mean(t_reply ), stdev(t_reply )))
        print('comm_2 : %10.6f +/- %10.6f' % (mean(t_comm_2), stdev(t_comm_2)))
        print('total  : %10.6f +/- %10.6f' % (mean(t_total), stdev(t_total)))

        result  = ' %6d %6d %6d' % (n_services, n_clients, n_requests)
        result += ' %10.6f %10.6f' % (mean(t_comm_1), stdev(t_comm_1))
        result += ' %10.6f %10.6f' % (mean(t_recv  ), stdev(t_recv  ))
        result += ' %10.6f %10.6f' % (mean(t_parse ), stdev(t_parse ))
        result += ' %10.6f %10.6f' % (mean(t_reply ), stdev(t_reply ))
        result += ' %10.6f %10.6f' % (mean(t_comm_2), stdev(t_comm_2))
        result += ' %10.6f %10.6f' % (mean(t_total ), stdev(t_total ))
        result += '\n'

        if n_services == n_clients:
            f_weak.write(result)

        if n_clients == 16:
            f_strong.write(result)

