import os
import requests
from astroquery.gaia import Gaia
import galah_processing

def download_spectrum(source_id):
    output_dir = 'spectra_csv'
    os.makedirs(output_dir, exist_ok=True)

    gaia_file_path, gaia_source_type = download_spectrum_from_gaia(source_id, output_dir)
    lamost_file_path, lamost_source_type = download_spectrum_from_lamost(source_id)
    galah_file_paths = galah_processing.download_and_process_galah(source_id)

    results = {}
    if gaia_file_path:
        results[gaia_source_type] = [gaia_file_path]
    if lamost_file_path:
        results[lamost_source_type] = [lamost_file_path]
    if galah_file_paths:
        results["GALAH"] = galah_file_paths

    return results

def download_spectrum_from_gaia(source_id, output_dir):
    try:
        datalink = Gaia.load_data(
            ids=[source_id],
            data_release="Gaia DR3",
            retrieval_type="RVS",
            format="votable"
        )
        for filename, votable in datalink.items():
            table = votable[0].to_table()
            csv_file = os.path.join(output_dir, f"{source_id}.csv")
            table.write(csv_file, format='csv', overwrite=True)

            return csv_file, "Gaia_RVS"
        print(f"No Gaia data found for source ID {source_id}")
        return None, "Gaia_RVS"
    except Exception as e:
        print(f"Error downloading Gaia data for {source_id}: {e}")
        return None, "Gaia_RVS"

def download_spectrum_from_lamost(source_id):
    lamost_catalog_path = '/Users/prashanta.srivastava/PycharmProjects/spectrator/backend/src/lamost_catalog/filtered_dr7.csv'
    try:
        with open(lamost_catalog_path, 'r') as file:
            for line in file:
                if source_id in line:
                    obsid = line.split(',')[0]
                    return download_spectrum_lamost(obsid)
        print(f"Source ID {source_id} not found in LAMOST catalog.")
        return None, "LAMOST"
    except Exception as e:
        print(f"Error reading LAMOST catalog: {e}")
        return None, "LAMOST"

def download_spectrum_lamost(obsid):
    url = f"http://dr7.lamost.org/spectrum/fits2csv/{obsid}"
    try:
        response = requests.get(url)
        response.raise_for_status()
        csv_content = response.text
        csv_file_path = f"spectra_csv/lamost_{obsid}.csv"
        with open(csv_file_path, 'w') as file:
            file.write(csv_content)
        return csv_file_path, "LAMOST"
    except Exception as e:
        print(f"Failed to download LAMOST spectrum for OBSID {obsid}: {e}")
        return None, "LAMOST"
