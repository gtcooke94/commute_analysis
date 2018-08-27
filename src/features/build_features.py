import polyline

def get_start_latlng(mp):
    pl = mp['summary_polyline']
    if pl:
        return(polyline.decode(pl)[0])
    
def get_end_latlng(mp):
    pl = mp['summary_polyline']
    if pl:
        return(polyline.decode(pl)[-1])
