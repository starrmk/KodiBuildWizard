
import xbmc, xbmcaddon, xbmcgui, xbmcplugin,os,base64,sys,xbmcvfs
import shutil
import urllib, urllib2
import re , glob
import extract
import downloader
import time
import plugintools

from addon.common.addon import Addon
from addon.common.net import Net

USER_AGENT   = 'Mozilla/5.0 (Windows; U; Windows NT 5.1; en-GB; rv:1.9.0.3) Gecko/2008092417 Firefox/3.0.3'
addon_id     = 'plugin.video.KodiBuildWizard'
#PLUGIN       = 'plugin.video.KodiBuildWizard'

ADDON        = xbmcaddon.Addon(id=addon_id)

PATH         = "The Kodi Build Wizard"
VERSION      = "2.0"

dialog       = xbmcgui.Dialog()
dp           = xbmcgui.DialogProgress()
net          = Net()
U            = ADDON.getSetting('User')

FANART       = xbmc.translatePath(os.path.join('special://home/addons/' + addon_id , 'icon.png'))
ICON         = xbmc.translatePath(os.path.join('special://home/addons/' + addon_id, 'icon.png'))
ART          = xbmc.translatePath(os.path.join('special://home/addons/' + addon_id + '/resources/art/'))

WZPATH       = xbmc.translatePath(os.path.join('special://home/addons/' + addon_id))
CMPATH       = xbmc.translatePath('special://home');
DBPATH       = xbmc.translatePath('special://database');
TNPATH       = xbmc.translatePath('special://thumbnails');

# Super Faves Output...
zip          = ADDON.getSetting('zip')
USB          = xbmc.translatePath(os.path.join(zip))
fav          = xbmc.translatePath(os.path.join('special://home/common/addon_data/plugin.program.super.favourites',))
# Lookup Parameters Here...
BDPATH       = ADDON.getSetting('base_url');
SCNAME       = ADDON.getSetting('COMMON_SELECTED');
SCPATH       = ADDON.getSetting(SCNAME);
SCPATH1      = xbmc.translatePath(SCPATH)
SCADDONS     = xbmc.translatePath('special://profile')
USEREXP      = ADDON.getSetting('UserExp');
WIZSTR       = ADDON.getSetting('WizStr');


restore_path     = os.path.join(xbmc.translatePath('special://profile/addon_data'), '')
restorexbmc_path = os.path.join(xbmc.translatePath('special://profile'), '')
restore_udata    = os.path.join(xbmc.translatePath('special://home/userdata'), '')
backup_path      = SCPATH1 + 'customisation/'
guide_path       = SCPATH1 + 'epg/'


# Config Path change from...
PWASN      = ADDON.getSetting('COMMON_HOME_SD');
PWAS       = PWASN
# Config Path change to....
PNOW       = SCPATH
BASEURL    = BDPATH
H          = 'http://'
EXCLUDES   = ['repository.xbmc.org','plugin.video.KodiBuildWizard','script.module.addon.common','repository.KodiBuildWizard','common','special://home/common',SCPATH,SCPATH1]

def INDEX():
    addDir('1 - INSTALL KODIBUILD    ',BASEURL,2,ART+'icon.png',FANART,'')
    addDir('2 - COMMON CONFIGURATION ',BASEURL,3,ART+'icon.png',FANART,'')
    addDir('3 - MAINTENANCE          ',BASEURL,4,ART+'icon.png',FANART,'')
    addDir('4 - BUILD ADMIN          ',BASEURL,17,ART+'icon.png',FANART,'')
    setView('movies', 'MAIN')

def BUILDMENU():
    link = OPEN_URL(BASEURL+'/build/wizard_'+WIZSTR+'.txt').replace('\n','').replace('\r','')
    match = re.compile('name="(.+?)".+?rl="(.+?)".+?mg="(.+?)".+?anart="(.+?)".+?escription="(.+?)"').findall(link)
    for name,url,iconimage,fanart,description in match:
        addDir(name,url,9,iconimage,fanart,description)

    setView('movies', 'MAIN')

def BUILDCOMMON():
    addDir('1 - Install Super Favourites Data ',fav  ,16,ART+'icon.png',FANART,'')
    addDir('2 - Install TvGuide Data  ',guide_path ,14,ART+'icon.png',FANART,'')
    addDir('==================================','url',1 ,ART+'icon.png',FANART,'')
    addDir('3 - Install CommonFiles to Path   ',SCPATH1  ,10,ART+'icon.png',FANART,'')
    addDir('4 - Install UserSettings From Zip ',restore_path,21,ART+'icon.png',FANART,'')
    addDir('==================================','url',1,ART+'icon.png',FANART,'')
    addDir('5 - Backup XML to Customisation   ','url',11,ART+'icon.png',FANART,'')
    addDir('6 - Patch XML Files with Path     ','url',13,ART+'icon.png',FANART,'')
    addDir('7 - Restore XML From Customisation','url',12,ART+'icon.png',FANART,'')
    setView('movies', 'MAIN')

def MAINTENANCE():
    addDir('1 - DELETE CACHE   ','url',6,ART+'icon.png',FANART,'')
    addDir('2 - FRESH START    ','url',7,ART+'icon.png',FANART,'')
    addDir('3 - DELETE PACKAGES','url',8,ART+'icon.png',FANART,'')
    setView('movies', 'MAIN')

