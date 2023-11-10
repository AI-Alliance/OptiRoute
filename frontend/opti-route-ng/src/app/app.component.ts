import { Component, OnInit, ViewChild } from '@angular/core';
import { environment } from '../environments/environment';
import { HttpClient } from '@angular/common/http';
import { Observable, catchError, map, of } from 'rxjs';
import { MapInfoWindow, MapMarker, MapGeocoder } from '@angular/google-maps';
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

  lastMatrix: google.maps.DistanceMatrixResponse | undefined;

  private distanceMatrixService: google.maps.DistanceMatrixService | undefined;
  constructor(private httpClient: HttpClient, private geocoder: MapGeocoder){
    this.apiLoaded = this.httpClient.jsonp('https://maps.googleapis.com/maps/api/js?key=' + environment.gMapsApiKey, 'callback').pipe(
      map(() => {this.onApiLoaded(); return true}),
      catchError((error) => {
        console.error(error);
        return of(false);
      }),
    );
  }



  onApiLoaded(){
    this.distanceMatrixService = new google.maps.DistanceMatrixService();
    
  }

  ngOnInit(): void {
   
  
  }

  getDistanceMatrix(){
    this.distanceMatrixService?.getDistanceMatrix(
      {
        origins: this.clientMarkers.map(m => m.latLng),
        destinations: this.clientMarkers.map(m => m.latLng),
        travelMode: google.maps.TravelMode.DRIVING
      },
      (response) => {
        console.log(response); 
        if(response){
          this.lastMatrix = response;
        }
      }
    )
  }

  getGeoInfo(marker: ClientMarker){
    this.geocoder.geocode({
      location: marker.latLng
    }).subscribe(({results}) => {
      console.log(results);
    });
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
