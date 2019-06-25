"""This set up a sever to deploy the result html"""

import cherrypy
import os

class SurveyResult(object):
    @cherrypy.expose
    def index(self, name=None, result=None):
        return open("result.html").read().format(name=name, result=result)

conf={'/result.css':
                    { 'tools.staticfile.on':True,
                      'tools.staticfile.filename': os.path.abspath("./result.css"),
                    }
      }

if __name__ == '__main__':
    cherrypy.quickstart(SurveyResult(), config=conf)
