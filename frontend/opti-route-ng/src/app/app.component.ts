import { Component, OnInit, ViewChild } from '@angular/core';
import { environment } from '../environments/environment';
import { HttpClient } from '@angular/common/http';
import { Observable, catchError, map, of } from 'rxjs';
import { MapInfoWindow, MapMarker } from '@angular/google-maps';
import { ClientMarker } from './models/ClientMarker';
@Component({
  selector: 'app-root',
  templateUrl: './app.component.html',
  styleUrls: ['./app.component.css']
})
export class AppComponent implements OnInit {

  apiLoaded: Observable<boolean>;
  options: google.maps.MapOptions = {
    center: {lat: 54.36975172380843, lng: 18.610832380277717},
    zoom: 20,
    
  };

  @ViewChild(MapInfoWindow) infoWindow: MapInfoWindow | undefined;

  lastMarker: ClientMarker | undefined;

  markerOptions: google.maps.MarkerOptions = {draggable: false};
  clientMarkers: ClientMarker[] = [];
  constructor(httpClient: HttpClient){
    this.apiLoaded = httpClient.jsonp('https://maps.googleapis.com/maps/api/js?key=' + environment.gMapsApiKey, 'callback').pipe(
      map(() => {
        return true;
      }),
      catchError((error) => {
        console.error(error);
        return of(false);
      }),
    );
  }

  ngOnInit(): void {
    
  
  }

  addMarker(event: google.maps.MapMouseEvent) {
    if(!event.latLng){
      return;
    }
    
    this.clientMarkers.push(new ClientMarker(event.latLng));
  }

  deleteMarker(marker: ClientMarker){
    let markerToDelete = this.clientMarkers.findIndex(m => m.uuid == marker.uuid);
    if (markerToDelete < 0){
      return;
    }
    
    this.clientMarkers.splice(markerToDelete, 1);
  }
  

  openInfoWindow(marker: ClientMarker, mapMarker: MapMarker) {
    this.lastMarker = marker;
    this.infoWindow?.open(mapMarker);
  }
}
