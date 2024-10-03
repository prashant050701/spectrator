import os
import numpy as np
from astropy.io import fits
import pandas as pd
import requests

def download_and_process_galah(source_id):
    output_dir = 'spectra_csv'
    os.makedirs(output_dir, exist_ok=True)
    galah_catalog_path = '/Users/prashanta.srivastava/PycharmProjects/spectrator/backend/src/galah_catalog/galah_dr4_filtered.csv'
    try:
        with open(galah_catalog_path, 'r') as file:
            for line in file:
                if source_id in line:
                    sobject_id = line.split(',')[0]
                    return download_galah_spectra(sobject_id, output_dir)
        print(f"Source ID {source_id} not found in GALAH catalog.")
        return None
    except Exception as e:
        print(f"Error reading GALAH catalog: {e}")
        return None

def download_galah_spectra(sobject_id, output_dir):
    base_url = "https://datacentral.org.au/vo/slink/links"
    filters = ['B', 'G', 'R', 'I']
    file_paths = []
    for filt in filters:
        url = f"{base_url}?ID={sobject_id}&DR=galah_dr3&IDX=0&FILT={filt}&RESPONSEFORMAT=fits"
        try:
            response = requests.get(url)
            if response.status_code == 200:
                fits_path = os.path.join(output_dir, f"{sobject_id}_{filt}.fits")
                with open(fits_path, 'wb') as f:
                    f.write(response.content)
                with fits.open(fits_path) as hdul:
                    data = hdul[0].data
                    header = hdul[0].header
                    wavelength_start = header['CRVAL1']
                    wavelength_delta = header['CDELT1']
                    wavelengths = wavelength_start + wavelength_delta * np.arange(len(data))
                    df = pd.DataFrame({'Wavelength': wavelengths, 'Flux': data})
                    csv_file = os.path.join(output_dir, f"{sobject_id}_{filt}.csv")
                    df.to_csv(csv_file, index=False)
                    file_paths.append(csv_file)
                os.remove(fits_path)
            else:
                print(f"Failed to download GALAH spectrum for {sobject_id} in filter {filt}.")
        except Exception as e:
            print(f"Error downloading GALAH spectrum for {sobject_id} in filter {filt}: {e}")
    if file_paths:
        return file_paths
    else:
        print(f"No GALAH spectra available for sobject_id {sobject_id}.")
        return None
