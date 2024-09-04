from flask import Flask, jsonify
from flask_cors import CORS  # Import CORS
import os
import pandas as pd
import matplotlib.pyplot as plt
from io import BytesIO
import base64
import pvlib
from pvlib import location
from pvlib.irradiance import get_total_irradiance
from pvlib.pvarray import pvefficiency_adr

app = Flask(__name__)
CORS(app)  # Apply CORS to your Flask app

@app.route('/calculate', methods=['POST'])
def calculate_pv():
    # Celsius to Fahrenheit conversion for Graph
    

    # Define location for Lubbock, Texas
    lubbock = location.Location(latitude=33.5779, longitude=-101.8552, tz='US/Central', altitude=1000, name='Lubbock')

    # Define the time range for the simulation
    times = pd.date_range(start='2024-07-01', end='2024-07-02', freq='1min', tz=lubbock.tz)

    # Get clear sky data for Lubbock
    cs = lubbock.get_clearsky(times)

    # Assuming constant air temperature and wind speed for simplicity
    df = pd.DataFrame({
        'ghi': cs['ghi'],
        'dhi': cs['dhi'],
        'dni': cs['dni'],
        'temp_air': 25,  # Example air temperature in Celsius
        'wind_speed': 2  # Example wind speed in m/s
    })

    # Calculate solar position
    solpos = lubbock.get_solarposition(times)

    # Define system parameters
    TILT = 30  # Tilt angle in degrees
    ORIENT = 180  # Azimuth angle in degrees

    # Calculate total irradiance on the plane of array
    total_irrad = get_total_irradiance(TILT, ORIENT,
                                       solpos.apparent_zenith, solpos.azimuth,
                                       df.dni, df.ghi, df.dhi)

    df['poa_global'] = total_irrad.poa_global

    # Calculate PV module temperature
    df['temp_pv'] = pvlib.temperature.faiman(df.poa_global, df.temp_air,
                                              df.wind_speed)

    # ADR model parameters for PV efficiency
    adr_params = {'k_a': 0.99924,
                  'k_d': -5.49097,
                  'tc_d': 0.01918,
                  'k_rs': 0.06999,
                  'k_rsh': 0.26144
                  }

    df['eta_rel'] = pvefficiency_adr(df['poa_global'], df['temp_pv'], **adr_params)

    # Set the desired array size:
    P_STC = 5000.   # (W)

    # and the irradiance level needed to achieve this output:
    G_STC = 1000.   # (W/m2)

    df['p_mp'] = P_STC * df['eta_rel'] * (df['poa_global'] / G_STC)

    # Plot 1: Relative Efficiency vs Irradiance
    fig1, ax1 = plt.subplots()
    pc = ax1.scatter(df['poa_global'], df['eta_rel'], c=df['temp_pv'], cmap='jet')
    fig1.colorbar(pc, label='Temperature [C]', ax=ax1)
    pc.set_alpha(0.25)
    ax1.grid(alpha=0.5)
    ax1.set_ylim(0.48)
    ax1.set_xlabel('Irradiance [W/m²]')
    ax1.set_ylabel('Relative efficiency [-]')
    
    img1 = BytesIO()
    fig1.savefig(img1, format='png')
    img1.seek(0)
    plot1_url = base64.b64encode(img1.getvalue()).decode('utf-8')

    # Plot 2: Array Power vs Irradiance
    fig2, ax2 = plt.subplots()
    pc = ax2.scatter(df['poa_global'], df['p_mp'], c=df['temp_pv'], cmap='jet')
    fig2.colorbar(pc, label='Temperature [C]', ax=ax2)
    pc.set_alpha(0.25)
    ax2.grid(alpha=0.5)
    ax2.set_xlabel('Irradiance [W/m²]')
    ax2.set_ylabel('Array power [W]')
    
    img2 = BytesIO()
    fig2.savefig(img2, format='png')
    img2.seek(0)
    plot2_url = base64.b64encode(img2.getvalue()).decode('utf-8')

    return jsonify({
        'plot1_url': f"data:image/png;base64,{plot1_url}",
        'plot2_url': f"data:image/png;base64,{plot2_url}",
    })

if __name__ == '__main__':
    app.run(debug=True)
