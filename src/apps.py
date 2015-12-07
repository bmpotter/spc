import re, sys, os
import config
import ConfigParser
import json
import xml.etree.ElementTree as ET
from gluino import DAL, Field
from model import *

# using convention over configuration 
# the executable is the name of the app
# and the input file is the name of the app + '.in'
apps_dir = config.apps_dir
user_dir = config.user_dir
# end set 

#class Parameter(object):
#    def __init__(self,data_type):
#        self.data_type 

def is_number(value):
  try:
    float(value)
    return True
  except ValueError:
    return False

class App(object):

    def __init__(self):
        pass

    def create(self, name, desc, cat, lang, info, cmd, pre, post):
        apps.insert(name=name, description=desc, category=cat, language=lang,  
                    input_format=info, command=cmd, preprocess=pre, 
                    postprocess=post)
        db.commit()

    def update(self):
        pass

    def delete(self,appid):
        del apps[appid]
        db.commit()

    def deploy(self):
        pass

    def create_template(self,html_tags=None,bool_rep="T",desc=None):
        # need to output according to blocks
        f = open('views/apps/'+self.appname+'.tpl', 'w')
        f.write("%include('header',title='confirm')\n")
        f.write("<body onload=\"init()\">\n")
        f.write("%include('navbar')\n")
        f.write("%include('apps/alert')\n")
        f.write("<div class=\"container-fluid\">\n")
        f.write("<form class=\"form-horizontal\" action=\"/confirm\" method=\"post\" novalidate>\n")
        f.write("<input type=\"hidden\" name=\"app\" value=\"{{app}}\">\n")
        f.write("%if defined('cid'):\n")
        f.write("<input type=\"hidden\" name=\"cid\" value=\"{{cid}}\">\n")
        f.write("%end\n")
        f.write("<div class=\"col-xs-12\" style=\"height:5px\"></div>\n")

        f.write("<div class=\"form-group\">\n")
        f.write("\t<div class=\"col-xs-2\">\n")
        f.write("\t\t<button type=\"submit\" class=\"btn btn-success\"> <!-- pull-right -->\n")
        f.write("\t\tContinue <em class=\"glyphicon glyphicon-forward\"></em> </button>\n")
        f.write("\t</div>\n")
        f.write("\t<label for=\"desc\" style=\"text-align:right\" class=\"control-label col-xs-4\">\n")
        f.write("\t\t<a href=\"#\" data-toggle=\"tooltip\" title=\"Separate labels by commas\">Labels:</a></label>\n")
        f.write("\t<div class=\"col-xs-6\">\n")
        f.write("\t\t<input type=\"text\" id=\"desc\" name=\"desc\" class=\"form-control\" style=\"width:100%\"\n")
        f.write("\t\t\tdata-role=\"tagsinput\" title=\"e.g. v2.5.1,bottleneck\">\n")
        f.write("\t</div>\n")
        f.write("</div>\n")
        # f.write("<input class=\"btn btn-success\" type=\"submit\"" + \
        #         " value=\"confirm\" />\n\n")
        f.write("<div class=\"col-xs-12\" style=\"height:5px\"></div>\n")

        # tabs
        f.write("<ul class=\"nav nav-pills\" role=\"tablist\">\n")
        #f.write("<ul class=\"nav nav-tabs\" role=\"tablist\">\n")
        first_tab = True
        for block in self.blockorder:
            if first_tab: 
                f.write("\t<li role=\"presentation\" class=\"active\">\n")
                first_tab = False
            else:
                f.write("\t<li role=\"presentation\">\n")
            f.write("\t\t<a href=\"#" + block + "\" aria-controls=\"home\" role=\"tab\"")
            f.write(" data-toggle=\"tab\">" + block + "</a>\n")
            f.write("\t</li>\n")
        f.write("</ul>\n")
        f.write("<div class=\"tab-content\">\n")

        for block in self.blockorder:
            f.write("<div role=\"tabpanel\" class=\"tab-pane fade in active\" id=\"" + block + "\">\n")
            for param in self.blockmap[block]:
                f.write("\t<div class=\"form-group\">\n")
                # label
                if not html_tags[param] == "hidden":
                    buf = "\t\t<label for=\"" + param + "\" class=\"control-label col-xs-6\">"
                    if desc: # description
                        buf += "\n\t\t\t" + desc[param]
                    else:
                        buf += param 
                    buf += ":</label>\n"
                # input box
                buf += "\t\t<div class=\"col-xs-6\">\n"               
                if html_tags[param] == "checkbox":
                    buf += "\t\t\t<input type=\"checkbox\" name=\"" \
                            + param + "\" value=\""+ bool_rep + "\"\n"
                    buf += "%if " + param + "== '" + bool_rep + "':\n"
                    buf += "checked\n"
                    buf += "%end\n"
                    buf += "\t\t/>\n"
                elif html_tags[param] == "hidden":
                    buf = "\t\t\t<input type=\"hidden\" name=\"" \
                              + param + "\" value=\"{{" + param + "}}\"/>\n"
                elif html_tags[param] == "select":
                    buf += "\t\t\t<select class=\"form-control\" name=\""+param+"\">\n"  \
                           "\t\t\t\t<option value=\"{{"+param+"}}\">"+ \
                                                "{{"+param+"}}</option>\n" \
                           "\t\t\t</select>"
                elif html_tags[param] == "textarea":
                    buf += "\t\t\t<textarea class=\"form-control\" name=\"" \
                                + param + ">{{" + param + "}}\"</textarea>\n"
                elif html_tags[param] == "number":
                    buf += "\t\t\t<input type=\"number\" class=\"form-control\" name=\"" \
                                + param + "\" value=\"{{" + param + "}}\"/>\n"
                else: 
                    buf += "\t\t\t<input type=\"text\" class=\"form-control\" name=\"" \
                                + param + "\" value=\"{{" + param + "}}\"/>\n"
                #if not html_tags[param] == "hidden":
                buf += "\t\t</div>\n"
                buf += "\t</div>\n"
                f.write(buf)
            f.write("</div>\n\n")
        f.write("</div>\n")
        f.write("</form>\n")
        f.write("%include('footer')\n")
        f.close()
        return True