def BUILDSC():
    addDir('1 - Export Super Favourites Data ','url',15,ART+'icon.png',FANART,'')
    addDir('2 - Export Build Data            ','url',18,ART+'icon.png',FANART,'')
    addDir('3 - Export BuildWizard           ','url',19,ART+'icon.png',FANART,'')
    addDir('4 - Export UserSettings to Zip   ','url',20,ART+'icon.png',FANART,'')
    setView('movies', 'MAIN')


#################################
####### POPUP TEXT BOXES ########
#################################

def TextBoxes(heading,announce):
  class TextBox():
    WINDOW=10147
    CONTROL_LABEL=1
    CONTROL_TEXTBOX=5
    def __init__(self,*args,**kwargs):
      xbmc.executebuiltin("ActivateWindow(%d)" % (self.WINDOW, )) # activate the text viewer window
      self.win=xbmcgui.Window(self.WINDOW) # get window
      xbmc.sleep(500) # give window time to initialize
      self.setControls()
    def setControls(self):
      self.win.getControl(self.CONTROL_LABEL).setLabel(heading) # set heading
      try: f=open(announce); text=f.read()
      except: text=announce
      self.win.getControl(self.CONTROL_TEXTBOX).setText(str(text))
      return
  TextBox()

#################################
####### OPEN URL         ########
#################################
def OPEN_URL(url):
    req = urllib2.Request(url)
    req.add_header('User-Agent', 'Mozilla/5.0 (Windows; U; Windows NT 5.1; en-GB; rv:1.9.0.3) Gecko/2008092417 Firefox/3.0.3')
    response = urllib2.urlopen(req)
    link=response.read()
    response.close()
    return link

#################################
#### COPY SUPER FAVES  ##########
#################################
def BACKUP_SF():
    if zip == '':
        dialog.ok('"Super Faves Extract"','You have not set your ZIP Folder.\nPlease update the addon settings and try again.','','')
        ADDON.openSettings(sys.argv[0])
    to_backup = xbmc.translatePath(os.path.join('special://home/common/addon_data/plugin.program.super.favourites',))
    backup_zip = xbmc.translatePath(os.path.join(USB,'SuperFav.zip'))
    import zipfile

    dp.create("USB BACKUP/RESTORE","Backing Up",'', 'Please Wait')
    zipobj = zipfile.ZipFile(backup_zip , 'w', zipfile.ZIP_DEFLATED)
    rootlen = len(to_backup)
    for_progress = []
    ITEM =[]
    for base, dirs, files in os.walk(to_backup):
        for file in files:
            ITEM.append(file)
    N_ITEM =len(ITEM)
    for base, dirs, files in os.walk(to_backup):
        for file in files:
            for_progress.append(file)
            progress = len(for_progress) / float(N_ITEM) * 100
            dp.update(int(progress),"Backing Up",'[COLOR yellow]%s[/COLOR]'%file, 'Please Wait')
            fn = os.path.join(base, file)
            if not 'temp' in dirs:
                if not 'plugin.video.KodiBuildWizard' in dirs:
                    import time
                    CUNT= '01/01/1980'
                    FILE_DATE=time.strftime('%d/%m/%Y', time.gmtime(os.path.getmtime(fn)))
                    if FILE_DATE > CUNT:
                        zipobj.write(fn, fn[rootlen:])
    zipobj.close()
    dp.close()
    dialog.ok("Super Faves Extract", "You Are Now Backed Up", '','')

#################################
#### COPY WIZARD       ##########
#################################
def BACKUP_WZ():
    if zip == '':
        dialog.ok('"Wizard Build.."','You have not set your ZIP Folder.\nPlease update the addon settings and try again.','','')
        ADDON.openSettings(sys.argv[0])
    to_backup = WZPATH
    backup_zip = xbmc.translatePath(os.path.join(USB,addon_id +  '.zip'))
    import zipfile

    dp.create("Extract Wizard","Backing Up",'', 'Please Wait')
    zipobj = zipfile.ZipFile(backup_zip , 'w', zipfile.ZIP_DEFLATED)
    rootlen = len(to_backup) - len(addon_id)
    for_progress = []
    ITEM =[]
    for base, dirs, files in os.walk(to_backup):
        for file in files:
            ITEM.append(file)
    N_ITEM =len(ITEM)
    for base, dirs, files in os.walk(to_backup):
        for file in files:
            for_progress.append(file)
            progress = len(for_progress) / float(N_ITEM) * 100
            dp.update(int(progress),"Backing Up",'[COLOR yellow]%s[/COLOR]'%file, 'Please Wait')
            fn = os.path.join(base, file)
            if not 'temp' in dirs:
                if not 'plugin.video.KodiBuildWizard' in dirs:
                    import time
                    CUNT= '01/01/1980'
                    FILE_DATE=time.strftime('%d/%m/%Y', time.gmtime(os.path.getmtime(fn)))
                    if FILE_DATE > CUNT:
                        zipobj.write(fn, fn[rootlen:])
    zipobj.close()
    dp.close()
    dialog.ok("Extract Wizard", "Wizard has been Extracted...", '','')

