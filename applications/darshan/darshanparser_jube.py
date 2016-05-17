#!/usr/bin/env python3
"""
This script is running the darshan-parser with the output file of the darshan
profiling tool.

- requires the output file of the darshan profiling tool as an argument
"""
from __future__ import print_function, division
import argparse
#import subprocess
from subprocess import Popen
from subprocess import PIPE
import shlex
import numpy as np
import re
from itertools import groupby


def io_percentage(nprocs, runtime, counters, data, out_file):
    """
    calculates average I/O cost per process (top left histogram of darshan pdf)

    :param nprocs: number of processes
    :param runtime: application runtime
    :param counters: mask for counters in data
    :param data: data generated by darshan-parser
    :param out_file: file handle for output file
    :return:
    """
    posix_read_time = data[counters["CP_F_POSIX_READ_TIME"]]["value"]
    posix_write_time = data[counters["CP_F_POSIX_WRITE_TIME"]]["value"]
    posix_meta_time = data[counters["CP_F_POSIX_META_TIME"]]["value"]

    posix_read_sum = np.sum(posix_read_time)
    posix_write_sum = np.sum(posix_write_time)
    posix_meta_sum = np.sum(posix_meta_time)

    posix_read_perc = (posix_read_sum/(runtime*nprocs))*100
    posix_write_perc = (posix_write_sum/(runtime*nprocs))*100
    posix_meta_perc = (posix_meta_sum/(runtime*nprocs))*100

    posix_io_time = (posix_read_perc + posix_write_perc + posix_meta_perc)/100 * runtime

    posix_other = ((runtime*nprocs - posix_read_sum -
                   posix_write_sum - posix_meta_sum)/(runtime*nprocs))*100

    posix = ["POSIX:", str(posix_other), str(posix_read_perc),
             str(posix_write_perc), str(posix_meta_perc)]

    mpi_read_time = data[counters["CP_F_MPI_READ_TIME"]]["value"]
    mpi_write_time = data[counters["CP_F_MPI_WRITE_TIME"]]["value"]
    mpi_meta_time = data[counters["CP_F_MPI_META_TIME"]]["value"]

    mpi_read_sum = np.sum(mpi_read_time)
    mpi_write_sum = np.sum(mpi_write_time)
    mpi_meta_sum = np.sum(mpi_meta_time)

    mpi_read_perc = (mpi_read_sum/(runtime*nprocs))*100
    mpi_write_perc = (mpi_write_sum/(runtime*nprocs))*100
    mpi_meta_perc = (mpi_meta_sum/(runtime*nprocs))*100

    mpi_io_time = (mpi_read_perc + mpi_write_perc + mpi_meta_perc)/100 * runtime

    mpi_other = ((runtime*nprocs - mpi_read_sum -
                  mpi_write_sum - mpi_meta_sum)/(runtime*nprocs))*100

    mpi = ["MPI-IO:", str(mpi_other), str(mpi_read_perc),
           str(mpi_write_perc), str(mpi_meta_perc)]

    table_head = ["", "other", "read", "write", "metadata"]

    io_table = [table_head, posix, mpi]
    table_head = "Average I/O cost per process"
    write_jube_table(table_head, io_table)

    for elem in posix:
        out_file.write('{0} '.format(elem))
    out_file.write('\n')
    for elem in mpi:
        out_file.write('{0} '.format(elem))
    out_file.write('\n')

    total_io_time = mpi_io_time if mpi_io_time > posix_io_time else posix_io_time
    out_file.write('io_time: {0}\n\n'.format(total_io_time))


