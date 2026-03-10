import requests
#if page.status_code == 200 or page.status_code == 304:
#   print(page.text)
#else:
#    print("ERROR:" + page.status_code )
import re

from http.server import BaseHTTPRequestHandler
from urllib import parse


class GetHandler(BaseHTTPRequestHandler):

    def do_GET(self):
        parsed_path = parse.urlparse(self.path)
        path = self.path[1:len(self.path)]
        baseurlpath = re.sub("https://|http://", " " , path)
        baseurl = re.sub("/.*","", baseurlpath)
        try:
            page = requests.get(path)
        except:
            page = "<p>404 Page Not Found</p>"
        a = re.sub("href=\"", f"href=\"https://{baseurl}", page.text)
        web = re.sub("src=\"", f"src=\"https://{baseurl}", a)
        message_parts = [
             '{}'.format(web),
        ]
        message = '\r\n'.join(message_parts)
        self.send_response(200)
        self.send_header('Content-Type',
                         'text/html; charset=utf-8')
        self.end_headers()
        self.wfile.write(message.encode('utf-8'))


if __name__ == '__main__':
    from http.server import HTTPServer
    server = HTTPServer(('localhost', 8080), GetHandler)
    print('Starting server, use <Ctrl-C> to stop')
    server.serve_forever()