#################################
#### COPY USER EXP.    ##########
#################################
def BACKUP_UX():
    if zip == '':
        dialog.ok('"Backup User Experience"','You have not set your ZIP Folder.\nPlease update the addon settings and try again.','','')
        ADDON.openSettings(sys.argv[0])
    to_backup = xbmc.translatePath(os.path.join(backup_path))
    backup_zip = xbmc.translatePath(os.path.join(USB, USEREXP + '.zip'))
    import zipfile

    dp.create("USB BACKUP/RESTORE","Backing Up",'', 'Please Wait')
    zipobj = zipfile.ZipFile(backup_zip , 'w', zipfile.ZIP_DEFLATED)
    rootlen = len(to_backup)
    for_progress = []
    ITEM =[]
    for base, dirs, files in os.walk(to_backup):
        for file in files:
            ITEM.append(file)
    N_ITEM =len(ITEM)
    for base, dirs, files in os.walk(to_backup):
        for file in files:
            for_progress.append(file)
            progress = len(for_progress) / float(N_ITEM) * 100
            dp.update(int(progress),"Backing Up",'[COLOR yellow]%s[/COLOR]'%file, 'Please Wait')
            fn = os.path.join(base, file)
            if not 'temp' in dirs:
                if not 'plugin.video.KodiBuildWizard' in dirs:
                    import time
                    CUNT= '01/01/1980'
                    FILE_DATE=time.strftime('%d/%m/%Y', time.gmtime(os.path.getmtime(fn)))
                    if FILE_DATE > CUNT:
                        zipobj.write(fn, fn[rootlen:])
    zipobj.close()
    dp.close()
    dialog.ok("Backup User Experience", "You Are Now Backed Up", '','')


#################################
#### COPY SUPER FAVES  ##########
#################################
def BACKUP_BD():
    if zip == '':
        dialog.ok('"Build Backup"','You have not set your ZIP Folder.\nPlease update the addon settings and try again.','','')
        ADDON.openSettings(sys.argv[0])
    to_backup  = xbmc.translatePath(os.path.join('special://home/addons',))
    to_backup0 = xbmc.translatePath(os.path.join('special://home/common',))
    to_backup1 = xbmc.translatePath(os.path.join('special://home/media',))
    to_backup2 = xbmc.translatePath(os.path.join('special://home/userdata',))

    backup_zip = xbmc.translatePath(os.path.join(USB,'ArchiveCURR.zip'))
    import zipfile

    dp.create("Extract Build...","Backing Up",'', 'Please Wait')
    zipobj = zipfile.ZipFile(backup_zip , 'w', zipfile.ZIP_DEFLATED)
    rootlen = len(to_backup)-7
    for_progress = []
    ITEM =[]

    for base, dirs, files in os.walk(to_backup):
        for file in files:
            ITEM.append(file)
        N_ITEM =len(ITEM)
    for base, dirs, files in os.walk(to_backup):
        for file in files:
            for_progress.append(file)
            progress = len(for_progress) / float(N_ITEM) * 100
            dp.update(int(progress),"Backing Up",'[COLOR yellow]%s[/COLOR]'%file, 'Please Wait')
            fn = os.path.join(base, file)
            if not 'temp' in dirs:
                if not 'plugin.video.KodiBuildWizard' in dirs:
                    import time
                    CUNT= '01/01/1980'
                    FILE_DATE=time.strftime('%d/%m/%Y', time.gmtime(os.path.getmtime(fn)))
                    if FILE_DATE > CUNT:
                        zipobj.write(fn, fn[rootlen:])

    for base, dirs, files in os.walk(to_backup0):
        for file in files:
            ITEM.append(file)
        N_ITEM =len(ITEM)
    for base, dirs, files in os.walk(to_backup0):
        for file in files:
            for_progress.append(file)
            progress = len(for_progress) / float(N_ITEM) * 100
            dp.update(int(progress),"Backing Up",'[COLOR yellow]%s[/COLOR]'%file, 'Please Wait')
            fn = os.path.join(base, file)
            if not 'temp' in dirs:
                if not 'plugin.video.KodiBuildWizard' in dirs:
                    import time
                    CUNT= '01/01/1980'
                    FILE_DATE=time.strftime('%d/%m/%Y', time.gmtime(os.path.getmtime(fn)))
                    if FILE_DATE > CUNT:
                        zipobj.write(fn, fn[rootlen:])

    for base, dirs, files in os.walk(to_backup1):
        for file in files:
            ITEM.append(file)
        N_ITEM =len(ITEM)
    for base, dirs, files in os.walk(to_backup1):
        for file in files:
            for_progress.append(file)
            progress = len(for_progress) / float(N_ITEM) * 100
            dp.update(int(progress),"Backing Up",'[COLOR yellow]%s[/COLOR]'%file, 'Please Wait')
            fn = os.path.join(base, file)
            if not 'temp' in dirs:
                if not 'plugin.video.KodiBuildWizard' in dirs:
                    import time
                    CUNT= '01/01/1980'
                    FILE_DATE=time.strftime('%d/%m/%Y', time.gmtime(os.path.getmtime(fn)))
                    if FILE_DATE > CUNT:
                        zipobj.write(fn, fn[rootlen:])

    for base, dirs, files in os.walk(to_backup2):
        for file in files:
            ITEM.append(file)
        N_ITEM =len(ITEM)
    for base, dirs, files in os.walk(to_backup2):
        for file in files:
            for_progress.append(file)
            progress = len(for_progress) / float(N_ITEM) * 100
            dp.update(int(progress),"Backing Up",'[COLOR yellow]%s[/COLOR]'%file, 'Please Wait')
            fn = os.path.join(base, file)
            if not 'temp' in dirs:
                if not 'plugin.video.KodiBuildWizard' in dirs:
                    import time
                    CUNT= '01/01/1980'
                    FILE_DATE=time.strftime('%d/%m/%Y', time.gmtime(os.path.getmtime(fn)))
                    if FILE_DATE > CUNT:
                        zipobj.write(fn, fn[rootlen:])


    zipobj.close()
    dp.close()
    dialog.ok("Build has been Extracted..", "You Are Now Backed Up....", '','')