def operation_counts(counters, data, out_file):
    """
    creates a table for the io operation counts
    (in darshan_job_summary first page, first row, second column)

    :param counters: mask for counters in data
    :param data: data generated by darshan-parser
    :param out_file: file handle for output file
    :return:
    """

    posix_opens = data[counters["CP_POSIX_OPENS"]]["value"]
    posix_fopens = data[counters["CP_POSIX_FOPENS"]]["value"]
    posix_fsyncs = data[counters["CP_POSIX_FSYNCS"]]["value"]
    posix_fdsyncs = data[counters["CP_POSIX_FDSYNCS"]]["value"]

    posix_reads = data[counters["CP_POSIX_READS"]]["value"]
    posix_freads = data[counters["CP_POSIX_FREADS"]]["value"]
    indep_reads = data[counters["CP_INDEP_READS"]]["value"]
    coll_reads = data[counters["CP_COLL_READS"]]["value"]
    posix_writes = data[counters["CP_POSIX_WRITES"]]["value"]
    posix_fwrites = data[counters["CP_POSIX_FWRITES"]]["value"]
    indep_writes = data[counters["CP_INDEP_WRITES"]]["value"]
    coll_writes = data[counters["CP_COLL_WRITES"]]["value"]
    indep_opens = data[counters["CP_INDEP_OPENS"]]["value"]
    coll_opens = data[counters["CP_COLL_OPENS"]]["value"]
    posix_stats = data[counters["CP_POSIX_STATS"]]["value"]
    posix_seeks = data[counters["CP_POSIX_SEEKS"]]["value"]
    posix_mmaps = data[counters["CP_POSIX_MMAPS"]]["value"]

    sum_posix_reads = np.sum(posix_reads) + np.sum(posix_freads)
    sum_indep_reads = np.sum(indep_reads)
    sum_coll_reads = np.sum(coll_reads)
    sum_posix_writes = np.sum(posix_writes) + np.sum(posix_fwrites)
    sum_indep_writes = np.sum(indep_writes)
    sum_coll_writes = np.sum(coll_writes)
    sum_posix_opens = np.sum(posix_opens) + np.sum(posix_fopens)
    sum_indep_opens = np.sum(indep_opens)
    sum_coll_opens = np.sum(coll_opens)
    sum_posix_stats = np.sum(posix_stats)
    sum_posix_seeks = np.sum(posix_seeks)
    sum_posix_mmaps = np.sum(posix_mmaps)
    sum_posix_fsyncs = np.sum(posix_fsyncs) + np.sum(posix_fdsyncs)

    reads = ['Read', int(sum_posix_reads), int(sum_indep_reads), int(sum_coll_reads)]
    writes = ['Write', int(sum_posix_writes), int(sum_indep_writes), int(sum_coll_writes)]
    opens = ['Open', int(sum_posix_opens), int(sum_indep_opens), int(sum_coll_opens)]
    stats = ['Stat', int(sum_posix_stats), 0, 0]
    seeks = ['Seek', int(sum_posix_seeks), 0, 0]
    mmaps = ['Mmap', int(sum_posix_mmaps), 0, 0]
    syncs = ['FSync', int(sum_posix_fsyncs), 0, 0]

    out_file.write('# read write open stats seeks mmaps fsyncs\n')
    out_file.write('posix calls: {0} {1} {2} {3} {4} {5} {6}\n\n'.format(
        int(sum_posix_reads), int(sum_posix_writes), int(sum_posix_opens),
        int(sum_posix_stats), int(sum_posix_seeks), int(sum_posix_mmaps),
        int(sum_posix_fsyncs)))

    col_head = ['', 'POSIX', 'MPI-IO Indep.', 'MPI-IO Coll.']
    op_cnt_table = [col_head, reads, writes, opens, stats, seeks, mmaps, syncs]
    op_cnt_table = [[str(col) for col in row] for row in op_cnt_table]
    table_head = "I/O Operation Counts"
    write_jube_table(table_head, op_cnt_table)


def io_sizes(counters, data):
    """
    creates a table that includes the io size counts
    (in darshan_job_summary first page, second row, first column)

    :param counters: mask for counters in data
    :param data: data generated by darshan-parser
    :return:
    """

    column_heads = ['0-100', '100-1K', '1K-10K', '10K-100K', '100K-1M',
                    '1M-4M', '4M-10M', '10M-100M', '100M-1G', '1G+']
    counter_sizes = [col.replace('-', '_').replace('+', '_PLUS')
                     for col in column_heads]
    read_counter = 'CP_SIZE_READ_{0}'
    write_counter = 'CP_SIZE_WRITE_{0}'

    read_cnt_str = [read_counter.format(size) for size in counter_sizes]
    write_cnt_str = [write_counter.format(size) for size in counter_sizes]
    reads = [str(int(np.sum(data[counters[read_cnt]]["value"])))
             for read_cnt in read_cnt_str]
    writes = [str(int(np.sum(data[counters[write_cnt]]["value"])))
              for write_cnt in write_cnt_str]
    reads.insert(0, 'Read')
    writes.insert(0, 'Write')
    column_heads.insert(0, '')
    table_head = 'I/O Sizes'
    io_size_table = [column_heads, reads, writes]
    write_jube_table(table_head, io_size_table)


