from datetime import datetime
import matplotlib as mpl
mpl.use('Agg')

import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from matplotlib import gridspec
import pytz
import pandas as pd
import numpy as np
import math
from math import log
import astropy.units as u
from astropy.time import Time
from astropy.coordinates import SkyCoord, EarthLocation, AltAz, solar_system_ephemeris,ICRS

def FigureTrack(tmin,tmax,cmd_status,addtext,dfpos,dfloadpin,dftrack,dftorque):
    print("FigureTrack %s %s"%(tmin,tmax))
    fig = plt.figure(figsize = (20, 12))
    plt.gcf().subplots_adjust(left = 0.1, bottom = 0.1,right = 0.9, top = 0.9, wspace = 0, hspace = 0.1)
    
    spec = gridspec.GridSpec(ncols=1, nrows=2,height_ratios=[2, 1])
    host1 = fig.add_subplot(spec[0])
    
    formatter = mdates.DateFormatter("%H:%M:%S")
    formatter.set_tzinfo(pytz.utc); 
    plt.gca().xaxis.set_major_formatter(formatter)
    
    par1 = host1.twinx()
    par2 = host1.twinx()
    par2.spines["right"].set_position(("axes", 1.08))
    
    par2.set_frame_on(True)
    par2.patch.set_visible(False)
    for sp in par2.spines.values():
        sp.set_visible(False)

    par2.spines["right"].set_visible(True)

    lines = []
    
    if dfloadpin is not None:
        mask107 = dfloadpin['LoadPin']==107
        mask207 = dfloadpin['LoadPin']==207

        p1, = host1.plot(dfloadpin[mask107]['T'],dfloadpin[mask107]['Load'], color='blue', label="Cable 107")
        p1b, = host1.plot(dfloadpin[mask207]['T'],dfloadpin[mask207]['Load'], color='green', label="Cable 207")
        lines.append(p1)
        lines.append(p1b)
        
    p2, = par1.plot(dfpos['T'],dfpos['Az'], color='red', label="Azimuth")
    lines.append(p2)
    if dftrack is not None:
        p2b, = par1.plot(dftrack['Tth'],dftrack['Azth'], color='red',ls='dashed', label="Azimuth Th.")
        lines.append(p2b)
    p3, = par2.plot(dfpos['T'],dfpos['ZA'], color='black', label="Zenith Angle")
    lines.append(p3)
    if dftrack is not None:
        p3b, = par2.plot(dftrack['Tth'],dftrack['ZAth'], color='black',ls='dashed', label="Zenith Angle Th.")
        lines.append(p3b)
    
    host1.set_xlabel("", fontsize=15)
    host1.set_ylabel("Load [kg]", fontsize=15)
    host1.set_title("figname", fontsize=15)
    par1.set_ylabel("Azimuth [deg]", fontsize=15)
    par2.set_ylabel("Zenith Angle [deg]", fontsize=15)

    host1.yaxis.label.set_color(p1.get_color())
    par1.yaxis.label.set_color(p2.get_color())
    par2.yaxis.label.set_color(p3.get_color())

    tkw = dict(size=4, width=1.5)
    host1.tick_params(axis='y', colors=p1.get_color(), **tkw)
    par1.tick_params(axis='y', colors=p2.get_color(), **tkw)
    par2.tick_params(axis='y', colors=p3.get_color(), **tkw)
    host1.tick_params(axis='x', **tkw)
        
    host1.set_xlim(datetime.fromtimestamp(tmin, tz=pytz.utc),datetime.fromtimestamp(tmax, tz=pytz.utc))
    host1.legend(lines, [l.get_label() for l in lines],fontsize=13)
    
    if cmd_status ==0:
        host1.text(0., 1., 'ACTION FINISHED',verticalalignment='bottom', horizontalalignment='left',transform=host1.transAxes,color='green', fontsize=15)
    if cmd_status ==2:
        host1.text(0., 1., 'ACTION STOPPED BY USER',verticalalignment='bottom', horizontalalignment='left',transform=host1.transAxes,color='orange', fontsize=15)
    if cmd_status ==1:
        host1.text(0., 1., 'ACTION STOPPED BY ERROR',verticalalignment='bottom', horizontalalignment='left',transform=host1.transAxes,color='red', fontsize=15)
    if cmd_status ==3:
        host1.text(0., 1., 'CUSTOM PERIOD',verticalalignment='bottom', horizontalalignment='left',transform=host1.transAxes,color='blue', fontsize=15)
    
    host2 = fig.add_subplot(spec[1])
    plt.gca().xaxis.set_major_formatter(formatter)
    
    if dftorque is not None:        
        p13b, =host2.plot(dftorque['T'],dftorque['El1_mean'], color='chocolate',label="El S")
        p23b, =host2.plot(dftorque['T'],dftorque['El2_mean'], color='red',label="El N")
        p12b, =host2.plot(dftorque['T'],dftorque['Az1_mean'], color='lime',label="Az SE")
        p22b, =host2.plot(dftorque['T'],dftorque['Az2_mean'], color='forestgreen',label="Az NE")
        p32b, =host2.plot(dftorque['T'],dftorque['Az3_mean'], color='cyan',label="Az NW")
        p42b, =host2.plot(dftorque['T'],dftorque['Az4_mean'], color='dodgerblue',label="Az SW")
        host2.set_xlabel('Time', fontsize=15)
        host2.set_ylabel('Torque [N.m]', fontsize=15)
        host2.set_xlim(datetime.fromtimestamp(tmin, tz=pytz.utc),datetime.fromtimestamp(tmax, tz=pytz.utc))

        lines = [p13b,p23b,p12b,p22b,p32b,p42b]
        host2.legend(lines, [l.get_label() for l in lines],fontsize=13,title=addtext)
    
    #addhtmlfile(fichierhtml,figname)

    plt.savefig("/Users/antoniojose/Desktop/data/example/data/R0/LST1/lst-drive/log/DisplayTrack/DriveMonitoringApp/DataStorage/static/img/generatedFig.png", bbox_inches='tight')
    #plt.show()
    plt.close()
    
