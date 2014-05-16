#!/usr/bin/env python3

import gtk.gdk
import datetime
import dropbox
import sys
import os
import time

def main():
    # Lets us print unicode characters through sys.stdout/stderr
    reload(sys).setdefaultencoding('utf8')

    prog_name = sys.argv[0]
    args = sys.argv[1:]

    if len(args) < 3 or len(args) > 3:
        sys.stderr.write("Usage:\n")
        sys.stderr.write("   %s is a program for taking screenshots.\n" % prog_name)
        sys.stderr.write("   For running it should contain three aruments:\n")
        sys.stderr.write("   app_key app_secret time (in seconds, 10 <= time <= 10000)\n")
        sys.exit(1)

    app_key = args[0]
    app_secret = args[1]
    sleep_time = args[2]

    # Check if sleep_time is a number
    try:
        float(sleep_time)
        sleep_time = int(sleep_time)
    except ValueError:
        sys.stderr.write("ERROR: Time value is invalid.\n")
        sys.exit(1)

    if sleep_time < 10 or sleep_time > 10000:
        print sleep_time
        sys.stderr.write("ERROR: Time value must be in range 10 .. 10000\n")
        sys.exit(1)

    auth_data = app_auth(app_key, app_secret)
    access_token, user_id = auth_data.split(':')

    while True:
        time.sleep(sleep_time)
        fname = make_screenshot()   
        upload_file(fname, access_token)

def app_auth(app_key, app_secret):

    flow = dropbox.client.DropboxOAuth2FlowNoRedirect(app_key, app_secret)
    authorize_url = flow.start()

    print "You need to sign in and authorize token:"
    print "   1. Go to: %s" % authorize_url
    print "   2. Click 'Allow' (you might have to log in first)."
    print "   3. Copy the authorization code and enter it here: "
    code = raw_input("Enter the authorization code here:\n")

    if code == '':
        sys.stderr.write("ERROR: Authorization code couldn't be empty\n")
        sys.exit(1)

    try:
        access_token, user_id = flow.finish(code)
        result = "%s:%s" % (access_token, user_id)
        sys.stdout.write("Linked to account.\n")
        return result
    except:
        sys.stderr.write("ERROR: Authorization code is invalid\n")
        sys.exit(1)

def make_screenshot():
    w = gtk.gdk.get_default_root_window()
    sz = w.get_size()
    pb = gtk.gdk.Pixbuf(gtk.gdk.COLORSPACE_RGB,False,8,sz[0],sz[1])
    pb = pb.get_from_drawable(w,w.get_colormap(),0,0,0,0,sz[0],sz[1])   

    date = datetime.datetime.now().isoformat()
    fname = "screenshot_%s.png" % date

    if (pb != None):
        try:
            pb.save(fname,"png")
            sys.stdout.write("%s saved.\n" % fname)
            return fname
        except:
            sys.stderr.write("ERROR: Unable to save screenshot\n")
            sys.exit(1)
    else:
        sys.stderr.write("ERROR: Unable to get screenshot\n")
        sys.exit(1)

def upload_file(fname, access_token):
    try:
        client = dropbox.client.DropboxClient(access_token)
    except:
        sys.stderr.write("ERROR: Couldn't connect to dropbox")
        sys.exit(1)
    try:
        f = open(fname, 'rb')
    except:
        sys.stderr.write("ERROR: Couldn't open %s." % fname)
        sys.exit(1)
    try:
        response = client.put_file('/%s' % fname, f)
        sys.stdout.write("%s uploaded to dropbox.\n" % fname)
    except:
        sys.stderr.write("ERROR: Couldn't upload %s to dropbox\n" % fname)
        sys.exit(1)    

if __name__ == '__main__':
    main()