def io_pattern(counters, data):
    """
    creates a table that includes the io pattern
    (in darshan_job_summary first page, second row, second column)

    :param counters: mask for counters in data
    :param data: data generated by darshan-parser
    :return:
    """
    posix_reads = int(np.sum(data[counters["CP_POSIX_READS"]]["value"]))
    posix_freads = int(np.sum(data[counters["CP_POSIX_FREADS"]]["value"]))
    seq_reads = int(np.sum(data[counters["CP_SEQ_READS"]]["value"]))
    consec_reads = int(np.sum(data[counters["CP_CONSEC_READS"]]["value"]))

    posix_writes = int(np.sum(data[counters["CP_POSIX_WRITES"]]["value"]))
    posix_fwrites = int(np.sum(data[counters["CP_POSIX_FWRITES"]]["value"]))
    seq_writes = int(np.sum(data[counters["CP_SEQ_WRITES"]]["value"]))
    consec_writes = int(np.sum(data[counters["CP_CONSEC_WRITES"]]["value"]))

    column_heads = ['', 'Total', 'Sequential', 'Consecutive']
    reads = ['Read', str(posix_reads + posix_freads),
             str(seq_reads), str(consec_reads)]
    writes = ['Write', str(posix_writes + posix_fwrites),
              str(seq_writes), str(consec_writes)]
    pattern_table = [column_heads, reads, writes]
    table_head = 'I/O Pattern'
    write_jube_table(table_head, pattern_table)


def access_size(counters, data, out_file, length=4):
    """
    calculates the 4 most common access sizes (bottom left table of darshan pdf)

    :param counters: mask for counters in data
    :param data: data generated by darshan-parser
    :param out_file: file handle for output file
    :param length: number of entries in the output table
    :return:
    """

    # get the four most common access sizes of each file
    ac_size = np.array([data[counters["CP_ACCESS{0}_ACCESS".format(i)]]["value"]
                        for i in range(1, 5)], np.int)
    # get the count of the four most common access sizes of each file
    ac_cnt = np.array([data[counters["CP_ACCESS{0}_COUNT".format(i)]]["value"]
                       for i in range(1, 5)], np.int)
    merged = np.array(zip(ac_size.flatten(), ac_cnt.flatten()))
    ac_sorted = merged[np.argsort(merged[:, 0])]
    # get different access sizes
    ac_val = [key for key, group in groupby(ac_sorted[:, 0])]
    # sum up the count of each access size (sorted by increasing access size
    cnt_sum = np.array([[val, np.sum(ac_sorted[ac_sorted[:, 0] == val][:, 1])]
                       for val in ac_val])
    # cnt_sum sorted by decreasing access counter
    cnt_sum_sort = cnt_sum[np.argsort(cnt_sum[:, 1])[::-1]]

    length = length if length > 0 else len(cnt_sum_sort)

    most_common_ac = [[str(cell) for cell in row]
                      for row in cnt_sum_sort[:length]]
    most_common_titel = ['access size', 'count']
    most_common_ac.insert(0, most_common_titel)

    table_head = "Most Common Access Sizes"
    write_jube_table(table_head, most_common_ac)

    out_file.write('# {0}:\n'.format(table_head))
    for i, title in enumerate(most_common_titel):
        out_file.write('{0}: '.format(title))
        for elem in np.array(most_common_ac[1:]).T[i]:
            out_file.write("{0} ".format(elem))
        out_file.write('\n')

    avg_io_ac_size = np.inner(cnt_sum_sort[:, 0], cnt_sum_sort[:, 1]) / \
                     np.sum(cnt_sum_sort[:, 1])
    out_file.write('avg_io_ac_size: {0}\n'.format(avg_io_ac_size))
    out_file.write('\n')


