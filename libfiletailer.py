import logging
import sys
import os

"""
#How to use it:

from libfiletailer import MyFileTailer

  tailer =  MyFileTailer(LOG_FILE, OFFSET_FILE)
  tailer.register_callback(self.callback_handle_line_read);
  tailer.read_lines()

#define the call back as
def callback_handle_line_read(line):

"""

class MyFileTailer:
    log_file    = "";
    offset_file = "";
    log_fd      = False

    current_offset          = 0;
    last_confirmed_offset   = 0;
    delegate    = False;


    def __init__(self, log_file, offset_file):
        self.log_file       = log_file;
        self.offset_file    = offset_file;

        #read the offset and FF to the point
        #read the last read offset point from the app log
        try:
            offset_log_fd = open(offset_file,'r')
            for t in offset_log_fd:
                self.current_offset = int(t)
                self.last_confirmed_offset = self.current_offset

            offset_log_fd.close()
        except IOError:
            #create of the file doesn't exist -- should log first time this is script
            try:
                logging.info(offset_file + " doesn't exist...creating")
                open(offset_file, 'w').close()
            except:
                logging.critical("Cannot create " + offset_file + ", check permission")
                sys.exit(1)

        #check if the file has rolled over
        if self.current_offset > os.path.getsize(log_file):
            #if the file has rolled over ...read the filename.{1} and read until the EOF is reached
            # set this offset to 0 only if the old file was read completely
            self.current_offset = 0

        try:
            self.log_fd = open(self.log_file, 'r', 0)
            self.log_fd.seek(self.current_offset)
        except IOError:
            logging.critical("Cannot read " + log_file + ", check path, permission")
            sys.exit(1)

    def register_callback(self, delegate):
        self.delegate = delegate;

    def read_lines(self):
        #confirms last consumption

        for line in self.log_fd:
            self.current_offset = self.log_fd.tell();
            line_len = len(line)
            if not self.delegate(line.rstrip()):
                break;

            self.last_confirmed_offset += line_len;

        #reaching here means nothing to read or over read
        try:
            offset_log_fd = open(self.offset_file, 'r+');

            offset_log_fd.write("%d" %self.last_confirmed_offset);
            offset_log_fd.close();
            logging.debug("Writing byte offset %d to file" %(self.last_confirmed_offset))
        except IOError as ex:
            logging.critical("Cannot create " + self.offset_file + ", check permission: " + ex.message)
            sys.exit(1)



