import os
import sys
from photobot_helpers import *


class Sample_Uploader(object):
    def upload_by_type(self,type='usb',width=None):

        print("doing sample upload for " + type)
        if width is None:
            sample_width_var = type + '_sample_width'
            width = self.settings[sample_width_var]

        orig_path = get_latest_photo_path(type)
        #print ("orig path was " + orig_path)
        self.send_image(orig_path,type,width)

    def send_image(self,path,type,width):

        last_sent_path = get_latest_photo_sent_path(type)


        #print( "last_sent_path was: " + last_sent_path)
        width = str(width)

        if last_sent_path == path:
            print("already sent")
            return

        dir, filename = os.path.split(path)
        samples_dir = dir + "/samples"
        ensure_dir(samples_dir)
        sample_path = samples_dir + "/sample_" + filename

        #print("convert -geometry " + width + "x" + width + " " + path + " " + sample_path)
        if width != '0':
            os.system("convert -strip -interlace Plane  -quality 50%  -geometry " + width + "x" + width + " " + path + " " + sample_path )
        else:
            os.system("cp " + path + " " + sample_path)

        #print("scp " + sample_path + " " + self.settings['samples_user_host'] + ":" + self.settings['samples_dest_path'])
        os.system("scp " + sample_path + " " + self.settings['samples_user_host'] + ":" + self.settings['samples_dest_path'])

        send_ping(type,"Sample Photo Uploaded: " +filename,"OK")
        log_latest_photo_sent_path(path,type)