#Used in GenerateFig
def FigAccuracyTime(addtext,dfacc):
    figname2 = "/Users/antoniojose/Desktop/data/example/data/R0/LST1/lst-drive/log/DisplayTrack/DriveMonitoringApp/DataStorage/static/img/generatedFig.png".replace(".png","_Diff.png")
    #addhtmlfile(fichierhtml,figname2)
    fig,hostd = plt.subplots(figsize = (25, 12))
    plt.gcf().subplots_adjust(left = 0.1, bottom = 0.1,right = 0.9, top = 0.9, wspace = 0.1, hspace = 0.1)

    #spec = gridspec.GridSpec(ncols=1, nrows=1,width_ratios=[4,1])
    #hostd = fig.add_subplot(0)

    formatter = mdates.DateFormatter("%H:%M:%S") ; 
    formatter.set_tzinfo(pytz.utc); 
    plt.gca().xaxis.set_major_formatter(formatter)

    pfill = plt.fill_between(dfacc['T'],-60.,60., color='palegreen',label="1' req.")
    pfill2 = plt.fill_between(dfacc['T'],-14.,14., color='limegreen',label="14'' req.")

    p1d = hostd.fill_between(dfacc['T'],dfacc['Azmax'],dfacc['Azmin'],facecolor='blue',alpha=0.5,label='Azimuth')
    p1bd = hostd.fill_between(dfacc['T'],dfacc['Zdmax'],dfacc['Zdmin'],facecolor='red',alpha=0.5,label='Zenith angle')

    hostd.set_ylabel("Pointing Error [arcsec]", fontsize=15)

    lines = [p1d,p1bd]

    hostd.axhline(y=0,xmin=0.05,xmax=0.95,linestyle='dotted')
    lines = [p1d,p1bd,pfill,pfill2]
    hostd.legend(lines, [l.get_label() for l in lines],fontsize=13,title=addtext)
    hostd.set_title(figname2, fontsize=15)    
    plt.legend()
    plt.savefig(figname2, bbox_inches='tight')
    plt.close()