#################################
####COPY CUSTOMISATION ##########
#################################
def backup_xml(url):
    for xml_file in glob.glob(os.path.join(restore_udata, "sources.xml")):
        shutil.copy(xml_file, backup_path)
    
        #for xml_file in glob.glob(os.path.join(restorexbmc_path, "*.xml")):
        #shutil.copy(xml_file, backup_path)
    directories = os.listdir(restore_path)
    for d in directories:
        create_directory(backup_path, d)
        source = os.path.join(restore_path, d)
        destination = os.path.join(backup_path, d)
        for xml_file in glob.glob(os.path.join(source, "settings.xml")):
            shutil.copy(xml_file, destination)
        for xml_file in glob.glob(os.path.join(source, "*.list")):
            shutil.copy(xml_file, destination)
    dialog = xbmcgui.Dialog()
    dialog.ok("XML Backup", "All userdata and addon settings.xml files backed up")


def restore_xml(url):
    for xml_file in glob.glob(os.path.join(restore_udata, "sources.xml")):
        shutil.copy(xml_file, backup_path)
        #for xml_file in glob.glob(os.path.join(backup_path, "*.xml")):
        #   shutil.copy(xml_file, restorexbmc_path)
    
    directories = os.listdir(backup_path)
    for d in directories:
        source = os.path.join(backup_path, d)
        destination = os.path.join(restore_path, d)
        for xml_file in glob.glob(os.path.join(source, "settings.xml")):
            shutil.copy(xml_file, destination)
        for xml_file in glob.glob(os.path.join(source, "*.list")):
            shutil.copy(xml_file, destination)

    dialog = xbmcgui.Dialog()
    if dialog.yesno("XML Backup", "All userdata/*.xml and addon 'settings.xml' files restored", "Reboot to load restored gui settings settings", '', "Reboot Later", "Reboot Now"):
        killxbmc()
    #else:
        #xbmc.executebuiltin('xbmc.activatewindow(0)')

def create_directory(dir_path, dir_name=None):
    if dir_name:
        dir_path = os.path.join(dir_path, dir_name)
    dir_path = dir_path.strip()
    if not os.path.exists(dir_path):
        os.makedirs(dir_path)
    return dir_path

#################################
####COPY CUSTOMISATION ##########
#################################

def patch_xml(url):
    for xml_file in glob.glob(os.path.join(restore_udata, "*.xml")):
        replace_xml(xml_file)
    
    directories = os.listdir(restore_udata)
    for d in directories:
        print "restore_udata" + restore_udata
        source = os.path.join(restore_udata, d)
        for xml_file in glob.glob(os.path.join(source, "settings.xml")):
            replace_xml(xml_file)
        for xml_file in glob.glob(os.path.join(source, "*.list")):
            replace_xml(xml_file)

def replace_xml(inpfile):
    f = open(inpfile,'r')
    filedata = f.read()
    f.close()
    newdata = filedata.replace( PWAS , PNOW )
    f = open(inpfile,'w')
    f.write(newdata)
    f.close

#################################
#### GET TV GUIDE ###############
#################################

def get_tvguide(url):
    path = xbmc.translatePath(os.path.join('special://home/addons','packages'))
    dp = xbmcgui.DialogProgress()
    dp.create("Kodi Build Wizard","Downloading TV GUIDE ", '', 'Please Wait')
    
    url2 = xbmc.translatePath(url)

    directories = os.listdir(url2)
    for d in directories:
        create_directory(url2, d)
    
    lib=os.path.join(path, 'tvguide.zip')
    try:
        os.remove(lib)
    except:
        pass
    downloader.download(BASEURL+'/epg/tvguide.zip',lib,dp)
    addonfolder = url2
    time.sleep(2)
    dp.update(0,"", "Extracting Zip Please Wait")
    print '======================================='
    print addonfolder
    print '======================================='
    extract.all(lib,addonfolder,dp)
    
    dialog = xbmcgui.Dialog()
    dialog.ok("The Kodi Build Wizard", "New TV Guide Data has been Downloaded, Data will be refreshed on Restart")

#################################
#### GET USER CUSTOM ZIP  ########
#################################

def get_usercustom(url):
    path = xbmc.translatePath(os.path.join('special://home/addons','packages'))
    dp = xbmcgui.DialogProgress()
    dp.create("Kodi Build Wizard","Get User Customisation ", '', 'Please Wait')

    
    directories = os.listdir(url)
    for d in directories:
        create_directory(url, d)
    
    lib=os.path.join(path, USEREXP + '.zip')
    try:
        os.remove(lib)
    except:
        pass
    downloader.download(BASEURL + '/build/' + USEREXP + '.zip',lib,dp)
    addonfolder = url
    time.sleep(2)
    dp.update(0,"", "Extracting Zip Please Wait")
    print '======================================='
    print addonfolder
    print '======================================='
    extract.all(lib,addonfolder,dp)
    
    dialog = xbmcgui.Dialog()
    dialog.ok("The Kodi Build Wizard", "User Customisation Have been downloaded. Enjoy!!!")

#################################
#### GET SUPER FAVS ZIP  ########
#################################