def file_cnt_summary(file_hash, counters, data):
    """
    file count summary (bottom right table in darshan pdf)

    :param file_hash:
    :param counters: mask for counters in data
    :param data: data generated by darshan-parser
    :return:
    """
    max_bytes_read = data[counters["CP_MAX_BYTE_READ"]]["value"]
    max_bytes_written = data[counters["CP_MAX_BYTE_WRITTEN"]]["value"]
    size_at_open = data[counters["CP_SIZE_AT_OPEN"]]["value"]
    size_at_open[size_at_open == -1] = 0

    # POSIX
    posix_read = data[counters["CP_POSIX_READS"]]["value"]
    posix_fread = data[counters["CP_POSIX_FREADS"]]["value"]
    posix_write = data[counters["CP_POSIX_WRITES"]]["value"]
    posix_fwrite = data[counters["CP_POSIX_FWRITES"]]["value"]

    # MPI-IO
    indep_opens = data[counters["CP_INDEP_OPENS"]]["value"]
    coll_opens = data[counters["CP_COLL_OPENS"]]["value"]
    indep_reads = data[counters["CP_INDEP_READS"]]["value"]
    coll_reads = data[counters["CP_COLL_READS"]]["value"]
    split_reads = data[counters["CP_SPLIT_READS"]]["value"]
    nb_reads = data[counters["CP_NB_READS"]]["value"]
    indep_writes = data[counters["CP_INDEP_WRITES"]]["value"]
    coll_writes = data[counters["CP_COLL_WRITES"]]["value"]
    split_writes = data[counters["CP_SPLIT_WRITES"]]["value"]
    nb_writes = data[counters["CP_NB_WRITES"]]["value"]

    # get the minimum CP_SIZE_AT_OPEN (min_open_size) and the maximum of
    # CP_MAX_BYTE_READ/WRITTEN (max_size) for each hash(file) and
    # decide if it was_read and/or was_written
    hash_files = dict()
    for i, f_hash in enumerate(file_hash):
        max_tmp = np.max([max_bytes_read[i]+1, max_bytes_written[i]+1])
        if f_hash not in hash_files.keys():
            hash_files[f_hash] = {"min_open_size": size_at_open[i],
                                  "max_size": max_tmp,
                                  "was_read": False,
                                  "was_written": False}
        else:
            if hash_files[f_hash]["min_open_size"] > size_at_open[i]:
                hash_files[f_hash]["min_open_size"] = size_at_open[i]
            if hash_files[f_hash]["max_size"] < max_tmp:
                hash_files[f_hash]["max_size"] = max_tmp

        if (indep_opens[i] > 0) or (coll_opens[i] > 0):
            # mpi file
            if (indep_reads[i] > 0) or (coll_reads[i] > 0) or \
                    (split_reads[i] > 0) or (nb_reads[i] > 0):
                hash_files[f_hash]['was_read'] = True
            if (indep_writes[i] > 0) or (coll_writes[i] > 0) or \
                    (split_writes[i] > 0) or (nb_writes[i] > 0):
                hash_files[f_hash]['was_written'] = True
        else:
            # posix file
            if (posix_read[i] > 0) or (posix_fread[i] > 0):
                hash_files[f_hash]['was_read'] = True
            if (posix_write[i] > 0) or (posix_fwrite[i] > 0):
                hash_files[f_hash]['was_written'] = True

    max_size = np.array([hash_files[key]['max_size']
                         for key in hash_files.keys()])
    min_open_size = np.array([hash_files[key]['min_open_size']
                              for key in hash_files.keys()])
    was_read = np.array([hash_files[key]['was_read']
                         for key in hash_files.keys()])
    was_written = np.array([hash_files[key]['was_written']
                            for key in hash_files.keys()])

    # total opened
    total = np.array([True]*len(hash_files))
    # read only files
    read_only = (was_read == True) & (was_written == False)
    # write only files
    write_only = (was_read == False) & (was_written == True)
    # read and write files
    read_write = (was_read == True) & (was_written == True)
    # created files
    create = (was_written == True) & (min_open_size == 0) & (max_size > 0)

    table_rows = [['total opened', total], ['read-only files', read_only],
                  ['write-only files', write_only],
                  ['read/write files', read_write], ['created files', create]]

    f_cnt_sum_title = [['', 'number of files', 'avg. size', 'max size']]
    table_str = f_cnt_sum_title
    for row in table_rows:
        #mb = True if row[0] != 'write-only files' else False
        cnt, avg, max_val = get_cnt_avg_max(row[1], max_size,
                                            min_open_size, False)
        table_str.append([row[0], str(int(np.ceil(cnt))),
                          str(int(np.ceil(avg))), str(int(np.ceil(max_val)))])
    table_head = 'File Count I/O Summary'
    write_jube_table(table_head, table_str)


def get_cnt_avg_max(mask, max_size, min_open_size, mb=True):
    """
    calculates count, average and max value depending on the mask

    :param mask: boolean array
    :param max_size:
    :param min_open_size:
    :param mb: convert avg and max value into MB
    :return:
    """

    mb = 2**20 if mb else 1
    count = len(max_size[mask])
    if count == 0:
        avg = 0
        max_value = 0
    else:
        max_elem = np.maximum(max_size[mask], min_open_size[mask])
        avg = np.sum(max_elem)/count/mb
        max_value = np.max([max_size[mask], min_open_size[mask]])/mb

    return count, avg, max_value


