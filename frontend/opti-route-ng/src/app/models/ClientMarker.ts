import { MapMarker } from '@angular/google-maps';
import { v4 as uuidv4 } from 'uuid';
export class ClientMarker{
    uuid: string;
    marker: MapMarker | undefined;
    latLng: google.maps.LatLng;

    constructor(latLng: google.maps.LatLng, marker: MapMarker | undefined = undefined){
        this.uuid = uuidv4();
        this.latLng = latLng;
        this.marker = marker;
    }
}