def get_superfav(url):
    path = xbmc.translatePath(os.path.join('special://home/addons','packages'))
    dp = xbmcgui.DialogProgress()
    dp.create("Kodi Build Wizard","Get New Favourites ", '', 'Please Wait')
    print "URL IS : " + url
    print "URL IS REALLY " + xbmc.translatePath(url)
    url2 = xbmc.translatePath(url)
    
    directories = os.listdir(url2)
    for d in directories:
        create_directory(url2, d)
    
    lib=os.path.join(path, 'SuperFav.zip')
    try:
        os.remove(lib)
    except:
        pass
    downloader.download(BASEURL+'/build/SuperFav.zip',lib,dp)
    addonfolder = url2
    time.sleep(2)
    dp.update(0,"", "Extracting Zip Please Wait")
    print '======================================='
    print addonfolder
    print '======================================='
    extract.all(lib,addonfolder,dp)
    
    dialog = xbmcgui.Dialog()
    dialog.ok("The Kodi Build Wizard", "New Favourites Have been downloaded. Enjoy!!!")


#################################
####BUILD COMMON ################
#################################

def MAKECOMMON(name,url,description):
    path = xbmc.translatePath(os.path.join('special://home/addons','packages'))
    dp = xbmcgui.DialogProgress()
    dp.create("Kodi Build Wizard","Downloading ", '', 'Please Wait')
    lib=os.path.join(path, 'common.zip')
    try:
        os.remove(lib)
    except:
        pass
    downloader.download(BASEURL+'/build/common.zip',lib,dp)

    addonfolder = url
    time.sleep(2)
    dp.update(0,"", "Extracting Zip Please Wait")
    print '======================================='
    print addonfolder
    print '======================================='
    extract.all(lib,addonfolder,dp)

    dialog = xbmcgui.Dialog()
    dialog.ok("The Kodi Build Wizard", "Common Folder Created in Selected Location, Press OK to force close Kodi")
    killxbmc()

#################################
####BUILD INSTALL################
#################################

def WIZARD(name,url,description):
    path = xbmc.translatePath(os.path.join('special://home/addons','packages'))
    dp = xbmcgui.DialogProgress()
    dp.create("The Kodi Build Wizard","Downloading ",'', 'Please Wait')
    lib=os.path.join(path, name+'.zip')
    try:
       os.remove(lib)
    except:
       pass
    downloader.download(url, lib, dp)
    addonfolder = xbmc.translatePath(os.path.join('special://','home'))
    time.sleep(2)
    dp.update(0,"", "Extracting Zip Please Wait")
    print '======================================='
    print addonfolder
    print '======================================='
    extract.all(lib,addonfolder,dp)
    dialog = xbmcgui.Dialog()
    dialog.ok("The Kodi Build Wizard", "To save changes you now need to force close Kodi, Press OK to force close Kodi")
    killxbmc()

################################
###DELETE PACKAGES##############
####THANKS GUYS @ XUNITY########

def DeletePackages(url):
    print '############################################################       DELETING PACKAGES             ###############################################################'
    packages_cache_path = xbmc.translatePath(os.path.join('special://home/addons/packages', ''))
    try:    
        for root, dirs, files in os.walk(packages_cache_path):
            file_count = 0
            file_count += len(files)
            
        # Count files and give option to delete
            if file_count > 0:
    
                dialog = xbmcgui.Dialog()
                if dialog.yesno("Delete Package Cache Files", str(file_count) + " files found", "Do you want to delete them?"):
                            
                    for f in files:
                        os.unlink(os.path.join(root, f))
                    for d in dirs:
                        shutil.rmtree(os.path.join(root, d))
                    dialog = xbmcgui.Dialog()
                    dialog.ok("The KodiStu Build Wizard", "Packages Successfuly Removed", "[COLOR blue] Time to Restart [/COLOR]")
    except: 
        dialog = xbmcgui.Dialog()
        dialog.ok("The KodiStu Build Wizard", "Sorry we were not able to remove Package Files", "[COLOR blue] Time to Restart [/COLOR]")

#################################
###DELETE CACHE##################
####THANKS GUYS @ XUNITY########
	