def avg_io(nprocs, ranks, counters, data, out_file):
    """
    average cumulative time spent in i/o functions and average amount of i/o
    for independent/shared reads/writes/metadata.
    (table on darshan pdf second page)

    :param nprocs: number of processes
    :param ranks: rank that opened the file/counter
    :param counters: mask for counters in data
    :param data: data generated by darshan-parser
    :param out_file: file handle for output file
    :return:
    """
    mb = 2**20

    posix_read_time = data[counters["CP_F_POSIX_READ_TIME"]]["value"]
    posix_write_time = data[counters["CP_F_POSIX_WRITE_TIME"]]["value"]
    posix_meta_time = data[counters["CP_F_POSIX_META_TIME"]]["value"]
    bytes_read = data[counters["CP_BYTES_READ"]]["value"]
    bytes_written = data[counters["CP_BYTES_WRITTEN"]]["value"]

    indep_reads_avg = np.sum(posix_read_time[ranks != -1]/nprocs)
    indep_read_bytes_avg = np.sum(bytes_read[ranks != -1]/nprocs)/mb
    indep_writes_avg = np.sum(posix_write_time[ranks != -1]/nprocs)
    indep_written_bytes_avg = np.sum(bytes_written[ranks != -1]/nprocs)/mb
    indep_meta_avg = np.sum(posix_meta_time[ranks != -1]/nprocs)

    shared_reads_avg = np.sum(posix_read_time[ranks == -1]/nprocs)
    shared_read_bytes_avg = np.sum(bytes_read[ranks == -1]/nprocs)/mb
    shared_writes_avg = np.sum(posix_write_time[ranks == -1]/nprocs)
    shared_written_bytes_avg = np.sum(bytes_written[ranks == -1]/nprocs)/mb
    shared_meta_avg = np.sum(posix_meta_time[ranks == -1]/nprocs)

    avg_io_table = [[indep_reads_avg, indep_read_bytes_avg],
                    [indep_writes_avg, indep_written_bytes_avg],
                    [indep_meta_avg, np.nan],
                    [shared_reads_avg, shared_read_bytes_avg],
                    [shared_writes_avg, shared_written_bytes_avg],
                    [shared_meta_avg, np.nan]]
    avg_io_table_str = [[str(np.around(cell, decimals=6)) for cell in row]
                        for row in avg_io_table]

    title = ['cumul_avg_io_time', 'avg_amout_io']
    for i, row in enumerate(np.array(avg_io_table_str).T):
        out_file.write('{0}: '.format(title[i]))
        for elem in row:
            out_file.write('{0} '.format(elem))
        out_file.write('\n')

    avg_table_titel = ['Cumulative time spent in I/O functions (seconds)',
                       'Amount of I/O (MB)']
    avg_io_table_str.insert(0, avg_table_titel)

    #a = ['', 'Independent reads', 'Independent writes', 'Independent metadada',
    #     'Shared reads', 'Shared writes', 'Shared metadata']
    #avg_io_table_str = [np.insert(row, 0, a[i])
    #                    for i, row in enumerate(avg_io_table_str)]

    table_head = "Average I/O per process"
    write_jube_table(table_head, avg_io_table_str)

    # calculate independent/shared read/write bandwidth
    if indep_reads_avg != 0:
        in_r_bw = np.around(indep_read_bytes_avg/indep_reads_avg*nprocs, 2)
    else:
        in_r_bw = 0.
    if indep_writes_avg != 0:
        in_w_bw = np.around(indep_written_bytes_avg/indep_writes_avg*nprocs, 2)
    else:
        in_w_bw = 0.

    if shared_reads_avg != 0:
        sh_r_bw = np.around(shared_read_bytes_avg/shared_reads_avg*nprocs, 2)
    else:
        sh_r_bw = 0.
    if shared_writes_avg != 0:
        sh_w_bw = np.around(shared_written_bytes_avg/shared_writes_avg*nprocs, 2)
    else:
        sh_w_bw = 0.

    # write information into the output file
    out_file.write('# Bandwidth: read write\n')
    out_file.write('Independent Bandwidth: {0} {1}\n'.format(in_r_bw, in_w_bw))
    out_file.write('Shared Bandwidth: {0} {1}\n'.format(sh_r_bw, sh_w_bw))

    total_mb_read = np.sum(bytes_read)/mb
    total_mb_written = np.sum(bytes_written)/mb
    out_file.write('# I/O Volume:\n')
    out_file.write('Total MB read: {0}\n'.format(total_mb_read))
    out_file.write('Total MB written: {0}\n'.format(total_mb_written))
    out_file.write('\n')