def FigureRADec(dfpos,dfbm,ra,dec,dfacc,dftrack):  
    figname3 = f"/Users/antoniojose/Desktop/data/example/data/R0/LST1/lst-drive/log/DisplayTrack/DriveMonitoringApp/DataStorage/static/img/generatedFig.png".replace(".png","_SkyCoord.png")

    dfpos['AzSky'] = dfpos['Az']+dfbm['AzC']
    dfpos['ZASky'] = dfpos['ZA']+dfbm['ZAC']
    dfpos['AltSky'] = 90.- dfpos['ZASky']

    #print(dftrack)
    #print(dfbm)
    
    tracksky = None
    if dftrack is not None:
        tracksky = pd.merge(dftrack, dfbm, on="T",how='inner')
        tracksky['AzSky'] = tracksky['Azth']+tracksky['AzC']
        tracksky['ZASky'] = tracksky['ZAth']+tracksky['ZAC']
        tracksky['AltSky'] = 90.- tracksky['ZASky']
    #print(tracksky)

    lst=EarthLocation.from_geodetic(-17.8915 * u.deg, 28.7615 * u.deg, 2202* u.m)
    #print(dfpos)
    direc_lst = AltAz(location=lst, obstime=dfpos['T'],az=dfpos['AzSky'] * u.deg, alt=dfpos['AltSky'] * u.deg,obswl=0.35*u.micron,relative_humidity=0.5,temperature=10*u.deg_C,pressure=790*u.hPa)
    sky_lst = SkyCoord(direc_lst.transform_to(ICRS()))
    target = SkyCoord(ra=ra*u.deg,dec=dec*u.deg, frame='icrs')
    distsky = target.separation(sky_lst)

    if tracksky is not None:
        direc_lst_track = AltAz(location=lst, obstime=tracksky['Tth'],az=tracksky['AzSky'] * u.deg, alt=tracksky['AltSky'] * u.deg,obswl=0.35*u.micron,relative_humidity=0.5,temperature=10*u.deg_C,pressure=790*u.hPa)
        sky_lst_track = SkyCoord(direc_lst_track.transform_to(ICRS()))
        target_track = SkyCoord(ra=ra*u.deg,dec=dec*u.deg, frame='icrs')
        distsky_track = target.separation(sky_lst_track)

    #addhtmlfile(fichierhtml,figname3)
    fig = plt.figure(figsize = (20, 12))
    plt.gcf().subplots_adjust(left = 0.1, bottom = 0.15,right = 0.9, top = 0.85, wspace = 0.1, hspace = 0.1)

    spec = gridspec.GridSpec(ncols=2, nrows=2)

    hostd = fig.add_subplot(spec[0])
    if tracksky is not None:
        plt.hist(sky_lst_track.ra.deg,bins=30,histtype='step',density=False,label='Drive target', alpha=0.7,linewidth=3)
    plt.hist(sky_lst.ra.deg,bins=30,histtype='step',density=False,label='Telescope pointing', alpha=0.7,linewidth=3)
    plt.axvline(x=ra, color='k', linestyle='--',label="Target")
    hostd.set_xlabel("RA[deg]", fontsize=15)
    #hostd.set_title(figname3, fontsize=15)    
    hostd.legend()

    hostd = fig.add_subplot(spec[1])
    if tracksky is not None:
        plt.hist(sky_lst_track.dec.deg,bins=30,histtype='step',density=False,label='Drive target', alpha=0.7,linewidth=3)
    plt.hist(sky_lst.dec.deg,bins=30,histtype='step',density=False,label='Telescope pointing', alpha=0.7,linewidth=3)
    plt.axvline(x=dec, color='k', linestyle='--',label="Target")
    hostd.set_xlabel("Declination[deg]", fontsize=15)
    #hostd.set_title(figname3, fontsize=15)    
    hostd.legend()

    hostd = fig.add_subplot(spec[2])
    if tracksky is not None:
        log10distsky_track = np.log10(distsky_track.deg*3600.)
        plt.hist(log10distsky_track,histtype='step',density=False,label='Drive target', alpha=0.7,linewidth=3)
    log10distsky = np.log10(distsky.deg*3600.)
    plt.hist(log10distsky,histtype='step',density=False,label='Telescope pointing', alpha=0.7,linewidth=3)
    for i in range(1,10):
        plt.axvline(x=math.log10(i), color='red', linestyle='--')
        plt.axvline(x=math.log10(i*10), color='blue', linestyle='--')
        plt.axvline(x=math.log10(i*100), color='k', linestyle='--')

    hostd.set_xlabel("Log10 Angular Distance to Target[arcsec]", fontsize=15)
    #hostd.set_title(figname3, fontsize=15)    
    hostd.legend()

    hostd = fig.add_subplot(spec[3])
    azmaxacc = np.log10(np.maximum(np.abs(dfacc.Azmax),np.abs(dfacc.Azmin)))
    zdmaxacc = np.log10(np.maximum(np.abs(dfacc.Zdmax),np.abs(dfacc.Zdmin)))

    plt.hist(np.log10(np.abs(dfacc.Azmean)),bins=30,histtype='step',density=True,label='Azimuth 2s average', alpha=0.7,linewidth=3)
    plt.hist(azmaxacc,bins=30,histtype='step', density=True,label='Azimuth 2s max', alpha=0.7,linewidth=3)
    plt.hist(np.log10(np.abs(dfacc.Zdmean)),bins=30,histtype='step',density=True,label='Elevation 2s average', alpha=0.7,linewidth=3)
    plt.hist(zdmaxacc,bins=30,histtype='step', density=True,label='Elevation 2s max', alpha=0.7,linewidth=3)
    plt.axvline(x=math.log10(30.), color='k', linestyle='--',label="30\"")
    plt.axvline(x=math.log10(4.e-02), color='red', linestyle='--',label="Encoder resolution")
    hostd.set_xlabel('log$_{10}$(Accuracy [arcsec])',fontsize=15)
    hostd.legend()

    plt.savefig(figname3, bbox_inches='tight')
    #plt.show()
    plt.close()