def deletecachefiles(url):
    print '############################################################       DELETING STANDARD CACHE             ###############################################################'
    xbmc_cache_path = os.path.join(xbmc.translatePath('special://home'), 'cache')
    if os.path.exists(xbmc_cache_path)==True:    
        for root, dirs, files in os.walk(xbmc_cache_path):
            file_count = 0
            file_count += len(files)
        
        # Count files and give option to delete
            if file_count > 0:
    
                dialog = xbmcgui.Dialog()
                if dialog.yesno("Delete Cache Files", str(file_count) + " files found", "Do you want to delete them?"):
                
                    for f in files:
                        try:
                            os.unlink(os.path.join(root, f))
                        except:
                            pass
                    for d in dirs:
                        try:
                            shutil.rmtree(os.path.join(root, d))
                        except:
                            pass
                        
            else:
                pass

    if xbmc.getCondVisibility('system.platform.ATV2'):
        atv2_cache_a = os.path.join('/private/var/mobile/Library/Caches/AppleTV/Video/', 'Other')
        
        for root, dirs, files in os.walk(atv2_cache_a):
            file_count = 0
            file_count += len(files)
        
            if file_count > 0:

                dialog = xbmcgui.Dialog()
                if dialog.yesno("Delete ATV2 Cache Files", str(file_count) + " files found in 'Other'", "Do you want to delete them?"):
                
                    for f in files:
                        os.unlink(os.path.join(root, f))
                    for d in dirs:
                        shutil.rmtree(os.path.join(root, d))
                        
            else:
                pass
        atv2_cache_b = os.path.join('/private/var/mobile/Library/Caches/AppleTV/Video/', 'LocalAndRental')
        
        for root, dirs, files in os.walk(atv2_cache_b):
            file_count = 0
            file_count += len(files)
        
            if file_count > 0:

                dialog = xbmcgui.Dialog()
                if dialog.yesno("Delete ATV2 Cache Files", str(file_count) + " files found in 'LocalAndRental'", "Do you want to delete them?"):
                
                    for f in files:
                        os.unlink(os.path.join(root, f))
                    for d in dirs:
                        shutil.rmtree(os.path.join(root, d))
                        
            else:
                pass
              # Set path to Cydia Archives cache files
                             

    # Set path to What th Furk cache files
    wtf_cache_path = os.path.join(xbmc.translatePath('special://profile/addon_data/plugin.video.whatthefurk/cache'), '')
    if os.path.exists(wtf_cache_path)==True:    
        for root, dirs, files in os.walk(wtf_cache_path):
            file_count = 0
            file_count += len(files)
        
        # Count files and give option to delete
            if file_count > 0:
    
                dialog = xbmcgui.Dialog()
                if dialog.yesno("Delete WTF Cache Files", str(file_count) + " files found", "Do you want to delete them?"):
                
                    for f in files:
                        os.unlink(os.path.join(root, f))
                    for d in dirs:
                        shutil.rmtree(os.path.join(root, d))
                        
            else:
                pass
                
                # Set path to 4oD cache files
    channel4_cache_path= os.path.join(xbmc.translatePath('special://profile/addon_data/plugin.video.4od/cache'), '')
    if os.path.exists(channel4_cache_path)==True:    
        for root, dirs, files in os.walk(channel4_cache_path):
            file_count = 0
            file_count += len(files)
        
        # Count files and give option to delete
            if file_count > 0:
    
                dialog = xbmcgui.Dialog()
                if dialog.yesno("Delete 4oD Cache Files", str(file_count) + " files found", "Do you want to delete them?"):
                
                    for f in files:
                        os.unlink(os.path.join(root, f))
                    for d in dirs:
                        shutil.rmtree(os.path.join(root, d))
                        
            else:
                pass
                
                # Set path to BBC iPlayer cache files
    iplayer_cache_path= os.path.join(xbmc.translatePath('special://profile/addon_data/plugin.video.iplayer/iplayer_http_cache'), '')
    if os.path.exists(iplayer_cache_path)==True:    
        for root, dirs, files in os.walk(iplayer_cache_path):
            file_count = 0
            file_count += len(files)
        
        # Count files and give option to delete
            if file_count > 0:
    
                dialog = xbmcgui.Dialog()
                if dialog.yesno("Delete BBC iPlayer Cache Files", str(file_count) + " files found", "Do you want to delete them?"):
                
                    for f in files:
                        os.unlink(os.path.join(root, f))
                    for d in dirs:
                        shutil.rmtree(os.path.join(root, d))
                        
            else:
                pass
                
                
                # Set path to Simple Downloader cache files
    downloader_cache_path = os.path.join(xbmc.translatePath('special://profile/addon_data/script.module.simple.downloader'), '')
    if os.path.exists(downloader_cache_path)==True:    
        for root, dirs, files in os.walk(downloader_cache_path):
            file_count = 0
            file_count += len(files)
        
        # Count files and give option to delete
            if file_count > 0:
    
                dialog = xbmcgui.Dialog()
                if dialog.yesno("Delete Simple Downloader Cache Files", str(file_count) + " files found", "Do you want to delete them?"):
                
                    for f in files:
                        os.unlink(os.path.join(root, f))
                    for d in dirs:
                        shutil.rmtree(os.path.join(root, d))
                        
            else:
                pass
                
                # Set path to ITV cache files
    itv_cache_path = os.path.join(xbmc.translatePath('special://profile/addon_data/plugin.video.itv/Images'), '')
    if os.path.exists(itv_cache_path)==True:    
        for root, dirs, files in os.walk(itv_cache_path):
            file_count = 0
            file_count += len(files)
        
        # Count files and give option to delete
            if file_count > 0:
    
                dialog = xbmcgui.Dialog()
                if dialog.yesno("Delete ITV Cache Files", str(file_count) + " files found", "Do you want to delete them?"):
                
                    for f in files:
                        os.unlink(os.path.join(root, f))
                    for d in dirs:
                        shutil.rmtree(os.path.join(root, d))
                        
            else:
                pass
				
                # Set path to temp cache files
    temp_cache_path = os.path.join(xbmc.translatePath('special://home/temp'), '')
    if os.path.exists(temp_cache_path)==True:    
        for root, dirs, files in os.walk(temp_cache_path):
            file_count = 0
            file_count += len(files)
        
        # Count files and give option to delete
            if file_count > 0:
    
                dialog = xbmcgui.Dialog()
                if dialog.yesno("Delete TEMP dir Cache Files", str(file_count) + " files found", "Do you want to delete them?"):
                
                    for f in files:
                        os.unlink(os.path.join(root, f))
                    for d in dirs:
                        shutil.rmtree(os.path.join(root, d))
                        
            else:
                pass
				

    dialog = xbmcgui.Dialog()
    dialog.ok("The Kodi Build Wizard", " All Cache Files Removed", "[COLOR blue] Time to Restart [/COLOR]")


def facebook():
    TextBoxes('The KodiStu Build Wizard', '[COLOR=red]Welcome to The KodiStu Build Wizard[/COLOR]')



###############################################################
###FORCE CLOSE KODI - ANDROID ONLY WORKS IF ROOTED#############
#######LEE @ COMMUNITY BUILDS##################################

