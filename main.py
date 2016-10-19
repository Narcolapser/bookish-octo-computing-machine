#python imports
import json
from os.path import join

#Kivy Imports.
import kivy
kivy.require('1.9.1')

from kivy.app import App
from kivy.config import ConfigParser
from kivy.storage.jsonstore import JsonStore

from kivy.properties import ObjectProperty, StringProperty

from kivy.uix.widget import Widget
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.settings import SettingsWithSidebar
from kivy.uix.settings import SettingOptions
from kivy.uix.popup import Popup
from kivy.uix.textinput import TextInput

from kivy.uix.gridlayout import GridLayout
from kivy.uix.floatlayout import FloatLayout

from kivy.uix.tabbedpanel import TabbedPanel
from kivy.uix.tabbedpanel import TabbedPanelItem
from kivy.uix.tabbedpanel import TabbedPanelHeader


#Octo imports
from info_panel import Info_Panel
from logback_panel import Logback_Panel
from catalina_panel import Catalina_Panel
from model import *

#Later I want to replace this with a proper settings system.
hosts = json.load(open("hosts.ini"))

class Octo(TabbedPanel):
    '''
    The main Octo class. A tabbed panel with tabs for each connection to a server.
    '''
    serverTab = ObjectProperty(None)
    
    def addServers(self):
        '''
        This method is called to create the servers tab and add the servers to it.
        '''
        self.serverTab.text = "Servers"
        self.serverTab.addServers()

    def addServer(self,config):
        '''
        This method is called to create with a config to add it to the servers tab.
        '''
        self.serverTab.text = "Servers"
        self.serverTab.addServer(config)

    def add_connection(self,val):
        '''
        This method is used for creating a new tab. A connection is made to the relevant server and
        then is passed to the OctoServer object that is created.
        '''
        OServ = OctoServer()
        OServ.connect(val)
        OServ.text = val['name']
        OServ.load_panels()
        self.add_widget(OServ)
        self.switch_to(OServ)
        
        
class OctoServersTab(TabbedPanelItem):
    '''
    The default tab that has the servers as tiles. 
    '''
    grid = ObjectProperty(None)

    def addServers(self):
        '''
        This method reads the hosts from json that was read in by hosts.ini. Then creates tiles for
        each of the hosts. Right now just buttons. hopefully in the future they'll be a cooler.
        '''
        for host in hosts:
            o = OctoLauncher()
            o.text = host
            o.config = hosts[host]
            self.grid.add_widget(o)

    def addServer(self,con):
        '''
        Takes a configuration and adds it to the server list.
        '''
        try:
            o = OctoLauncher()
            o.text=con['name']
            con['password'] = decrypt(con['password'])
            o.config=con
            self.grid.add_widget(o)
        except Exception as e:
            print(e)
        
        

class OctoServer(TabbedPanelItem):
    '''
    The holder for the server info panels. This is a subclass of tabbed panel item, so it is also
    the tab at the top of the display. So this holds the info panels and represents itself in the
    tab row on the top.
    '''
    info_panel = ObjectProperty(None)

    def connect(self,configs):
        '''
        Create the connection that the info panels will use.
        '''
        self.server = Server(configs)
    
    def load_panels(self):
        '''
        Instantiate and load the info panels into the display. Note that the order they are
        displayed is opposite the order that they are entered below.
        '''
        ip = Info_Panel()
        ip.setServer(self.server)
        self.info_panel.add_widget(ip)
        
        lb = Logback_Panel()
        lb.setServer(self.server)
        self.info_panel.add_widget(lb)        

        cp = Catalina_Panel()
        cp.setServer(self.server)
        self.info_panel.add_widget(cp)
        

class OctoLauncher(Button):
    pass

class OctoOverlay(FloatLayout):
    octo = ObjectProperty(None)
    sb = ObjectProperty(None)
    settings_string = StringProperty(u'...')#Things I wanted: ⚙⋮≡
    
    data_dir = ''

    def settingsPressed(self):
        self.octo.size=(0,0)
        self.sb.size=(0,0)
        self.octo.size_hint=(0,0)

        self.oed = OctoEditServer()
        self.oed.doneButton.bind(on_press=self.settingsReturn)
        self.add_widget(self.oed)

    def settingsReturn(self,val):
        self.remove_widget(self.oed)
        self.sb.size=(45,45)
        self.octo.size_hint=(1,1)
        try:
            config = {}
            config['name'] = self.oed.ids['name'].text
            config['address'] = self.oed.ids['address'].text
            config['username'] = self.oed.ids['username'].text
            config['password'] = encrypt(self.oed.ids['password'].text)
            self.store.put(config['name'],
                           name=config['name'],
                           address=config['address'],
                           username=config['username'],
                           password=config['password'])
            self.octo.addServer(config)
        except:
            pass

    def loadServers(self):
        self.store = JsonStore(join(self.data_dir, 'hosts.json'))

        for key in self.store.keys():
            self.octo.addServer(self.store.get(key))
        
class OctoEditServer(GridLayout):
    doneButton = ObjectProperty(None)
    pass

class OctoApp(App):
    def build(self):
        #self.settings_cls = OctoSettings
        octo_over = OctoOverlay()
        self.octo = octo_over.octo
        self.octo_over = octo_over
        self.octo_over.data_dir = self.data_dir
        octo_over.loadServers()

        return octo_over

    def on_pause(self):
        return True

    def on_resume(self):
        pass

    def open_connection(self,val):
        self.octo.add_connection(val)

    def build_config(self,config):
        self.data_dir = getattr(self, 'user_data_dir')
        self.config = config
        config.read('octo.ini')
        config.setdefaults('Octo',
            {'optionsOcto':'Click to add server.'})

    def build_settings(self,settings):
        with open(join(self.data_dir,'Octo.json')) as val_file:
            vals = val_file.read()
            settings.add_json_panel('Octo',self.config,data=vals)

appPointer = None

if __name__ == '__main__':
    appPointer = OctoApp()
    appPointer.run()
