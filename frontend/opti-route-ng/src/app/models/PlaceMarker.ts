import { MapMarker } from '@angular/google-maps';
import { v4 as uuidv4 } from 'uuid';
export class PlaceMarker{
    uuid: string;
    placeId: string = '';
    latLng: google.maps.LatLng;
    type: PlaceType;
    demand: number;
    markerOptions!: google.maps.MarkerOptions;
    text: string | null = null;

    constructor(latLng: google.maps.LatLng, type: PlaceType){
        this.uuid = uuidv4();
        this.latLng = latLng;
        this.type = type;
        this.demand = 0;
        this.setMarketOptions();
    }

    setText(text: string | null){
        this.text = text;
        this.setMarketOptions();
    }

    private setMarketOptions(){
       let opitons: google.maps.MarkerOptions = {
        draggable: false, 
        label: {text: this.text ?? this.type.charAt(0).toUpperCase(), fontSize: '30px'}
        };
        let icon: google.maps.Symbol = {path: '', fillColor: '', fillOpacity: 0.5, scale: 0.7 };
        
        switch(this.type){
            case PlaceType.DEPOT: {
                icon.path = Icons.DEPOT;
                icon.fillColor = 'blue';
                break;
            }
            default: {
                icon.path = Icons.CLIENT;
                icon.fillColor = 'red';
            }
        }
        
        opitons.icon = icon;

        this.markerOptions = opitons;
    }
}
enum Icons{
    CLIENT = 'M24-28.3c-.2-13.3-7.9-18.5-8.3-18.7l-1.2-.8-1.2.8c-2 1.4-4.1 2-6.1 2-3.4 0-5.8-1.9-5.9-1.9l-1.3-1.1-1.3 1.1c-.1.1-2.5 1.9-5.9 1.9-2.1 0-4.1-.7-6.1-2l-1.2-.8-1.2.8c-.8.6-8 5.9-8.2 18.7-.2 1.1 2.9 22.2 23.9 28.3 22.9-6.7 24.1-26.9 24-28.3z',
    DEPOT = 'M24-8c0 4.4-3.6 8-8 8h-32c-4.4 0-8-3.6-8-8v-32c0-4.4 3.6-8 8-8h32c4.4 0 8 3.6 8 8v32z'
}

export enum PlaceType {
    DEPOT = 'depot',
    CLIENT = 'client'
}