def data_transfer(counters, data, mount_pt):
    """

    :param counters:
    :param data:
    :param mount_pt:
    :return:
    """

    bytes_read = data[counters["CP_BYTES_READ"]]["value"]
    bytes_written = data[counters["CP_BYTES_WRITTEN"]]["value"]
    filesystems = set(mount_pt)

    byte_table = [[str(key), str(int(np.sum(bytes_written[mount_pt == key]))),
                   str(int(np.sum(bytes_read[mount_pt == key])))]
                  for key in filesystems]

    table_head = "Data Transfer Per Filesystem"
    column_heads = ['File System', 'write', 'read']

    # test output converted to MB
    #mb_out = [[i[0], str(np.around(float(i[1])/2**20, 5)),
    #           str(np.around(float(i[2])/2**20, 5))] for i in byte_table]
    #mb_out.insert(0, column_heads)
    #print(mb_out)
    #write_jube_table(table_head, mb_out)

    byte_table.insert(0, column_heads)
    #print(byte_table)
    write_jube_table(table_head, byte_table)

    # read/write/metadata time spent in each file system
    mpi_read_time = data[counters["CP_F_MPI_READ_TIME"]]["value"]
    mpi_write_time = data[counters["CP_F_MPI_WRITE_TIME"]]["value"]
    mpi_meta_time = data[counters["CP_F_MPI_META_TIME"]]["value"]
    posix_read_time = data[counters["CP_F_POSIX_READ_TIME"]]["value"]
    posix_write_time = data[counters["CP_F_POSIX_WRITE_TIME"]]["value"]
    posix_meta_time = data[counters["CP_F_POSIX_META_TIME"]]["value"]

    table_head = "Time For Data Transfer Per Filesystem"
    column_heads = ['File System', 'mpi_read', 'mpi_write', 'mpi_meta',
                    'posix_read', 'posix_write', 'posix_meta']
    time_table = [[str(key), str(np.sum(mpi_read_time[mount_pt == key])),
                   str(np.sum(mpi_write_time[mount_pt == key])),
                   str(np.sum(mpi_meta_time[mount_pt == key])),
                   str(np.sum(posix_read_time[mount_pt == key])),
                   str(np.sum(posix_write_time[mount_pt == key])),
                   str(np.sum(posix_meta_time[mount_pt == key]))]
                  for key in filesystems]
    time_table.insert(0, column_heads)
    write_jube_table(table_head, time_table)


def create_ind_sha_table(nprocs, ranks, file_hash, counters, data, mount_pt):
    """
    creates a table containing every independent file and a table containing
    every shared file, because the darshan-job-summary.pl shows statistics of
    only 20 files.

    :param nprocs: number of processes
    :param ranks: rank corresponding to files in data
    :param file_hash: has for every file in data
    :param counters: mask for counters in data
    :param data: data generated by darshan-parser
    :param mount_pt:
    :return:
    """

    name = data[counters["CP_F_OPEN_TIMESTAMP"]]["name_suffix"]
    read_start_time = data[counters["CP_F_READ_START_TIMESTAMP"]]["value"]
    read_end_time = data[counters["CP_F_READ_END_TIMESTAMP"]]["value"]
    posix_read_time = data[counters["CP_F_POSIX_READ_TIME"]]["value"]
    write_start_time = data[counters["CP_F_WRITE_START_TIMESTAMP"]]["value"]
    write_end_time = data[counters["CP_F_WRITE_END_TIMESTAMP"]]["value"]
    posix_write_time = data[counters["CP_F_POSIX_WRITE_TIME"]]["value"]

    file_count = [list(file_hash).count(i) for i in file_hash]

    file_count = [nprocs if r == -1 else file_count[i]
                  for i, r in enumerate(ranks)]

    collected_dtype = [("rank", np.int), ("name_suffix", object),
                       ("file_cnt", np.int), ("rstart", np.float64),
                       ("rend", np.float64), ("maxr", np.float64),
                       ("wstart", np.float64), ("wend", np.float64),
                       ("maxw", np.float64), ("mount_pt", object)]
    collected_data = zip(ranks, name, file_count, read_start_time,
                         read_end_time, posix_read_time, write_start_time,
                         write_end_time, posix_write_time, mount_pt)
    collected_data = np.array(collected_data, dtype=collected_dtype)

    table_headline = [['rank', 'file_suffix', 'np', 'read_start', 'read_end',
                      'cumul_read', 'write_start', 'write_end', 'cumul_write',
                       'mount_pt']]

    indep_data = collected_data[collected_data["rank"] != -1]
    indep_str = [[str(cell) for cell in row] for row in indep_data]
    indep_str = table_headline + indep_str

    table_head = "independent files"
    write_jube_table(table_head, indep_str)

    shared_data = collected_data[collected_data["rank"] == -1]
    shared_str = [[str(cell) for cell in row] for row in shared_data]
    shared_str = table_headline + shared_str

    table_head = "shared files"
    write_jube_table(table_head, shared_str)


def write_jube_table(table_head, data):
    """

    :param table_head:
    :param data:
    :return:
    """
    if not NOSTDOUT and JUBE_TABLE:
        import jube2.util
        print(table_head)
        print(jube2.util.text_table(data, use_header_line=True))
        print()
    elif not NOSTDOUT:
        import sys
        print(table_head)
        np.savetxt(sys.stdout, np.array(data), fmt='%s', delimiter=' | ')
        print()