# user must write their own function for how to write the output file
class Namelist(App):
    '''Class for reading/writing Fortran namelist.input style files.'''
    
    def __init__(self,appname,preprocess=0,postprocess=0):
        self.appname = appname
        self.appdir = os.path.join(apps_dir,appname)
        self.outfn = appname + '.out'
        self.simfn = appname + '.in'
        self.user_dir = user_dir
        self.preprocess = preprocess
        self.postprocess = postprocess
        self.params, self.blockmap, self.blockorder = self.read_params()
        self.exe = os.path.join(apps_dir,self.appname,self.appname)

    def write_params(self,form_params,user):
        '''write the input file needed for the simulation'''

        cid = form_params['case_id']
        sim_dir=os.path.join(self.user_dir,user,self.appname,cid)
       
        if not os.path.exists(sim_dir):
            os.makedirs(sim_dir)

        fn = os.path.join(sim_dir,self.simfn)

        ## output parameters to output log
        #for i, fp in enumerate(form_params):
        #    print i,fp, form_params[fp]

        f = open(fn, 'w')
        # need to know what attributes are in what blocks
        for section in self.blockorder:
            f.write("&%s\n" % section)
            for key in self.blockmap[section]:
                # if the keys are not in the params, it means that
                # the checkboxes were not checked, or that the input
                # has been disabled.  So, add the keys
                # to the form_params here and set the values to False.
                # Also, found that when textboxes get disabled e.g. via JS 
                # they also don't show up in the dictionary.
                if key not in form_params:
                    #print "key not found - inserting:", key
                    form_params[key] = "F"
                    #if self.appname == "terra":
                    #        form_params[key] = "0"
                    #else:
                    #        form_params[key] = "F"

                # replace checked checkboxes with T value
                form_params[key].replace("'","")
                if form_params[key] == 'on': form_params[key] = "T"

                # detect strings (except Booleans) and enclose with single quotes
                if not is_number(form_params[key]) \
                   and form_params[key] != 'T' and form_params[key] != '.true.' \
                   and form_params[key] != 'F' and form_params[key] != '.false.':
                    form_params[key] = "'" + form_params[key] + "'"

                f.write(key + ' = ' + form_params[key] + ",\n")
            f.write("/\n\n")
        f.close
        return 1

    def read_params(self,user=None,cid=None):
        '''read the namelist file and return as a dictionary'''
        if cid is None or user is None:
            fn = self.appdir
        else:
            fn = os.path.join(self.user_dir,user,self.appname,cid)
        # append name of input file to end of string
        fn += os.sep + self.simfn
        params = dict()   # a dictionary of parameter keys and default values
        blockmap = dict() # a dictionary with section headings as keys with 
                          # values being a list of parameters in that section
        blockorder = []   # a list used to maintain the order of the sections
 
        if not os.path.isfile(fn):
            print "ERROR: input file does not exist: " + fn

        for line in open(fn, 'rU'):
            m = re.search(r'&(\w+)',line) # section title
            n = re.search(r'(\w+)\s*=\s*(.*$)',line) # parameter
            if m:
                section = m.group(1)  
                blockorder += [ m.group(1) ]
            elif n:
                # Delete apostrophes
                val = re.sub(r"'", "", n.group(2))
                # Delete commas only when they are at the end of the line
                val = re.sub(r",\s*$", "", val)
                # Delete Fortran comments and whitespace
                params[n.group(1)] = re.sub(r'\!.*$', "", val).strip()
                # Append to blocks e.g. {'basic': ['case_id', 'mutn_rate']}
                blockmap.setdefault(section,[]).append(n.group(1))
		#print n.group(1), val
        #print "params:",params
        #print "blockmap:",blockmap
        #print "blockorder:",blockorder
        return params, blockmap, blockorder

