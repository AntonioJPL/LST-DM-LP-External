from datetime import datetime
import pandas as pd
import numpy as np
import astropy.units as u
from astropy.time import Time
from astropy.coordinates import SkyCoord, EarthLocation, AltAz, solar_system_ephemeris,ICRS
import plotly.graph_objects as go
import plotly.io as pio
from plotly.subplots import make_subplots
from django.contrib.staticfiles import finders
import os

def fig_to_responsive_json(fig):
    """
    Convert a Plotly figure into a responsive JSON spec (no fixed width/height).
    This keeps the plot fluid in the frontend.
    """
    fig.update_layout(autosize=True)
    spec = fig.to_plotly_json()
    spec.get("layout", {}).pop("width", None)
    spec.get("layout", {}).pop("height", None)
    return spec

#This function generates the first and seccond plots. The first plot is the LOAD (fig variable) one and the seccond one is the Torque plot (fig2 variable). Here is all personalization of the plots and the treatment of the data. Once each plot is generated it saves them into the given path as an HTML file
def FigureTrack(addText, dfpos,dfloadpin,dftrack,dftorque, path):
    fig = go.Figure()
    generatedCableLegend = False
    generatedPositionLegend = False
    generatedPositionTTHLegend = False
    for i in range(0, len(dfpos)):
        if dfloadpin[i] is not None and dfloadpin[i].empty != True:
            mask107 = dfloadpin[i]['LoadPin']==107
            mask207 = dfloadpin[i]['LoadPin']==207
            loadPinSorted = dfloadpin[i].sort_values(by=["T"])
            if generatedCableLegend == False:
                fig.add_trace(go.Scatter(x=loadPinSorted[mask107]["T"], y=loadPinSorted[mask107]["Load"], line= dict(color="blue"), name="Cable 107", legendgroup="Cable 107", mode="lines"))
                fig.add_trace(go.Scatter(x=loadPinSorted[mask207]["T"], y=loadPinSorted[mask207]["Load"], line= dict(color="green"), name="Cable 207", legendgroup="Cable 207", mode="lines"))
                generatedCableLegend = True
            else:
                fig.add_trace(go.Scatter(x=loadPinSorted[mask107]["T"], y=loadPinSorted[mask107]["Load"], line= dict(color="blue"), name="Cable 107", legendgroup="Cable 107", showlegend=False, mode="lines"))
                fig.add_trace(go.Scatter(x=loadPinSorted[mask207]["T"], y=loadPinSorted[mask207]["Load"], line= dict(color="green"), name="Cable 207", legendgroup="Cable 207", showlegend=False, mode="lines"))
        if dfpos[i] is not None and dfpos[i].empty != True:
            dfposSorted = dfpos[i].sort_values(by=["T"])
            if generatedPositionLegend == False:
                fig.add_trace(go.Scatter(x=dfposSorted["T"], y=dfposSorted["Az"], line= dict(color="red"), yaxis="y2", name="Azimuth", legendgroup="Azimuth", mode="lines"))
                fig.add_trace(go.Scatter(x=dfposSorted["T"], y=dfposSorted["ZA"], line= dict(color="black"), yaxis="y3", name="Zenith Angle", legendgroup="Zenith Angle", mode="lines"))
                generatedPositionLegend = True
            else:
                fig.add_trace(go.Scatter(x=dfposSorted["T"], y=dfposSorted["Az"], line= dict(color="red"), yaxis="y2", name="Azimuth", legendgroup="Azimuth", showlegend=False, mode="lines"))
                fig.add_trace(go.Scatter(x=dfposSorted["T"], y=dfposSorted["ZA"], line= dict(color="black"), yaxis="y3", name="Zenith Angle", legendgroup="Zenith Angle", showlegend=False, mode="lines"))
        dftrackSorted = None
        if dftrack[i] is not None and dftrack[i].empty != True:
            dftrackSorted = dftrack[i].sort_values(by=["T"])
            if generatedPositionTTHLegend == False:
                fig.add_trace(go.Scatter(x=dftrackSorted["Tth"], y=dftrackSorted["Azth"], line= dict(color="red", dash="dash"), yaxis="y2", name="Azimuth Th.", legendgroup="Azimuth Th.", mode="lines"))
                fig.add_trace(go.Scatter(x=dftrackSorted["Tth"], y=dftrackSorted["ZAth"], line= dict(color="black", dash="dash"), yaxis="y3", name="Zenith Angle Th.", legendgroup="Zenith Angle Th.", mode="lines"))
                generatedPositionTTHLegend = True
            else:
                fig.add_trace(go.Scatter(x=dftrackSorted["Tth"], y=dftrackSorted["Azth"], line= dict(color="red", dash="dash"), yaxis="y2", name="Azimuth Th.", legendgroup="Azimuth Th.", showlegend=False, mode="lines"))
                fig.add_trace(go.Scatter(x=dftrackSorted["Tth"], y=dftrackSorted["ZAth"], line= dict(color="black", dash="dash"), yaxis="y3", name="Zenith Angle Th.", legendgroup="Zenith Angle Th.", showlegend=False, mode="lines"))
    pngName = path.split("/")
    fig.update_layout(
        xaxis_tickformat = "%H:%M:%S",
        yaxis= dict(
            #dtick=50,
            title="Load [KG]",
            titlefont=dict(
                color='blue'
            ),
            tickfont=dict(
                color='blue', 
                size=10
            ),
            autorange=True
        ),
        yaxis2= dict(
            #dtick=25,
            title="Azimuth [DEG]",
            titlefont=dict(
                color='red'
            ),
            tickfont=dict(
                color='red',
                size=10
            ),
            anchor="x",
            overlaying="y",
            side="right",
            autorange=True
        ),
        yaxis3= dict(
            #dtick=5,
            title="Zenith Angle [DEG]",
            titlefont=dict(
                color='black'
            ),
            tickfont=dict(
                color='black'
            ),
            anchor="free",
            overlaying="y",
            side="right",
            autoshift=True,
            shift=30,
            autorange=True
        ),
        legend= dict( 
            orientation="h",
            yanchor="middle",
            y=1.2,
            xanchor="center",
            x=0.5,
        ),
)
    fig.update_yaxes(tickangle=7.5)
    
    os.makedirs(os.path.dirname(path), exist_ok=True)

    json_path = path.replace(".json", ".json")
    pio.write_json(fig, json_path, pretty=False)
    
    os.chmod(json_path, 0o755)

    #fig.write_html(path, full_html=False, include_plotlyjs='cdn', auto_open=False, config=dict(toImageButtonOptions=dict(filename=pngName[-1].replace(".html", ""))))
    fig2 = go.Figure()
    generatedTorqueLegend = False
    if dftorque is not None:
        for i in range(0, len(dftorque)):
            if dftorque[i].empty != True:
                torqueSorted = dftorque[i].sort_values(by=["T"])
                if generatedTorqueLegend == False:
                    fig2.add_trace(go.Scatter(x=torqueSorted["T"], y=list({0: torqueSorted["T"][0]}), line= dict(color="rgba(0,0,0,0)"), name=addText)) #This is for the legend title
                    fig2.add_trace(go.Scatter(x=torqueSorted["T"], y=torqueSorted['El1_mean'], line= dict(color="chocolate"), name="El S", legendgroup="El S", mode="lines"))
                    fig2.add_trace(go.Scatter(x=torqueSorted["T"], y=torqueSorted['El2_mean'], line= dict(color="red"), name="El N", legendgroup="El N", mode="lines"))
                    fig2.add_trace(go.Scatter(x=torqueSorted["T"], y=torqueSorted['Az1_mean'], line= dict(color="lime"), name="Az SE", legendgroup="Az SE", mode="lines"))
                    fig2.add_trace(go.Scatter(x=torqueSorted["T"], y=torqueSorted['Az2_mean'], line= dict(color="forestgreen"), name="Az NE", legendgroup="Az NE", mode="lines"))
                    fig2.add_trace(go.Scatter(x=torqueSorted["T"], y=torqueSorted['Az3_mean'], line= dict(color="cyan"), name="Az NW", legendgroup="Az NW", mode="lines"))
                    fig2.add_trace(go.Scatter(x=torqueSorted["T"], y=torqueSorted['Az4_mean'], line= dict(color="dodgerblue"), name="Az SW", legendgroup="Az SW", mode="lines"))
                    generatedTorqueLegend = True
                if i == len(dftorque)-1:
                    fig2.add_trace(go.Scatter(x=torqueSorted["T"], y=torqueSorted['El1_mean'], line= dict(color="chocolate"), name="El S", legendgroup="El S", showlegend=False, mode="lines"))
                    fig2.add_trace(go.Scatter(x=torqueSorted["T"], y=torqueSorted['El2_mean'], line= dict(color="red"), name="El N", legendgroup="El N", showlegend=False, mode="lines"))
                    fig2.add_trace(go.Scatter(x=torqueSorted["T"], y=torqueSorted['Az1_mean'], line= dict(color="lime"), name="Az SE", legendgroup="Az SE", showlegend=False, mode="lines"))
                    fig2.add_trace(go.Scatter(x=torqueSorted["T"], y=torqueSorted['Az2_mean'], line= dict(color="forestgreen"), name="Az NE", legendgroup="Az NE", showlegend=False, mode="lines"))
                    fig2.add_trace(go.Scatter(x=torqueSorted["T"], y=torqueSorted['Az3_mean'], line= dict(color="cyan"), name="Az NW", legendgroup="Az NW", showlegend=False, mode="lines"))
                    fig2.add_trace(go.Scatter(x=torqueSorted["T"], y=torqueSorted['Az4_mean'], line= dict(color="dodgerblue"), name="Az SW", legendgroup="Az SW", showlegend=False, mode="lines"))
                else:
                    fig2.add_trace(go.Scatter(x=torqueSorted["T"], y=torqueSorted['El1_mean'], line= dict(color="chocolate"), name="El S", legendgroup="El S", showlegend=False, mode="lines"))
                    fig2.add_trace(go.Scatter(x=torqueSorted["T"], y=torqueSorted['El2_mean'], line= dict(color="red"), name="El N", legendgroup="El N", showlegend=False, mode="lines"))
                    fig2.add_trace(go.Scatter(x=torqueSorted["T"], y=torqueSorted['Az1_mean'], line= dict(color="lime"), name="Az SE", legendgroup="Az SE", showlegend=False, mode="lines"))
                    fig2.add_trace(go.Scatter(x=torqueSorted["T"], y=torqueSorted['Az2_mean'], line= dict(color="forestgreen"), name="Az NE", legendgroup="Az NE", showlegend=False, mode="lines"))
                    fig2.add_trace(go.Scatter(x=torqueSorted["T"], y=torqueSorted['Az3_mean'], line= dict(color="cyan"), name="Az NW", legendgroup="Az NW", showlegend=False, mode="lines"))
                    fig2.add_trace(go.Scatter(x=torqueSorted["T"], y=torqueSorted['Az4_mean'], line= dict(color="dodgerblue"), name="Az SW", legendgroup="Az SW", showlegend=False, mode="lines"))
            else:
                print("There is no data")
    fig2.update_layout(
        xaxis_tickformat = "%H:%M:%S",
        xaxis= dict(
            title="Time",
        ),
        yaxis= dict(
            #dtick=10,
            title="Torque [N.m]",
            titlefont=dict(
                color='black'
            ),
            tickfont=dict(
                color='black', 
                size=10
            ),
        ),
        legend= dict(
            orientation="h",
            yanchor="middle",
            y=1.2,
            xanchor="center",
            x=0.5,
        ),
    )
    fig2.update_yaxes(tickangle=7.5)
    os.makedirs(os.path.dirname(path), exist_ok=True)

    json_path = path.replace(".json", "-torque.json")
    pio.write_json(fig2, json_path, pretty=False)
    
    os.chmod(json_path, 0o755)
    #fig2.write_html(path.replace(".html", "-torque.html"), full_html=False, include_plotlyjs='cdn', auto_open=False, config=dict(toImageButtonOptions=dict(filename=pngName[-1].replace(".html", "")+"-torque")))  