def killxbmc():
    choice = xbmcgui.Dialog().yesno('Force Close Kodi', 'You are about to close Kodi', 'Would you like to continue?', nolabel='No, Cancel',yeslabel='Yes, Close')
    if choice == 0:
        return
    elif choice == 1:
        pass
    myplatform = platform()
    print "Platform: " + str(myplatform)
    if myplatform == 'osx': # OSX
        print "############   try osx force close  #################"
        try: os.system('killall -9 XBMC')
        except: pass
        try: os.system('killall -9 Kodi')
        except: pass
        dialog.ok("[COLOR=red][B]WARNING  !!![/COLOR][/B]", "If you\'re seeing this message it means the force close", "was unsuccessful. Please force close XBMC/Kodi [COLOR=lime]DO NOT[/COLOR] exit cleanly via the menu.",'')
    elif myplatform == 'linux': #Linux
        print "############   try linux force close  #################"
        try: os.system('killall XBMC')
        except: pass
        try: os.system('killall Kodi')
        except: pass
        try: os.system('killall TVMC')
        except: pass
        try: os.system('killall SPMC')
        except: pass
        try: os.system('killall -9 xbmc.bin')
        except: pass
        try: os.system('killall -9 kodi.bin')
        except: pass
        try: os.system('killall -9 TVMC.bin')
        except: pass
        try: os.system('killall -9 SPMC.bin')
        except: pass
        dialog.ok("[COLOR=red][B]WARNING  !!![/COLOR][/B]", "If you\'re seeing this message it means the force close", "was unsuccessful. Please force close XBMC/Kodi [COLOR=lime]DO NOT[/COLOR] exit cleanly via the menu.",'')
    elif myplatform == 'android': # Android  
        print "############   try android force close  #################"
        try: os.system('adb shell am force-stop org.xbmc.kodi')
        except: pass
        try: os.system('adb shell am force-stop org.kodi')
        except: pass
        try: os.system('adb shell am force-stop com.sempermax.spmc')
        except: pass
        try: os.system('adb shell am force-stop org.tvmc')
        except: pass
        try: os.system('adb shell am force-stop org.tvmc.tvmc')
        except: pass
        try: os.system('adb shell am force-stop org.xbmc.xbmc')
        except: pass
        try: os.system('adb shell am force-stop org.xbmc')
        except: pass        
        dialog.ok("[COLOR=yellow][B]TO COMPLETE UPDATE[/COLOR][/B]", "Press the HOME button on your remote and [COLOR=red][B]FORCE STOP[/COLOR][/B] KODI via the Manage Installed Applications menu in settings on your Amazon home page then re-launch KODI")
    elif myplatform == 'windows': # Windows
        print "############   try windows force close  #################"
        try:
            os.system('@ECHO off')
            os.system('tskill XBMC.exe')
        except: pass
        try:
            os.system('@ECHO off')
            os.system('tskill Kodi.exe')
        except: pass
        try:
            os.system('@ECHO off')
            os.system('TASKKILL /im Kodi.exe /f')
        except: pass
        try:
            os.system('@ECHO off')
            os.system('TASKKILL /im XBMC.exe /f')
        except: pass
        dialog.ok("[COLOR=red][B]WARNING  !!![/COLOR][/B]", "If you\'re seeing this message it means the force close", "was unsuccessful. Please force close XBMC/Kodi [COLOR=lime]DO NOT[/COLOR] exit cleanly via the menu.","Use task manager and NOT ALT F4")
    else: #ATV
        print "############   try atv force close  #################"
        try: os.system('killall AppleTV')
        except: pass
        print "############   try raspbmc force close  #################" #OSMC / Raspbmc
        try: os.system('sudo initctl stop kodi')
        except: pass
        try: os.system('sudo initctl stop xbmc')
        except: pass
        dialog.ok("[COLOR=red][B]WARNING  !!![/COLOR][/B]", "If you\'re seeing this message it means the force close", "was unsuccessful. Please force close XBMC/Kodi [COLOR=lime]DO NOT[/COLOR] exit via the menu.","iOS detected.  Press and hold both the Sleep/Wake and Home button for at least 10 seconds, until you see the Apple logo.")    

##########################
###DETERMINE PLATFORM#####
##########################
        
def platform():
    if xbmc.getCondVisibility('system.platform.android'):
        return 'android'
    elif xbmc.getCondVisibility('system.platform.linux'):
        return 'linux'
    elif xbmc.getCondVisibility('system.platform.windows'):
        return 'windows'
    elif xbmc.getCondVisibility('system.platform.osx'):
        return 'osx'
    elif xbmc.getCondVisibility('system.platform.atv2'):
        return 'atv2'
    elif xbmc.getCondVisibility('system.platform.ios'):
        return 'ios'
    
############################
###FRESH START##############
####THANKS TO TVADDONS######

