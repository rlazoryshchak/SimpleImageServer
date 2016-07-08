import SimpleHTTPServer 
import os
import posixpath
import BaseHTTPServer
import urllib
import cgi
import sys
import shutil
import mimetypes
try:
    from cStringIO import StringIO
except ImportError:
    from StringIO import StringIO

class SimpleHTTPRequestHandler(SimpleHTTPServer.SimpleHTTPRequestHandler):
    def list_directory(self, path):
        """Helper to produce a directory listing (absent index.html).
        Return value is either a file object, or None (indicating an
        error).  In either case, the headers are sent, making the
        interface the same as for send_head().
        """
        try:
            list = os.listdir(path)
        except os.error:
            self.send_error(404, "No permission to list directory")
            return None
        images = filter(lambda x: x.split('.')[-1].lower() in ['jpg', 'jpeg', 'png', 'ico'], list)
        other_files = set(list) - set(images)
        f = StringIO()
        displaypath = cgi.escape(urllib.unquote(self.path))
        f.write('<!DOCTYPE html PUBLIC "-//W3C//DTD HTML 3.2 Final//EN">')
        f.write('<html>\n<title>Directory listing for %s</title>' % displaypath)
        f.write('''<style type="text/css">
            .thumbnail{
              position: relative;
              z-index: 0;
              padding: 10px;
            }
            .thumbnail:hover{
              background-color: transparent;
              z-index: 50;
            }
            .thumbnail span{ 
              position: absolute;
              visibility: hidden;
              color: black;
              background-color: lightyellow;
              border: 1px dashed gray;
              padding: 5px;
            }
            .thumbnail img{ 
              height: 15%;
            }
            .thumbnail span img{ 
              height: 600px;
            }
            .thumbnail:hover span{ 
              visibility: visible;
              position: fixed;
              top: 20%;
              left: 20%;
            }
            </style>\n''')
        f.write("<body>\n<h2>Directory listing for %s</h2>\n" % displaypath)
        f.write("<hr>\n<ul>\n")
        for name in sorted(images):
            f.write('''<a class="thumbnail">
                <img src="%s"/>
                <span><img src="%s" /></span></a>'''
                    % (urllib.quote(name), cgi.escape(name)))
        for name in sorted(other_files):
            fullname = os.path.join(path, name)
            displayname = linkname = name
            # Append / for directories or @ for symbolic links
            if os.path.isdir(fullname):
                displayname = name + "/"
                linkname = name + "/"
            if os.path.islink(fullname):
                displayname = name + "@"
                # Note: a link to a directory displays with @ and links with /
            f.write('<li><a href="%s">%s</a>\n'
                    % (urllib.quote(linkname), cgi.escape(displayname)))
        f.write("</ul>\n<hr>\n</body>\n</html>\n")
        length = f.tell()
        f.seek(0)
        self.send_response(200)
        encoding = sys.getfilesystemencoding()
        self.send_header("Content-type", "text/html; charset=%s" % encoding)
        self.send_header("Content-Length", str(length))
        self.end_headers()
        return f

if __name__ == '__main__':
    BaseHTTPServer.test(SimpleHTTPRequestHandler, BaseHTTPServer.HTTPServer)