#This function generates the third plot, it is just present some times. Here is all personalization of the plot and the treatment of the data. Once the plot is generated it is saved into the given path as an HTML file
def FigAccuracyTime(dfacc, path):
    #addhtmlfile(fichierhtml,figname2)
    fig = go.Figure()
    if dfacc is not None:
        minuteDict = {}
        minuteDict["times"] = {}
        minuteDict["values"] = {}
        minuteDict["type"] = {}
        minuteDict["values"][0] = -60
        minuteDict["type"][0] = 0
        minuteDict["times"][0] = dfacc[0]["T"][0]
        minuteDict["values"][1] = -60
        minuteDict["type"][1] = 0
        minuteDict["times"][1] = dfacc[-1]["T"][len(dfacc[-1]["T"])-1]
        minuteDict["values"][2] = 60
        minuteDict["type"][2] = 1
        minuteDict["times"][2] = dfacc[0]["T"][0]
        minuteDict["values"][3] = 60
        minuteDict["type"][3] = 1
        minuteDict["times"][3] = dfacc[-1]["T"][len(dfacc[-1]["T"])-1]
        dfMin = pd.DataFrame.from_dict(minuteDict)
        mask1 = dfMin["type"]==1
        mask0 = dfMin["type"]==0
        seccondsDict = {}
        seccondsDict["times"] = {}
        seccondsDict["values"] = {}
        seccondsDict["type"] = {}
        seccondsDict["values"][0] = -14
        seccondsDict["type"][0] = 0
        seccondsDict["times"][0] = dfacc[0]["T"][0]
        seccondsDict["values"][1] = -14
        seccondsDict["type"][1] = 0
        seccondsDict["times"][1] = dfacc[-1]["T"][len(dfacc[-1]["T"])-1]
        seccondsDict["values"][2] = 14
        seccondsDict["type"][2] = 1
        seccondsDict["times"][2] = dfacc[0]["T"][0]
        seccondsDict["values"][3] = 14
        seccondsDict["type"][3] = 1
        seccondsDict["times"][3] = dfacc[-1]["T"][len(dfacc[-1]["T"])-1]
        dfSec = pd.DataFrame.from_dict(seccondsDict)
        mask1Sec = dfSec["type"]==1
        mask0Sec = dfSec["type"]==0
        fig.add_trace(go.Scatter(x=dfMin[mask0]["times"], y=dfMin[mask0]["values"], line= dict(color="palegreen"), name="1' req", legendgroup="1' req", fill="tonexty", fillcolor="palegreen", mode="lines"))
        fig.add_trace(go.Scatter(x=dfMin[mask1]["times"], y=dfMin[mask1]["values"], line= dict(color="palegreen"), name="1' req", legendgroup="1' req", fill="tonexty", fillcolor="palegreen", showlegend=False, mode="lines"))
        fig.add_trace(go.Scatter(x=dfSec[mask0Sec]["times"], y=dfSec[mask0Sec]["values"], line= dict(color="limegreen"), name="14'' req", legendgroup="14' req", fill="tozeroy", fillcolor="limegreen", mode="lines"))
        fig.add_trace(go.Scatter(x=dfSec[mask1Sec]["times"], y=dfSec[mask1Sec]["values"], line= dict(color="limegreen"), name="14'' req", legendgroup="14' req", fill="tozeroy", fillcolor="limegreen", showlegend=False, mode="lines"))
        fig.add_trace(go.Scatter(x=dfSec[mask1Sec]["times"], y=[0 for x in dfSec[mask1Sec]["times"]], line= dict(color="black", dash="dash", width=0.5), name="0 req", legendgroup="0 req", mode="lines",))
        for i in range(0, len(dfacc)):
            if i == 0:
                fig.add_trace(go.Scatter(x=dfacc[i]["T"], y=dfacc[i]["Azmin"], line= dict(color=("rgba(0,0,0,0)")), name="Azimuth", legendgroup="Azimuth", showlegend=False, mode="lines"))
                fig.add_trace(go.Scatter(x=dfacc[i]["T"], y=dfacc[i]["Azmax"], line= dict(color=("rgba(0,0,0,0)")), name="Azimuth", legendgroup="Azimuth", fill="tonexty", fillcolor="rgba(0,0,255,0.5)", mode="lines"))
                fig.add_trace(go.Scatter(x=dfacc[i]["T"], y=dfacc[i]["Zdmin"], line= dict(color=("rgba(0,0,0,0)")), name="Zenith angle", legendgroup="Zenith angle", showlegend=False, mode="lines"))
                fig.add_trace(go.Scatter(x=dfacc[i]["T"], y=dfacc[i]["Zdmax"], line= dict(color=("rgba(0,0,0,0)")), name="Zenith angle", legendgroup="Zenith angle", fill="tonexty", fillcolor="rgba(255,0,0,0.5)", mode="lines"))
            else:
                fig.add_trace(go.Scatter(x=dfacc[i]["T"], y=dfacc[i]["Azmin"], line= dict(color=("rgba(0,0,0,0)")), name="Azimuth", legendgroup="Azimuth", showlegend=False, mode="lines"))
                fig.add_trace(go.Scatter(x=dfacc[i]["T"], y=dfacc[i]["Azmax"], line= dict(color=("rgba(0,0,0,0)")), name="Azimuth", legendgroup="Azimuth", fill="tonexty", fillcolor="rgba(0,0,255,0.5)", showlegend=False, mode="lines"))
                fig.add_trace(go.Scatter(x=dfacc[i]["T"], y=dfacc[i]["Zdmin"], line= dict(color=("rgba(0,0,0,0)")), name="Zenith angle", legendgroup="Zenith angle", showlegend=False, mode="lines"))
                fig.add_trace(go.Scatter(x=dfacc[i]["T"], y=dfacc[i]["Zdmax"], line= dict(color=("rgba(0,0,0,0)")), name="Zenith angle", legendgroup="Zenith angle", fill="tonexty", fillcolor="rgba(255,0,0,0.5)", showlegend=False, mode="lines"))
        pngName = path.split("/")
        fig.update_layout(
            xaxis_tickformat = "%H:%M:%S",
            yaxis= dict(
                range=[-100, 100],
                #dtick = 100,
                title="Pointing Error [arcsec]",
                titlefont=dict(
                    color='black'
                ),
                tickfont=dict(
                    color='black',
                    size=10
                ),
            ),
            legend= dict( 
                orientation="h",
                yanchor="middle",
                y=1.2,
                xanchor="center",
                x=0.5,
            ),
        )
        fig.update_yaxes(tickangle=7.5)
        os.makedirs(os.path.dirname(path), exist_ok=True)

        json_path = path.replace(".json", "_Diff.json")
        pio.write_json(fig, json_path, pretty=False)
        
        os.chmod(json_path, 0o755)
        #fig.write_html(path.replace(".html", "_Diff.html"), full_html=False, include_plotlyjs='cdn', auto_open=False, config=dict(toImageButtonOptions=dict(filename=pngName[-1].replace(".html", "")+"_Diff")))