class INI(App):

    def __init__(self,appname,preprocess=0,postprocess=0):
        self.appname = appname
        self.appdir = os.path.join(apps_dir,appname)
        self.outfn = appname + '.out'
        self.simfn = appname + '.ini'
        self.user_dir = user_dir
        self.params, self.blockmap, self.blockorder = self.read_params()
        self.exe = os.path.join(apps_dir,self.appname,self.appname)
        self.preprocess = preprocess
        self.postprocess = postprocess

    def read_params(self,user=None,cid=None):
        '''read the INI file and return as a dictionary'''
        if cid is None or user is None:
            fn = self.appdir
        else:
            fn = os.path.join(self.user_dir,user,self.appname,cid)
        # append name of input file to end of string
        fn += os.sep + self.simfn

        Config = ConfigParser.ConfigParser()
        Config.read(fn)
        params = {}
        blockmap = {}
        blockorder = []

        if not os.path.isfile(fn):
            print "ERROR: input file does not exist: " + fn

        for section in Config.sections():
            options = Config.options(section)
            blockorder += [ section ]
            for option in options:
                try:
                    params[option] = Config.get(section, option)
                    blockmap.setdefault(section,[]).append(option)
                    if params[option] == -1:
                        DebugPrint("skip: %s" % option)
                except:
                    print("exception on %s!" % option)
                    params[option] = None
        #print 'params:',params
        #print 'blockmap:',blockmap
        #print 'blockorder:',blockorder
        return params, blockmap, blockorder

    def write_params(self,form_params,user):
        Config = ConfigParser.ConfigParser()
        cid = form_params['case_id']
        sim_dir=os.path.join(self.user_dir,user,self.appname,cid)
        if not os.path.exists(sim_dir):
            os.makedirs(sim_dir)
        fn = os.path.join(sim_dir,self.simfn)

        # write out parameters to screen
        #for (i,fp) in enumerate(form_params):
        #    print i,fp, form_params[fp]

        # create the ini file
        cfgfile = open(fn,'w')
        for section in self.blockorder:
            Config.add_section(section)
            for key in self.blockmap[section]:
                # for checkboxes that dont get sent when unchecked
                if key not in form_params: form_params[key] = 'false'
                #print key, form_params[key]
                # if the user leaves the value blank, don't output the parameter
                if form_params[key]:
                    Config.set(section,key,form_params[key])
        Config.write(cfgfile)
        cfgfile.close()
        return 1