def variance_table(nprocs, ranks, file_hash, counters, data):
    """

    :param nprocs:
    :param ranks:
    :param file_hash:
    :param counters:
    :param data:
    :return:
    """

    names = data[counters["CP_F_OPEN_TIMESTAMP"]]["name_suffix"]
    slow_rank = data[counters['CP_SLOWEST_RANK']]["value"]
    slow_rank_time = data[counters['CP_F_SLOWEST_RANK_TIME']]["value"]
    slow_rank_byte = data[counters['CP_SLOWEST_RANK_BYTES']]["value"]
    fast_rank = data[counters['CP_FASTEST_RANK']]["value"]
    fast_rank_time = data[counters['CP_F_FASTEST_RANK_TIME']]["value"]
    fast_rank_byte = data[counters['CP_FASTEST_RANK_BYTES']]["value"]
    var_rank_time = data[counters['CP_F_VARIANCE_RANK_TIME']]["value"]
    var_rank_byte = data[counters['CP_F_VARIANCE_RANK_BYTES']]["value"]
    posix_meta = data[counters['CP_F_POSIX_META_TIME']]["value"]
    posix_read = data[counters['CP_F_POSIX_READ_TIME']]["value"]
    posix_write = data[counters['CP_F_POSIX_WRITE_TIME']]["value"]
    bytes_read = data[counters['CP_BYTES_READ']]["value"]
    bytes_written = data[counters['CP_BYTES_WRITTEN']]["value"]

    table_dtype = [('hash', np.uint64), ('name_suffix', object),
                   ('procs', np.int), ('fastest_rank', np.int),
                   ('fastest_time', np.float64), ('fastest_bytes', np.uint64),
                   ('slowest_rank', np.int), ('slowest_time', np.float64),
                   ('slowest_bytes', np.uint64), ('variance_time', np.float64),
                   ('variance_bytes', np.float64)]
    table = np.array(list(), dtype=table_dtype)

    var_dtype = [('hash', np.uint64), ('var_time_S', np.float64),
                 ('var_time_T', np.float64), ('var_time_n', np.int),
                 ('var_bytes_S', np.float64), ('var_bytes_T', np.float64),
                 ('var_bytes_n', np.int)]
    var_help = np.array(list(), dtype=var_dtype)

    for i, f_hash in enumerate(file_hash):
        if ranks[i] == -1:
            row = np.array([(f_hash, names[i], nprocs, fast_rank[i],
                             fast_rank_time[i], fast_rank_byte[i], slow_rank[i],
                             slow_rank_time[i], slow_rank_byte[i],
                             var_rank_time[i], var_rank_byte[i])],
                           dtype=table_dtype)
            table = np.append(table, row)
        else:
            total_time = posix_meta[i] + posix_read[i] + posix_write[i]
            total_bytes = bytes_read[i] + bytes_written[i]
            if f_hash not in table['hash']:
                row = np.array([(f_hash, names[i], 1, ranks[i], total_time,
                                 total_bytes, ranks[i], total_time, total_bytes,
                                 0, 0)], dtype=table_dtype)
                table = np.append(table, row)
                # set temporary table to calculate the variance
                row = np.array([(f_hash, 0, total_time, 1, 0, total_bytes, 1)],
                               dtype=var_dtype)
                var_help = np.append(var_help, row)
            else:
                hash_ind = var_help['hash'] == f_hash
                # calculate variance of time
                n_tmp = var_help['var_time_n'][hash_ind]
                m_tmp = 1.
                t_tmp = var_help['var_time_T'][hash_ind]
                var_help['var_time_S'][hash_ind] += \
                    (m_tmp/(n_tmp*(n_tmp+m_tmp))) * \
                    ((n_tmp/m_tmp)*total_time - t_tmp)**2
                var_help['var_time_T'][hash_ind] += total_time
                var_help['var_time_n'][hash_ind] += 1
                table['variance_time'][table['hash'] == f_hash] =  \
                    var_help['var_time_S'][hash_ind] / \
                    var_help['var_time_n'][hash_ind]

                # calculate variance of bytes
                n_tmp = var_help['var_bytes_n'][hash_ind]
                m_tmp = 1.
                t_tmp = var_help['var_bytes_T'][hash_ind]
                var_help['var_bytes_S'][hash_ind] += \
                    (m_tmp/(n_tmp*(n_tmp+m_tmp))) * \
                    ((n_tmp/m_tmp)*total_bytes - t_tmp)**2
                var_help['var_bytes_T'][hash_ind] += total_bytes
                var_help['var_bytes_n'][hash_ind] += 1
                table['variance_bytes'][table['hash'] == f_hash] =  \
                    var_help['var_bytes_S'][hash_ind] / \
                    var_help['var_bytes_n'][hash_ind]

                # increase number of processes accessing the file
                table['procs'][table['hash'] == f_hash] = \
                    var_help['var_time_n'][hash_ind]

                # update slowest/fastest time/rank/bytes
                if table['slowest_time'][table['hash'] == f_hash] < total_time:
                    table['slowest_time'][table['hash'] == f_hash] = total_time
                    table['slowest_rank'][table['hash'] == f_hash] = ranks[i]
                    table['slowest_bytes'][table['hash'] == f_hash] = total_bytes
                if table['fastest_time'][table['hash'] == f_hash] > total_time:
                    table['fastest_time'][table['hash'] == f_hash] = total_time
                    table['fastest_rank'][table['hash'] == f_hash] = ranks[i]
                    table['fastest_bytes'][table['hash'] == f_hash] = total_bytes

    table['variance_bytes'] = np.around(np.sqrt(table['variance_bytes']),
                                        decimals=5)
    table['variance_time'] = np.around(np.sqrt(table['variance_time']),
                                       decimals=5)

    #tab_sort = np.sort(table[table['procs'] > 1], order='slowest_time')[::-1]
    tab_sort = np.sort(table, order='slowest_time')[::-1]

    # remove first column including the hash
    cols = list(table.dtype.names[1:])
    table_str = [[str(row[cell]) for cell in cols] for row in tab_sort[:20]]
    # alternative: remove first column including the hash
    # tab_sort = tab_sort[list(table.dtype.names[1:])]
    # table_str = [[str(cell) for cell in row] for row in tab_sort]
    table_head = "Variance in Files"
    column_heads = ['File', '#Procs', 'Fast Rank', 'Fast Time', 'Fast Bytes',
                    'Slow Rank', 'Slow Time', 'Slow Bytes',
                    'Std Time', 'Std Bytes']
    table_str.insert(0, column_heads)
    write_jube_table(table_head, table_str)

    # exit()


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('-f', '--file',
                        help='output file of the darshan profiling tool')
    parser.add_argument('-j', '--jube', action='store_true',
                        help='create jube table output')
    parser.add_argument('-nout', '--nostdout', action='store_true',
                        help='disable stdout output')
    parser.add_argument('-s', '--short', action='store_true',
                        help='without list of files')

    args = parser.parse_args()
    
    global NOSTDOUT
    NOSTDOUT = args.nostdout
    
    global JUBE_TABLE
    JUBE_TABLE = args.jube

    darshan_logfile = args.file
    # alternative for python version > 2.6
    #output = subprocess.check_output(shlex.split("darshan-parser {0}".format(darshan_logfile)))

    output = Popen(shlex.split("darshan-parser {0}".format(darshan_logfile)),
                   stdout=PIPE).communicate()[0]
    output = output.decode().strip()
    # print header
    # print("\n".join(output.split("\n")[:94]))
    re_nprocs = re.search("# nprocs: (?P<nprocs>\d*)", output)
    nprocs = int(re_nprocs.group("nprocs"))
    re_runtime = re.search("# run time: (?P<runtime>\d*)", output)
    runtime = int(re_runtime.group("runtime"))
    if not NOSTDOUT: print("Runtime: ", runtime) 

    raw = [tuple(line.split()) for line in
                output[output.find("<fs type>\n") + 10:].split("\n")]

    # save input file column-wise
    log_dtype = [("rank", np.int64), ("file", np.uint64), ("counter", object),
                 ("value", np.float64), ("name_suffix", object),
                 ("mount_pt", object), ("fs type", object)]
    data = np.array(raw, dtype=log_dtype)

    # get all counter names; remove doubles
    all_counters = np.array(sorted(list(
            set(data[data["file"] == data["file"][0]]["counter"]))))
    # get boolean mask for every counter to collect
    # all values belonging to a counter in data
    counters = dict([(counter, data["counter"] == counter)
                     for counter in all_counters])
    # alternative
    # counters = {counter: data["counter"] == counter for counter in all_counters}

    ranks = data["rank"][0::len(all_counters)]
    file_hash = data["file"][0::len(all_counters)]
    mount_pt = data["mount_pt"][0::len(all_counters)]

    out_file = open('./darshan.jube', 'w')
    out_file.write('runtime: {0}\n\n'.format(runtime))

    variance_table(nprocs, ranks, file_hash, counters, data)
    #exit()

    io_percentage(nprocs, runtime, counters, data, out_file)
    #exit()
    #####################################################################
    operation_counts(counters, data, out_file)
    # exit()
    #######################################################
    io_sizes(counters, data)
    #exit()
    ###############################################
    io_pattern(counters, data)
    #exit()
    ################################################
    access_size(counters, data, out_file, length=-1) #4)
    #exit()
    ###########################################################
    file_cnt_summary(file_hash, counters, data)
    #exit()
    ############################################################
    avg_io(nprocs, ranks, counters, data, out_file)
    #exit()
    ###########################################################
    data_transfer(counters, data, mount_pt)
    #exit()
    #####################################################################
    if not args.short and not NOSTDOUT:
        create_ind_sha_table(nprocs, ranks, file_hash, counters, data, mount_pt)


if __name__ == "__main__":
    main()