def FRESHSTART(params):
    plugintools.log("freshstart.main_list "+repr(params)); yes_pressed=plugintools.message_yes_no(PATH,"Do you wish to restore your","Kodi configuration to default settings?")
    if yes_pressed:
        addonPath=xbmcaddon.Addon(id=addon_id).getAddonInfo('path'); addonPath=xbmc.translatePath(addonPath); 
        xbmcPath=os.path.join(addonPath,"..",".."); xbmcPath=os.path.abspath(xbmcPath); plugintools.log("freshstart.main_list xbmcPath="+xbmcPath); failed=False
        try:
            for root, dirs, files in os.walk(xbmcPath,topdown=True):
                dirs[:] = [d for d in dirs if d not in EXCLUDES]
                for name in files:
                    try: os.remove(os.path.join(root,name))
                    except:
                        if name not in ["Addons15.db","MyVideos75.db","Textures13.db","xbmc.log"]: failed=True
                        plugintools.log("Error removing "+root+" "+name)
                for name in dirs:
                    try: os.rmdir(os.path.join(root,name))
                    except:
                        if name not in ["Database","userdata"]: failed=True
                        plugintools.log("Error removing "+root+" "+name)
            if not failed: plugintools.log("freshstart.main_list All user files removed, you now have a clean install"); plugintools.message(PATH,"The process is complete!","Please reboot your system or restart Kodi in order for the changes to be applied.")
            else: plugintools.log("freshstart.main_list User files partially removed"); plugintools.message(PATH,"The process is complete!","Please reboot your system or restart Kodi in order for the changes to be applied.")
        except: plugintools.message(PATH,"Problem found","Your settings has not been changed"); import traceback; plugintools.log(traceback.format_exc()); plugintools.log("freshstart.main_list NOT removed")
        plugintools.add_item(action="",title="Now Exit Kodi",folder=False)
    else: plugintools.message(PATH,"Your settings","has not been changed"); plugintools.add_item(action="",title="Done",folder=False)

def get_params():
        param=[]
        paramstring=sys.argv[2]
        if len(paramstring)>=2:
                params=sys.argv[2]
                cleanedparams=params.replace('?','')
                if (params[len(params)-1]=='/'):
                        params=params[0:len(params)-2]
                pairsofparams=cleanedparams.split('&')
                param={}
                for i in range(len(pairsofparams)):
                        splitparams={}
                        splitparams=pairsofparams[i].split('=')
                        if (len(splitparams))==2:
                                param[splitparams[0]]=splitparams[1]
                                
        return param

N = base64.decodestring('')
T = base64.decodestring('L2FkZG9ucy50eHQ=')
B = base64.decodestring('')
F = base64.decodestring('')

def addDir(name,url,mode,iconimage,fanart,description):
        u=sys.argv[0]+"?url="+urllib.quote_plus(url)+"&mode="+str(mode)+"&name="+urllib.quote_plus(name)+"&iconimage="+urllib.quote_plus(iconimage)+"&fanart="+urllib.quote_plus(fanart)+"&description="+urllib.quote_plus(description)
        ok=True
        liz=xbmcgui.ListItem(name, iconImage="DefaultFolder.png", thumbnailImage=iconimage)
        liz.setInfo( type="Video", infoLabels={ "Title": name, "Plot": description } )
        liz.setProperty( "Fanart_Image", fanart )
        if mode==5 :
            ok=xbmcplugin.addDirectoryItem(handle=int(sys.argv[1]),url=u,listitem=liz,isFolder=False)
        else:
            ok=xbmcplugin.addDirectoryItem(handle=int(sys.argv[1]),url=u,listitem=liz,isFolder=True)
        return ok

        
                      
params=get_params()
url=None
name=None
mode=None

iconimage=None
fanart=None
description=None


try:
        url=urllib.unquote_plus(params["url"])
except:
        pass
try:
        name=urllib.unquote_plus(params["name"])
except:
        pass
try:
        iconimage=urllib.unquote_plus(params["iconimage"])
except:
        pass
try:        
        mode=int(params["mode"])
except:
        pass
try:        
        fanart=urllib.unquote_plus(params["fanart"])
except:
        pass
try:        
        description=urllib.unquote_plus(params["description"])
except:
        pass
        
        
print str(PATH)+': '+str(VERSION)
print " Mode        : "+str(mode)
print " URL         : "+str(url)
print " Name        : "+str(name)
print " IconImage   : "+str(iconimage)

print " * SCPATH 1  : " + SCPATH1


#print " -- COMMON PATH  : " + SCPATH1
#print " -- BACK THIS UP : " + restore_path
#print " -- INTO HERE    : " + backup_path
#print " -- BACKUP_PATH   : " + backup_path
#print " -- restore_udata : " + restore_udata
#print " -- restore_path : " + restore_path
#print " -- PWAS " + PWAS
#print " -- PNOW " + PNOW
#print " -- WZPATH = " + WZPATH
#print " -- ZIP TO GET : " + BASEURL+'/build/' + USEREXP + '.zip'



def setView(content, viewType):
    # set content type so library shows more views and info
    if content:
        xbmcplugin.setContent(int(sys.argv[1]), content)
    if ADDON.getSetting('auto-view')=='true':
        xbmc.executebuiltin("Container.SetViewMode(%s)" % ADDON.getSetting(viewType) )
if mode==None or url==None or len(url)<1:
        INDEX()
elif mode==2:
        BUILDMENU()
elif mode==3:
        BUILDCOMMON()
elif mode==4:
        MAINTENANCE()
elif mode==5:
        BUILDSC()
elif mode==6:
        deletecachefiles(url)
elif mode==7:
        FRESHSTART(params)
elif mode==8:
        DeletePackages(url)
elif mode==9:
        WIZARD(name,url,description)
elif mode==10:
        MAKECOMMON(name,url,description)
elif mode==11:
        backup_xml(url)
elif mode==12:
        restore_xml(url)
elif mode==13:
        patch_xml(url)
elif mode==14:
        get_tvguide(url)
elif mode==15:
        BACKUP_SF()
elif mode==16:
        get_superfav(url)
elif mode==17:
        BUILDSC()
elif mode==18:
        BACKUP_BD()
elif mode==19:
        BACKUP_WZ()
elif mode==20:
        BACKUP_UX()
elif mode==21:
        get_usercustom(url)
elif mode==99:
        facebook()




xbmcplugin.endOfDirectory(int(sys.argv[1]))
