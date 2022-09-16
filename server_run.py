import json
import os
import http.server as server
import datetime


class HTTPRequestHandler(server.SimpleHTTPRequestHandler):
    if not os.path.isdir('files'):
        os.mkdir('files')

    def __last_command(self, command='GET'):
        self.list_files = os.listdir(path='files')
        if command != 'GET':
            self.dt_dct_files = {
                'description': 'file_server',
                'data': self.list_files,
                'last_command': command,
                'change_time': str(datetime.datetime.now())
            }

            with open('log.txt', 'w') as lw:
                lw.write(str(self.dt_dct_files))
            return

        if not os.path.exists('log.txt'):
            self.dt_dct_files = {
                'description': 'file_server',
                'data': self.list_files,
                'last_command': 'unknown',
                'change_time': 'unknown'
            }
            return self.dt_dct_files

        else:
            with open('log.txt', 'r') as lr:
                return lr.readline()

    def do_GET(self):
        self.send_response(200)
        self.send_header("Content-type", "application/json")
        self.end_headers()
        self.wfile.write(json.dumps(self.__last_command()).encode('UTF-8'))

    def do_PUT(self):
        filename = os.path.basename(self.path)
        if os.path.exists(f'files/{filename}'):
            self.send_response(409)
            self.end_headers()
            reply_body = '"%s" file already exists\n' % filename
            self.wfile.write(reply_body.encode('UTF-8'))

        file_length = int(self.headers['Content-Length'])
        read = 0

        with open(f'files/{filename}', 'wb+') as output_file:
            while read < file_length:
                new_read = self.rfile.read(min(66556, file_length - read))
                read += len(new_read)
                output_file.write(new_read)
        self.send_response(201)
        self.end_headers()
        reply_body = '"%s" file saved\n' % filename
        self.wfile.write(reply_body.encode('UTF-8'))
        self.__last_command('PUT')

    def do_POST(self):
        filename = os.path.basename(self.path)
        if not os.path.exists(f'files/{filename}'):
            self.send_response(409)
            self.end_headers()
            reply_body = '"%s" file not found\n' % filename
            self.wfile.write(reply_body.encode('UTF-8'))
            return

        with open(f'files/{filename}', 'rb') as file:
            self.send_response(202)
            self.end_headers()
            self.wfile.write(file.read())
            self.__last_command('POST')

    def do_DELETE(self):
        filename = os.path.basename(self.path)
        if os.path.exists(f'files/{filename}'):
            self.send_response(301)
            self.end_headers()
            os.remove(f'files/{filename}')
            reply_body = '"%s" file deleted\n' % filename
        else:
            self.send_response(302)
            self.end_headers()
            reply_body = '"%s" file not found\n' % filename
        self.wfile.write(reply_body.encode('UTF-8'))
        self.__last_command('DELETE')


if __name__ == '__main__':
    server.test(HandlerClass=HTTPRequestHandler)
