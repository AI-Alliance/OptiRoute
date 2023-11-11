import { Component, OnInit, ViewChild } from '@angular/core';
import { environment } from '../environments/environment';
import { HttpClient } from '@angular/common/http';
import { Observable, catchError, map, of } from 'rxjs';
import { MapInfoWindow, MapMarker, MapGeocoder } from '@angular/google-maps';
import { PlaceMarker, PlaceType } from './models/PlaceMarker';
import { Vehicle } from './models/Vehicle';
import { TaskService } from './services/task.service';




@Component({
  selector: 'app-root',
  templateUrl: './app.component.html',
  styleUrls: ['./app.component.css']
})
export class AppComponent implements OnInit {
  PlaceType: typeof PlaceType = PlaceType;
  selectedType: PlaceType = PlaceType.DEPOT;

  apiLoaded: Observable<boolean>;
  options: google.maps.MapOptions = {
    center: {lat: 54.36975172380843, lng: 18.610832380277717},
    zoom: 20,
    
  };

  @ViewChild(MapInfoWindow) infoWindow: MapInfoWindow | undefined;

  lastMarker: PlaceMarker | undefined;


  placeMarkers: PlaceMarker[] = [];
  vehicles: Vehicle[] = [];

  lastMatrix: google.maps.DistanceMatrixResponse | undefined;

  private distanceMatrixService: google.maps.DistanceMatrixService | undefined;
  constructor(private httpClient: HttpClient, private geocoder: MapGeocoder, private taskService: TaskService){
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

  getGeoInfo(marker: PlaceMarker){
    this.geocoder.geocode({
      location: marker.latLng
    }).subscribe(({results}) => {
      // this.placeMarkers.push(new PlaceMarker(results[0].geometry.location, PlaceType.CLIENT))
      console.log(results);
    });
  }

  addMarker(event: google.maps.MapMouseEvent) {
    if(!event.latLng){
      return;
    }
    
    if(this.hasDepotMarker() && this.selectedType == PlaceType.DEPOT){
      return;
    }

    this.placeMarkers.push(new PlaceMarker(event.latLng, this.selectedType));
    if(this.selectedType == PlaceType.DEPOT){
      this.selectedType = PlaceType.CLIENT;
    }
  }

  hasDepotMarker(){
    return this.placeMarkers.find((m) => m.type == PlaceType.DEPOT);
  }

  deleteMarker(marker: PlaceMarker){
    let markerToDelete = this.placeMarkers.findIndex(m => m.uuid == marker.uuid);
    if (markerToDelete < 0){
      return;
    }
    
    this.placeMarkers.splice(markerToDelete, 1);
  }
  

  openInfoWindow(marker: PlaceMarker, mapMarker: MapMarker) {
    this.lastMarker = marker;
    this.infoWindow?.open(mapMarker);
  }

  addVehicle(){
    this.vehicles.push(new Vehicle(0));
  }

  sendTask(){

    this.distanceMatrixService?.getDistanceMatrix(
      {
        origins: this.placeMarkers.map(m => m.latLng),
        destinations: this.placeMarkers.map(m => m.latLng),
        travelMode: google.maps.TravelMode.DRIVING
      },
      (response: google.maps.DistanceMatrixResponse | null) => {
        console.log(response); 
        if(!response){
          return;
        }

        this.taskService.sendTask(this.vehicles, this.placeMarkers, response).subscribe((response)=> console.log(response));

      }
    )
  }
}
