from astroquery.simbad import Simbad
from astropy.coordinates import SkyCoord
from astropy import units as u


def fetch_object_info(identifier):
    """
    Helper function to query SIMBAD for a single identifier and returns details including RA and Dec in decimal degrees.
    """
    Simbad.add_votable_fields('ids', 'ra', 'dec')
    result_info = {
        "gaia_id": None,
        "ra": None,
        "dec": None,
        "all_ids": []
    }

    try:
        result = Simbad.query_object(identifier)
        if result is not None:

            coord = SkyCoord(ra=result['RA'][0], dec=result['DEC'][0], unit=(u.hourangle, u.deg), frame='icrs')
            result_info['ra'] = coord.ra.deg
            result_info['dec'] = coord.dec.deg

            result_ids = Simbad.query_objectids(identifier)
            if result_ids is not None:
                result_info['all_ids'] = [id[0] for id in result_ids]

                gaia_entries = [entry for entry in result_info['all_ids'] if 'Gaia DR3' in entry]
                if gaia_entries:
                    result_info['gaia_id'] = gaia_entries[0].split()[-1]
        return result_info
    except Exception as e:
        print(f"Error querying SIMBAD for {identifier}: {e}")
        return None


#object_info = fetch_object_info("ATO J344.3272+45.2009")
#print(object_info)