class XML(App):
    """Class for reading/writing XML files."""
    def __init__(self,appname,preprocess=0,postprocess=0):
        self.appname = appname
        self.appdir = os.path.join(apps_dir,appname)
        self.outfn = appname + '.out'
        self.simfn = appname + '.xml'
        self.preprocess = preprocess
        self.postprocess = postprocess
        self.user_dir = user_dir
        self.params, self.blockmap, self.blockorder = self.read_params()
        self.exe = os.path.join(apps_dir,self.appname,self.appname)

    def read_params(self,user=None,cid=None):
        """read the XML file and return as a dictionary"""
        if cid is None or user is None:
            fn = self.appdir
        else:
            fn = os.path.join(self.user_dir,user,self.appname,cid)

        # append name of input file to end of string
        fn += os.sep + self.simfn
        tree = ET.parse(fn)
        root = tree.getroot()
        self.rootlabel = root.tag
        #for child in root:
        #    print child.tag, child.attrib, child.text
        params = {} 
        blockmap = {} 
        blockorder = [] 

        # Currently does not support multiple subsections within xml file
        # but needs to be included in the future 
        for section in root:
            blockorder += [ section.tag ]
            for child in section.getchildren():
                try:
                    params[child.tag] = child.text
                    blockmap.setdefault(section.tag,[]).append(child.tag)
                    if params[child.tag] == -1:
                        DebugPrint("skip: %s" % child.tag)
                except:
                    print("exception on %s!" % child.tag)
                    params[child.tag] = None
        if not params:
            print "ERROR: parameters not read correctly.\n"
            print "Please check xml file, and make sure it has a tree depth of three:"
            print "\t(1) a root element,"
            print "\t(2) subelements for each sections, and "
            print "\t(3) sub-elements under each section."
            sys.exit()
        #print '\nparams:',params
        #print '\nblockmap:',blockmap
        #print '\nblockorder:',blockorder
        return params, blockmap, blockorder

    def write_params(self,form_params,user):
        """Write parameters to file."""
        cid = form_params['case_id']
        sim_dir=os.path.join(self.user_dir,user,self.appname,cid)
        if not os.path.exists(sim_dir):
            os.makedirs(sim_dir)
        fn = os.path.join(sim_dir,self.simfn)

        f = open(fn, 'w')
        f.write("<?xml version=\"1.0\" encoding=\"UTF-8\"?>\n")

        f.write("<"+self.rootlabel+">\n")
        for section in self.blockorder:
            # following line is commented out because jmendel doesn't use subsections
            # need an option in the future to better understand how file is constructed
            #f.write("<%s>\n" % section)
            for key in self.blockmap[section]:
                f.write("\t<"+key+">"+form_params[key]+"</"+key+">\n")
            #f.write("</%s>\n" % section)
        f.write("</"+self.rootlabel+">\n")
        return 1

class JSON(App):
    """Class for reading/writing JSON files."""
    def __init__(self,appname,preprocess=0,postprocess=0):
        self.appname = appname
        self.appdir = os.path.join(apps_dir,appname)
        self.outfn = appname + '.out'
        self.simfn = appname + '.json'
        self.preprocess = preprocess
        self.postprocess = postprocess
        self.user_dir = user_dir
        self.params, self.blockmap, self.blockorder = self.read_params()
        self.exe = os.path.join(apps_dir,self.appname,self.appname)

    def read_params(self,user=None,cid=None):
        """read the JSON file and return as a dictionary"""
        if cid is None or user is None:
            fn = self.appdir
        else:
            fn = os.path.join(self.user_dir,user,self.appname,cid)
        # append name of input file to end of string
        fn += os.sep + self.simfn

        # read file
        with open(fn,'r') as f: data = f.read()
        # parse data
        parsed = json.loads(data)

        params = {}
        blockmap = {}
        blockorder = []

        if not os.path.isfile(fn):
            print "ERROR: input file does not exist: " + fn

        for section in parsed:
            # options = Config.options(section)
            blockorder += [ section ]
            for option in parsed[section]:
                try:
                    params[option] = parsed[section][option]
                    blockmap.setdefault(section,[]).append(option)
                    if params[option] == -1:
                        DebugPrint("skip: %s" % option)
                except:
                    print("exception on %s!" % option)
                    params[option] = None
        # print 'params:',params
        # print 'blockmap:',blockmap
        # print 'blockorder:',blockorder
        return params, blockmap, blockorder

    def write_params(self,form_params,user):
        """Write parameters to the JSON file."""
        cid = form_params['case_id']
        sim_dir=os.path.join(self.user_dir,user,self.appname,cid)
        if not os.path.exists(sim_dir):
            os.makedirs(sim_dir)
        fn = os.path.join(sim_dir,self.simfn)

        # write out parameters to screen\
        #for (i,fp) in enumerate(form_params):
        #    print i,fp, form_params[fp]

        # create the JSON file
        cfgfile = open(fn,'w')
        params = dict()
        for section in self.blockorder:
            params[section] = dict()
            for key in self.blockmap[section]:
                params[section][key] = form_params[key]
                # for checkboxes that dont get sent when unchecked
                if key not in form_params: params[key] = 'false'
                #print key, form_params[key]

        cfgfile.write(json.dumps(params))
        cfgfile.close()
        return 1