#This generates the final section of the plots, right now is NOT BEING USED
def FigureRADec(dfpos,dfbm,ra,dec,dfacc,dftrack, path):  
    fig1 = make_subplots(specs=[[{"secondary_y": True}]])
    fig2 = make_subplots(specs=[[{"secondary_y": True}]])
    fig3 = make_subplots(specs=[[{"secondary_y": True}]])
    fig4 = make_subplots(specs=[[{"secondary_y": True}]])
    for i in range(0, 1):
        i = 0
        dfpos[i]['AzSky'] = dfpos[i]['Az']+dfbm[i]['AzC']
        dfpos[i]['ZASky'] = dfpos[i]['ZA']+dfbm[i]['ZAC']
        dfpos[i]['AltSky'] = 90.- dfpos[i]['ZASky']
        tracksky = None
        if dftrack is not None:
            tracksky = pd.merge(dftrack[i], dfbm[i], on="T",how='inner')
            tracksky['AzSky'] = tracksky['Azth']+tracksky['AzC']
            tracksky['ZASky'] = tracksky['ZAth']+tracksky['ZAC']
            tracksky['AltSky'] = 90.- tracksky['ZASky']
        lst=EarthLocation.from_geodetic(-17.8915 * u.deg, 28.7615 * u.deg, 2202* u.m)
        direc_lst = AltAz(location=lst, obstime=dfpos[i]['T'],az=dfpos[i]['AzSky'] * u.deg, alt=dfpos[i]['AltSky'] * u.deg,obswl=0.35*u.micron,relative_humidity=0.5,temperature=10*u.deg_C,pressure=790*u.hPa)
        sky_lst = SkyCoord(direc_lst.transform_to(ICRS()))
        target = SkyCoord(ra=ra[i]*u.deg,dec=dec[i]*u.deg, frame='icrs')
        distsky = target.separation(sky_lst)
        if tracksky is not None:
            direc_lst_track = AltAz(location=lst, obstime=tracksky['Tth'],az=tracksky['AzSky'] * u.deg, alt=tracksky['AltSky'] * u.deg,obswl=0.35*u.micron,relative_humidity=0.5,temperature=10*u.deg_C,pressure=790*u.hPa)
            sky_lst_track = SkyCoord(direc_lst_track.transform_to(ICRS()))
            target_track = SkyCoord(ra=ra[i]*u.deg,dec=dec[i]*u.deg, frame='icrs')
            distsky_track = target.separation(sky_lst_track)
        #Here it starts to generate the Plot
        if tracksky is not None:
            fig1.add_trace(go.Histogram(x=sky_lst_track.ra.deg, name="Drive Target", legendgroup="Drive Target", marker= dict(color="blue"), xbins=dict(size= 0.0000005)), secondary_y=True)   
        fig1.add_trace(go.Histogram(x=sky_lst.ra.deg, opacity=0.7, name="Telescope pointing", legendgroup="Telescope pointing", marker= dict(color="orange"), alignmentgroup=1))
        fig1.add_vline(x=ra[i], line=dict(color="black", dash="dash"), name="Target", legendgroup="Target")
        fig1.update_layout(
            xaxis = dict(dtick=0.025),
            xaxis_title="RA[deg]"
        )
        date = str(dfpos[0]["T"][len(dfpos[0]["T"])-1]).split(" ")
        time = date[0].split("+")
        fig1.update_yaxes(tickangle=7.5)
        fig1.show()
        #fig1.write_html(path.replace(".html", "_"+time[0]+"_"+"_SkyCoord1.html"))
        """ if tracksky is not None:
            fig2.add_trace(go.Histogram(x=sky_lst_track.dec.deg, name="Drive Target", legendgroup="Drive Target", marker= dict(color="blue"), xbins=dict(size= 0.0000005)), secondary_y=True)   
        fig2.add_trace(go.Histogram(x=sky_lst.dec.deg, opacity=0.7, name="Telescope pointing", legendgroup="Telescope pointing", marker= dict(color="orange"), alignmentgroup=1))
        fig2.add_vline(x=ra[i], line=dict(color="black", dash="dash"), name="Target", legendgroup="Target")
        fig2.update_layout(
            xaxis = dict(dtick=0.025),
            xaxis_title="Declination[deg]"
        )
        date = str(dfpos[0]["T"][len(dfpos[0]["T"])-1]).split(" ")
        time = date[0].split("+")
        fig2.show() """
        #fig2.write_html(path.replace(".html", "_"+time[0]+"_"+"_SkyCoord2.html"))
