import { MapMarker } from '@angular/google-maps';
import { v4 as uuidv4 } from 'uuid';
export class PlaceMarker{
    uuid: string;
    latLng: google.maps.LatLng;
    type: PlaceType;
    demand: number;

    constructor(latLng: google.maps.LatLng, type: PlaceType){
        this.uuid = uuidv4();
        this.latLng = latLng;
        this.type = type;
        this.demand = 0;
    }
}

export enum PlaceType {
    DEPOT = 'depot',
    CLIENT = 'client'
}