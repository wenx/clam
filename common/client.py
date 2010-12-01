#!/usr/bin/env python
#-*- coding:utf-8 -*-

###############################################################
# CLAM: Computational Linguistics Application Mediator
# -- Client --
#       by Maarten van Gompel (proycon)
#       http://ilk.uvt.nl/~mvgompel
#       Induction for Linguistic Knowledge Research Group
#       Universiteit van Tilburg
#       
#       Licensed under GPLv3
#
###############################################################

import codecs
import os.path
import httplib2
import urllib2
from urllib import urlencode


from clam.external.poster.encode import multipart_encode
from clam.external.poster.streaminghttp import register_openers



import clam.common.status
import clam.common.parameters
import clam.common.formats
from clam.common.data import CLAMData, CLAMFile, CLAMInputFile, CLAMOutputFile, CLAMMetaData, InputTemplate, OutputTemplate, VERSION as DATAAPIVERSION

VERSION = '0.5'
if VERSION != DATAAPIVERSION:
    raise Exception("Version mismatch beween Client API ("+clam.common.data.VERSION+") and Data API ("+DATAAPIVERSION+")!")

# Register poster's streaming http handlers with urllib2
register_openers()


class BadRequest(Exception):
         def __init__(self):
            pass
         def __str__(self):
            return "Bad Request"

class NotFound(Exception):
         def __init__(self, msg=""):
            self.msg = msg
         def __str__(self):
            return "Not Found: " +  self.msg

class PermissionDenied(Exception):
         def __init__(self, msg = ""):
            self.msg = msg
         def __str__(self, msg):
            return "Permission Denied: " + self.msg

class ServerError(Exception):
         def __init__(self, msg = ""):
            self.msg = msg
         def __str__(self):
            return "Server Error: " + self.msg

class AuthRequired(Exception):
         def __init__(self, msg = ""):
            self.msg = msg            
         def __str__(self):
            return "Authorization Required: " + self.msg

class NoConnection(Exception):
         def __init__(self):
            pass
         def __str__(self):
            return "Can't establish a connection with the server" 