#This function generates the LoadPin plots, it takes all the load pin data from a whole day and represents all the tension of each cable on it. This is divided on two plots the 10X cables (fig variable) and the 20X cables (fig2 variable). Once the plots are generated and personlized they are saved as HTLM files into the given path
def FigureLoadPin(dfloadpin, path, date):
    pathParts = path.split("/")
    newPath = None
    if len(pathParts) <= 2:
        newPath = "static/"+path+"/LoadPin"
        file = finders.find(newPath)
        if file is None:
            file = os.path.abspath("DataStorage/"+newPath)
            if not os.path.exists(file):
                os.makedirs(file)
    else:
        newPath = pathParts[-4]+"/"+pathParts[-3]+"/LoadPin"
        file = finders.find(newPath)
        if file is None:
            file = path.replace(pathParts[-4]+"/"+pathParts[-3]+"/"+pathParts[-2]+"/"+pathParts[-1], newPath)
            os.mkdir(file)
    path = file+"/"+"LoadPin_"+date+".json"
    print("This is the actual path: "+path)
    fig = go.Figure()
    fig2 = go.Figure()
    dfloadpin = pd.DataFrame.from_dict(dfloadpin)
    if dfloadpin is not None and dfloadpin.empty != True:
        mask101 = dfloadpin['LoadPin']==101
        mask102 = dfloadpin['LoadPin']==102
        mask103 = dfloadpin['LoadPin']==103
        mask104 = dfloadpin['LoadPin']==104
        mask105 = dfloadpin['LoadPin']==105
        mask106 = dfloadpin['LoadPin']==106
        mask107 = dfloadpin['LoadPin']==107
        mask108 = dfloadpin['LoadPin']==108
        mask109 = dfloadpin['LoadPin']==109
        mask110 = dfloadpin['LoadPin']==110
        mask111 = dfloadpin['LoadPin']==111
        mask112 = dfloadpin['LoadPin']==112
        mask113 = dfloadpin['LoadPin']==113
        mask201 = dfloadpin['LoadPin']==201
        mask202 = dfloadpin['LoadPin']==202
        mask203 = dfloadpin['LoadPin']==203
        mask204 = dfloadpin['LoadPin']==204
        mask205 = dfloadpin['LoadPin']==205
        mask206 = dfloadpin['LoadPin']==206
        mask207 = dfloadpin['LoadPin']==207
        mask208 = dfloadpin['LoadPin']==208
        mask209 = dfloadpin['LoadPin']==209
        mask210 = dfloadpin['LoadPin']==210
        mask211 = dfloadpin['LoadPin']==211
        mask212 = dfloadpin['LoadPin']==212
        mask213 = dfloadpin['LoadPin']==213
        loadPinSorted = dfloadpin.sort_values(by=["T"])
        fig.add_trace(go.Scatter(x=loadPinSorted[mask101]["T"], y=loadPinSorted[mask101]["Load"], line= dict(color="orange"), name="Cable 101", legendgroup="Cable 101", mode="lines"))
        fig.add_trace(go.Scatter(x=loadPinSorted[mask102]["T"], y=loadPinSorted[mask102]["Load"], line= dict(color="green"), name="Cable 102", legendgroup="Cable 102", mode="lines"))
        fig.add_trace(go.Scatter(x=loadPinSorted[mask103]["T"], y=loadPinSorted[mask103]["Load"], line= dict(color="blueviolet"), name="Cable 103", legendgroup="Cable 103", mode="lines"))
        fig.add_trace(go.Scatter(x=loadPinSorted[mask104]["T"], y=loadPinSorted[mask104]["Load"], line= dict(color="teal"), name="Cable 104", legendgroup="Cable 104", mode="lines"))
        fig.add_trace(go.Scatter(x=loadPinSorted[mask105]["T"], y=loadPinSorted[mask105]["Load"], line= dict(color="violet"), name="Cable 105", legendgroup="Cable 105", mode="lines"))
        fig.add_trace(go.Scatter(x=loadPinSorted[mask106]["T"], y=loadPinSorted[mask106]["Load"], line= dict(color="tomato"), name="Cable 106", legendgroup="Cable 106", mode="lines"))
        fig.add_trace(go.Scatter(x=loadPinSorted[mask107]["T"], y=loadPinSorted[mask107]["Load"], line= dict(color="blue"), name="Cable 107", legendgroup="Cable 107", mode="lines"))
        fig.add_trace(go.Scatter(x=loadPinSorted[mask108]["T"], y=loadPinSorted[mask108]["Load"], line= dict(color="gray"), name="Cable 108", legendgroup="Cable 108", mode="lines"))
        fig.add_trace(go.Scatter(x=loadPinSorted[mask109]["T"], y=loadPinSorted[mask109]["Load"], line= dict(color="brown"), name="Cable 109", legendgroup="Cable 109", mode="lines"))
        fig.add_trace(go.Scatter(x=loadPinSorted[mask110]["T"], y=loadPinSorted[mask110]["Load"], line= dict(color="cyan"), name="Cable 110", legendgroup="Cable 110", mode="lines"))
        fig.add_trace(go.Scatter(x=loadPinSorted[mask111]["T"], y=loadPinSorted[mask111]["Load"], line= dict(color="yellow"), name="Cable 111", legendgroup="Cable 111", mode="lines"))
        fig.add_trace(go.Scatter(x=loadPinSorted[mask112]["T"], y=loadPinSorted[mask112]["Load"], line= dict(color="purple"), name="Cable 112", legendgroup="Cable 112", mode="lines"))
        fig.add_trace(go.Scatter(x=loadPinSorted[mask113]["T"], y=loadPinSorted[mask113]["Load"], line= dict(color="red"), name="Cable 113", legendgroup="Cable 113", mode="lines"))
        fig2.add_trace(go.Scatter(x=loadPinSorted[mask201]["T"], y=loadPinSorted[mask201]["Load"], line= dict(color="orange"), name="Cable 201", legendgroup="Cable 201", mode="lines"))
        fig2.add_trace(go.Scatter(x=loadPinSorted[mask202]["T"], y=loadPinSorted[mask202]["Load"], line= dict(color="green"), name="Cable 202", legendgroup="Cable 202", mode="lines"))
        fig2.add_trace(go.Scatter(x=loadPinSorted[mask203]["T"], y=loadPinSorted[mask203]["Load"], line= dict(color="blueviolet"), name="Cable 203", legendgroup="Cable 203", mode="lines"))
        fig2.add_trace(go.Scatter(x=loadPinSorted[mask204]["T"], y=loadPinSorted[mask204]["Load"], line= dict(color="teal"), name="Cable 204", legendgroup="Cable 204", mode="lines"))
        fig2.add_trace(go.Scatter(x=loadPinSorted[mask205]["T"], y=loadPinSorted[mask205]["Load"], line= dict(color="violet"), name="Cable 205", legendgroup="Cable 205", mode="lines"))
        fig2.add_trace(go.Scatter(x=loadPinSorted[mask206]["T"], y=loadPinSorted[mask206]["Load"], line= dict(color="tomato"), name="Cable 206", legendgroup="Cable 206", mode="lines"))
        fig2.add_trace(go.Scatter(x=loadPinSorted[mask207]["T"], y=loadPinSorted[mask207]["Load"], line= dict(color="blue"), name="Cable 207", legendgroup="Cable 207", mode="lines"))
        fig2.add_trace(go.Scatter(x=loadPinSorted[mask208]["T"], y=loadPinSorted[mask208]["Load"], line= dict(color="gray"), name="Cable 208", legendgroup="Cable 208", mode="lines"))
        fig2.add_trace(go.Scatter(x=loadPinSorted[mask209]["T"], y=loadPinSorted[mask209]["Load"], line= dict(color="brown"), name="Cable 209", legendgroup="Cable 209", mode="lines"))
        fig2.add_trace(go.Scatter(x=loadPinSorted[mask210]["T"], y=loadPinSorted[mask210]["Load"], line= dict(color="cyan"), name="Cable 210", legendgroup="Cable 210", mode="lines"))
        fig2.add_trace(go.Scatter(x=loadPinSorted[mask211]["T"], y=loadPinSorted[mask211]["Load"], line= dict(color="yellow"), name="Cable 211", legendgroup="Cable 211", mode="lines"))
        fig2.add_trace(go.Scatter(x=loadPinSorted[mask212]["T"], y=loadPinSorted[mask212]["Load"], line= dict(color="purple"), name="Cable 212", legendgroup="Cable 212", mode="lines"))
        fig2.add_trace(go.Scatter(x=loadPinSorted[mask213]["T"], y=loadPinSorted[mask213]["Load"], line= dict(color="red"), name="Cable 213", legendgroup="Cable 213", mode="lines"))
        pngName = path.split('/')
        fig.update_layout(
            yaxis=dict(
                title="Load[KG]"
            ),
            legend= dict( 
                orientation="h",
                yanchor="middle",
                y=1.15,
                xanchor="center",
                x=0.5,
            ),
        )
        fig2.update_layout(
            yaxis=dict(
                title="Load[KG]"
            ),
            legend= dict( 
                orientation="h",
                yanchor="middle",
                y=1.15,
                xanchor="center",
                x=0.5,
            ),
        )
        fig.update_yaxes(tickangle=7.5)
        os.makedirs(os.path.dirname(path), exist_ok=True)

        json_path = path.replace(".json", "_LoadPins10X.json")
        pio.write_json(fig, json_path, pretty=False)
        
        os.chmod(json_path, 0o755)
        fig2.update_yaxes(tickangle=7.5)
        os.makedirs(os.path.dirname(path), exist_ok=True)

        json_path = path.replace(".json", "_LoadPins20X.json")
        pio.write_json(fig2, json_path, pretty=False)
        
        os.chmod(json_path, 0o755)
        
        #fig.write_html(path.replace(".html", "_LoadPins10X.html"), full_html=False, include_plotlyjs='cdn', auto_open=False, config=dict(toImageButtonOptions=dict(filename=pngName[-1].replace(".html", "")+"_LoadPins10X")))
        #fig2.write_html(path.replace(".html", "_LoadPins20X.html"), full_html=False, include_plotlyjs='cdn', auto_open=False, config=dict(toImageButtonOptions=dict(filename=pngName[-1].replace(".html", "")+"_LoadPins20X"))) #Added this two options to make the html file lighter, it causes a plotly.js to be loaded on the browser
