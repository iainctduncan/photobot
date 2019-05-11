import os
import sys
from photobot_helpers import *


class Sample_Uploader(object):
    def upload_by_type(self,type='usb'):

        sample_width_var = type + '_sample_width'

        width = self.settings[sample_width_var]

        orig_path = get_lastest_photo_path(type)
        self.send_image(orig_path,type,width)

    def send_image(self,path,type,width):

        last_sent_path = get_lastest_photo_sent_path(type)

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
            os.system("convert -geometry " + width + "x" + width + " " + path + " " + sample_path )
        else:
            os.system("cp " + path + " " + sample_path)

        #print("scp " + sample_path + " " + self.settings['samples_user_host'] + ":" + self.settings['samples_dest_path'])
        os.system("scp " + sample_path + " " + self.settings['samples_user_host'] + ":" + self.settings['samples_dest_path'])

        send_ping(type,"Sample Photo Uploaded: " +filename,"OK")
        log_latest_photo_path(path,type)

