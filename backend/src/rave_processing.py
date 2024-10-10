import pyvo as vo
import requests
import pandas as pd
from astropy.io import fits
import os
import numpy as np


def download_spectra_from_rave(ra, dec, token, output_dir='spectra_csv', search_radius=0.1):
    service_name = 'rave-survey.org'
    url = "https://www.rave-survey.org/tap"

    tap_session = requests.Session()
    tap_session.headers['Authorization'] = f'Token {token}'

    tap_service = vo.dal.TAPService(url, session=tap_session)

    sr = search_radius

    query_name = "simple_cs_adql"
    lang = 'ADQL'

    query = f'''
    SELECT rave_obs_id, ra_input, dec_input, DISTANCE(
        POINT('ICRS', ra_input, dec_input),
        POINT('ICRS', {ra:.4f}, {dec:.4f})
    ) AS dist
    FROM ravedr6.dr6_obsdata
    WHERE 1 = CONTAINS(
        POINT('ICRS', ra_input, dec_input),
        CIRCLE('ICRS', {ra:.4f}, {dec:.4f}, {sr:.4f})
    )
    '''

    try:
        job = tap_service.submit_job(query, language=lang, runid=query_name, queue="60s")
        job.run()
        job.wait(phases=["COMPLETED", "ERROR", "ABORTED"], timeout=300.) #don't know if it was really timing out but increased the time just in case.
        job.raise_if_error()
    except vo.dal.exceptions.DALQueryError:
        return []
    except Exception:
        return []

    try:
        tap_results = job.fetch_result()
        results = tap_results.to_table().to_pandas()
    except Exception:
        return []

    csv_paths = []

    fits_dir = './fits'
    spectra_csv_dir = output_dir

    os.makedirs(fits_dir, exist_ok=True)
    os.makedirs(spectra_csv_dir, exist_ok=True)

    for obs_id in results['rave_obs_id']:
        date = obs_id.split('_')[0]
        fits_url = f'https://www.rave-survey.org/files/fits/{date}/RAVE_{obs_id}.fits'
        fits_path = os.path.join(fits_dir, f'RAVE_{obs_id}.fits')

        try:
            response = requests.get(fits_url, timeout=60)
            if response.status_code == 200:
                with open(fits_path, 'wb') as f:
                    f.write(response.content)
            else:
                continue
        except requests.RequestException:
            continue

        try:
            with fits.open(fits_path) as hdul:
                spectrum_hdu = hdul['SPECTRUM']
                error_hdu = hdul['ERROR']

                crval1 = spectrum_hdu.header.get('CRVAL1')
                cdelt1 = spectrum_hdu.header.get('CDELT1')
                crpix1 = spectrum_hdu.header.get('CRPIX1')
                naxis1 = spectrum_hdu.header.get('NAXIS1')

                if None in (crval1, cdelt1, crpix1, naxis1):
                    continue

                wavelength = crval1 + (np.arange(naxis1) + 1 - crpix1) * cdelt1
                flux = spectrum_hdu.data
                error = error_hdu.data

                if flux is None or error is None:
                    continue

                df = pd.DataFrame({
                    'wavelength': wavelength,
                    'flux': flux,
                    'error': error
                })

                csv_path = os.path.join(spectra_csv_dir, f'{obs_id}.csv')
                df.to_csv(csv_path, index=False)
                csv_paths.append(csv_path)
        except Exception:
            continue
        finally:
            if os.path.exists(fits_path):
                try:
                    os.remove(fits_path)
                except Exception:
                    continue

    return csv_paths