class CLAMClient:
    def __init__(self, url, user=None, password=None):
        self.http = httplib2.Http()
        if url[-1] != '/': url += '/'
        self.url = url
        if user and password:
            #for most things we use httplib2
            self.http.add_credentials(user, password)
            
            #for file upload we use urllib2:
            passman = urllib2.HTTPPasswordMgrWithDefaultRealm()
            # this creates a password manager
            passman.add_password(None, url, user, password)
            authhandler = urllib2.HTTPDigestAuthHandler(passman)
            opener = urllib2.build_opener(authhandler)
            urllib2.install_opener(opener)
            
            
            
    def request(self, url, method = 'GET', data = None):
        """Returns a CLAMData object if a proper CLAM XML response is received. Otherwise: returns True, on success, False on failure.  Raises an Exception on most HTTP errors!"""
        try:
            if data: 
                response, content = self.http.request(self.url + url, method, data)
            else:
                response, content = self.http.request(self.url + url, method)
        except:
            raise NoConnection()
        return self._parse(response, content)

    def _parse(self, response, content):    
        if content.find('<clam') != -1:
            data = CLAMData(content)
        else:
            data = False
            
        if response['status'] == '200' or response['status'] == '201' or response['status'] == '202':
            if not data: data = True
        elif response['status'] == '400':
            raise BadRequest()
        elif response['status'] == '401':
            raise AuthRequired()
        elif response['status'] == '403' and not data:
            raise PermissionDenied(content)
        elif response['status'] == '404' and not data:
            raise NotFound(content)
        elif response['status'] == '500':
            raise ServerError(content)
        else:
            raise Exception("Server returned HTTP response " + response['status'])
        
        return data
                
   

 
    def index(self):
        """get index of projects"""
        return self.request('')

    def get(self, project):
        """query the project status"""
        try:
            data = self.request(project + '/')
        except:
            raise
        if not isinstance(data, CLAMData):
            raise Exception("Unable to retrieve CLAM Data")
        else:
            return data
            

    def create(self,project):
        """create a new project"""
        return self.request(project + '/', 'PUT')
     

    def start(self, project, **parameters):
        """start a run"""
        auth = None
        if 'auth' in parameters:
            auth = parameters['auth']
            del parameters['auth']

        return self.request(project + '/', 'POST', urlencode(parameters))


    def delete(self,project):
        """aborts AND deletes a project"""
        return self.request(project + '/', 'DELETE')

    def abort(self, project): #alias
        return self.abort(project)


    def downloadarchive(self, project, targetfile, format = 'zip'):
        """download all output as archive"""
        #TODO: Redo
        req = urllib2.urlopen(self.url + project + '/output/?format=' + format) #TODO: Auth support
        CHUNK = 16 * 1024
        while True:
            chunk = req.read(CHUNK)
            if not chunk: break
            targetfile.write(chunk)


    def getinputfilename(self, inputtemplate, filename):        
        """Determine the final filename for an input file given an inputtemplate and a given filename"""
        if inputtemplate.filename:
            filename = inputtemplate.filename
        elif inputtemplate.extension: 
            if filename[-len(inputtemplate.extension) - 1:].lower() != inputtemplate.extension.lower():
                filename += '.' + inputtemplate.extension        
                
        return filename


    def addinputfile(self, project, inputtemplate, sourcefile, **kwargs):
        """Add/upload an input file to the CLAM service.
        
        project - the ID of the project you want to add the file to.
        inputtemplate - The input template you want to use to add this file (InputTemplate instance)
        sourcefile - The file you want to add: either an instance of 'file' or a string containing a filename 
        
        Keyword arguments (optional but recommended!):
            filename - the filename on the server (will be same as sourcefile if not specified)
            metadata - A metadata object.
            metafile - A metadata file (filename)
            Any other keyword arguments will be passed as metadata and matched with the input template's parameters.
        """
        if not isinstance(inputtemplate, InputTemplate):
            raise Exception("inputtemplate must be instance of InputTemplate. Get from CLAMData.inputtemplate(id)")
        
        if not isinstance(sourcefile, file):
            sourcefile = open(sourcefile,'r')
        
        if 'filename' in kwargs:
            filename = self.getinputfilename(inputtemplate, kwargs['filename'])
        else:
            filename = self.getinputfilename(inputtemplate, os.path.basename(sourcefile.name) )
                    
        data = {"file": sourcefile, 'inputtemplate': inputtemplate.id}
        for key, value in kwargs.items():
            if key == 'filename':
                pass #nothing to do
            elif key == 'metadata':
                assert isinstance(value, CLAMMetaData)
                data['metadata'] =  value.xml()
            elif key == 'metafile':
                data['metafile'] = open(value,'r')
            else:
                data[key] = value
        
        datagen, headers = multipart_encode(data)

        # Create the Request object
        request = urllib2.Request(self.url + project + '/input/' + filename, datagen, headers)
        return urllib2.urlopen(request).read()

    def addinput(self, project, inputtemplate, contents, **kwargs):
        """Add an input file to the CLAM service. Explictly providing the contents as a string
                
        project - the ID of the project you want to add the file to.
        inputtemplate - The input template you want to use to add this file (InputTemplate instance)
        contents - The contents for the file to add (string)
        
        Keyword arguments (optional but recommended!):
            filename - the filename on the server (mandatory!)
            metadata - A metadata object.
            metafile - A metadata file (filename)
            Any other keyword arguments will be passed as metadata and matched with the input template's parameters.
        """ 
        if not isinstance(inputtemplate, InputTemplate):
            raise Exception("inputtemplate must be instance of InputTemplate. Get from CLAMData.inputtemplate(id)")
        
        
        if 'filename' in kwargs:
            filename = self.getinputfilename(inputtemplate, kwargs['filename'])
        else:
            raise Exception("No filename provided!")
                    
        data = {"contents": contents, 'inputtemplate': inputtemplate.id}
        for key, value in kwargs.items():
            if key == 'filename':
                pass #nothing to do
            elif key == 'metadata':
                assert isinstance(value, CLAMMetaData)
                data['metadata'] =  value.xml()
            elif key == 'metafile':
                data['metafile'] = open(value,'r')
            else:
                data[key] = value
        
        datagen, headers = multipart_encode(data)

        # Create the Request object
        request = urllib2.Request(self.url + project + '/input/' + filename, datagen, headers)
        return urllib2.urlopen(request).read()        
               

    def upload(self,project, inputtemplate, sourcefile, **kwargs):
        """Alias for addinputfile."""
        return self.addinputfile(project, inputtemplate,sourcefile, **kwargs)

